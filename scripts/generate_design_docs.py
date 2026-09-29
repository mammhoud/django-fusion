#!/usr/bin/env python3
"""Generate and repair the django-fusion package docs (`design.md` + namespace `README.md`).

Every doc under ``src/django_fusion`` declares which package it documents — in a
title, a ``Path:`` line, a ``## Contents`` list, a ``## Usage`` import, or a
provenance footer. Those declarations are generated, so they must be regenerated
whenever a package moves; otherwise the docs keep advertising the module path a
package used to have (``django_fusion.comp.plugins``, ``django_fusion.site.views``,
…), and every copy-pasted example in them fails.

This script does two jobs:

1. **Renders** the generated *sections* of a ``design.md`` — the architecture /
   ERD / class diagram, the derived usage example, and the command list — from
   the package's real AST.
2. **Repairs** each doc's self-declarations so they match the package's real
   dotted path, and prunes declaration lists down to what actually exists.
3. **Validates** every ``django_fusion.*`` reference in every library doc —
   generated package docs, the numbered guides under ``docs/`` and ``README.md``
   — against the real module tree. A reference is accepted when its longest
   real module prefix resolves and any trailing segment is a name that module
   actually exposes (parsed with ``ast``, never imported). Repair only touches
   generated *declarations*, so hand-written prose is where stale paths survive;
   this third job is what turns them into a failing gate.

Repair is deliberately targeted, never a whole-file rewrite:

* curated prose, hand-written sections, and cross-package references that resolve
  to a real module are left untouched;
* a reference is only rewritten when it does **not** resolve to a module that
  exists — the signature of a path left behind by a package move — and only
  inside a generated section (``## Contents``, ``### Modules``, ``## Usage``,
  ``## Usage Example``) or a header declaration.

Usage::

    python scripts/generate_design_docs.py                     # repair everything
    python scripts/generate_design_docs.py --only django_fusion.plugins
    python scripts/generate_design_docs.py --check             # report drift; exit 1

``--check`` never writes and exits non-zero while any doc still declares a path
that is not real, which makes it usable as a CI gate. It runs both the repair
pass and the reference pass; a stale path in hand-written prose fails it too.

Scope limit: repair covers a doc's *declarations* (title, path, declaration
lists, generated usage blocks, footer) and the diagram/example sections it
renders. Free prose is deliberately left alone — a sentence such as "re-exports
from ``django_fusion.<old>``" is a content claim, and rewriting the module name
inside it could produce a confident, wrong sentence. Those are reported for a
human to fix instead.

The reference pass comments on prose but never edits it. Two escape hatches keep
it honest rather than noisy: a path named inside a paragraph that is *asserting
absence* ("there is no `django_fusion.wagtail` app", "the historical ... package
was removed") is documentation, not drift, so the surrounding paragraph is read
for absence cues before a reference is flagged; and a line carrying
``<!-- doc-path-check: allow -->`` is exempt outright for cases the cue list
cannot express.
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Any

LIBRARY_DIR = Path(__file__).parent.parent
BASE_DIR = LIBRARY_DIR / "src" / "django_fusion"

SKIP_DIRS = {"__pycache__", "migrations", "templates", "static", "locale"}

#: Provenance footer written on generated namespace READMEs. Older files credit a
#: script that does not exist in this repository; repair rewrites it to this one.
GENERATOR = "scripts/generate_design_docs.py"

PACKAGE_ROOT = "django_fusion"


# ─────────────────────────────────────────────────────────────────────────────
# Resolution helpers — the authority on "does this module path exist?"
# ─────────────────────────────────────────────────────────────────────────────
def _module_exists(dotted: str) -> bool:
    """True when *dotted* names a real module or package under ``src/django_fusion``.

    A directory counts as a package when it has an ``__init__.py`` **or** holds
    Python files directly — the latter covers implicit namespace packages such as
    ``django_fusion.core.encoder``, which are importable but have no
    ``__init__.py``. Treating those as non-existent silently skipped their
    repairs (the resolver refuses to rewrite a reference whose target it cannot
    resolve).
    """
    if dotted == PACKAGE_ROOT:
        return (BASE_DIR / "__init__.py").exists()
    prefix = PACKAGE_ROOT + "."
    if not dotted.startswith(prefix):
        return False
    relative = dotted[len(prefix) :].replace(".", "/")
    if not relative:
        return False
    target = BASE_DIR / relative
    if target.with_suffix(".py").exists() or (target / "__init__.py").exists():
        return True
    # Implicit namespace package: a directory reachable with no __init__.py.
    # ``rglob`` rather than ``glob`` because namespace packages nest —
    # ``django_fusion.site`` holds only ``site/auth/mixins.py`` yet imports fine.
    return target.is_dir() and any(target.rglob("*.py"))


#: Dotted ``django_fusion`` references in prose, e.g. ``django_fusion.core.assets``
#: or ``django_fusion.fragments.viewsets.BaseSnippetViewSet``.
_REFERENCE_RE = re.compile(r"\bdjango_fusion(?:\.[A-Za-z_][A-Za-z0-9_]*)+")

#: A path named inside a paragraph asserting it is gone is documentation, not
#: drift. The cue is looked for in the whole paragraph, because the list of dead
#: paths and the sentence calling them dead are often adjacent lines.
_ABSENCE_CUE_RE = re.compile(
    r"there is no|there are no|no longer|no such|does not exist|do not exist|"
    r"never existed|never resolved|never shipped|previously|historical|"
    r"was removed|were removed|has been removed|have been removed|"
    r"not an? (?:installable )?app|not a package|not a module|none of those|"
    r"does not ship|absent|retired|deleted|renamed|moved to",
    re.IGNORECASE,
)

#: Explicit per-line exemption for anything the cue list cannot express.
_ALLOW_MARKER = "<!-- doc-path-check: allow -->"

#: Doc trees under ``docs/`` that are archival, translated, vendored, or
#: prospective. They record past or proposed layouts deliberately, so a path that
#: no longer resolves there is content rather than drift. Excluded from the
#: reference pass and reported as a count so the exclusion stays visible.
ARCHIVAL_DOC_DIRS = ("agenda", "ar-content", "changelogs", "legacy", "plans")

_ATTR_CACHE: dict[str, set[str]] = {}


def _module_source(dotted: str) -> Path | None:
    """Source file backing *dotted*, or ``None`` when it is not a real module."""
    if dotted == PACKAGE_ROOT:
        candidate = BASE_DIR / "__init__.py"
    else:
        base = BASE_DIR / dotted[len(PACKAGE_ROOT) + 1 :].replace(".", "/")
        candidate = base / "__init__.py" if base.is_dir() else base.with_suffix(".py")
    return candidate if candidate.exists() else None


def _assigned_names(node: ast.AST) -> set[str]:
    """Names bound by an assignment target (handles tuple/list unpacking)."""
    if isinstance(node, ast.Name):
        return {node.id}
    if isinstance(node, (ast.Tuple, ast.List)):
        names: set[str] = set()
        for element in node.elts:
            names |= _assigned_names(element)
        return names
    return set()


def _string_constants(node: ast.AST) -> set[str]:
    """String literals in an ``__all__`` value (list/tuple, or concatenation)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return {node.value}
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        names: set[str] = set()
        for element in node.elts:
            names |= _string_constants(element)
        return names
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _string_constants(node.left) | _string_constants(node.right)
    return set()


