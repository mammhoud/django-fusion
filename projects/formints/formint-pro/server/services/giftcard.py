"""POS Full — Gift Card service (P2, Professional+).

Implements digital gift card issuance, balance lookup, redemption, reload
and disabling on top of ``GiftCard`` / ``GiftCardTransaction``:

* ``issue``    — create a card with an initial balance + ``issue`` ledger row.
* ``get_card`` — normalize the code and fetch the card (None when missing).
* ``redeem``   — spend from the balance (atomic), mark ``used`` at zero.
* ``reload``   — add balance (gift card top-up).
* ``disable``  — void the card so it can no longer be redeemed.

Every balance movement records an immutable ``GiftCardTransaction``. Money
math uses ``Decimal`` throughout. Codes are case-insensitive (normalized to
uppercase on lookup).
"""

from __future__ import annotations

import secrets
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.utils import timezone

from models.giftcard import GiftCard, GiftCardTransaction


class GiftCardError(ValueError):
    """Raised for invalid gift card operations."""


def generate_code() -> str:
    """Return a fresh human-readable gift card code (``GC-XXXXXXXX``)."""
    return f"GC-{secrets.token_hex(4).upper()}"


def _normalize(code: str) -> str:
    return (code or "").strip().upper()


def _q(value) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _record(card: GiftCard, tx_type: str, amount: Decimal, sale_id=None) -> GiftCardTransaction:
    return GiftCardTransaction.objects.create(
        gift_card=card,
        transaction_type=tx_type,
        amount=amount,
        balance_after=card.balance,
        sale_id=sale_id,
    )


def get_card(code: str) -> GiftCard | None:
    """Fetch a card by its (normalized) code, or None."""
    normalized = _normalize(code)
    if not normalized:
        return None
    return GiftCard.objects.filter(code=normalized).first()


def issue(
    initial_balance,
    currency: str = "USD",
    recipient_name: str = "",
    recipient_email: str = "",
    expires_at=None,
    notes: str = "",
) -> GiftCard:
    """Create a gift card with ``initial_balance`` and an issue ledger row."""
    balance = _q(initial_balance)
    if balance <= 0:
        raise GiftCardError("initial_balance must be positive")

    # Retry a couple of times in the unlikely event of a code collision.
    for _ in range(5):
        code = generate_code()
        if not GiftCard.objects.filter(code=code).exists():
            break
    else:
        raise GiftCardError("could not allocate a unique gift card code")

    with transaction.atomic():
        card = GiftCard.objects.create(
            code=code,
            initial_balance=balance,
            balance=balance,
            currency=currency or "USD",
            recipient_name=recipient_name or "",
            recipient_email=recipient_email or "",
            notes=notes or "",
            expires_at=expires_at,
        )
        _record(card, "issue", balance)
    return card


def redeem(code: str, amount, sale_id=None) -> GiftCard:
    """Spend ``amount`` from a card's balance (atomic).

    Marks the card ``used`` when the balance reaches zero. Raises
    ``GiftCardError`` on a missing/disabled/expired card or insufficient
    balance.
    """
    spend = _q(amount)
    if spend <= 0:
        raise GiftCardError("redeem amount must be positive")

    card = get_card(code)
    if card is None:
        raise GiftCardError("gift card not found")
    if card.status != "active":
        raise GiftCardError(f"gift card is not active ({card.status})")
    if card.expires_at and timezone.now() > card.expires_at:
        card.status = "expired"
        card.save(update_fields=["status", "updated_at"])
        raise GiftCardError("gift card has expired")
    if card.balance < spend:
        raise GiftCardError(
            f"insufficient balance (requested {spend}, available {card.balance})"
        )

    with transaction.atomic():
        card = GiftCard.objects.select_for_update().get(pk=card.pk)
        card.balance = (card.balance - spend).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP,
        )
        if card.balance == 0:
            card.status = "used"
        card.save(update_fields=["balance", "status", "updated_at"])
        _record(card, "redeem", -spend, sale_id=sale_id)
    return card


def reload(code: str, amount) -> GiftCard:
    """Top up a card's balance (records a ``reload`` ledger row)."""
    add = _q(amount)
    if add <= 0:
        raise GiftCardError("reload amount must be positive")

    card = get_card(code)
    if card is None:
        raise GiftCardError("gift card not found")
    if card.status == "disabled":
        raise GiftCardError("gift card is disabled")

    with transaction.atomic():
        card = GiftCard.objects.select_for_update().get(pk=card.pk)
        card.balance = (card.balance + add).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP,
        )
        if card.status in ("used", "expired"):
            card.status = "active"
        card.save(update_fields=["balance", "status", "updated_at"])
        _record(card, "reload", add)
    return card


def disable(code: str) -> GiftCard:
    """Void a card so it can no longer be redeemed (records a ``void`` row)."""
    card = get_card(code)
    if card is None:
        raise GiftCardError("gift card not found")
    if card.status == "disabled":
        return card
    with transaction.atomic():
        card.status = "disabled"
        card.save(update_fields=["status", "updated_at"])
        _record(card, "void", Decimal("0"))
    return card
