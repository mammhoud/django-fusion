#!/usr/bin/env python3
"""Generate and gate plugin ``PRODUCT.md`` files.

Owning plan: ``docs/plans/structa-cloud/plugins/product-description-and-attach.md``
(deliverable 1). The plan's rule is the whole point of this script:

    a description may only state what the repository can prove.

so every claim in a ``PRODUCT.md`` is checked against something real:

* ``capabilities`` / ``signals`` must equal what the plugin's ``PluginSpec``
  registers — in **both** directions (rule D1). A description that advertises a
  capability the plugin does not provide fails, and so does a plugin capability
  the description silently omits.
* every ``evidence[].path`` must exist in the tree (rule D2).
* ``limits`` must be present and non-empty (rule D3) — an honest "what it does
  not do" is what keeps a listing free of unprovable claims.

Usage::

    python scripts/generate_plugin_products.py --list       # what exists vs what is missing
    python scripts/generate_plugin_products.py --check      # the gate; exit 1 on drift
    python scripts/generate_plugin_products.py --template htmx   # skeleton for a new plugin
    python scripts/generate_plugin_products.py --root <product plugins dir>

**One contract, two readers.** The rules live in
``src/django_fusion/plugins/descriptions.py``, which is also what
``manage.py plugin {describe,doctor,check}`` applies to the *live* registry. This
script does not re-implement them; it loads that module **by file path**
(``importlib.util.spec_from_file_location``) so no ``django_fusion`` package
``__init__`` runs and the gate keeps needing no virtualenv, no installed package
and no Django settings — the same property that lets the docs gate run in a bare
CI job. The catalog itself is read with :mod:`ast` for the same reason: a static
read of ``catalog.py`` rather than an import. ``tests/test_plugin_command.py``
asserts the static reader and the runtime catalog agree, so the two cannot drift
apart silently.

**Scope limit — what this gate does not do.** It does not rewrite
``PluginSpec.description``. The runtime one-liner is hand-maintained in
``catalog.py``, and generating source (rather than docs) would mean rewriting a
file that holds curated comments; instead a ``summary`` that is not reflected in
the catalog description is reported as a **warning** for a human, and the exit
code stays 0. Warnings never block, so nobody is tempted to make the gate quiet
by editing the claim instead of the code.
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
LIBRARY_DIR = HERE.parent
CATALOG_PATH = LIBRARY_DIR / "src" / "django_fusion" / "plugins" / "catalog.py"
#: ``src/django_fusion`` — the root spec names resolve against. The shared
#: contract module derives the same directory from its own ``__file__``; keeping
#: one source of truth here would be a second thing to drift, so the script does
#: not pass an override and lets the module resolve it.
DESCRIPTIONS_PATH = LIBRARY_DIR / "src" / "django_fusion" / "plugins" / "descriptions.py"


def load_descriptions():
    """Load the shared contract module by path — no package import, no Django.

    ``django_fusion.plugins`` imports :mod:`pluggy` through ``.manager``, so a
    normal ``import`` would make this gate depend on an installed environment.
    Loading the file directly executes only that file.
    """
    spec = importlib.util.spec_from_file_location("_fusion_plugin_descriptions", DESCRIPTIONS_PATH)
    if spec is None or spec.loader is None:  # pragma: no cover - layout damage
        raise SystemExit(f"✖ cannot load the description contract from {DESCRIPTIONS_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


descriptions = load_descriptions()


# ─────────────────────────────────────────────────────────────────────────────
# Static catalog reader — no import, no Django
# ─────────────────────────────────────────────────────────────────────────────
def _literal(node: ast.AST):
    """Evaluate the literal forms the catalog uses (str, bool, set/frozenset)."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, (ast.Set, ast.List, ast.Tuple)):
        return {_literal(element) for element in node.elts}
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        if node.func.id in {"frozenset", "set"} and node.args:
            return _literal(node.args[0])
    raise ValueError(f"unsupported literal: {ast.dump(node)[:60]}")


def _kwargs(call: ast.Call) -> dict[str, object]:
    out: dict[str, object] = {}
    for keyword in call.keywords:
        if keyword.arg is None:
            continue
        try:
            out[keyword.arg] = _literal(keyword.value)
        except ValueError:
            continue
    return out


def read_catalog() -> tuple[dict[str, dict], tuple[str, ...]]:
    """Return ``({spec name: spec fields}, CORE_PLUGINS)`` parsed from source."""
    tree = ast.parse(CATALOG_PATH.read_text(encoding="utf-8"))
    specs: dict[str, dict] = {}
    core: tuple[str, ...] = ()

    for node in tree.body:
        target = getattr(node, "target", None) or (node.targets[0] if isinstance(node, ast.Assign) else None)
        if not isinstance(target, ast.Name) or node.value is None:
            continue
        if target.id == "CORE_PLUGINS":
            core = tuple(_literal(node.value))
            continue
        if target.id != "PLUGIN_CATALOG" or not isinstance(node.value, ast.Dict):
            continue
        for value in node.value.values:
            if not isinstance(value, ast.Call):
                continue
            fields = _kwargs(value)
            name = fields.get("name")
            if not isinstance(name, str):
                continue
            specs[name] = {
                "name": name,
                "capabilities": set(fields.get("capabilities") or set()),
                "signals": set(fields.get("signals") or set()),
                "description": fields.get("description") or "",
                "core": bool(fields.get("core", False)),
            }
    if not specs:
        raise SystemExit(f"✖ no PluginSpec entries found in {CATALOG_PATH}")
    return specs, core