def _collect_module_names(nodes, names: set[str]) -> None:
    """Names bound at module level, including inside top-level ``try``/``if`` blocks.

    ``models/__init__.py`` imports ``BackgroundTaskLog`` inside a ``try`` so the
    optional task dependency can be missing; that import still creates the
    attribute, so a conditional import must count as a real name.
    """
    for node in nodes:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    names |= _string_constants(node.value)
                names |= _assigned_names(target)
        elif isinstance(node, ast.AugAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "__all__":
                names |= _string_constants(node.value)
            names |= _assigned_names(node.target)
        elif isinstance(node, ast.AnnAssign):
            names |= _assigned_names(node.target)
        elif isinstance(node, (ast.Try, ast.If)):
            _collect_module_names(node.body, names)
            _collect_module_names(node.orelse, names)
            _collect_module_names(getattr(node, "finalbody", []), names)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            _collect_module_names(node.body, names)


def _module_attrs(dotted: str) -> set[str]:
    """Top-level names *dotted* exposes: defs, classes, assignments, imports, submodules.

    Parsed with :mod:`ast` rather than imported, so the check stays stdlib-only
    and cannot be perturbed by Django settings or import side effects.
    """
    if dotted in _ATTR_CACHE:
        return _ATTR_CACHE[dotted]
    names: set[str] = set()
    source = _module_source(dotted)
    if source is not None:
        try:
            tree: ast.Module | None = ast.parse(source.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            tree = None
        if tree is not None:
            _collect_module_names(tree.body, names)
        if source.name == "__init__.py":
            # Packages also expose their submodules directly.
            for child in source.parent.iterdir():
                if child.is_dir() and (child / "__init__.py").exists():
                    names.add(child.name)
                elif child.suffix == ".py" and child.name != "__init__.py":
                    names.add(child.stem)
    _ATTR_CACHE[dotted] = names
    return names


def _reference_ok(dotted: str) -> bool:
    """True when *dotted* resolves to a real module, or a real name on one."""
    parts = dotted.split(".")
    for end in range(len(parts), 0, -1):
        module = ".".join(parts[:end])
        if not _module_exists(module):
            continue
        remainder = parts[end:]
        return not remainder or remainder[0] in _module_attrs(module)
    return False


def _doc_surfaces() -> list[Path]:
    """Every library doc scanned for stale references.

    Wider than :func:`_iter_docs`: the generated package docs *plus* the numbered
    guides under ``docs/`` and the library ``README.md``, which are hand-written
    and therefore exactly where a moved package leaves a stale path behind.
    """
    docs = list(_iter_docs())
    docs += [
        doc
        for doc in sorted((LIBRARY_DIR / "docs").rglob("*.md"))
        if not _is_archival(doc)
    ]
    readme = LIBRARY_DIR / "README.md"
    if readme.exists():
        docs.append(readme)
    seen: set[Path] = set()
    return [doc for doc in docs if not (doc in seen or seen.add(doc))]


def _is_archival(doc: Path) -> bool:
    """True for a doc inside an :data:`ARCHIVAL_DOC_DIRS` tree under ``docs/``."""
    try:
        relative = doc.relative_to(LIBRARY_DIR / "docs")
    except ValueError:
        return False
    return bool(relative.parts) and relative.parts[0] in ARCHIVAL_DOC_DIRS


def count_archival_docs() -> int:
    """Archival docs the reference pass deliberately does not judge."""
    return sum(
        1 for doc in (LIBRARY_DIR / "docs").rglob("*.md") if _is_archival(doc)
    )


def _surfaces_for(only: list[str]) -> list[Path]:
    """Doc surfaces to reference-check, restricted to ``--only`` packages when given."""
    surfaces = _doc_surfaces()
    if not only:
        return surfaces
    selected: list[Path] = []
    for selector in only:
        if not selector.startswith(PACKAGE_ROOT + "."):
            continue
        target = BASE_DIR / selector[len(PACKAGE_ROOT) + 1 :].replace(".", "/")
        selected += [
            doc for doc in surfaces if doc == target or target in doc.parents
        ]
    seen: set[Path] = set()
    return [doc for doc in selected if not (doc in seen or seen.add(doc))]


def _paragraph_window(lines: list[str], index: int) -> str:
    """The blank-line delimited block containing ``lines[index]``."""
    start = index
    while start > 0 and lines[start - 1].strip():
        start -= 1
    end = index
    while end + 1 < len(lines) and lines[end + 1].strip():
        end += 1
    return "\n".join(lines[start : end + 1])


def find_stale_references(doc: Path) -> list[tuple[int, str]]:
    """``(line number, reference)`` for every ``django_fusion.*`` path that is not real."""
    try:
        lines = doc.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    findings: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        if _ALLOW_MARKER in line:
            continue
        references = set(_REFERENCE_RE.findall(line))
        if not references:
            continue
        window = _paragraph_window(lines, index)
        # Strip markdown emphasis so "There is **no** X" and "`no` X" both read
        # as the absence claim they are.
        if _ABSENCE_CUE_RE.search(re.sub(r"[*`_]", "", window)):
            continue
        findings += [
            (index + 1, ref) for ref in sorted(references) if not _reference_ok(ref)
        ]
    return findings


def check_doc_references(docs: list[Path], quiet: bool = False) -> int:
    """Report unresolvable ``django_fusion.*`` paths. Returns the finding count."""
    total = 0
    for doc in docs:
        findings = find_stale_references(doc)
        if not findings:
            continue
        total += len(findings)
        if not quiet:
            label = doc.relative_to(LIBRARY_DIR)
            for line_number, reference in findings:
                print(f"  stale path  {label}:{line_number}  {reference}")
    return total


def _package_path(directory: Path) -> str:
    """Dotted import path for a package directory."""
    relative = directory.relative_to(BASE_DIR)
    if str(relative) == ".":
        return PACKAGE_ROOT
    return f"{PACKAGE_ROOT}.{str(relative).replace('/', '.')}"


def _subpackages(directory: Path) -> list[str]:
    return sorted(
        child.name
        for child in directory.iterdir()
        if child.is_dir()
        and child.name not in SKIP_DIRS
        and child.name != "__pycache__"
        and (child / "__init__.py").exists()
    )


def _modules(directory: Path) -> list[str]:
    return sorted(
        child.name for child in directory.glob("*.py") if child.name != "__init__.py"
    )


def _parse_public_api(directory: Path) -> list[str] | None:
    """Names from ``__all__`` in the package ``__init__``, or ``None`` if absent."""
    init = directory / "__init__.py"
    if not init.exists():
        return None
    try:
        tree = ast.parse(init.read_text(encoding="utf-8"))
    except SyntaxError:
        return None
    for node in tree.body:
        target_value: ast.expr | None = None
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets
        ):
            target_value = node.value
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "__all__"
        ):
            target_value = node.value
        if target_value is None:
            continue
        if isinstance(target_value, (ast.List, ast.Tuple, ast.Set)):
            names = [
                element.value
                for element in target_value.elts
                if isinstance(element, ast.Constant) and isinstance(element.value, str)
            ]
            if names:
                return sorted(names)
    return None


