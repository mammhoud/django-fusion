"""
Project Config — layered configuration with priority resolution
================================================================

A Django-free loader that resolves configuration for a Django-Fusion project
from layered sources, lowest → highest priority:

    1. Shared product defaults   ``projects/<product>/configs/Env/*.yml``
    2. Project configs           ``<project>/configs/*.yml``
    3. Site overrides            ``<project>/Env/_site.yml``
    4. Dotenv files              ``<repo>/.env`` → ``<project>/.env``
    5. Environment variables     ``DJANGO_*`` / bare ``KEY`` (always wins)

The cascade is optional sugar: every value can be supplied through environment
variables alone, so a project without a ``configs/`` directory behaves exactly
as before. ``settings.py`` modules use it to source *defaults*; environment
variables always win.

Priority resolution by base URL
-------------------------------
Use :meth:`ProjectConfig.resolve` to apply site-identity priority for a given
request origin. Given a backend or frontend base URL (e.g.
``https://lms.structa.cloud`` or ``http://localhost:3000``) and an optional
side (``"front"`` / ``"back"``), the loader finds the matching site entry in
the merged config (``SITE`` / ``SITE.websites``) and overlays its identity —
domains, allowed hosts, admin URL — on top of the cascade, still below
environment variables. This is how each front/back base URL gets the right
site configuration with clear priority.

Usage
-----
    from django_fusion.config.project import load_config, staticfiles_plan

    config = load_config(project_dir="projects/precis/precis-main")
    domain = config.get("SITE.primary_domain", "structa.cloud")

    # Resolve identity for a specific origin (front or back road).
    resolved = config.resolve(base_url="https://lms.structa.cloud", side="back")
    admin_url = resolved.get("ADMIN.wagtailadmin_base_url")

    plan = staticfiles_plan(project_dir="projects/precis/precis-main")
    print(plan.render())  # static read → output → deploy reference table

YAML parsing uses ``dynaconf.vendor.ruamel`` (dynaconf is a hard dependency of
django-fusion and bundles ruamel.yaml), falling back to PyYAML when present and
finally to an empty config — the module must never raise at settings import.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence
from urllib.parse import urlsplit

try:
    from dynaconf.vendor.ruamel import yaml  # type: ignore[import-not-found]
except Exception:  # pragma: no cover — degrade gracefully
    try:
        import yaml  # type: ignore[no-redef]
    except Exception:  # pragma: no cover
        yaml = None  # type: ignore[assignment]

__all__ = [
    "ProjectConfig",
    "StaticFilesPlan",
    "load_config",
    "staticfiles_plan",
]

# Shared Env YAML files (product-wide defaults), mirroring the load order used
# by ``projects/precis/configs/settings/conf.py``.
_SHARED_ENV_FILES: tuple[str, ...] = (
    "default/_core.yml",
    "database.yml",
    "security.yml",
    "storage.yml",
    "email.yml",
    "logging.yml",
    "payments.yml",
)

# Conventional project-level configs files, loaded in this order so identity/
# admin/theme layers sit on top of the local-dev defaults.
_PROJECT_CONFIG_ORDER: tuple[str, ...] = (
    "defaults.yml",
    "site.yml",
    "admin.yml",
    "theme.yml",
)

_ENVIRONMENT_SECTIONS = ("default", "development", "demo", "staging", "testing", "production")

# Well-known dev ports for each road — used by resolve() when matching
# localhost base URLs for a given side.
_FRONT_PORTS = frozenset({3000, 3001, 3002, 4321, 5173})
_BACK_PORTS = frozenset({8000, 8074, 5070, 5080, 3458})


# ── low-level helpers ────────────────────────────────────────────────────────


def _deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    """Recursively merge two mappings; ``override`` wins for scalar/list keys."""
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file into a plain dict; never raises."""
    if not path.exists() or yaml is None:
        return {}
    try:
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _select_env_section(data: Mapping[str, Any], env: str) -> dict[str, Any]:
    """Select the active environment section from Dynaconf-style YAML.

    Files may be flat (``key: value``) or environment-scoped
    (``default: {...}`` / ``development: {...}``). For environment-scoped
    files the ``default`` section is merged first, then the active environment
    section (if any) is deep-merged on top.
    """
    if not any(section in data for section in _ENVIRONMENT_SECTIONS):
        return dict(data)
    merged: dict[str, Any] = {}
    default_section = data.get("default")
    if isinstance(default_section, Mapping):
        merged = _deep_merge(merged, default_section)
    env_section = data.get(env) if env else None
    if isinstance(env_section, Mapping):
        merged = _deep_merge(merged, env_section)
    return merged


