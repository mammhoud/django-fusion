#!/usr/bin/env python3
"""Pre-issuance DNS check for Let's Encrypt HTTP-01.

Scans the Traefik dynamic config for routers that carry
``tls.certResolver: letsencrypt-http`` (i.e. the domains that will trigger ACME
issuance), resolves each domain's A/AAAA records against public resolvers, and
warns when a record points off-host or is missing entirely.

Off-host records are the exact cause of:

    acme: error: tls :: <ipv6>: ... remote error: tls: internal error

which happens when a stale AAAA record resolves to a host that is not this
server, so Let's Encrypt follows the HTTP->HTTPS redirect on the wrong box and
fails the challenge.

Exit codes: 0 = all clear, 1 = DNS misconfigured, 2 = tooling missing.
"""

from __future__ import annotations

import argparse
import ipaddress
import pathlib
import re
import shutil
import subprocess
import sys

import yaml

PROXY_DIR = pathlib.Path(__file__).resolve().parents[1]
DYNAMIC_DIR = PROXY_DIR / "configs" / "traefik" / "dynamic"

RESOLVERS = ("1.1.1.1", "8.8.8.8")

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
NC = "\033[0m"


def _run(cmd: list[str]) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None


def host_public_ips() -> tuple[set[str], set[str]]:
    """Return (ipv4, ipv6) sets of public (global unicast) addresses on this host."""
    ipv4: set[str] = set()
    ipv6: set[str] = set()
    if not shutil.which("ip"):
        return ipv4, ipv6
    result = _run(["ip", "-o", "addr", "show", "scope", "global"])
    if not result or result.returncode != 0:
        return ipv4, ipv6
    for line in result.stdout.splitlines():
        match = re.search(r"\binet6?\s+([0-9a-fA-F:.]+)/", line)
        if not match:
            continue
        try:
            addr = ipaddress.ip_address(match.group(1))
        except ValueError:
            continue
        if not addr.is_global:
            continue
        (ipv6 if addr.version == 6 else ipv4).add(str(addr))
    return ipv4, ipv6


def resolve(host: str, qtype: str) -> list[str]:
    """Resolve *host* via public resolvers, returning deduped A/AAAA addresses."""
    addresses: list[str] = []
    for resolver in RESOLVERS:
        result = _run(["dig", "+short", qtype, host, f"@{resolver}"])
        if not result:
            continue
        for token in result.stdout.split():
            token = token.rstrip(".")
            try:
                ipaddress.ip_address(token)
            except ValueError:
                continue  # CNAME chain or other non-address token
            if token not in addresses:
                addresses.append(token)
    return addresses


def cert_resolver_domains() -> list[str]:
    """Return public domains whose router uses the HTTP-01 cert resolver."""
    domains: list[str] = []
    for file in sorted(DYNAMIC_DIR.glob("*.yml")):
        try:
            doc = yaml.safe_load(file.read_text())
        except Exception:
            continue
        if not isinstance(doc, dict):
            continue
        routers = (doc.get("http") or {}).get("routers") or {}
        for router in routers.values():
            if not isinstance(router, dict):
                continue
            tls = router.get("tls")
            if not (isinstance(tls, dict) and tls.get("certResolver") == "letsencrypt-http"):
                continue
            for host in re.findall(r"Host\(`([^`]+)`\)", router.get("rule", "")):
                if host == "localhost" or host.endswith(".localhost"):
                    continue
                if host not in domains:
                    domains.append(host)
    return domains


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "domains",
        nargs="*",
        help="Extra domains to check (defaults to HTTP-01 certResolver domains)",
    )
    args = parser.parse_args()

    if not shutil.which("dig"):
        print(f"{RED}✗{NC} 'dig' is required but not installed (bind-utils / dnsutils).")
        return 2

    domains = cert_resolver_domains()
    for extra in args.domains:
        if extra not in domains:
            domains.append(extra)

    ipv4, ipv6 = host_public_ips()
    if not ipv4 and not ipv6:
        print(
            f"{YELLOW}⚠{NC} could not detect any public IP on this host; "
            "off-host comparisons will be skipped (A/AAAA presence still checked)."
        )

    print(f"Public host IPv4: {', '.join(sorted(ipv4)) or '(none detected)'}")
    print(f"Public host IPv6: {', '.join(sorted(ipv6)) or '(none detected)'}")
    print()

    problems = 0
    for host in domains:
        a_records = resolve(host, "A")
        aaaa_records = resolve(host, "AAAA")

        issues: list[str] = []

        if not a_records:
            issues.append("no public A record (NXDOMAIN) — HTTP-01 will fail DNS")
        elif ipv4:
            off_host = [a for a in a_records if a not in ipv4]
            if off_host:
                issues.append(f"A {', '.join(off_host)} is off-host")

        if aaaa_records and ipv6:
            off_host = [a for a in aaaa_records if a not in ipv6]
            if off_host:
                issues.append(
                    f"AAAA {', '.join(off_host)} is off-host "
                    "(causes 'acme: error: tls ... remote error: tls: internal error')"
                )
        elif aaaa_records and not ipv6:
            issues.append(
                f"AAAA {', '.join(aaaa_records)} present but this host has no public IPv6 "
                "(remove the AAAA record or add the address to this host)"
            )

        if issues:
            problems += 1
            print(f"{RED}✗{NC} {host}")
            for issue in issues:
                print(f"    - {issue}")
        else:
            a_summary = f"A={', '.join(a_records) or '-'}"
            aaaa_summary = f"AAAA={', '.join(aaaa_records) or '-'}"
            print(f"{GREEN}✓{NC} {host:<28} {a_summary:<28} {aaaa_summary}")

    print()
    if problems:
        print(
            f"{RED}{problems} domain(s) have off-host or missing records.{NC} "
            "Fix DNS before triggering issuance, then restart the proxy."
        )
        return 1
    print(f"{GREEN}All {len(domains)} domain(s) resolve to this host.{NC}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
