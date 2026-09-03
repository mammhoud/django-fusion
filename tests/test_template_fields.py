"""Tests for the sandboxed dynamic template field engine.

The engine is pure Python (no database, no Wagtail), so these tests run in
the plain pytest suite without the django_db marker.
"""

from __future__ import annotations

import pytest
from django_fusion.template_fields import (
    FilterSpec,
    TemplateFieldEngine,
    parse_fields,
    register_filter,
    sanitize_url,
)
from django_fusion.template_fields.filters import default_registry


@pytest.fixture
def engine():
    return TemplateFieldEngine()


class TestParseFields:
    def test_simple_path(self):
        refs = parse_fields("Hi {{ customer.name }}")
        assert len(refs) == 1
        assert refs[0].path == "customer.name"
        assert refs[0].root == "customer"
        assert refs[0].filters == ()

    def test_nested_path(self):
        refs = parse_fields("{{ order.billing.address.city }}")
        assert refs[0].path == "order.billing.address.city"

    def test_filter_with_arg(self):
        refs = parse_fields('{{ order.total|currency:"USD" }}')
        assert refs[0].filters == (FilterSpec(name="currency", arg="USD"),)

    def test_bare_arg(self):
        refs = parse_fields("{{ text|truncate:30 }}")
        assert refs[0].filters == (FilterSpec(name="truncate", arg="30"),)

    def test_chained_filters(self):
        refs = parse_fields("{{ name|lower|title }}")
        assert [f.name for f in refs[0].filters] == ["lower", "title"]

    def test_multiple_fields(self):
        refs = parse_fields("{{ a.x }} and {{ b.y|upper }}")
        assert [r.path for r in refs] == ["a.x", "b.y"]

    def test_no_fields(self):
        assert parse_fields("plain text") == []

    def test_escaped_quote_in_arg(self):
        refs = parse_fields(r'{{ x|default:"say \"hi\"" }}')
        assert refs[0].filters[0].arg == 'say "hi"'


class TestRender:
    def test_simple(self, engine):
        assert engine.render("Hi {{ customer.name }}", {"customer": {"name": "Alice"}}) == "Hi Alice"

    def test_nested(self, engine):
        ctx = {"order": {"billing": {"address": {"city": "Cairo"}}}}
        assert engine.render("{{ order.billing.address.city }}", ctx) == "Cairo"

    def test_missing_fails_safe(self, engine):
        assert engine.render("{{ nope }}", {}) == ""

    def test_missing_nested_fails_safe(self, engine):
        assert engine.render("{{ a.b.c }}", {"a": {}}) == ""

    def test_default_filter_fallback(self, engine):
        assert engine.render('{{ company|default:"N/A" }}', {}) == "N/A"

    def test_allowlist_blocks_roots(self, engine):
        ctx = {"customer": {"name": "A"}, "secret": {"key": "x"}}
        out = engine.render("{{ customer.name }}/{{ secret.key }}", ctx, allowlist=["customer"])
        assert out == "A/"

    def test_auto_escape(self, engine):
        assert engine.render("{{ v }}", {"v": "<script>alert(1)</script>"}) == "&lt;script&gt;alert(1)&lt;/script&gt;"

    def test_auto_escape_off(self, engine):
        assert engine.render("{{ v }}", {"v": "<b>x</b>"}, auto_escape=False) == "<b>x</b>"

    def test_linebreaks_is_safe(self, engine):
        out = engine.render("{{ v|linebreaks }}", {"v": "a\n\nb"})
        assert isinstance(out, str)
        assert "<p>a</p><p>b</p>" in out
        # The input is escaped before wrapping.
        out2 = engine.render("{{ v|linebreaks }}", {"v": "<b>a</b>"})
        assert "&lt;b&gt;a&lt;/b&gt;" in out2

    def test_safe_url_filter(self, engine):
        assert engine.render("{{ u|safe_url }}", {"u": "javascript:alert(1)"}) == "#"
        assert engine.render("{{ u|safe_url }}", {"u": "https://example.com"}) == "https://example.com"

    def test_string_length_cap(self):
        e = TemplateFieldEngine(max_string_length=5)
        assert e.render("{{ v }}", {"v": "abcdefghij"}) == "abcde"

    def test_list_length_cap(self):
        e = TemplateFieldEngine(max_list_items=3)
        assert e.render('{{ v|join:", " }}', {"v": ["a", "b", "c", "d"]}) == "a, b, c"

    def test_bare_arg_render(self, engine):
        assert engine.render("{{ text|truncate:4 }}", {"text": "abcdefgh"}) == "abc…"

    def test_callables_never_resolve(self, engine):
        class Thing:
            def secret(self):
                return "leak"

        assert engine.render("{{ t.secret }}", {"t": Thing()}) == ""

    def test_list_index(self, engine):
        assert engine.render("{{ items.0 }}", {"items": ["x", "y"]}) == "x"

    def test_unknown_filter_raises(self, engine):
        with pytest.raises(KeyError):
            engine.render("{{ v|bogus }}", {"v": "x"})


