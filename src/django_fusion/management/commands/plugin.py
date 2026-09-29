"""``manage.py plugin`` — inspect, describe and verify django-fusion plugins.

Owning plan: ``docs/plans/structa-cloud/plugins/product-description-and-attach.md``
(deliverable 2). Subcommands::

    python manage.py plugin list                  # every spec: available? registered? attached? described?
    python manage.py plugin describe htmx         # the PRODUCT.md view (--json for tooling)
    python manage.py plugin doctor                # drift report: attached-vs-declared, undescribed, unavailable
    python manage.py plugin check                 # the blocking gate — exit 1 on any drift
    python manage.py plugin attach learning       # preview the edit (--apply to write)
    python manage.py plugin detach learning       # preview the removal (--apply to write)

Why a command and not just the script: the same contract has two readers. The
docs gate (``scripts/generate_plugin_products.py``) reads the catalog with
:mod:`ast` so it runs in a bare CI job, while this command reads the **live**
:class:`~django_fusion.plugins.registry.PluginRegistry` — including plugin specs
a site contributed through the ``register_plugin_specs`` hook, which a static
reader cannot see. Both apply the rules in
:mod:`django_fusion.plugins.descriptions`, so the two cannot drift apart.

**The mutating path is preview-by-default.** ``attach``/``detach`` print the exact
diff and stop unless ``--apply`` is passed, because these edit a site's
``settings.py`` and the cost of an unintended edit is much higher than the cost
of typing one more flag. Every write is confined to the marker region (see
:mod:`django_fusion.plugins.attach`), refuses when the markers are absent, and is
rolled back if ``manage.py check`` fails afterwards — a half-attached site would
otherwise be committed by the next person to push.

What attach will **not** do: it attaches an **app-shaped** plugin (one with an
``apps.py``, as the plugin plan specifies) by adding it to the marker region, or
by adding an ``OPTIONAL_APP_MAP`` entry with ``--optional``. A config-only or
entry-point plugin has no app to add, so the command refuses rather than writing
an app entry that would do nothing. Migrations stay opt-in: ``--migrate`` shows
the plan and asks before applying it (decision D7), because a convenience flag on
a command that also edits source is how a production schema moves by accident.
"""
from __future__ import annotations

import importlib
import io
import json
import os
from pathlib import Path

from django.conf import settings
from django.core.management import call_command

from django_fusion.management.commands.base import BaseCommand
from django_fusion.plugins import attach as editing
from django_fusion.plugins import get_plugin_registry
from django_fusion.plugins import descriptions as desc

#: Every subcommand. ``attach``/``detach`` preview by default; ``--apply`` writes.
SUBCOMMANDS = ("list", "describe", "doctor", "check", "attach", "detach")

#: Where the optional-app map lives, relative to the repository root.
DEFAULT_OPTIONAL_MAP = Path("projects/Clients/configs/base/apps.py")

#: Settings that may hold an app list, in the order a site is likely to use them.
_APP_LIST_SETTINGS = ("LOCAL_APPS", "INSTALLED_APPS", "SHARED_APPS", "TENANT_APPS")


def _declared_apps() -> list[str]:
    """Every app string the site declares, across the app-list settings it uses."""
    declared: list[str] = []
    for key in _APP_LIST_SETTINGS:
        value = getattr(settings, key, None) or []
        if isinstance(value, (list, tuple)):
            declared.extend(str(item) for item in value)
    return declared


def _import_problem(name: str) -> str | None:
    """Why a plugin module is not importable — ``"external"``, ``"broken"`` or ``None``.

    The catalog deliberately lists plugins a site opts into (``robyn``, ``tasks``)
    whose third-party dependency may simply not be installed in the environment
    running the gate — that is the environment's business, not drift, and failing
    on it would make the gate unusable in a bare CI job. A failure to import an
    *internal* module, or any non-import error, is a real defect in the catalog or
    the package, so the two are separated rather than lumped together.
    """
    try:
        importlib.import_module(name)
        return None
    except ModuleNotFoundError as exc:
        root = str(exc.name or "").split(".")[0]
        return "broken" if (not root or root == "django_fusion") else "external"
    except Exception:
        return "broken"