# ─────────────────────────────────────────────────────────────────────────────
# AST parsing (models / views / commands)
# ─────────────────────────────────────────────────────────────────────────────
def _is_abstract(node: ast.ClassDef) -> bool:
    if node.name.startswith("Abstract"):
        return True
    for child in node.body:
        if isinstance(child, ast.ClassDef) and child.name == "Meta":
            for meta_child in child.body:
                if isinstance(meta_child, ast.Assign):
                    for target in meta_child.targets:
                        if isinstance(target, ast.Name) and target.id == "abstract":
                            return isinstance(meta_child.value, ast.Constant) and meta_child.value.value is True
    return False


def _model_names_in_module(tree: ast.AST) -> set[str]:
    """Return the names of all concrete Django model classes in the AST."""
    base_map: dict[str, list[str]] = {}
    abstract_set: set[str] = set()
    known_model_bases = {
        "Model",
        "BaseModel",
        "TimeStampedModel",
        "UUIDModel",
        "TimestampedModel",
        "SoftDeleteModel",
        "UUIDPrimaryKeyModel",
        "AbstractDataToken",
    }

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        bases: list[str] = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                if (
                    isinstance(base.value, ast.Name)
                    and base.value.id == "models"
                    and base.attr == "Model"
                ):
                    bases.append("Model")
                elif isinstance(base.value, ast.Name):
                    bases.append(base.attr)
                else:
                    bases.append(base.attr)
        base_map[node.name] = bases

        for child in node.body:
            if isinstance(child, ast.ClassDef) and child.name == "Meta":
                for item in child.body:
                    if not isinstance(item, ast.Assign):
                        continue
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == "abstract":
                            if isinstance(item.value, ast.Constant) and item.value.value is True:
                                abstract_set.add(node.name)

    def is_model(name: str, _seen: set[str] | None = None) -> bool:
        if name in known_model_bases:
            return True
        if name not in base_map:
            return False
        if _seen is None:
            _seen = set()
        if name in _seen:
            return False
        _seen.add(name)
        for b in base_map.get(name, []):
            if is_model(b, _seen):
                return True
        return False

    result: set[str] = set()
    for name, bases in base_map.items():
        if name in abstract_set:
            continue
        if is_model(name):
            result.add(name)
    return result