class TestValidate:
    def test_unknown_filter_is_error(self, engine):
        issues = engine.validate("{{ v|bogus }}")
        assert any(i.level == "ERROR" and i.code == "unknown_filter" for i in issues)

    def test_blocked_root_is_warning(self, engine):
        issues = engine.validate("{{ secret.x }}", allowlist=["customer"])
        assert any(i.code == "blocked_root" for i in issues)

    def test_unresolved_is_warning(self, engine):
        issues = engine.validate("{{ a.b }}", context={"a": {}})
        assert any(i.code == "unresolved" for i in issues)

    def test_clean_template_has_no_issues(self, engine):
        issues = engine.validate("{{ customer.name }}", context={"customer": {"name": "A"}}, allowlist=["customer"])
        assert issues == []


class TestPreview:
    def test_resolved_and_unresolved(self, engine):
        result = engine.preview("{{ a }} and {{ b }}", {"a": "yes"})
        assert result.resolved == ["a"]
        assert result.unresolved == ["b"]
        assert result.html == "yes and "
        assert any(i.code == "unresolved" for i in result.issues)


class TestFilters:
    def test_currency(self):
        assert default_registry().apply("currency", 99.5, ("USD",)) == "$99.50"

    def test_date(self):
        from datetime import datetime

        value = datetime(2024, 1, 15, 14, 30)
        assert default_registry().apply("date", value, ("M d, Y",)) == "Jan 15, 2024"

    def test_date_iso_string(self):
        assert default_registry().apply("date", "2024-01-15", ("M d, Y",)) == "Jan 15, 2024"

    def test_upper_lower_title(self):
        assert default_registry().apply("upper", "acme", ()) == "ACME"
        assert default_registry().apply("lower", "ACME", ()) == "acme"
        assert default_registry().apply("title", "premium coffee", ()) == "Premium Coffee"

    def test_truncate(self):
        assert default_registry().apply("truncate", "a very long title here", (10,)) == "a very lo…"

    def test_yesno(self):
        assert default_registry().apply("yesno", True, ("Paid,Pending",)) == "Paid"
        assert default_registry().apply("yesno", False, ("Paid,Pending",)) == "Pending"

    def test_phone(self):
        assert default_registry().apply("phone", "5551234567", ("+1",)) == "+1 (555) 123-4567"

    def test_length_and_join(self):
        assert default_registry().apply("length", [1, 2, 3], ()) == "3"
        assert default_registry().apply("join", ["coffee", "tea"], (", ",)) == "coffee, tea"

    def test_url_encode(self):
        assert default_registry().apply("url_encode", "hello world", ()) == "hello%20world"

    def test_custom_filter_registration(self):
        register_filter("shout", lambda v, args: str(v).upper() + "!")
        assert default_registry().apply("shout", "hi", ()) == "HI!"


class TestSanitizeUrl:
    @pytest.mark.parametrize(
        "url,expected",
        [
            ("javascript:alert(1)", "#"),
            ("JaVaScRiPt:alert(1)", "#"),
            ("data:text/html;base64,xxx", "#"),
            ("vbscript:msgbox(1)", "#"),
            ("file:///etc/passwd", "#"),
            ("https://example.com", "https://example.com"),
            ("/relative/path", "/relative/path"),
        ],
    )
    def test_schemes(self, url, expected):
        assert sanitize_url(url) == expected