def _load_dotenv(path: Path) -> dict[str, str]:
    """Parse a simple ``KEY=VALUE`` dotenv file (comments + [sections] skipped).

    ``DJANGO_*`` keys are normalized to their base name so ``DJANGO_DEBUG=0``
    in a dotenv file drives the same ``DEBUG`` key as the YAML layers.
    """
    if not path.exists():
        return {}
    result: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("[") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key.startswith("DJANGO_"):
            key = key[len("DJANGO_"):]
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        result[key] = value
    return result


def _workspace_dir(project_dir: Path) -> Path:
    """Walk up from a project to the monorepo root (the dir owning ``libs/``)."""
    current = project_dir.resolve()
    for parent in (current, *current.parents):
        if (parent / "libs").is_dir() or (parent / "application").is_dir():
            return parent
    return current


def _get_nested(source: Mapping[str, Any], dotted_key: str, default: Any = None) -> Any:
    """Read a dotted key (``SITE.domains.primary``) from nested mappings."""
    current: Any = source
    for part in dotted_key.split("."):
        if isinstance(current, Mapping) and part in current:
            current = current[part]
        else:
            return default
    return current


def _resolve_env_value(value: Any, default: Any = None) -> Any:
    """Resolve Dynaconf-style ``@env NAME`` placeholders from the environment."""
    if isinstance(value, str) and value.startswith("@env "):
        parts = value.split(maxsplit=2)
        env_name = parts[1] if len(parts) > 1 else ""
        fallback = parts[2] if len(parts) > 2 else default
        return os.environ.get(env_name, fallback)
    return value


# ── ProjectConfig ────────────────────────────────────────────────────────────