def _base_name(base: ast.expr) -> str:
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Attribute):
        return f"{_base_name(base.value)}.{base.attr}"
    return ""


def _field_info(assign: ast.Assign | ast.AnnAssign) -> dict[str, Any] | None:
    target: ast.Name | None = None
    if isinstance(assign, ast.Assign):
        for t in assign.targets:
            if isinstance(t, ast.Name):
                target = t
                break
    elif isinstance(assign, ast.AnnAssign) and isinstance(assign.target, ast.Name):
        target = assign.target

    if target is None:
        return None

    value = assign.value
    if value is None or not isinstance(value, ast.Call):
        return None

    func = value.func
    if isinstance(func, ast.Name):
        field_type = func.id
    elif isinstance(func, ast.Attribute):
        field_type = func.attr
    else:
        return None

    # Skip managers (e.g. objects = TokenCachedManager())
    if field_type.endswith("Manager") or target.id == "objects":
        return None

    # Skip choice / config constants
    if field_type.endswith("Choices") or target.id.endswith("_CHOICES"):
        return None

    # GenericForeignKey is a virtual relation; represent it but don't draw a relation line
    if field_type == "GenericForeignKey":
        return {"name": target.id, "type": "GenericForeignKey", "relation": None}

    relation = None
    if field_type in {"ForeignKey", "OneToOneField", "ManyToManyField"}:
        relation = _first_arg_str(value)

    return {"name": target.id, "type": field_type, "relation": relation}