def _is_attached(name: str, declared: set[str]) -> bool:
    """True when a plugin is **active** in this environment.

    Two ways a plugin can be active, and both are checked by exact dotted name:
    it is registered with the pluggy manager (how the framework's opt-in plugins
    are switched on), or its module is one of the site's installed apps (how a
    product plugin is attached).

    Matching by Django app *label* was deliberately removed: ``staticfiles`` is
    the label of ``django.contrib.staticfiles``, so label matching reported
    ``django_fusion.config.staticfiles`` attached on the strength of an unrelated
    Django app. A column that can be right by coincidence is worse than one that
    is narrow.
    """
    if name in declared:
        return True
    return get_plugin_registry().is_registered(name)


class Command(BaseCommand):
    help = "Inspect, describe and verify django-fusion plugins (list, describe, doctor, check)."

    def add_arguments(self, parser) -> None:
        parser.add_argument("subcommand", choices=SUBCOMMANDS, help="what to do")
        parser.add_argument(
            "name",
            nargs="?",
            help="plugin name for `describe` — a full dotted name or a short one (e.g. htmx)",
        )
        parser.add_argument("--json", action="store_true", help="machine-readable output")
        parser.add_argument(
            "--root",
            action="append",
            default=[],
            metavar="DIR",
            help="also scan a product plugin directory (e.g. backend/plugins); repeatable",
        )
        # attach/detach only. The default is to show the diff and change nothing;
        # --dry-run is accepted as well so the plan's documented invocation works.
        parser.add_argument(
            "--apply", action="store_true", help="actually write the edit (default: preview only)"
        )
        parser.add_argument(
            "--dry-run", action="store_true", help="show the diff and write nothing (the default)"
        )
        parser.add_argument(
            "--optional",
            action="store_true",
            help="write the OPTIONAL_APP_MAP entry instead of the site's plugin region",
        )
        parser.add_argument(
            "--optional-map",
            metavar="PATH",
            default=None,
            help=f"the optional-app map file (default: <repo>/{DEFAULT_OPTIONAL_MAP})",
        )
        parser.add_argument(
            "--migrate",
            action="store_true",
            help="after a write, show the migration plan and ask before applying it",
        )
        parser.add_argument("--yes", action="store_true", help="skip the migration confirmation")

    # ── resolution helpers ────────────────────────────────────────────────
    def _resolve(self, name: str):
        """Find a spec by full dotted name or by short name."""
        registry = get_plugin_registry()
        spec = registry.get(name)
        if spec is not None:
            return spec
        matches = [s for s in registry.catalog() if s.short_name == name]
        if len(matches) == 1:
            return matches[0]
        if not matches:
            return None
        return matches  # ambiguous — reported by the caller

    def _product_roots(self, options) -> list[Path]:
        return [Path(root) for root in options.get("root") or []]

    def _product_descriptions(self, roots: list[Path]) -> list[Path]:
        """``PRODUCT.md`` files under product plugin directories."""
        found: list[Path] = []
        for root in roots:
            if root.is_dir():
                found.extend(sorted(root.glob(f"*/{desc.PRODUCT_FILENAME}")))
        return found

    # ── subcommands ───────────────────────────────────────────────────────
    def _list(self, options) -> int:
        registry = get_plugin_registry()
        declared = set(_declared_apps())
        report = registry.summary()
        # Resolve descriptions the same way `doctor`/`check` do, so a product
        # plugin's PRODUCT.md is not reported missing simply because `list` forgot
        # to look in the `--root` directory it was given.
        roots = {root.name: root for root in self._product_roots(options)}
        rows = []
        for entry in report["plugins"]:
            name = entry["name"]
            path = self._description_path(name, roots)
            described = bool(path and path.exists())
            rows.append(
                {
                    "name": name,
                    "available": entry["available"],
                    "registered": entry["registered"],
                    "attached": _is_attached(name, declared),
                    "described": described,
                    "capabilities": entry["capabilities"],
                    "core": entry["core"],
                }
            )

        if options["json"]:
            self.stdout.write(json.dumps({"total": len(rows), "plugins": rows}, indent=2))
            return 0

        self.stdout.write("")
        self.stdout.write(
            f"{'plugin':42} {'avail':6} {'reg':6} {'attach':7} {'desc':5} caps"
        )
        for row in rows:
            self.stdout.write(
                f"{row['name']:42} "
                f"{'yes' if row['available'] else 'no':6} "
                f"{'yes' if row['registered'] else 'no':6} "
                f"{'yes' if row['attached'] else 'no':7} "
                f"{'yes' if row['described'] else 'NO':5} "
                f"{','.join(row['capabilities'])}"
            )
        self.stdout.write("")
        described = sum(1 for row in rows if row["described"])
        self.stdout.write(
            f"{described}/{len(rows)} described · "
            f"{report['registered']} registered · {report['available']} available"
        )
        return 0

    def _describe(self, options) -> int:
        name = options.get("name")
        if not name:
            self.log_error("`describe` needs a plugin name — run `plugin list` to see them")
            return 2
        spec = self._resolve(name)
        if isinstance(spec, list):
            self.log_error(f"{name!r} is ambiguous — use the full name: " + ", ".join(s.name for s in spec))
            return 2
        if spec is None:
            self.log_error(f"unknown plugin {name!r}")
            registry = get_plugin_registry()
            hints = sorted(registry.capabilities())
            self.stdout.write("Available capabilities: " + ", ".join(hints))
            return 2

        path = desc.expected_product_path(spec.name)
        if path is None or not path.exists():
            self.log_error(
                f"{spec.name} has no {desc.PRODUCT_FILENAME}"
                + (f" (expected at {path})" if path else " (not shipped in this library)")
            )
            return 1

        front = desc.read_frontmatter(path)
        body = desc.read_body(path)
        failures, warnings = desc.check_product_for_spec(spec)

        if options["json"]:
            self.stdout.write(
                json.dumps(
                    {
                        "name": spec.name,
                        "path": str(path),
                        "frontmatter": front,
                        "body": body,
                        "failures": failures,
                        "warnings": warnings,
                    },
                    indent=2,
                    default=str,
                )
            )
            return 1 if failures else 0

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(str(front.get("title") or spec.short_name)))
        self.stdout.write(f"  id           {front.get('id', '—')}")
        self.stdout.write(f"  summary      {front.get('summary', '—')}")
        self.stdout.write(f"  capabilities {', '.join(front.get('capabilities') or []) or '—'}")
        self.stdout.write(f"  signals      {', '.join(front.get('signals') or []) or '—'}")
        self.stdout.write(f"  surface      {front.get('surface', '—')}")
        self.stdout.write(f"  owner        {front.get('owner', '—')}")
        self.stdout.write(f"  source       {path}")
        self.stdout.write("")
        self.stdout.write(body)
        for warning in warnings:
            self.log_warning(warning)
        for failure in failures:
            self.log_error(failure)
        return 1 if failures else 0

    def _description_path(self, name: str, roots: dict[str, Path]) -> Path | None:
        """Where a spec's PRODUCT.md should be — framework package, else a product root.

        A framework spec lives under ``src/django_fusion``. A *product* spec
        (``plugins.learning``) has no such directory, so it resolves against the
        ``--root`` directories by first segment: ``plugins`` + ``learning`` →
        ``<root>/learning/PRODUCT.md``.
        """
        library_path = desc.expected_product_path(name)
        if library_path is not None:
            return library_path
        head, _, tail = name.partition(".")
        root = roots.get(head)
        if root is not None and tail:
            return desc.product_path(head, tail.replace(".", "/"), root=root)
        return None

    def _drift(self, options) -> tuple[list[str], list[str]]:
        """The shared drift report used by both ``doctor`` and ``check``.

        Scope note: a plugin directory is only judged when the repository says it
        *is* a plugin — it has a ``PRODUCT.md``, a catalog spec, or is an installed
        app. A helper package that is none of those (``plugins/workers`` holds the
        Dramatiq actors) is not guessed at, because inventing a failure for it
        would train people to ignore the gate. How many directories were skipped
        is printed so the narrowing stays visible.
        """
        registry = get_plugin_registry()
        failures: list[str] = []
        warnings: list[str] = []
        declared = set(_declared_apps())
        roots = {root.name: root for root in self._product_roots(options)}

        for spec in registry.catalog():
            path = self._description_path(spec.name, roots)
            # A spec whose name points at nothing in the tree is a catalog defect
            # (the class of defect the prefix audit found); a spec that exists but
            # cannot be imported is only reported, because the usual cause is an
            # optional dependency this environment has not installed.
            if path is None:
                failures.append(
                    f"{spec.name}: catalog entry points at nothing in the tree "
                    "(pass --root for a product plugin directory)"
                )
            else:
                problem = _import_problem(spec.name)
                if problem == "broken":
                    failures.append(f"{spec.name}: not importable — the module exists but fails to load")
                elif problem == "external":
                    warnings.append(
                        f"{spec.name}: not importable here — an optional dependency is missing"
                    )
                if not path.exists():
                    failures.append(f"{spec.name}: catalog entry has no {desc.PRODUCT_FILENAME} ({path})")
                else:
                    spec_failures, spec_warnings = desc.check_product(
                        path,
                        name=spec.name,
                        capabilities=spec.capabilities,
                        signals=spec.signals,
                        description=spec.description,
                        claims_text=desc.load_claims(desc.default_repo_root()),
                    )
                    failures += [f"{path}: {message}" for message in spec_failures]
                    warnings += [f"{path}: {message}" for message in spec_warnings]

        # Product roots: a description with no spec is a listing that would
        # advertise something the registry cannot describe.
        for prefix, root in sorted(roots.items()):
            if not root.is_dir():
                failures.append(f"--root {root}: not a directory")
                continue
            skipped = 0
            for child in sorted(root.iterdir()):
                if not child.is_dir() or child.name.startswith((".", "_")):
                    continue
                module = f"{prefix}.{child.name}"
                described = (child / desc.PRODUCT_FILENAME).exists()
                if not described and registry.get(module) is None:
                    skipped += 1
                    continue
                if described and registry.get(module) is None:
                    failures.append(
                        f"{module}: has a {desc.PRODUCT_FILENAME} but no catalog spec "
                        "— register it in the site's register_plugin_specs hook"
                    )
            if skipped:
                # Printed, not logged: the whole point is that a narrowed scope is
                # visible, and a silent scope is the failure mode this gate's
                # sibling tool already had once.
                self.stdout.write(
                    f"  · {root}: {skipped} director{'y' if skipped == 1 else 'ies'} "
                    "skipped (neither described nor catalogued)"
                )

        # Attached-but-not-in-catalog: an installed app under a plugin root that
        # no spec describes. Compared by *name* — an earlier version tested the
        # dotted string against the list of PluginSpec objects, which is always
        # true and so reported every correctly-attached plugin as a failure.
        catalog_names = {spec.name for spec in registry.catalog()}
        for declared in _declared_apps():
            head = declared.split(".")[0]
            if head in roots and declared not in catalog_names:
                failures.append(
                    f"{declared}: attached but not in the catalog "
                    "(add it to the site's register_plugin_specs hook)"
                )

        # An installed app that no longer registers itself is a real half-attached
        # state — reported, since silently reporting it as "attached" would hide it.
        for spec in registry.catalog():
            if spec.name in declared and not registry.is_registered(spec.name):
                warnings.append(
                    f"{spec.name}: installed but not registered with the pluggy manager"
                )
        return failures, warnings

    def _doctor(self, options) -> int:
        failures, warnings = self._drift(options)
        registry = get_plugin_registry()
        if options["json"]:
            self.stdout.write(
                json.dumps(
                    {
                        "total": registry.summary()["total"],
                        "failures": failures,
                        "warnings": warnings,
                    },
                    indent=2,
                )
            )
            return 0
        for warning in warnings:
            self.log_warning(warning)
        for failure in failures:
            self.log_error(failure)
        if not failures:
            self.log_success(f"no drift across {registry.summary()['total']} catalog spec(s)")
        else:
            self.stdout.write(f"\n{len(failures)} drift finding(s) — `plugin check` fails on these")
        return 0

    def _check(self, options) -> int:
        failures, warnings = self._drift(options)
        for warning in warnings:
            self.log_warning(warning)
        for failure in failures:
            self.log_error(failure)
        if failures:
            self.stdout.write("")
            self.log_error(
                f"plugin description gate failed — {len(failures)} finding(s); "
                "a description must match its spec and cite real paths"
            )
            return 1
        self.log_success("plugin description gate clean")
        return 0

    # ── attach / detach ───────────────────────────────────────────────────
    def _site_settings_path(self) -> Path:
        """The file declaring this site's app lists, located through SETTINGS_MODULE."""
        module_name = getattr(settings, "SETTINGS_MODULE", None) or os.environ.get(
            "DJANGO_SETTINGS_MODULE"
        )
        if not module_name:
            raise editing.RegionMissing(
                "cannot locate the site settings — DJANGO_SETTINGS_MODULE is unset"
            )
        module = importlib.import_module(module_name)
        origin = getattr(module, "__file__", None)
        if not origin:
            raise editing.RegionMissing(f"{module_name} has no source file to edit")
        return Path(origin)

    def _edit_target(self, options) -> tuple[Path, bool]:
        """Return ``(file, is_optional_map)`` for the write, refusing when absent."""
        if options.get("optional"):
            path = Path(options.get("optional_map") or (desc.default_repo_root() / DEFAULT_OPTIONAL_MAP))
            if not path.exists():
                raise editing.RegionMissing(
                    f"optional-app map not found at {path} — pass --optional-map PATH"
                )
            return path, True
        return self._site_settings_path(), False

    @staticmethod
    def _is_app_plugin(name: str) -> bool:
        """True when the plugin is a Django app — i.e. it has an ``apps.py``.

        The plugin plan defines a plugin package with ``apps.py`` (an
        ``AppConfig`` carrying ``name="plugins.<vertical>"`` and a ``label``). A
        config-only helper or an entry-point plugin has no app to add to an app
        list, so attaching it would write a line that does nothing.
        """
        try:
            spec = importlib.util.find_spec(name)
        except (ImportError, ValueError):
            return False
        if spec is None or not spec.submodule_search_locations:
            return False
        return any(
            (Path(location) / "apps.py").exists()
            for location in spec.submodule_search_locations
        )

    @staticmethod
    def _capability_for(spec) -> str:
        """The capability recorded alongside an optional map entry.

        Prefers the plugin's own short name when it is one of its capabilities
        (``plugins.ecommerce`` → ``ecommerce``, matching the plan's example) and
        otherwise takes the alphabetically first, so the recorded reason is always
        something the spec actually declares.
        """
        capabilities = sorted(spec.capabilities)
        return spec.short_name if spec.short_name in capabilities else (capabilities[0] if capabilities else "")

    def _migrations(self, options) -> None:
        """D7: show the migration plan, then ask before applying anything."""
        plan = io.StringIO()
        try:
            call_command("makemigrations", dry_run=True, verbosity=2, stdout=plan)
        except Exception as exc:  # noqa: BLE001 — reported verbatim, never swallowed
            self.log_warning(f"could not build a migration plan: {exc}")
            return
        output = plan.getvalue().strip()
        if not output:
            self.log_success("no model changes to migrate")
            return
        self.stdout.write(output)
        if not options.get("yes") and not self.confirm("Apply these migrations?"):
            self.log_warning("migrations skipped — run them deliberately when you are ready")
            return
        call_command("makemigrations", verbosity=0)
        call_command("migrate", verbosity=1)
        self.log_success("migrations applied")

    def _run_check(self) -> str | None:
        """Run ``manage.py check``; return the error verbatim, or ``None`` when clean."""
        captured = io.StringIO()
        try:
            call_command("check", stdout=captured, stderr=captured)
        except Exception as exc:  # noqa: BLE001 — the verbatim failure is the point (A3)
            return f"{type(exc).__name__}: {exc}"
        return None

    def _mutate(self, options, *, add: bool) -> int:
        """The shared attach/detach body: preview, write, verify, roll back on failure."""
        verb = "attach" if add else "detach"
        name = options.get("name")
        if not name:
            self.log_error(f"`{verb}` needs a plugin name — run `plugin list` to see them")
            return 2
        spec = self._resolve(name)
        if isinstance(spec, list):
            self.log_error(f"{name!r} is ambiguous — use the full name: " + ", ".join(s.name for s in spec))
            return 2
        if spec is None:
            self.log_error(f"unknown plugin {name!r}")
            registry = get_plugin_registry()
            self.stdout.write(
                "Attach by capability instead — `plugin list` shows what is available: "
                + ", ".join(sorted(registry.capabilities()))
            )
            return 2

        if add and not get_plugin_registry().is_available(spec.name):
            self.log_error(f"{spec.name} is not importable in this environment — install it first")
            return 1
        if add and not options.get("optional") and not self._is_app_plugin(spec.name):
            self.log_error(
                f"{spec.name} is not an app-shaped plugin (no apps.py), so it cannot be "
                "attached to an app list — use --optional for the optional-app map"
            )
            return 1

        try:
            path, is_optional = self._edit_target(options)
        except editing.RegionMissing as exc:
            self.log_error(str(exc))
            return 1

        before = path.read_text(encoding="utf-8")
        try:
            if is_optional:
                after = editing.with_optional_app(
                    before, spec.name, self._capability_for(spec), add=add
                )
            else:
                after = editing.with_app(before, spec.name, add=add)
        except editing.RegionMissing as exc:
            self.log_error(f"{path}: {exc}")
            return 1

        if after == before:
            state = "already attached" if add else "not attached"
            self.log_success(f"{spec.name} is {state} in {path} — nothing to do")
            return 0

        # A relative label reads better in a review than an absolute path, and the
        # diff is meant to be reviewed before it is applied.
        try:
            label = os.path.relpath(path)
        except ValueError:  # pragma: no cover - different drive (Windows)
            label = str(path)
        self.stdout.write(editing.unified_diff(before, after, label))
        if not options.get("apply"):
            self.stdout.write("")
            self.log_warning(
                f"preview only — nothing written. Re-run with --apply to {verb} {spec.short_name}."
            )
            return 0

        path.write_text(after, encoding="utf-8")
        failure = self._run_check()
        if failure:
            path.write_text(before, encoding="utf-8")
            self.log_error(f"`manage.py check` failed after {verb}; the edit was rolled back")
            self.stdout.write(failure)
            return 1

        self.log_success(f"{spec.name} {'attached' if add else 'detached'} in {path}")
        if add:
            self.stdout.write("  next: run your site's check/tests, then commit the settings change")
            if options.get("migrate"):
                self._migrations(options)
            elif self._is_app_plugin(spec.name):
                self.stdout.write("  models? add --migrate to review and apply migrations")
        return 0

    def _attach(self, options) -> int:
        return self._mutate(options, add=True)

    def _detach(self, options) -> int:
        return self._mutate(options, add=False)

    def handle(self, *args, **options) -> str | None:
        subcommand = options["subcommand"]
        if subcommand == "list":
            code = self._list(options)
        elif subcommand == "attach":
            code = self._attach(options)
        elif subcommand == "detach":
            code = self._detach(options)
        elif subcommand == "describe":
            code = self._describe(options)
        elif subcommand == "doctor":
            code = self._doctor(options)
        else:
            code = self._check(options)
        if code:
            raise SystemExit(code)
        return None
