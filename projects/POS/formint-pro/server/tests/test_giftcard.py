"""
Gift Cards (P2) — issue / redeem / reload / disable tests.

Covers ``services.giftcard``:
  * ``issue`` — creates a card + ``issue`` ledger row; rejects non-positive.
  * ``get_card`` — case-insensitive code lookup.
  * ``redeem`` — atomic spend, ``used`` at zero, insufficient-balance and
    disabled/expired/missing rejections.
  * ``reload`` — top-up + reactivation.
  * ``disable`` — void + ``void`` ledger row.

Models and the service are imported lazily (the conftest ``django_bootstrap``
fixture configures Django first).
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from django.utils import timezone


def _svc():
    import services.giftcard as g

    return g


def _models():
    from models.giftcard import GiftCard, GiftCardTransaction
    return GiftCard, GiftCardTransaction


@pytest.fixture(autouse=True)
def _clean(django_bootstrap):
    GiftCard, GiftCardTransaction = _models()
    GiftCardTransaction.objects.all().delete()
    GiftCard.objects.all().delete()
    yield


class TestIssue:
    def test_issue_creates_card_and_ledger(self):
        g = _svc()
        GiftCard, GiftCardTransaction = _models()
        card = g.issue(50, recipient_name="Jane")
        assert card.balance == card.initial_balance == 50
        assert card.code.startswith("GC-")
        txs = GiftCardTransaction.objects.filter(gift_card=card)
        assert txs.count() == 1
        assert txs.first().transaction_type == "issue"
        assert float(txs.first().amount) == 50.0

    def test_issue_rejects_non_positive(self):
        g = _svc()
        with pytest.raises(g.GiftCardError):
            g.issue(0)
        with pytest.raises(g.GiftCardError):
            g.issue(-5)

    def test_codes_are_unique(self):
        g = _svc()
        a = g.issue(10)
        b = g.issue(10)
        assert a.code != b.code


class TestGetCard:
    def test_lookup_is_case_insensitive(self):
        g = _svc()
        card = g.issue(20)
        found = g.get_card(card.code.lower())
        assert found is not None
        assert found.id == card.id

    def test_missing_returns_none(self):
        g = _svc()
        assert g.get_card("GC-NOPE") is None


class TestRedeem:
    def test_redeem_decrements_and_records_negative_amount(self):
        g = _svc()
        GiftCard, GiftCardTransaction = _models()
        card = g.issue(100)
        card = g.redeem(card.code, 25)
        assert card.balance == 75
        txs = GiftCardTransaction.objects.filter(gift_card=card).order_by("id")
        assert [t.transaction_type for t in txs] == ["issue", "redeem"]
        assert float(txs[1].amount) == -25.0
        assert float(txs[1].balance_after) == 75.0

    def test_redeem_marks_used_at_zero(self):
        g = _svc()
        card = g.issue(10)
        card = g.redeem(card.code, 10)
        assert card.status == "used"
        assert card.balance == 0

    def test_redeem_insufficient_balance(self):
        g = _svc()
        card = g.issue(10)
        with pytest.raises(g.GiftCardError):
            g.redeem(card.code, 11)
        card.refresh_from_db()
        assert float(card.balance) == 10.0

    def test_redeem_missing_card(self):
        g = _svc()
        with pytest.raises(g.GiftCardError):
            g.redeem("GC-MISSING", 5)

    def test_redeem_disabled_card(self):
        g = _svc()
        card = g.issue(10)
        g.disable(card.code)
        with pytest.raises(g.GiftCardError):
            g.redeem(card.code, 5)

    def test_redeem_expired_card(self):
        g = _svc()
        GiftCard, _ = _models()
        card = g.issue(10)
        card.expires_at = timezone.now() - timedelta(days=1)
        card.save(update_fields=["expires_at"])
        with pytest.raises(g.GiftCardError):
            g.redeem(card.code, 5)
        card.refresh_from_db()
        assert card.status == "expired"

    def test_redeem_negative_amount(self):
        g = _svc()
        card = g.issue(10)
        with pytest.raises(g.GiftCardError):
            g.redeem(card.code, 0)


class TestReload:
    def test_reload_adds_balance(self):
        g = _svc()
        GiftCard, GiftCardTransaction = _models()
        card = g.issue(20)
        card = g.reload(card.code, 30)
        assert card.balance == 50
        txs = GiftCardTransaction.objects.filter(gift_card=card).order_by("id")
        assert txs.last().transaction_type == "reload"
        assert float(txs.last().amount) == 30.0

    def test_reload_reactivates_used_card(self):
        g = _svc()
        card = g.issue(10)
        card = g.redeem(card.code, 10)
        assert card.status == "used"
        card = g.reload(card.code, 10)
        assert card.status == "active"
        assert float(card.balance) == 10.0


class TestDisable:
    def test_disable_voids_card(self):
        g = _svc()
        GiftCard, GiftCardTransaction = _models()
        card = g.issue(10)
        card = g.disable(card.code)
        assert card.status == "disabled"
        assert GiftCardTransaction.objects.filter(
            gift_card=card, transaction_type="void",
        ).exists()

    def test_disable_missing_card(self):
        g = _svc()
        with pytest.raises(g.GiftCardError):
            g.disable("GC-NOPE")