# Common settings-based model references that are not statically resolvable.
_SETTINGS_TO_MODEL = {
    "settings.AUTH_USER_MODEL": "auth.User",
}


def _first_arg_str(call: ast.Call) -> str:
    for arg in call.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return arg.value
        if isinstance(arg, ast.Name):
            return arg.id
        if isinstance(arg, ast.Attribute):
            parts: list[str] = []
            node: ast.expr = arg
            while isinstance(node, ast.Attribute):
                parts.append(node.attr)
                node = node.value
            if isinstance(node, ast.Name):
                parts.append(node.id)
            dotted = ".".join(reversed(parts))
            return _SETTINGS_TO_MODEL.get(dotted, dotted)
    return ""


def parse_models(tree: ast.AST) -> list[dict[str, Any]]:
    model_names = _model_names_in_module(tree)
    models: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.ClassDef) and node.name in model_names):
            continue
        fields = []
        for child in node.body:
            if isinstance(child, (ast.Assign, ast.AnnAssign)):
                info = _field_info(child)
                if info:
                    fields.append(info)
        models.append({"name": node.name, "fields": fields})
    return models


def parse_views(tree: ast.AST) -> list[dict[str, Any]]:
    views = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = [_base_name(b) for b in node.bases]
            relevant = any(
                b.endswith(("View", "Viewset", "Mixin", "Component", "ViewSet"))
                for b in bases
            )
            if relevant:
                methods = [
                    child.name
                    for child in node.body
                    if isinstance(child, ast.FunctionDef) and not child.name.startswith("_")
                ]
                views.append({"name": node.name, "bases": bases, "methods": methods})
    return views


def parse_commands(directory: Path) -> list[dict[str, str]]:
    commands = []
    cmd_dir = directory / "management" / "commands"
    if not cmd_dir.exists():
        return commands
    for py_file in cmd_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and any(
                _base_name(b) == "BaseCommand" for b in node.bases
            ):
                help_text = ""
                for child in node.body:
                    if isinstance(child, ast.Assign):
                        for target in child.targets:
                            if isinstance(target, ast.Name) and target.id == "help" and isinstance(child.value, ast.Constant):
                                help_text = child.value.value
                commands.append({"name": py_file.stem, "help": help_text})
    return commands


# ─────────────────────────────────────────────────────────────────────────────
# Section rendering
# ─────────────────────────────────────────────────────────────────────────────
def _mermaid_id(name: str) -> str:
    """Return a valid Mermaid entity identifier (quote if needed)."""
    if not name:
        return '""'
    if name.isidentifier():
        return name
    return f'"{name}"'


def generate_erd(models: list[dict[str, Any]]) -> str:
    if not models:
        return "_No Django models found in this package._"
    lines = ["```mermaid", "erDiagram"]
    relations: list[str] = []
    for model in models:
        lines.append(f"    {model['name']} {{")
        for field in model["fields"]:
            type_name = field["type"]
            lines.append(f"        {type_name} {field['name']}")
            relation = field.get("relation")
            if not relation:
                continue
            target = _mermaid_id(relation)
            if relation == "self":
                target = model["name"]
                label = f'{field["name"]} (self)'
            else:
                label = field["name"]

            if type_name == "OneToOneField":
                cardinality = "||--||"
            elif type_name == "ManyToManyField":
                cardinality = "}o--o{"
            else:
                cardinality = "||--o|"

            relations.append(
                f'    {model["name"]} {cardinality} {target} : "{label}"'
            )
        lines.append("    }")
    if relations:
        lines.append("")
        lines.extend(relations)
    lines.append("```")
    return "\n".join(lines)


def generate_class_diagram(views: list[dict[str, Any]]) -> str:
    if not views:
        return "_No view/component classes found in this package._"
    lines = ["```mermaid", "classDiagram"]
    for view in views[:12]:  # limit classes shown
        lines.append(f"    class {view['name']} {{")
        for method in view["methods"][:5]:  # limit methods per class
            lines.append(f"      +{method}()")
        lines.append("    }")
        for base in view["bases"]:
            if base and not base.startswith("(") and base not in {"object", "View", "TemplateView", "FormView", "ListView", "DetailView", "UpdateView", "CreateView", "DeleteView"}:
                lines.append(f"    {base} <|-- {view['name']}")
    lines.append("```")
    return "\n".join(lines)


