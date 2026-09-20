#!/usr/bin/env python3
"""Post-deployment health and certificate check for a live vhost.

If ``make proxy-dns-check`` answers "will ACME issuance work?", this answers
"is the site actually serving?". For each host it verifies, over a real TLS
connection:

  * the HTTPS endpoint answers, and with which status code;
  * the served certificate is **publicly trusted** (a host that fell back to the
    development self-signed certificate fails here — that is exactly what a
    certificate request including an unresolvable name like
    ``www.<domain>`` silently causes, because one router requests ONE
    certificate for all of its rule's hostnames);
  * the certificate actually covers the host, and how long it has left.

The defaults target the PlanInc deployment at notes.structa.cloud. Any number of
other hosts may be given as arguments, and ``--path`` selects the probe path.

Exit codes: 0 = all healthy, 1 = a problem was found, 2 = invalid usage.
"""

from __future__ import annotations

import argparse
import datetime
import http.client
import os
import socket
import ssl
import sys
import tempfile

DEFAULT_HOST = "notes.structa.cloud"
DEFAULT_PATH = "/health"
# Renewal starts well before this; a shorter window means Traefik is not
# renewing and the certificate is about to expire.
EXPIRY_WARN_DAYS = 14

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
NC = "\033[0m"


def decode_der(raw: bytes | None) -> dict:
    """Decode a DER certificate into the same mapping getpeercert() returns.

    Python only parses the peer certificate for a *verifying* context, so an
    untrusted chain reports an empty dict exactly when the details are most
    useful — naming which hosts a fallback self-signed certificate covers.
    """
    if not raw:
        return {}
    handle, path = tempfile.mkstemp(suffix=".pem")
    try:
        with os.fdopen(handle, "wb") as pem:
            pem.write(ssl.DER_cert_to_PEM_cert(raw).encode())
        return ssl._ssl._test_decode_cert(path)  # noqa: SLF001 - stdlib-only decoder
    except (OSError, ssl.SSLError, ValueError):
        return {}
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def probe(host: str, path: str, timeout: float = 10.0) -> dict:
    """Fetch https://host/path, reporting the response and the peer certificate.

    The request is first attempted with a verifying context. A development
    self-signed certificate raises SSLCertVerificationError, so the probe is
    repeated unverified purely to describe what the host served — that is the
    failure this check exists to surface, not to hide.
    """
    result: dict = {
        "status": None,
        "trusted": False,
        "verify_error": None,
        "cert": None,
        "error": None,
    }

    for context in (ssl.create_default_context(), ssl._create_unverified_context()):  # noqa: SLF001
        connection = http.client.HTTPSConnection(host, 443, timeout=timeout, context=context)
        try:
            connection.request("GET", path, headers={"user-agent": "proxy-site-check"})
            response = connection.getresponse()
            response.read(2048)
            result["status"] = response.status
            if context.verify_mode == ssl.CERT_REQUIRED:
                result["cert"] = connection.sock.getpeercert()
                result["trusted"] = True
            else:
                result["cert"] = decode_der(connection.sock.getpeercert(binary_form=True))
            return result
        except ssl.SSLCertVerificationError as exc:
            result["verify_error"] = exc.verify_message or str(exc)
        except (OSError, http.client.HTTPException, socket.error) as exc:
            # Connection refused / DNS failure / timeout: nothing more to learn.
            result["error"] = str(exc)
            return result
        finally:
            connection.close()

    return result


def cert_days_left(cert: dict | None) -> int | None:
    if not cert or not cert.get("notAfter"):
        return None
    expires = datetime.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(
        tzinfo=datetime.timezone.utc
    )
    return (expires - datetime.datetime.now(datetime.timezone.utc)).days


def cert_names(cert: dict | None) -> tuple[str, set[str]]:
    """Return (subject common name, every name the certificate covers).

    Both DNS and IP subjectAltName entries are collected, so probing an address
    (for example 127.0.0.1) reports coverage rather than an empty name set.
    """
    if not cert:
        return "", set()
    subject = ""
    for rdn in cert.get("subject", ()):
        for key, value in rdn:
            if key == "commonName":
                subject = value
    names = {value for kind, value in cert.get("subjectAltName", ()) if kind in ("DNS", "IP Address")}
    if subject:
        names.add(subject)
    return subject, names


def check_host(host: str, path: str) -> int:
    """Print the report for one host; return the number of problems found."""
    result = probe(host, path)

    if result["error"]:
        print(f"{RED}✗{NC} {host}")
        print(f"    - unreachable: {result['error']}")
        return 1

    subject, names = cert_names(result["cert"])
    days = cert_days_left(result["cert"])
    problems: list[str] = []

    if not result["trusted"]:
        problems.append(
            "certificate is NOT publicly trusted"
            + (f" ({result['verify_error']})" if result["verify_error"] else "")
            + " — the host fell back to the development self-signed certificate; "
              "check that every hostname in its router rule has a DNS record"
        )
    if not names:
        # The certificate could not be parsed at all; the trust problem above is
        # the finding, and coverage/expiry would only add noise.
        problems.append("certificate details unavailable — could not parse the served certificate")
    elif host not in names:
        problems.append(f"certificate does not cover {host} (covers: {', '.join(sorted(names))})")
    if days is None:
        if names:
            problems.append("could not read the certificate expiry")
    elif days < 0:
        problems.append("certificate has EXPIRED")
    elif days < EXPIRY_WARN_DAYS:
        problems.append(f"certificate expires in {days} day(s) — renewal is not happening")

    status = result["status"]
    if status is None or status >= 500:
        problems.append(f"endpoint returned {status} (backend unavailable?)")
    elif status >= 400 and status not in (401, 403):
        problems.append(f"endpoint returned {status}")

    # 401/403 are expected answers for a protected app and still prove that
    # TLS, routing and the backend are all working.
    if problems:
        print(f"{RED}✗{NC} {host}{path} — HTTP {status}")
        for problem in problems:
            print(f"    - {problem}")
        return len(problems)

    print(
        f"{GREEN}✓{NC} {host}{path} — HTTP {status}, "
        f"cert CN={subject or '-'}, expires in {days} day(s)"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "hosts",
        nargs="*",
        default=[DEFAULT_HOST],
        help=f"hosts to check (default: {DEFAULT_HOST})",
    )
    parser.add_argument("--path", default=DEFAULT_PATH, help=f"probe path (default: {DEFAULT_PATH})")
    args = parser.parse_args()

    hosts = args.hosts or [DEFAULT_HOST]
    problems = sum(check_host(host, args.path) for host in hosts)

    print()
    if problems:
        print(f"{RED}{problems} problem(s) found.{NC}")
        return 1
    print(f"{GREEN}All {len(hosts)} host(s) healthy.{NC}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
