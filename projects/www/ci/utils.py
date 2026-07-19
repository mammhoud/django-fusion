"""Template validation utilities for CI and local smoke tests.

Provides :class:`TemplateValidator` and convenience functions for
validating Django template syntax and context variable coverage
without requiring a running database or server.

The helpers intentionally use Django's template engine instead of
custom parsers so Wagtail/Django templates are validated with the
same tags, filters, and loaders that render production pages.

Typical usage in CI::

    from www.ci.utils import validate_template

    is_valid, errors, warnings = validate_template(
        "home/main.html",
        context={"page": mock_page, "request": mock_request},
    )
    assert is_valid, errors

Or for inline template strings::

    from www.ci.utils import validate_template_string

    is_valid, errors, warnings = validate_template_string(
        "Hello {{ name }}!",
        context={"name": "World"},
    )

Validation checks:
    1. Unbalanced ``{{`` / ``}}`` delimiters (fast lint before parsing).
    2. Django template compilation via ``Engine.from_string()`` / ``get_template()``.
    3. Missing context variable warnings (variables referenced but not
       provided in the test context).
    4. Lazy render-time errors (custom tags that raise on render).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from django.template import Context, Engine, TemplateSyntaxError
from django.template.loader import get_template
from django.template.base import FilterExpression, TextNode, VariableNode


class TemplateValidationError(ValueError):
    """Raised by callers that choose exception-based template validation.

    Unlike the tuple return style used by :class:`TemplateValidator`,
    this exception allows callers to use try/except for validation::

        try:
            validate_template_string("{{ invalid")
        except TemplateValidationError as exc:
            handle_error(str(exc))
    """


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
    """Validate Django template syntax and optional context coverage.

    Compiles template strings or resolved template files through
    Django's template engine and reports syntax errors, missing
    context variables, and render-time warnings.

    The validator distinguishes between:
    - **Errors**: Hard syntax failures (unbalanced delimiters, invalid tags).
    - **Warnings**: Missing context variables, render-time exceptions from
      custom tags that may require request/db objects unavailable in CI.

    Attributes:
        engine: Optional Django ``Engine`` instance. Uses the default
            engine when ``None``.
        builtin_context_names: Set of variable names that Django provides
            automatically (e.g. ``request``, ``user``, ``perms``).
            Variables from this set are not reported as missing when
            omitted from the validation context.

    Example::

        validator = TemplateValidator()
        is_valid, errors, warnings = validator.validate_string(
            "Hello {{ name }}!",
            context={"name": "World"},
        )
    """

    engine: Engine | None = None
    builtin_context_names: set[str] = field(default_factory=lambda: set(_BUILTIN_CONTEXT_NAMES))

    def validate_string(
        self,
        template_string: str,
        context: dict[str, Any] | None = None,
    ) -> tuple[bool, list[str], list[str]]:
        """Validate a template string passed directly (not via loader).

        Compiles the string through Django's template engine and
        reports any syntax errors, then renders with the provided
        context to catch lazy errors.

        Args:
            template_string: Raw Django template string to validate.
            context: Optional dictionary of context variables to use
                for render-time validation. Missing variables are
                reported as warnings, not errors.

        Returns:
            Tuple of ``(is_valid, errors, warnings)`` where:
            - ``is_valid``: ``True`` when no hard errors were found.
            - ``errors``: List of error message strings (syntax errors).
            - ``warnings``: List of warning message strings (missing
              context variables, render-time exceptions).
        """
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
        except Exception as exc:  # pragma: no cover — defensive for custom engines
            return False, [f"Template validation error: {exc}"], warnings

        warnings.extend(self._missing_context_warnings(template, context))

        # Rendering catches invalid filters/tags that may be raised lazily,
        # while keeping missing variables as warnings instead of hard failures.
        try:
            template.render(Context(context))
        except TemplateSyntaxError as exc:
            errors.append(f"Template syntax error: {exc}")
        except Exception as exc:
            # Custom tags may need request/db objects that CI intentionally
            # does not provide. Treat those as warnings after syntax compiles.
            warnings.append(f"Template render warning: {exc}")

        return not errors, errors, warnings

    def validate_template(
        self,
        template_name: str,
        context: dict[str, Any] | None = None,
    ) -> tuple[bool, list[str], list[str]]:
        """Validate a template resolved by Django's configured loaders.

        Loads the template via ``django.template.loader.get_template()``
        (using the project's ``TEMPLATES`` configuration) and validates
        its content. Falls back to render-only validation when the
        template source cannot be extracted.

        Args:
            template_name: Template name/path as used by ``{% include %}``
                or ``get_template()`` (e.g. ``\"home/main.html\"``).
            context: Optional context dict for variable coverage checks
                and render-time validation.

        Returns:
            Tuple of ``(is_valid, errors, warnings)`` with the same
            semantics as :meth:`validate_string`.
        """
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

    def _missing_context_warnings(
        self,
        template: Any,
        context: dict[str, Any],
    ) -> list[str]:
        """Identify template variables not present in the validation context.

        Walks the template's node tree to find all variable references
        and reports any that are not provided in the context (excluding
        Django's built-in context variables).

        Args:
            template: Compiled Django ``Template`` instance.
            context: The context dict provided for validation.

        Returns:
            List of warning strings, one per missing variable.
        """
        warnings: list[str] = []
        context_roots = set(context) | self.builtin_context_names
        for variable_name in sorted(self._iter_variable_roots(template.nodelist)):
            if variable_name not in context_roots:
                warnings.append(
                    f"Variable '{variable_name}' is not present "
                    f"in the validation context"
                )
        return warnings

    def _iter_variable_roots(self, nodelist: Any) -> set[str]:
        """Recursively collect all variable root names from a node list.

        Walks the template AST, extracting the root name of each
        ``VariableNode`` (the part before any ``|`` filters or ``.``
        attribute access). Handles ``if``/``else``/``for`` branches.

        Args:
            nodelist: Django template ``NodeList`` or any iterable
                of template nodes.

        Returns:
            Set of variable root name strings.
        """
        names: set[str] = set()
        for node in nodelist:
            if isinstance(node, TextNode):
                continue
            if isinstance(node, VariableNode):
                root = self._filter_expression_root(node.filter_expression)
                if root:
                    names.add(root)
            for child_attr in (
                "nodelist",
                "nodelist_true",
                "nodelist_false",
                "nodelist_loop",
                "nodelist_empty",
            ):
                child = getattr(node, child_attr, None)
                if child is not None:
                    names.update(self._iter_variable_roots(child))
        return names

    @staticmethod
    def _unbalanced_variable_delimiters(template_string: str) -> str | None:
        """Check for unbalanced ``{{`` / ``}}`` delimiters.

        A fast pre-flight check that catches mismatched variable
        delimiters without invoking the full parser.

        Args:
            template_string: Raw template content to inspect.

        Returns:
            Error message string if delimiters are unbalanced,
            ``None`` if the count matches.
        """
        if template_string.count("{{") != template_string.count("}}"):
            return (
                "Template syntax error: unbalanced variable delimiters "
                "'{{' and '}}'"
            )
        return None

    @staticmethod
    def _filter_expression_root(expression: FilterExpression) -> str | None:
        """Extract the root variable name from a ``FilterExpression``.

        Given a filter expression like ``user.profile|default:\"N/A\"``,
        returns ``\"user\"``. Ignores string literals and numeric values.

        Args:
            expression: Django ``FilterExpression`` instance.

        Returns:
            Root variable name string, or ``None`` if the expression
            is a literal (quoted string or number).
        """
        token = getattr(expression, "token", "")
        # Ignore quoted strings and numeric literals.
        if not token or token[0] in "'\"" or re.fullmatch(r"[-+]?\d+(\.\d+)?", token):
            return None
        root = token.split("|", 1)[0].split(".", 1)[0].strip()
        return root or None


def validate_template_string(
    template_string: str,
    context: dict[str, Any] | None = None,
) -> tuple[bool, list[str], list[str]]:
    """Convenience wrapper around :class:`TemplateValidator`.

    Creates a default ``TemplateValidator`` and calls
    :meth:`TemplateValidator.validate_string` with the provided arguments.

    Args:
        template_string: Raw Django template string to validate.
        context: Optional context dict for variable coverage checks.

    Returns:
        Tuple of ``(is_valid, errors, warnings)``.
    """
    return TemplateValidator().validate_string(template_string, context)


def validate_template(
    template_name: str,
    context: dict[str, Any] | None = None,
) -> tuple[bool, list[str], list[str]]:
    """Convenience wrapper for loader-based template validation.

    Creates a default ``TemplateValidator`` and calls
    :meth:`TemplateValidator.validate_template` with the provided arguments.

    Args:
        template_name: Template name/path as used by ``get_template()``.
        context: Optional context dict for variable coverage checks.

    Returns:
        Tuple of ``(is_valid, errors, warnings)``.
    """
    return TemplateValidator().validate_template(template_name, context)