def generate_flow_diagram(package_name: str) -> str:
    """Fallback architecture diagram for a package with no models or views.

    Both edges are interpolated — the trailing edge used to be a plain string, so
    every generated diagram rendered a literal ``{package_name}`` node.
    """
    return (
        "```mermaid\n"
        "flowchart LR\n"
        f"    Request --> {package_name}\n"
        f"    {package_name} --> Response\n"
        "```"
    )


def generate_model_example(models: list[dict[str, Any]], package_path: str) -> str:
    if not models:
        return ""
    model = models[0]
    example_fields = [f"{f['name']}='...'" for f in model["fields"][:3] if f['type'] != 'Any']
    if not example_fields:
        example_fields = ["name='...'"]
    return (
        f"```python\n"
        f"from django_fusion.{package_path} import {model['name']}\n\n"
        f"# Query and create instances\n"
        f"qs = {model['name']}.objects.all()\n"
        f"obj = {model['name']}.objects.create({', '.join(example_fields)})\n"
        f"```"
    )


def generate_view_example(views: list[dict[str, Any]], package_path: str) -> str:
    if not views:
        return ""
    view = views[0]
    name = view["name"]
    if "Mixin" in name:
        return (
            f"```python\n"
            f"from django_fusion.{package_path} import {name}\n\n"
            f"# Use the mixin in your own view/component class\n"
            f"class MyView({name}, TemplateView):\n"
            f"    pass\n"
            f"```"
        )
    return (
        f"```python\n"
        f"from django_fusion.{package_path} import {name}\n\n"
        f"# Wire into urls.py\n"
        f"from django.urls import path\n"
        f"urlpatterns = [\n"
        f"    path('{name.lower()}/', {name}.as_view()),\n"
        f"]\n"
        f"```"
    )


def _replace_section(content: str, heading: str, body: str) -> tuple[str, bool]:
    """Replace a section's body, stopping at the next heading (levels 1–3)."""
    pattern = re.compile(
        rf"{re.escape(heading)}\n(.*?)(?=\n#{{1,3}} |\Z)", re.DOTALL
    )
    new_content, count = pattern.subn(f"{heading}\n\n{body}\n", content, count=1)
    return new_content, bool(count)


def render_design_md(
    content: str,
    models: list[dict],
    views: list[dict],
    commands: list[dict],
    package_path: str,
) -> str:
    """Refresh the generated sections of a ``design.md``."""
    if models:
        new_arch = f"## Architecture / ERD\n\n{generate_erd(models)}\n"
    elif views:
        new_arch = f"## Architecture / Class Diagram\n\n{generate_class_diagram(views)}\n"
    else:
        new_arch = f"## Architecture\n\n{generate_flow_diagram(package_path)}\n"

    content = re.sub(r"## Architecture.*?\n(?=## |$)", new_arch, content, flags=re.DOTALL)

    # Usage example — only replace if the section is a placeholder/TODO, so a
    # hand-written example survives (its imports are repaired separately).
    example_lines = []
    if models:
        example_lines.append(generate_model_example(models, package_path))
    if views:
        example_lines.append(generate_view_example(views, package_path))

    if example_lines:
        new_usage = "## Usage Example\n\n" + "\n\n".join(example_lines) + "\n"
        existing_usage_match = re.search(r"## Usage Example(.*?)(?=\n## |\Z)", content, flags=re.DOTALL)
        if existing_usage_match and "TODO" in existing_usage_match.group(1):
            content = re.sub(r"## Usage Example.*?\n(?=## |$)", new_usage, content, flags=re.DOTALL)
        elif "## Usage Example" not in content:
            content += "\n" + new_usage

    # Commands
    if commands:
        cmd_block = "## Commands / Entry Points\n\n```bash\n"
        for cmd in commands:
            cmd_block += f"python manage.py {cmd['name']}  # {cmd['help']}\n"
        cmd_block += "```\n"
        if "## Commands / Entry Points" in content:
            content = re.sub(r"## Commands / Entry Points.*?\n(?=## |$)", cmd_block, content, flags=re.DOTALL)
        else:
            content += "\n" + cmd_block

    return content


# ─────────────────────────────────────────────────────────────────────────────
# Self-declaration repair
# ─────────────────────────────────────────────────────────────────────────────
def _fix_module_path(module: str, expected: str) -> str | None:
    """Map a stale module path onto *expected*, or ``None`` if it is not stale.

    Resolution is the test, not pattern matching: anything that resolves to a real
    module is a legitimate (possibly cross-package) reference and is kept. For a
    path that does **not** resolve, the legacy prefix is replaced by the package's
    real path, keeping any trailing submodule that then resolves.
    """
    if module == expected or _module_exists(module):
        return None

    parts = module.split(".")
    leaf = expected.rsplit(".", 1)[-1]
    for index, part in enumerate(parts, start=1):
        if part != leaf:
            continue
        tail = parts[index:]
        candidate = expected + ("." + ".".join(tail) if tail else "")
        if _module_exists(candidate):
            return candidate

    # No shared anchor (e.g. ``django_fusion.site.responses`` for
    # ``django_fusion.core.encoder``): fall back to the package itself, which is
    # what a doc generated *for that package* must reference.
    return expected if _module_exists(expected) else None


