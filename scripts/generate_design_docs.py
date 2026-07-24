#!/usr/bin/env python3
"""Enhance django-fusion design.md files with accurate ERDs and concrete examples."""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).parent.parent / "src" / "django_fusion"

SKIP_DIRS = {"__pycache__", "migrations", "templates", "static", "locale"}


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
    return (
        "```mermaid\n"
        "flowchart LR\n"
        f"    Request --> {package_name}\n"
        "    {package_name} --> Response\n"
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


def update_design_md(design_path: Path, models: list[dict], views: list[dict], commands: list[dict], package_path: str) -> None:
    content = design_path.read_text(encoding="utf-8")

    # Architecture / ERD section
    if models:
        erd = generate_erd(models)
        new_arch = f"## Architecture / ERD\n\n{erd}\n"
    elif views:
        diagram = generate_class_diagram(views)
        new_arch = f"## Architecture / Class Diagram\n\n{diagram}\n"
    else:
        new_arch = f"## Architecture\n\n{generate_flow_diagram(package_path)}\n"

    content = re.sub(r"## Architecture.*?\n(?=## |$)", new_arch, content, flags=re.DOTALL)

    # Usage example — only replace if the section is a placeholder/TODO
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

    design_path.write_text(content, encoding="utf-8")


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


def main() -> None:
    for design_path in sorted(BASE_DIR.rglob("design.md")):
        package_dir = design_path.parent
        if any(part in SKIP_DIRS for part in package_dir.parts):
            continue

        all_models, all_views, all_commands = collect_from_directory(package_dir)

        # Build import path relative to django_fusion
        relative = package_dir.relative_to(BASE_DIR)
        package_path = str(relative).replace("/", ".").replace("\\", ".")

        update_design_md(design_path, all_models, all_views, all_commands, package_path)
        print(f"Updated {design_path.relative_to(BASE_DIR.parent)}")


if __name__ == "__main__":
    main()
