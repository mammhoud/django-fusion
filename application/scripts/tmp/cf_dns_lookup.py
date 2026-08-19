#!/usr/bin/env python3
"""Read-only Cloudflare API probe.

Reads credentials from application/proxy/.env, then lists the structa.cloud
zone and the DNS records for the four hosts we care about. Never prints secret
values (only lengths and record data).
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ENV_PATH = Path("application/proxy/.env")


def load_env(path: Path) -> dict:
    env = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        env[key] = val
    return env


def cf(method: str, url: str, token: str, email: str = "", api_key: str = "") -> dict:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    elif email and api_key:
        headers["X-Auth-Email"] = email
        headers["X-Auth-Key"] = api_key
    req = urllib.request.Request(url, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def main() -> int:
    env = load_env(ENV_PATH)
    token = env.get("CLOUDFLARE_DNS_API_TOKEN") or env.get("CF_DNS_API_TOKEN") or ""
    email = env.get("CLOUDFLARE_EMAIL") or env.get("CF_API_EMAIL") or ""
    api_key = env.get("CLOUDFLARE_API_KEY") or env.get("CF_API_KEY") or ""

    print(f"token_len={len(token)} email_len={len(email)} api_key_len={len(api_key)}")
    if not token and not (email and api_key):
        print("ERROR: no usable Cloudflare credentials in .env")
        return 1

    zones = cf("GET", "https://api.cloudflare.com/client/v4/zones?name=structa.cloud",
               token, email, api_key)
    print("zone_lookup_success:", zones.get("success"))
    if not zones.get("success"):
        print("zone_errors:", json.dumps(zones.get("errors")))
        return 1

    zone_id = None
    for z in zones.get("result", []):
        print(f"  zone: {z['name']}  id={z['id']}  status={z['status']}")
        if z["name"] == "structa.cloud":
            zone_id = z["id"]

    if not zone_id:
        print("ERROR: structa.cloud zone not found for this account/token")
        return 1

    hosts = ["filegator", "code", "ws", "blinko", "docs"]
    for h in hosts:
        name = f"{h}.structa.cloud"
        url = (f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
               f"?name={name}")
        try:
            rec = cf("GET", url, token, email, api_key)
        except Exception as exc:  # noqa: BLE001
            print(f"  {name}: ERROR {exc}")
            continue
        if not rec.get("success"):
            print(f"  {name}: API error {json.dumps(rec.get('errors'))}")
            continue
        for r in rec.get("result", []):
            print(f"  {name}: type={r['type']} content={r['content']} "
                  f"proxied={r.get('proxied')} ttl={r.get('ttl')} id={r['id']}")
        if not rec.get("result"):
            print(f"  {name}: (no records)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