def _repair_imports(text: str, expected: str, fixes: list[str], label: str) -> str:
    def _sub(match: re.Match[str]) -> str:
        module = match.group(1)
        fixed = _fix_module_path(module, expected)
        if fixed is None:
            return match.group(0)
        fixes.append(f"{label}:{module}->{fixed}")
        return f"from {fixed} import"

    return re.sub(r"from (django_fusion[\w.]*) import", _sub, text)


def repair_declarations(
    content: str, directory: Path, expected: str
) -> tuple[str, list[str]]:
    """Repair a doc's self-declarations in place. Returns content + applied fixes."""
    fixes: list[str] = []

    # ── Header block (everything before the first level-2 heading) ────────────
    head, separator, tail = content.partition("\n## ")
    original_head = head

    # Title: # `django_fusion.old` → # `django_fusion`
    def _title_sub(match: re.Match[str]) -> str:
        declared = match.group(1)
        if declared == expected:
            return match.group(0)
        fixes.append(f"title:{declared}->{expected}")
        return f"# `{expected}`"

    head = re.sub(r"^# `(django_fusion[\w.]*)`", _title_sub, head, flags=re.M)

    # Legacy bare heading artifact: "django_fusion.old — Title ====="
    def _artifact_sub(match: re.Match[str]) -> str:
        declared = match.group(1)
        if declared == expected:
            return match.group(0)
        fixes.append(f"heading:{declared}->{expected}")
        return expected + match.group(2)

    head = re.sub(
        r"^(django_fusion[\w.]*)((?:\s+[^\n=]*?)?[ \t]*=+[ \t]*)$",
        _artifact_sub,
        head,
        flags=re.M,
    )

    head = _repair_imports(head, expected, fixes, "header-import")
    if head != original_head:
        content = head + separator + tail

    # ── Overview parenthetical:  This package (`old`) ─────────────────────────
    # Written relative to the package root, and stale whenever the package moved.
    # This lives in a section body (## Overview), not the header block.
    relative = (
        expected[len(PACKAGE_ROOT) + 1 :]
        if expected.startswith(PACKAGE_ROOT + ".")
        else PACKAGE_ROOT
    )

    def _parenthetical_sub(match: re.Match[str]) -> str:
        declared = match.group(1)
        current = (
            declared[len(PACKAGE_ROOT) + 1 :]
            if declared.startswith(PACKAGE_ROOT + ".")
            else declared
        )
        if current == relative:
            return match.group(0)
        fixes.append(f"overview:{declared}->{relative}")
        return f"This package (`{relative}`)"

    content = re.sub(r"This package \(`([\w.]+)`\)", _parenthetical_sub, content)

    # ── Directory path ────────────────────────────────────────────────────────
    def _path_sub(match: re.Match[str]) -> str:
        declared = match.group(1).replace("/", ".")
        if declared == expected:
            return match.group(0)
        fixes.append(f"path:{declared}->{expected}")
        return f"Path: `{expected.replace('.', '/')}`"

    content = re.sub(
        r"^Path:\s*`?([\w./]+)`?[ \t]*$", _path_sub, content, flags=re.M
    )

    # ── Declaration lists — prune to what exists ──────────────────────────────
    if "## Contents" in content:
        modules = _modules(directory)
        subpackages = _subpackages(directory)
        body = "\n".join(
            [f"- `{name}/`" for name in subpackages]
            + [f"- `{name[:-3] if name.endswith('.py') else name}`" for name in modules]
        )
        if not body:
            body = "_No modules found in this package._"
        content, changed = _replace_section(content, "## Contents", body)
        if changed:
            fixes.append("contents")

    if "### Modules" in content:
        modules = _modules(directory)
        subpackages = _subpackages(directory)
        body = "\n".join(
            [f"- `{name}`" for name in modules]
            + [f"- `{name}/`" for name in subpackages]
        )
        if not body:
            body = "_No modules found in this package._"
        content, changed = _replace_section(content, "### Modules", body)
        if changed:
            fixes.append("modules")

    # ── Public API — only when the package declares __all__ ───────────────────
    public_api = _parse_public_api(directory)
    if public_api and "## Public API" in content:
        body = "\n".join(f"- `{name}`" for name in public_api)
        content, changed = _replace_section(content, "## Public API", body)
        if changed:
            fixes.append("public-api")

    # ── Generated usage blocks — fix import paths only ────────────────────────
    for heading in ("## Usage Example", "## Usage"):
        if heading + "\n" not in content:
            continue
        pattern = re.compile(
            rf"({re.escape(heading)}\n.*?)(?=\n#{{1,3}} |\Z)", re.DOTALL
        )

        def _usage_sub(match: re.Match[str], _expected: str = expected) -> str:
            return _repair_imports(match.group(1), _expected, fixes, "usage-import")

        content = pattern.sub(_usage_sub, content, count=1)

    # ── Provenance footer ─────────────────────────────────────────────────────
    def _footer_sub(match: re.Match[str]) -> str:
        credited = match.group(1)
        if credited == GENERATOR:
            return match.group(0)
        fixes.append(f"footer:{credited}->{GENERATOR}")
        return f"*Auto-generated by `{GENERATOR}`*"

    content = re.sub(
        r"\*Auto-generated by `([^`]+)`\*", _footer_sub, content
    )

    return content, fixes


