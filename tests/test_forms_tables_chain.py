"""Regression tests for ``FormMixin`` / ``TableMixin`` template-resolution chains.

These tests pin the **exact list of template names** that
``get_form_template_names()`` and ``get_table_template_names()`` return, so
that any future chain edit is caught by CI before it ships.

Why pin these chains?
---------------------
Each chain encodes the resolution order:

  1. Site-specific override (where a site can drop a custom template)
  2. django-fusion canonical (resolved via ``APP_DIRS=True``)

If a future PR adds, removes, or reorders an entry, sites will silently
fall through to a different template, or the canonical will be skipped
entirely. The tests below fail loudly instead.

History
-------
Added after the shim-cleanup pass that:
- deleted ``components/form.html`` (3-line shim → ``form/form.html``),
- deleted ``components/pagination/htmx_pagination.html`` and
  ``plugins/tables/table.html`` (asset-side backward-compat shims),
- and re-pinned the ``forms_tables.py`` chains to their canonical
  ``APP_DIRS``-resolved paths.

Without these tests, a future accidental edit to the chain would
silently break site template overrides.
"""
from __future__ import annotations

import pytest

from django_fusion.comp.routes.forms_tables import FormMixin, TableMixin


class _FormComponent(FormMixin):
    """Minimal ``FormMixin`` subclass for chain assertions.

    Subclassing ``FormMixin`` is required because the methods are
    instance methods that read class attributes (``form_name``,
    ``form_class``). ``form_class`` is left as ``None`` because
    ``get_form_class()`` is never called in these tests — we only assert
    on the chain, not on form instantiation.
    """
    form_name = "user_form"
    form_class = None


class _TableComponent(TableMixin):
    """Minimal ``TableMixin`` subclass for chain assertions."""
    table_name = "user_table"


# ── Form chain ────────────────────────────────────────────────────────────


def test_form_template_names_chain_is_pinned() -> None:
    """``FormMixin.get_form_template_names()`` must return the canonical chain.

    Order matters: site-specific first (``components/form/{name}.html``),
    canonical fallback second (``components/form/form.html``).
    """
    assert _FormComponent().get_form_template_names() == [
        "components/form/user_form.html",
        "components/form/form.html",
    ]


def test_form_chain_is_exactly_two_entries() -> None:
    """Sanity: form chain has exactly two entries (no accidental duplicates)."""
    chain = _FormComponent().get_form_template_names()
    assert len(chain) == 2
    # Ensure no duplicate (the previous bug we fixed).
    assert len(set(chain)) == len(chain)


def test_form_chain_substitutes_form_name() -> None:
    """The chain interpolates ``form_name`` only into the first (site-specific) entry.

    The canonical fallback must NOT be templated on the form name — it is
    the generic fallback, used only when no site override exists.
    """
    chain = _FormComponent().get_form_template_names()
    assert "user_form" in chain[0]
    assert "user_form" not in chain[1]


# ── Table chain ───────────────────────────────────────────────────────────


def test_table_template_names_chain_is_pinned() -> None:
    """``TableMixin.get_table_template_names()`` must return the canonical chain.

    Order matters: site-specific first (``plugins/tables/{name}.html``),
    canonical fallback second (``components/table.html``).
    """
    assert _TableComponent().get_table_template_names() == [
        "plugins/tables/user_table.html",
        "components/table.html",
    ]


def test_table_chain_is_exactly_two_entries() -> None:
    """Sanity: table chain has exactly two entries (no accidental duplicates)."""
    chain = _TableComponent().get_table_template_names()
    assert len(chain) == 2
    assert len(set(chain)) == len(chain)


def test_table_chain_substitutes_table_name() -> None:
    """The chain interpolates ``table_name`` only into the first (site-specific) entry.

    The canonical fallback must NOT be templated on the table name — it is
    the generic fallback, used only when no site override exists.
    """
    chain = _TableComponent().get_table_template_names()
    assert "user_table" in chain[0]
    assert "user_table" not in chain[1]


# ── Cross-cutting invariants ──────────────────────────────────────────────


def test_form_chain_has_no_dead_shim_paths() -> None:
    """Form chain must not reference any deleted shim paths.

    Guards against re-introduction of the retired shims:
    - ``components/form.html`` (deleted in the shim-cleanup pass)
    - any path that does not start with ``components/form/``
    """
    chain = _FormComponent().get_form_template_names()
    for entry in chain:
        assert "components/form/" in entry, f"unexpected form entry: {entry!r}"
        assert not entry.endswith("components/form.html"), (
            f"form chain references the deleted shim `components/form.html`: {entry!r}"
        )


def test_table_chain_has_no_dead_shim_paths() -> None:
    """Table chain must not reference any deleted shim paths.

    Guards against re-introduction of the retired shims:
    - ``plugins/tables/table.html`` (deleted generic fallback)
    - any path that does not start with ``plugins/tables/`` (for the
      site-specific entry) or ``components/table.html`` (for canonical)
    """
    chain = _TableComponent().get_table_template_names()
    for entry in chain:
        assert entry.startswith("plugins/tables/") or entry == "components/table.html", (
            f"unexpected table entry: {entry!r}"
        )
        assert entry != "plugins/tables/table.html", (
            f"table chain references the deleted shim `plugins/tables/table.html`: {entry!r}"
        )


# ── Determinism ───────────────────────────────────────────────────────────


def test_form_chain_is_deterministic() -> None:
    """``get_form_template_names()`` must return equal lists across calls.

    Catches any accidental list-mutation bug (e.g. a future refactor that
    appends to ``self._chain`` instead of returning a fresh list).
    """
    component = _FormComponent()
    first = component.get_form_template_names()
    second = component.get_form_template_names()
    assert first == second
    assert first is not second  # fresh list each call, not a shared mutable


def test_table_chain_is_deterministic() -> None:
    """``get_table_template_names()`` must return equal lists across calls."""
    component = _TableComponent()
    first = component.get_table_template_names()
    second = component.get_table_template_names()
    assert first == second
    assert first is not second
