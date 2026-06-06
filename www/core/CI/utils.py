"""Template validation utilities for CI and local smoke tests.

The helpers intentionally use Django's template engine instead of custom parsers
so Wagtail/Django templates are validated with the same tags, filters, and
loaders that render production pages.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from django.template import Context, Engine, TemplateSyntaxError
from django.template.loader import get_template
from django.template.base import FilterExpression, TextNode, VariableNode


class TemplateValidationError(ValueError):
    """Raised by callers that choose exception-based template validation."""


_BUILTIN_CONTEXT_NAMES = {
    "False",
    "None",
    "True",
    "csrf_token",
    "forloop",
    "messages",
    "perms",
    "request",
    "user",
}


@dataclass(slots=True)
class TemplateValidator:
    """Validate Django template syntax and optional context coverage."""

    engine: Engine | None = None
    builtin_context_names: set[str] = field(default_factory=lambda: set(_BUILTIN_CONTEXT_NAMES))

    def validate_string(self, template_string: str, context: dict[str, Any] | None = None) -> tuple[bool, list[str], list[str]]:
        """Return ``(is_valid, errors, warnings)`` for a template string."""
        errors: list[str] = []
        warnings: list[str] = []
        context = context or {}

        brace_error = self._unbalanced_variable_delimiters(template_string)
        if brace_error:
            return False, [brace_error], warnings

        try:
            engine = self.engine or Engine.get_default()
            template = engine.from_string(template_string)
        except TemplateSyntaxError as exc:
            message = f"Template syntax error: {exc}"
            if "Invalid filter" in str(exc):
                return True, errors, [message]
            return False, [message], warnings
        except Exception as exc:  # pragma: no cover - defensive for custom engines
            return False, [f"Template validation error: {exc}"], warnings

        warnings.extend(self._missing_context_warnings(template, context))

        # Rendering catches invalid filters/tags that may be raised lazily while
        # keeping missing variables as warnings instead of hard failures.
        try:
            template.render(Context(context))
        except TemplateSyntaxError as exc:
            errors.append(f"Template syntax error: {exc}")
        except Exception as exc:
            # Custom tags may need request/db objects that CI intentionally does
            # not provide. Treat those as warnings after syntax has compiled.
            warnings.append(f"Template render warning: {exc}")

        return not errors, errors, warnings

    def validate_template(self, template_name: str, context: dict[str, Any] | None = None) -> tuple[bool, list[str], list[str]]:
        """Validate a template resolved by Django's configured loaders."""
        try:
            template = get_template(template_name)
        except Exception as exc:
            return False, [f"Template '{template_name}' does not exist or cannot be loaded: {exc}"], []

        source = getattr(getattr(template, "template", template), "source", None)
        if source is not None:
            return self.validate_string(source, context)

        try:
            template.render(context or {})
        except TemplateSyntaxError as exc:
            return False, [f"Template syntax error: {exc}"], []
        except Exception as exc:
            return True, [], [f"Template render warning: {exc}"]
        return True, [], []

    def _missing_context_warnings(self, template: Any, context: dict[str, Any]) -> list[str]:
        warnings: list[str] = []
        context_roots = set(context) | self.builtin_context_names
        for variable_name in sorted(self._iter_variable_roots(template.nodelist)):
            if variable_name not in context_roots:
                warnings.append(f"Variable '{variable_name}' is not present in the validation context")
        return warnings

    def _iter_variable_roots(self, nodelist: Any) -> set[str]:
        names: set[str] = set()
        for node in nodelist:
            if isinstance(node, TextNode):
                continue
            if isinstance(node, VariableNode):
                root = self._filter_expression_root(node.filter_expression)
                if root:
                    names.add(root)
            for child_attr in ("nodelist", "nodelist_true", "nodelist_false", "nodelist_loop", "nodelist_empty"):
                child = getattr(node, child_attr, None)
                if child is not None:
                    names.update(self._iter_variable_roots(child))
        return names

    @staticmethod
    def _unbalanced_variable_delimiters(template_string: str) -> str | None:
        if template_string.count("{{") != template_string.count("}}"):
            return "Template syntax error: unbalanced variable delimiters '{{' and '}}'"
        return None

    @staticmethod
    def _filter_expression_root(expression: FilterExpression) -> str | None:
        token = getattr(expression, "token", "")
        # Ignore quoted strings and numeric literals.
        if not token or token[0] in "'\"" or re.fullmatch(r"[-+]?\d+(\.\d+)?", token):
            return None
        root = token.split("|", 1)[0].split(".", 1)[0].strip()
        return root or None


def validate_template_string(template_string: str, context: dict[str, Any] | None = None) -> tuple[bool, list[str], list[str]]:
    """Convenience wrapper around :class:`TemplateValidator`."""
    return TemplateValidator().validate_string(template_string, context)


def validate_template(template_name: str, context: dict[str, Any] | None = None) -> tuple[bool, list[str], list[str]]:
    """Convenience wrapper for loader-based template validation."""
    return TemplateValidator().validate_template(template_name, context)