# ─────────────────────────────────────────────────────────────────────────────
# Directory walking
# ─────────────────────────────────────────────────────────────────────────────
def collect_from_directory(package_dir: Path, depth: int = 0) -> tuple[list[dict], list[dict], list[dict]]:
    all_models: list[dict] = []
    all_views: list[dict] = []
    all_commands: list[dict] = []

    for py_file in package_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        all_models.extend(parse_models(tree))
        all_views.extend(parse_views(tree))

    all_commands.extend(parse_commands(package_dir))

    # Recurse into immediate subpackages if this is a parent package
    if depth == 0:
        for subdir in package_dir.iterdir():
            if subdir.is_dir() and (subdir / "__init__.py").exists():
                sub_models, sub_views, sub_commands = collect_from_directory(subdir, depth=depth + 1)
                all_models.extend(sub_models)
                all_views.extend(sub_views)
                all_commands.extend(sub_commands)

    return all_models, all_views, all_commands


def _iter_docs() -> list[Path]:
    docs: list[Path] = []
    for pattern in ("design.md", "README.md"):
        for doc in sorted(BASE_DIR.rglob(pattern)):
            if any(part in SKIP_DIRS for part in doc.parent.parts):
                continue
            docs.append(doc)
    return docs


def _matches(package_path: str, only: list[str]) -> bool:
    if not only:
        return True
    return any(
        package_path == selector or package_path.startswith(selector + ".")
        for selector in only
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="PACKAGE",
        help="limit to one package (dotted path, e.g. django_fusion.plugins); repeatable",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="report drift without writing; exit 1 when any doc declares a non-real path",
    )
    parser.add_argument("--quiet", action="store_true", help="only print the summary")
    parser.add_argument(
        "--no-references",
        action="store_true",
        help="skip the stale-path pass over every library doc",
    )
    args = parser.parse_args(argv)

    changed: list[tuple[Path, list[str]]] = []
    scanned = 0

    for doc in _iter_docs():
        directory = doc.parent
        expected = _package_path(directory)
        if not _matches(expected, args.only):
            continue
        scanned += 1

        original = doc.read_text(encoding="utf-8")
        content = original

        if doc.name == "design.md":
            models, views, commands = collect_from_directory(directory)
            content = render_design_md(content, models, views, commands, expected)

        content, fixes = repair_declarations(content, directory, expected)

        if content == original:
            continue
        changed.append((doc, fixes))
        if not args.check:
            doc.write_text(content, encoding="utf-8")
        if not args.quiet:
            action = "would update" if args.check else "updated"
            print(f"{action} {doc.relative_to(BASE_DIR.parent)}  [{', '.join(fixes)}]")

    verb = "need repair" if args.check else "updated"
    print(f"\nscanned {scanned} doc(s); {len(changed)} {verb}")

    stale = 0
    surfaces: list[Path] = []
    if not args.no_references:
        surfaces = _surfaces_for(args.only)
        if not args.quiet:
            skipped = count_archival_docs()
            print(
                f"\nchecking {len(surfaces)} doc(s) for stale django_fusion.* paths "
                f"({skipped} archival/planning doc(s) excluded)..."
            )
        stale = check_doc_references(surfaces, quiet=args.quiet)
        print(f"stale path reference(s): {stale}")

    if args.check and (changed or stale):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
