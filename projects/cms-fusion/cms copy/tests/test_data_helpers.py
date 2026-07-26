"""
Tests for API helper functions — pagination, request parsing, auth helpers.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from www.api.data.helpers import (
    get_image_url,
    get_user_display_name,
    paginate_queryset,
    parse_body,
    _int_param,
)


# ═══════════════════════════════════════════════════════════════════════
# get_image_url
# ═══════════════════════════════════════════════════════════════════════


class TestGetImageUrl:
    def test_returns_empty_string_for_none(self):
        assert get_image_url(None) == ""

    def test_returns_url_from_file_field(self):
        mock_field = MagicMock()
        mock_field.file.url = "/media/images/test.png"
        assert get_image_url(mock_field) == "/media/images/test.png"

    def test_falls_back_to_direct_url(self):
        mock_field = MagicMock(spec=[])
        # No file attribute — fallback to direct url
        mock_field.url = "/media/test.jpg"
        assert get_image_url(mock_field) == "/media/test.jpg"

    def test_returns_empty_on_all_failures(self):
        mock_field = MagicMock(spec=["id"])
        # No file or url attribute — returns empty
        assert get_image_url(mock_field) == ""


# ═══════════════════════════════════════════════════════════════════════
# get_user_display_name
# ═══════════════════════════════════════════════════════════════════════


class TestGetUserDisplayName:
    def test_returns_empty_for_none(self):
        assert get_user_display_name(None) == ""

    def test_returns_full_name_when_both_present(self):
        user = MagicMock()
        user.first_name = "John"
        user.last_name = "Doe"
        user.get_full_name.return_value = "John Doe"
        user.username = "johndoe"
        assert get_user_display_name(user) == "John Doe"

    def test_returns_first_name_only(self):
        user = MagicMock()
        user.first_name = "Alice"
        user.last_name = ""
        user.get_full_name.return_value = "Alice"
        user.username = "alice"
        assert get_user_display_name(user) == "Alice"

    def test_falls_back_to_username(self):
        user = MagicMock()
        user.first_name = ""
        user.last_name = ""
        user.get_full_name.return_value = ""
        user.username = "bob"
        assert get_user_display_name(user) == "bob"

    def test_returns_str_on_exception(self):
        user = MagicMock()
        user.first_name = MagicMock(side_effect=AttributeError)
        user.get_full_name.side_effect = AttributeError
        user.username = MagicMock(side_effect=AttributeError)
        result = get_user_display_name(user)
        assert isinstance(result, str)
        assert len(result) > 0


# ═══════════════════════════════════════════════════════════════════════
# _int_param
# ═══════════════════════════════════════════════════════════════════════


class TestIntParam:
    def test_extracts_valid_int(self):
        request = MagicMock()
        request.GET = {"page": "3"}
        del request.query  # MagicMock has every attr — force Django GET fallback
        assert _int_param(request, "page", 1) == 3

    def test_returns_default_on_missing(self):
        request = MagicMock()
        request.GET = {}
        del request.query
        assert _int_param(request, "page", 1) == 1

    def test_returns_default_on_invalid(self):
        request = MagicMock()
        request.GET = {"page": "abc"}
        del request.query
        assert _int_param(request, "page", 1) == 1


# ═══════════════════════════════════════════════════════════════════════
# paginate_queryset
# ═══════════════════════════════════════════════════════════════════════


class TestPaginateQueryset:
    def test_returns_first_page(self):
        items = [1, 2, 3, 4, 5]
        qs = MagicMock()
        qs.count.return_value = len(items)
        qs.__getitem__.side_effect = lambda s: items[s]

        request = MagicMock()
        request.GET = {"page": "1", "per_page": "2"}
        del request.query  # MagicMock has every attr — force Django GET fallback

        result, pagination = paginate_queryset(qs, request, default_per_page=20)

        assert result == items[0:2]
        assert pagination["page"] == 1
        assert pagination["per_page"] == 2
        assert pagination["total"] == 5
        assert pagination["total_pages"] == 3

    def test_returns_second_page(self):
        items = [1, 2, 3, 4, 5]
        qs = MagicMock()
        qs.count.return_value = len(items)
        qs.__getitem__.side_effect = lambda s: items[s]

        request = MagicMock()
        request.GET = {"page": "2", "per_page": "2"}
        del request.query

        result, pagination = paginate_queryset(qs, request, default_per_page=20)

        assert result == items[2:4]
        assert pagination["page"] == 2
        assert pagination["total_pages"] == 3

    def test_returns_empty_page_gracefully(self):
        qs = MagicMock()
        qs.count.return_value = 0
        qs.__getitem__.return_value = []

        request = MagicMock()
        request.GET = {"page": "1"}
        del request.query

        result, pagination = paginate_queryset(qs, request, default_per_page=20)

        assert result == []
        assert pagination["total"] == 0
        assert pagination["total_pages"] == 1

    def test_uses_default_per_page(self):
        items = list(range(50))
        qs = MagicMock()
        qs.count.return_value = len(items)
        qs.__getitem__.side_effect = lambda s: items[s]

        request = MagicMock()
        request.GET = {"page": "1"}
        del request.query

        result, pagination = paginate_queryset(qs, request, default_per_page=10)

        assert len(result) == 10
        assert pagination["per_page"] == 10
        assert pagination["total_pages"] == 5


# ═══════════════════════════════════════════════════════════════════════
# parse_body
# ═══════════════════════════════════════════════════════════════════════


class TestParseBody:
    def test_parses_valid_json(self):
        request = MagicMock()
        request.body = b'{"name": "test", "value": 42}'
        assert parse_body(request) == {"name": "test", "value": 42}

    def test_returns_empty_dict_on_empty_body(self):
        request = MagicMock()
        request.body = b""
        assert parse_body(request) == {}

    def test_returns_empty_dict_on_invalid_json(self):
        request = MagicMock()
        request.body = b"not json"
        assert parse_body(request) == {}

    def test_returns_empty_dict_on_exception(self):
        request = MagicMock()
        request.body = MagicMock(side_effect=Exception("Boom"))
        assert parse_body(request) == {}
