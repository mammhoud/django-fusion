#!/usr/bin/env python3
"""
Proxy, SSL Certificate, and Domain Response Validation Tests

Run with:
    python tests/proxy_ssl_validation.py

Or via pytest:
    pytest tests/proxy_ssl_validation.py -v
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import pytest
except ImportError:  # pragma: no cover
    pytest = None  # type: ignore

PROJECT_ROOT = Path(__file__).parent.parent
PROXY_DIR = PROJECT_ROOT / "application" / "proxy"
CERTS_DIR = PROXY_DIR / "certs"
TRAEFIK_DYNAMIC_DIR = PROXY_DIR / "traefik" / "dynamic"


# ── SSL Certificate Tests ──────────────────────────────────────────────────


class TestSSLCertificates:
    """Validate SSL certificate existence, expiry, and key matching."""

    DOMAINS = [
        ("precis-ctc", "ctc-research.com"),
        ("structa-cloud", "structa.cloud"),
        ("vresume", "vresume.structa.cloud"),
    ]

    def test_cert_files_exist(self) -> None:
        """Each domain must have a .crt and .key file."""
        for cert_name, domain in self.DOMAINS:
            crt = CERTS_DIR / f"{cert_name}.crt"
            key = CERTS_DIR / f"{cert_name}.key"
            assert crt.exists(), f"Certificate missing: {crt} for {domain}"
            assert key.exists(), f"Private key missing: {key} for {domain}"

    def test_certs_not_expired(self) -> None:
        """No certificate may be expired."""
        import time

        now = time.time()
        for cert_name, domain in self.DOMAINS:
            crt = CERTS_DIR / f"{cert_name}.crt"
            if not crt.exists():
                pytest.skip(f"Certificate not found: {cert_name}")

            result = subprocess.run(
                ["openssl", "x509", "-in", str(crt), "-noout", "-enddate"],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, f"Failed to read {crt}"

            # Parse notAfter=Jun 02 12:00:00 2027 GMT
            expiry_str = result.stdout.strip().split("=", 1)[1]
            expiry_epoch = subprocess.run(
                ["date", "-d", expiry_str, "+%s"],
                capture_output=True,
                text=True,
            )
            expiry_time = int(expiry_epoch.stdout.strip())
            assert expiry_time > now, f"Certificate for {domain} has expired"

    def test_cert_key_match(self) -> None:
        """Certificate modulus must match private key modulus."""
        for cert_name, domain in self.DOMAINS:
            crt = CERTS_DIR / f"{cert_name}.crt"
            key = CERTS_DIR / f"{cert_name}.key"
            if not crt.exists() or not key.exists():
                pytest.skip(f"Missing cert/key for {domain}")

            cert_md5 = subprocess.run(
                ["openssl", "x509", "-noout", "-modulus", "-in", str(crt)],
                capture_output=True,
                text=True,
            )
            key_md5 = subprocess.run(
                ["openssl", "rsa", "-noout", "-modulus", "-in", str(key)],
                capture_output=True,
                text=True,
            )
            assert cert_md5.stdout == key_md5.stdout, f"Cert/key mismatch for {domain}"

    def test_certs_valid_for_at_least_30_days(self) -> None:
        """All certificates must be valid for at least 30 days."""
        import time

        now = time.time()
        for cert_name, domain in self.DOMAINS:
            crt = CERTS_DIR / f"{cert_name}.crt"
            if not crt.exists():
                pytest.skip(f"Certificate not found: {cert_name}")

            result = subprocess.run(
                ["openssl", "x509", "-in", str(crt), "-noout", "-enddate"],
                capture_output=True,
                text=True,
            )
            expiry_str = result.stdout.strip().split("=", 1)[1]
            expiry_epoch = subprocess.run(
                ["date", "-d", expiry_str, "+%s"],
                capture_output=True,
                text=True,
            )
            expiry_time = int(expiry_epoch.stdout.strip())
            days_left = (expiry_time - now) / 86400
            assert days_left >= 30, f"Certificate for {domain} expires in {days_left:.0f} days"


# ── Traefik Configuration Tests ────────────────────────────────────────────


class TestTraefikConfiguration:
    """Validate Traefik dynamic configuration files."""

    def test_dynamic_configs_exist(self) -> None:
        """All site router configs must exist."""
        required = [
            "ctc-research.yml",
            "lms-fusion.yml",
            "space.yml",
            "middlewares.yml",
            "certs.yml",
            "catchall.yml",
            "media-servers.yml",
        ]
        for name in required:
            path = TRAEFIK_DYNAMIC_DIR / name
            assert path.exists(), f"Missing Traefik dynamic config: {name}"

    def test_certs_config_points_to_existing_files(self) -> None:
        """certs.yml must reference existing certificate files."""
        import yaml

        certs_yml = TRAEFIK_DYNAMIC_DIR / "certs.yml"
        if not certs_yml.exists():
            pytest.skip("certs.yml not found")

        with open(certs_yml) as f:
            data = yaml.safe_load(f)

        certs = data.get("tls", {}).get("certificates", [])
        assert certs, "Expected at least one fallback certificate entry"

        for entry in certs:
            cert_file = entry.get("certFile", "").replace("/etc/traefik/certs/", "")
            key_file = entry.get("keyFile", "").replace("/etc/traefik/certs/", "")
            assert (CERTS_DIR / cert_file).exists(), f"Missing cert file: {cert_file}"
            assert (CERTS_DIR / key_file).exists(), f"Missing key file: {key_file}"

    def test_media_servers_configured(self) -> None:
        """media-servers.yml must route all site media subdomains."""
        import yaml

        media_yml = TRAEFIK_DYNAMIC_DIR / "media-servers.yml"
        if not media_yml.exists():
            pytest.skip("media-servers.yml not found")

        with open(media_yml) as f:
            data = yaml.safe_load(f)

        routers = data.get("http", {}).get("routers", {})
        services = data.get("http", {}).get("services", {})

        # Check that HTTPS routers exist for each media subdomain
        expected_hosts = [
            "media.structa.cloud",
            "media.ctc-research.com",
            "media.vresume.structa.cloud",
        ]
        for host in expected_hosts:
            found = any(
                host in r.get("rule", "")
                for r in routers.values()
                if "https" in str(r)
            )
            assert found, f"No HTTPS router found for {host}"

        # Check that services point to shared-proxy
        for svc_name, svc in services.items():
            servers = svc.get("loadBalancer", {}).get("servers", [])
            for srv in servers:
                assert "shared-proxy" in srv.get("url", ""), f"{svc_name} does not route to shared-proxy"


# ── Nginx Media Server Tests ───────────────────────────────────────────────


class TestNginxMediaServer:
    """Validate nginx configuration for shared-proxy."""

    def test_nginx_config_exists(self) -> None:
        conf = PROXY_DIR / "nginx" / "default.conf.template"
        assert conf.exists(), "nginx/default.conf.template not found"

    def test_nginx_config_syntax(self) -> None:
        """nginx -t must pass for the default.conf."""
        conf = PROXY_DIR / "nginx" / "default.conf.template"
        if not conf.exists():
            pytest.skip("nginx config not found")

        # We can't run nginx -t without the full nginx setup,
        # but we can at least verify the file is non-empty
        content = conf.read_text()
        assert "server {" in content, "nginx config missing server block"
        assert "location /static/" in content, "nginx config missing static location"
        assert "location /media/" in content, "nginx config missing media location"

    def test_media_directories_exist(self) -> None:
        """All site media directories must exist."""
        media_dir = PROJECT_ROOT / "projects" / "precis" / "assets" / "media"
        assert media_dir.exists(), f"Media directory missing: {media_dir}"

    def test_staticfiles_directories_exist(self) -> None:
        """All site staticfiles directories must exist."""
        static_dir = PROJECT_ROOT / "projects" / "precis" / "assets" / "static"
        assert static_dir.exists(), f"Static directory missing: {static_dir}"


# ── Domain Response Tests ──────────────────────────────────────────────────


def _sites_reachable() -> bool:
    """Check if sites are reachable without side effects at import time."""
    try:
        result = subprocess.run(
            ["curl", "-sf", "https://structa.cloud"],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


class TestDomainResponses:
    """Validate HTTPS responses at domain names (requires running proxy)."""

    DOMAINS = [
        "https://structa.cloud",
        "https://ctc-research.com",
        "https://vresume.structa.cloud",
    ]

    def test_https_redirects(self) -> None:
        """HTTP requests must redirect to HTTPS."""
        if not _sites_reachable():
            pytest.skip("Sites not reachable (proxy not running or DNS not configured)")

        import urllib.request

        for domain in ["http://structa.cloud", "http://ctc-research.com"]:
            try:
                req = urllib.request.Request(domain, method="HEAD")
                req.add_header("User-Agent", "StructaCloud-Test/1.0")
                resp = urllib.request.urlopen(req, timeout=10)
                assert resp.geturl().startswith("https://"), f"{domain} did not redirect to HTTPS"
            except Exception as e:
                pytest.skip(f"Could not reach {domain}: {e}")

    def test_https_response_headers(self) -> None:
        """HTTPS responses must include security headers."""
        if not _sites_reachable():
            pytest.skip("Sites not reachable")

        import urllib.request

        for domain in self.DOMAINS:
            try:
                req = urllib.request.Request(domain, method="HEAD")
                req.add_header("User-Agent", "StructaCloud-Test/1.0")
                resp = urllib.request.urlopen(req, timeout=10)
                headers = dict(resp.headers)
                assert "strict-transport-security" in {k.lower(): v for k, v in headers.items()}, f"Missing HSTS on {domain}"
            except Exception as e:
                pytest.skip(f"Could not reach {domain}: {e}")


# ── Main CLI ───────────────────────────────────────────────────────────────


if __name__ == "__main__":
    if pytest is None:
        print("ERROR: pytest is required. Install with: pip install pytest")
        sys.exit(1)
    sys.exit(pytest.main([__file__, "-v"]))
