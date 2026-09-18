"""
Loyalty tests — reversal transaction type + customer marketing consent.

Covers the P1 "Loyalty System" additions: an immutable points ledger can
record reversals (negative entries), and customers carry a GDPR marketing
consent flag with a grant timestamp.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _clean_loyalty(django_bootstrap):
    from models.loyalty import LoyaltyTransaction
    from models.pos import Customer

    LoyaltyTransaction.objects.all().delete()
    Customer.objects.all().delete()
    yield


class TestReversalTransaction:
    def test_reversal_type_is_valid(self, django_bootstrap, customer_factory):
        from models.loyalty import LoyaltyTransaction
        cust = customer_factory()
        txn = LoyaltyTransaction.objects.create(
            customer=cust,
            transaction_type="reversal",
            points_change=-100,
            balance_after=0,
            reason="Refund reversal",
        )
        assert txn.transaction_type == "reversal"
        assert txn.points_change == -100
        assert txn.balance_after == 0

    def test_all_types_accepted(self, django_bootstrap, customer_factory):
        from models.loyalty import LoyaltyTransaction
        cust = customer_factory()
        for ttype in ("earn", "redeem", "adjust", "expire", "reversal"):
            txn = LoyaltyTransaction.objects.create(
                customer=cust, transaction_type=ttype, points_change=0, balance_after=0,
            )
            assert txn.transaction_type == ttype

    def test_negative_points_change_represents_reversal(self, django_bootstrap, customer_factory):
        from models.loyalty import LoyaltyTransaction
        cust = customer_factory()
        txn = LoyaltyTransaction.objects.create(
            customer=cust, transaction_type="reversal",
            points_change=-250, balance_after=0,
        )
        assert txn.points_change < 0


class TestCustomerConsent:
    def test_consent_defaults_false(self, customer_factory):
        cust = customer_factory()
        assert cust.marketing_consent is False
        assert cust.consent_granted_at is None

    def test_consent_can_be_granted(self, customer_factory):
        from django.utils import timezone
        cust = customer_factory(marketing_consent=True, consent_granted_at=timezone.now())
        cust.refresh_from_db()
        assert cust.marketing_consent is True
        assert cust.consent_granted_at is not None

    def test_consent_can_be_revoked(self, customer_factory):
        from django.utils import timezone
        cust = customer_factory(marketing_consent=True, consent_granted_at=timezone.now())
        cust.marketing_consent = False
        cust.save()
        cust.refresh_from_db()
        assert cust.marketing_consent is False