class ProjectConfig:
    """Layered configuration source for a Django-Fusion project.

    Priority (low → high): shared Env YAML → project ``configs/*.yml`` →
    ``Env/_site.yml`` → dotenv files → environment variables.

    Parameters
    ----------
    project_dir:
        Project root — the directory that owns ``frontend/``, ``backend/``
        and (optionally) ``configs/``.
    env:
        Active environment (``development``, ``production``, ...). Detected
        from ``SERVER_ENV``/``DJANGO_ENV`` when not provided.
    shared_config_dir:
        Directory of shared Env YAML files. Defaults to
        ``<project_dir>/../configs/Env`` (the Precis shared configs package).
    dotenv_paths:
        Additional dotenv files, loaded after the automatic workspace and
        project files.
    """

    def __init__(
        self,
        project_dir: str | Path,
        *,
        env: str | None = None,
        shared_config_dir: str | Path | None = None,
        dotenv_paths: Sequence[str | Path] = (),
    ) -> None:
        self.project_dir = Path(project_dir)
        self.workspace_dir = _workspace_dir(self.project_dir)
        self.env = env or os.environ.get("SERVER_ENV") or os.environ.get("DJANGO_ENV") or "development"
        if shared_config_dir is None:
            shared_config_dir = self.project_dir.parent / "configs" / "Env"
        self.shared_config_dir = Path(shared_config_dir)
        self.dotenv_paths = [Path(p) for p in dotenv_paths]
        self._data: dict[str, Any] = {}
        self._loaded = False

    # ── layer discovery ────────────────────────────────────────────────

    def _shared_files(self) -> list[Path]:
        """Shared product-wide YAML files (skipped when absent)."""
        files: list[Path] = []
        if not self.shared_config_dir.is_dir():
            return files
        for rel in _SHARED_ENV_FILES:
            if rel == "default/_<env>.yml":
                candidate = self.shared_config_dir / "default" / f"_{self.env}.yml"
            else:
                candidate = self.shared_config_dir / rel
            if candidate.is_file():
                files.append(candidate)
        return files

    def _project_files(self) -> list[Path]:
        """Project-level ``configs/*.yml`` files in conventional order."""
        configs_dir = self.project_dir / "configs"
        if not configs_dir.is_dir():
            return []
        files: list[Path] = []
        seen: set[str] = set()
        for name in _PROJECT_CONFIG_ORDER:
            candidate = configs_dir / name
            if candidate.is_file():
                files.append(candidate)
                seen.add(name)
        for candidate in sorted(configs_dir.glob("*.yml")):
            if candidate.name not in seen:
                files.append(candidate)
        return files

    def _site_file(self) -> Path:
        return self.project_dir / "Env" / "_site.yml"

    # ── loading ────────────────────────────────────────────────────────

    def load(self) -> dict[str, Any]:
        """Load and merge all layers; returns the merged dict (cached)."""
        if self._loaded:
            return self._data

        merged: dict[str, Any] = {}

        # 1. Shared product-wide defaults (lowest priority).
        for path in self._shared_files():
            merged = _deep_merge(merged, _select_env_section(_load_yaml(path), self.env))

        # 2. Project-level configs dir (beside frontend/backend).
        for path in self._project_files():
            merged = _deep_merge(merged, _select_env_section(_load_yaml(path), self.env))

        # 3. Site-level Env overrides.
        merged = _deep_merge(merged, _select_env_section(_load_yaml(self._site_file()), self.env))

        # 4. Dotenv files — workspace root, shared Env, project, then explicit.
        dotenv_files: list[Path] = []
        for candidate in (
            self.workspace_dir / ".env",
            self.shared_config_dir / ".env",
            self.project_dir / ".env",
        ):
            if candidate.is_file() and candidate not in dotenv_files:
                dotenv_files.append(candidate)
        for candidate in self.dotenv_paths:
            if candidate.is_file() and candidate not in dotenv_files:
                dotenv_files.append(candidate)
        for path in dotenv_files:
            merged = _deep_merge(merged, _load_dotenv(path))

        # 5. Environment variables (highest priority).
        #    DJANGO_<KEY> vars map to their base key (compose/container truth),
        #    then a bare <KEY> env var wins over the DJANGO_-prefixed value.
        #    A scalar env value must never replace a structured section (e.g.
        #    DJANGO_SITE=precis-ctc is a site *name*, not the SITE dict), so
        #    Mapping sections are kept intact below the env layer.
        for env_key, env_value in os.environ.items():
            if env_key.startswith("DJANGO_") and env_key != "DJANGO_SETTINGS_MODULE":
                key = env_key[len("DJANGO_"):]
                if not isinstance(merged.get(key), Mapping):
                    merged[key] = env_value
        for key in list(merged.keys()):
            bare_value = os.environ.get(key)
            if bare_value is not None and not isinstance(merged.get(key), Mapping):
                merged[key] = bare_value
        # 6. Dotenv normalization can map DJANGO_SITE → SITE and clobber the
        #    section; re-guard against scalar-over-Mapping now that the
        #    section may have arrived from a later file.
        for key in list(merged.keys()):
            if isinstance(merged.get(key), Mapping):
                continue
            # No-op: env layer already applied; kept for clarity/ordering.

        self._data = merged
        self._loaded = True
        return self._data

    # ── accessors ──────────────────────────────────────────────────────

    def get(self, key: str, default: Any = None) -> Any:
        """Return a (possibly dotted) key, resolving ``@env`` placeholders."""
        value = _get_nested(self.load(), key, default)
        return _resolve_env_value(value, default)

    def section(self, name: str, default: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Return a top-level section as a plain dict (upper/lower-case tolerant)."""
        data = self.load()
        for candidate in (name, name.upper(), name.lower(), name.capitalize()):
            value = data.get(candidate)
            if isinstance(value, Mapping):
                return dict(value)
        return dict(default or {})

    def as_dict(self) -> dict[str, Any]:
        """Return the merged configuration as a plain dict."""
        return dict(self.load())

    # ── base-URL priority resolution ───────────────────────────────────

    def resolve(
        self,
        base_url: str | None = None,
        side: str | None = None,
    ) -> dict[str, Any]:
        """Resolve configuration for a specific origin with site priority.

        Parameters
        ----------
        base_url:
            The backend or frontend base URL — e.g. ``https://lms.structa.cloud``
            or ``http://localhost:3000``. ``None`` falls back to the active
            site (``SITE_NAME``/``WEBSITE`` env or the project's own ``SITE``).
        side:
            ``"front"`` (Astro) or ``"back"`` (Django) — used to match
            localhost/dev ports and to tag the result.

        Returns
        -------
        dict
            The full merged config with the matched site's identity overlaid
            under ``SITE`` (still below environment variables), plus
            ``SITE.base_url`` and ``SITE.side`` markers.
        """
        data = dict(self.load())
        site = self._match_site(base_url, side)
        if site:
            merged_site = _deep_merge(
                data.get("SITE", {}) if isinstance(data.get("SITE"), Mapping) else {},
                site,
            )
            data["SITE"] = merged_site
        if base_url:
            data.setdefault("SITE", {})
            data["SITE"]["base_url"] = base_url
        if side:
            data.setdefault("SITE", {})
            data["SITE"]["side"] = side
        # Environment still wins for identity-critical keys after resolution.
        for key in ("SITE_DOMAIN", "DOMAIN_NAME", "WEBSITE_NAME"):
            env_value = os.environ.get(key) or os.environ.get(f"DJANGO_{key}")
            if env_value is not None:
                data[key] = env_value
        return data

    def _match_site(self, base_url: str | None, side: str | None) -> dict[str, Any] | None:
        """Find the site entry whose domain matches ``base_url``.

        Candidates come from the top-level ``SITE`` section and the registry
        ``SITE.websites``. Matching priority: exact host → host in a site's
        ``domains``/``allowed_hosts`` → (localhost only) port-based side match.
        """
        data = self.load()
        host, port = self._split_base_url(base_url)
        if host:
            host = host.lower()

        sites: dict[str, Mapping[str, Any]] = {}
        top_site = data.get("SITE")
        if isinstance(top_site, Mapping):
            sites["_self"] = top_site
            registry = top_site.get("websites")
            if isinstance(registry, Mapping):
                for name, entry in registry.items():
                    if isinstance(entry, Mapping):
                        sites[name] = entry

        if host:
            # 1. Exact host match on primary_domain.
            for name, entry in sites.items():
                primary = entry.get("primary_domain") or entry.get("domain")
                if primary and str(primary).lower() == host:
                    return dict(entry)
            # 2. Host in domains / allowed_hosts lists.
            for name, entry in sites.items():
                hosts = []
                for key in ("domains", "allowed_hosts"):
                    value = entry.get(key)
                    if isinstance(value, (list, tuple)):
                        hosts.extend(str(item).lower() for item in value)
                    elif value:
                        hosts.append(str(value).lower())
                if host in hosts:
                    return dict(entry)
            # 3. Localhost/dev — side-aware port match.
            if port and (host in {"localhost", "127.0.0.1", "0.0.0.0"}):
                port_int = int(port)
                wanted: frozenset[int]
                if side == "front":
                    wanted = _FRONT_PORTS
                elif side == "back":
                    wanted = _BACK_PORTS
                else:
                    wanted = _FRONT_PORTS | _BACK_PORTS
                if port_int in wanted:
                    # Pick the site whose ports include this port.
                    for name, entry in sites.items():
                        ports = entry.get("ports")
                        if isinstance(ports, Mapping):
                            for value in ports.values():
                                if str(value) == str(port):
                                    return dict(entry)
                    return dict(sites["_self"]) if "_self" in sites else None

        return dict(sites["_self"]) if not host and "_self" in sites else None

    @staticmethod
    def _split_base_url(base_url: str | None) -> tuple[str | None, str | None]:
        """Return ``(host, port)`` from a URL, tolerating missing schemes."""
        if not base_url:
            return None, None
        value = base_url.strip()
        if "://" not in value:
            value = f"http://{value}"
        parts = urlsplit(value)
        host = parts.hostname
        port = parts.port
        return host, (str(port) if port else None)


def load_config(
    project_dir: str | Path,
    *,
    env: str | None = None,
    shared_config_dir: str | Path | None = None,
    dotenv_paths: Sequence[str | Path] = (),
) -> ProjectConfig:
    """Build and load a :class:`ProjectConfig` for a project directory.

    Convenience wrapper that returns an already-merged config so callers can
    ``config.get(...)`` / ``config.resolve(...)`` immediately.
    """
    config = ProjectConfig(
        project_dir=project_dir,
        env=env,
        shared_config_dir=shared_config_dir,
        dotenv_paths=dotenv_paths,
    )
    config.load()
    return config


# ── StaticFilesPlan ──────────────────────────────────────────────────────────


@dataclass(frozen=True)
class StaticFilesPlan:
    """Reference of where static files are read, collected, and deployed.

    Attributes mirror the Django settings that produce them:

    * ``read_dirs``     — ``STATICFILES_DIRS`` (source assets read by collectstatic)
    * ``output_dir``    — ``STATIC_ROOT`` (collectstatic output, served by whitenoise)
    * ``media_dir``     — ``MEDIA_ROOT`` (user/editor uploads)
    * ``bundle_stats``  — django-webpack-loader ``bundles.json``
    * ``css_path``      — compiled design-system stylesheet (``make css`` output)
    * ``deploy``        — named volumes / shared-proxy destinations
    """

    project_dir: Path
    read_dirs: tuple[Path, ...]
    output_dir: Path
    media_dir: Path
    bundle_stats: Path
    css_path: Path
    deploy: dict[str, str]

    def as_dict(self) -> dict[str, Any]:
        """Plain-dict form for checks, docs, and JSON output."""
        return {
            "project_dir": str(self.project_dir),
            "read_dirs": [str(p) for p in self.read_dirs],
            "output_dir": str(self.output_dir),
            "media_dir": str(self.media_dir),
            "bundle_stats": str(self.bundle_stats),
            "css_path": str(self.css_path),
            "deploy": dict(self.deploy),
        }

    def render(self) -> str:
        """Render the plan as a readable ASCII table (``make config-show``)."""
        lines = [f"STATIC FILES PLAN — {self.project_dir.name}", "=" * 58]
        lines.append("Read (STATICFILES_DIRS):")
        for path in self.read_dirs:
            lines.append(f"  - {path}")
        lines.extend(
            [
                f"Output (STATIC_ROOT): {self.output_dir}",
                f"Media  (MEDIA_ROOT):  {self.media_dir}",
                f"Bundles (webpack):    {self.bundle_stats}",
                f"Design CSS (fusion):  {self.css_path}",
                "Deploy:",
            ]
        )
        for key, value in self.deploy.items():
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)


def staticfiles_plan(
    project_dir: str | Path,
    *,
    overrides: Optional[Mapping[str, Any]] = None,
    backend_rel: str = "backend",
) -> StaticFilesPlan:
    """Resolve the conventional static-files layout for a project.

    ``overrides`` (typically ``config.section("STATIC")`` from the project
    ``configs/defaults.yml``) can replace any conventional path with a
    relative path (resolved against ``project_dir``) or an absolute path.

    Conventional layout (matching Precis products):

    * read:  ``backend/assets/static``, ``assets/static``, ``frontend/public``
    * out:   ``backend/assets/staticfiles``   (STATIC_ROOT)
    * media: ``backend/assets/media``         (MEDIA_ROOT)
    * bundle:``backend/assets/static/bundles/bundles.json``
    * css:   ``assets/static/css/fusion.css`` (``make css`` output)
    """
    project = Path(project_dir)
    backend = project / backend_rel
    overrides = dict(overrides or {})

    def _rel_path(key: str, default: Path) -> Path:
        value = overrides.get(key)
        if value is None:
            return default
        path = Path(str(value))
        return path if path.is_absolute() else (project / path)

    # Read dirs (STATICFILES_DIRS): configured list wins, otherwise the
    # conventional layout, filtered to directories that actually exist.
    configured_reads = overrides.get("read_dirs")
    if configured_reads:
        resolved: list[Path] = []
        for entry in configured_reads:
            path = Path(str(entry))
            if not path.is_absolute():
                path = project / path
            if path.is_dir():
                resolved.append(path)
        read_dirs = tuple(resolved)
    else:
        read_dirs = tuple(
            p
            for p in (
                backend / "assets" / "static",
                project / "assets" / "static",
                project / "frontend" / "public",
            )
            if p.is_dir()
        )

    output_dir = _rel_path("output_dir", backend / "assets" / "staticfiles")
    media_dir = _rel_path("media_dir", backend / "assets" / "media")
    bundle_stats = _rel_path("bundle_stats", backend / "assets" / "static" / "bundles" / "bundles.json")
    css_path = _rel_path("css_path", project / "assets" / "static" / "css" / "fusion.css")

    deploy = dict(
        overrides.get("deploy")
        or {
            "static_volume": f"{project.name}-static",
            "media_volume": f"{project.name}-media",
            "static_url": "/static/",
            "media_url": "/media/",
            "static_server": "whitenoise (backend) behind traefik /static/",
            "media_server": "shared-proxy nginx (application/proxy)",
        }
    )

    return StaticFilesPlan(
        project_dir=project,
        read_dirs=read_dirs,
        output_dir=output_dir,
        media_dir=media_dir,
        bundle_stats=bundle_stats,
        css_path=css_path,
        deploy=deploy,
    )