def expected_product_path(name: str) -> Path | None:
    """Canonical PRODUCT.md location for a spec (see the shared contract module)."""
    return descriptions.expected_product_path(name)


def discover(catalog: dict[str, dict], extra_roots: list[Path]) -> dict[str, Path]:
    """Map spec name → existing PRODUCT.md.

    Product plugins (``--root``) are reported under their dotted app path so a
    future catalog entry registers them with a stable name.
    """
    found: dict[str, Path] = {}
    for name in sorted(catalog):
        candidate = expected_product_path(name)
        if candidate is not None and candidate.exists():
            found[name] = candidate
    for root in extra_roots:
        if not root.is_dir():
            continue
        for child in sorted(root.iterdir()):
            candidate = child / descriptions.PRODUCT_FILENAME
            if candidate.exists():
                found.setdefault(f"{root.name}.{child.name}", candidate)
    return found


def render_template(name: str, spec: dict) -> str:
    """A skeleton whose frontmatter is already true — capabilities come from the spec."""
    short = name.rsplit(".", 1)[-1]
    capabilities = ", ".join(sorted(spec["capabilities"])) or "  # TODO: none registered"
    signals = ", ".join(sorted(spec["signals"])) or ""
    return f"""---
id: plugin.{short}
title: {short.replace('_', ' ').title()}
summary: TODO — one line, matching PluginSpec.description
capabilities: [{capabilities}]
signals: [{signals}]
requires: []
provides: []
surface: first-party
owner: TODO
evidence:
  - path: TODO/real/path.py
    what: TODO — what this file proves
limits:
  - "TODO — what this plugin deliberately does not do."
---

# {short.replace('_', ' ').title()}

## What it does

TODO — bullets, each traceable to an `evidence[].path` above.

## What it does not do

TODO — must match `limits:` and must stay empty-free (rule D3).
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="gate: exit 1 when a PRODUCT.md drifts or is missing")
    parser.add_argument("--list", action="store_true", help="list catalog plugins and their description state")
    parser.add_argument("--template", metavar="PLUGIN", help="print a PRODUCT.md skeleton for a plugin")
    parser.add_argument(
        "--root",
        action="append",
        default=[],
        metavar="DIR",
        help="also scan a product plugin directory (e.g. .../backend/plugins); repeatable",
    )
    parser.add_argument("--json", action="store_true", help="machine-readable report")
    args = parser.parse_args(argv)

    catalog, core = read_catalog()
    repo_root = LIBRARY_DIR.parent.parent  # <repo>/libs/django-fusion → <repo>
    # D4: a commercial claim in a description must be backed by a claims entry.
    claims = descriptions.load_claims(repo_root)
    roots = [Path(r) for r in args.root]

    if args.template:
        key = args.template if args.template in catalog else next(
            (n for n in catalog if n.endswith(f".{args.template}")), None
        )
        if key is None:
            print(f"✖ unknown plugin {args.template!r}", file=sys.stderr)
            return 2
        print(render_template(key, catalog[key]))
        return 0

    found = discover(catalog, roots)

    if args.list:
        print(f"\nPlugin descriptions — {len(catalog)} catalog spec(s), {len(found)} PRODUCT.md\n")
        for name in sorted(catalog):
            state = "documented" if name in found else "MISSING"
            core_flag = " · core" if name in core else ""
            print(f"  {name:42} {state:12}{core_flag}")
            if name not in found:
                expected = expected_product_path(name)
                if expected is not None:
                    print(f"       expected: {expected.relative_to(LIBRARY_DIR)}")
        print()
        return 0

    report = {"total": len(catalog), "documented": 0, "failures": [], "warnings": []}
    for name in sorted(catalog):
        spec = catalog[name]
        path = found.get(name)
        if path is None:
            expected = expected_product_path(name)
            where = expected.relative_to(LIBRARY_DIR) if expected else "(not shipped in this library)"
            report["failures"].append(f"{name}: no PRODUCT.md — expected at {where}")
            continue
        report["documented"] += 1
        failures, warnings = descriptions.check_product(
            path,
            name=name,
            capabilities=spec["capabilities"],
            signals=spec["signals"],
            description=str(spec["description"] or ""),
            repo_root=repo_root,
            claims_text=claims,
        )
        report["failures"] += [f"{path}: {message}" for message in failures]
        report["warnings"] += [f"{path}: {message}" for message in warnings]

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for failure in report["failures"]:
            print(f"  ✖ {failure}")
        for warning in report["warnings"]:
            print(f"  ⚠ {warning}")
        print(
            f"\n{report['documented']}/{report['total']} plugin(s) documented; "
            f"{len(report['failures'])} failure(s), {len(report['warnings'])} warning(s)"
        )

    if not args.check:
        return 0
    if report["failures"]:
        print("\n✖ description gate failed — a description must match the spec and cite real paths")
        return 1
    print("\n✔ description gate clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
