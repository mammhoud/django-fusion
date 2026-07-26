"""
Withdrawals API — instructor payout requests (bolt-pattern adapter).

Endpoints:
    GET    /apis/withdrawals/               — List my withdrawals (instructor)
    POST   /apis/withdrawals/create/         — Request a withdrawal (instructor)
    GET    /apis/withdrawals/<pk>/           — Withdrawal detail
    PATCH  /apis/withdrawals/<pk>/cancel/    — Cancel a pending withdrawal
    PATCH  /apis/withdrawals/<pk>/approve/   — Approve withdrawal (admin)
    PATCH  /apis/withdrawals/<pk>/reject/    — Reject withdrawal (admin)
"""

from __future__ import annotations

import logging

from decimal import Decimal

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone

from plugins.lms.models import Withdrawal
from www.api.data_adapter import bolt_view, login_required, parse_body
from www.api.data.helpers import paginate_queryset, paginated_response

logger = logging.getLogger(__name__)


# ── Serializer ──


def _serialize_withdrawal(w: Withdrawal) -> dict:
    """Serialize a withdrawal request for the frontend."""
    return {
        "id": w.id,
        "instructor": w.instructor_id,
        "instructor_name": w.instructor.get_full_name() or w.instructor.username,
        "amount": float(w.amount),
        "current_balance": float(w.current_balance),
        "status": w.status,
        "status_display": w.status_display,
        "payment_method": w.payment_method,
        "payment_method_display": w.get_payment_method_display(),
        "payment_details": w.payment_details,
        "notes": w.notes,
        "reference": w.reference,
        "processed_by": w.processed_by_id,
        "created_at": w.created_at.isoformat() if w.created_at else None,
        "updated_at": w.updated_at.isoformat() if w.updated_at else None,
        "processed_at": w.processed_at.isoformat() if w.processed_at else None,
        "can_cancel": w.can_cancel,
        "is_completed": w.is_completed,
        "is_pending": w.is_pending,
    }


# ── List Withdrawals ──


@bolt_view
@login_required
def withdrawal_list(request):
    """GET /apis/withdrawals/ — List withdrawal requests.

    Instructors see their own withdrawals.
    Staff/admins see all withdrawals.
    """
    user = request.user

    if user.is_staff:
        qs = Withdrawal.objects.all()
    elif user.groups.filter(name="Instructors").exists():
        qs = Withdrawal.objects.filter(instructor=user)
    else:
        return {"status": "error", "message": "Access denied"}, 403

    # Optional filters
    status_filter = request.GET.get("status")
    if status_filter:
        qs = qs.filter(status=status_filter)

    qs = qs.order_by("-created_at")
    items, pagination = paginate_queryset(qs, request)
    return paginated_response(
        items, pagination, request, [_serialize_withdrawal(w) for w in items]
    )


# ── Create Withdrawal Request ──


@bolt_view
@login_required
def withdrawal_create(request):
    """POST /apis/withdrawals/create/ — Request a withdrawal (instructor only)."""
    if not request.user.groups.filter(name="Instructors").exists() and not request.user.is_staff:
        return {"status": "error", "message": "Only instructors can request withdrawals"}, 403

    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    amount = body.get("amount")
    payment_method = body.get("payment_method", "paypal")
    payment_details = body.get("payment_details", {})

    if not amount:
        return {"status": "error", "message": "Amount is required"}, 400

    try:
        amount_decimal = Decimal(str(amount))
    except Exception:
        return {"status": "error", "message": "Invalid amount"}, 400

    if amount_decimal < Decimal("50.00"):
        return {"status": "error", "message": "Minimum withdrawal amount is $50.00"}, 400

    # Validate payment method
    valid_methods = [m.value for m in Withdrawal.PaymentMethod]
    if payment_method not in valid_methods:
        return {"status": "error", "message": f"Invalid payment method. Valid: {', '.join(valid_methods)}"}, 400

    if not isinstance(payment_details, dict):
        payment_details = {}

    # Calculate current balance from completed enrollments
    from django.db.models import Sum
    from plugins.lms.models import Enrollment

    total_earned = float(
        Enrollment.objects.filter(
            course__instructor=request.user,
            payment_status="completed",
        ).aggregate(
            total=Sum("amount_paid")
        )["total"] or 0
    )

    # Subtract already withdrawn amounts
    already_withdrawn = float(
        Withdrawal.objects.filter(
            instructor=request.user,
            status__in=["approved", "processing", "completed"],
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0
    )

    current_balance = round(total_earned - already_withdrawn, 2)

    if amount_decimal > Decimal(str(current_balance)):
        return {
            "status": "error",
            "message": f"Insufficient balance. Available: ${current_balance:,.2f}",
        }, 400

    withdrawal = Withdrawal.objects.create(
        instructor=request.user,
        amount=amount_decimal,
        current_balance=current_balance,
        payment_method=payment_method,
        payment_details=payment_details,
    )

    return {"status": "success", "data": _serialize_withdrawal(withdrawal)}, 201


# ── Withdrawal Detail ──


@bolt_view
@login_required
def withdrawal_detail(request, pk):
    """GET /apis/withdrawals/<pk>/ — Get withdrawal detail."""
    withdrawal = get_object_or_404(Withdrawal, pk=pk)

    if withdrawal.instructor_id != request.user.id and not request.user.is_staff:
        return {"status": "error", "message": "Permission denied"}, 403

    return {"status": "success", "data": _serialize_withdrawal(withdrawal)}


# ── Cancel Withdrawal (instructor) ──


@bolt_view
@login_required
def withdrawal_cancel(request, pk):
    """PATCH /apis/withdrawals/<pk>/cancel/ — Cancel a pending withdrawal (instructor)."""
    withdrawal = get_object_or_404(Withdrawal, pk=pk)

    if withdrawal.instructor_id != request.user.id:
        return {"status": "error", "message": "Permission denied"}, 403

    if not withdrawal.can_cancel:
        return {"status": "error", "message": "Only pending withdrawals can be cancelled"}, 400

    withdrawal.status = Withdrawal.Status.CANCELLED
    withdrawal.save(update_fields=["status", "processed_at"])

    return {"status": "success", "data": _serialize_withdrawal(withdrawal)}


# ── Admin: Approve Withdrawal ──


@bolt_view
@login_required
def withdrawal_approve(request, pk):
    """PATCH /apis/withdrawals/<pk>/approve/ — Approve a withdrawal request (admin/staff)."""
    if not request.user.is_staff:
        return {"status": "error", "message": "Admin access required"}, 403

    withdrawal = get_object_or_404(Withdrawal, pk=pk)

    if withdrawal.status != Withdrawal.Status.PENDING:
        return {"status": "error", "message": "Only pending withdrawals can be approved"}, 400

    withdrawal.status = Withdrawal.Status.APPROVED
    withdrawal.processed_by = request.user
    withdrawal.save(update_fields=["status", "processed_by", "updated_at"])

    return {"status": "success", "data": _serialize_withdrawal(withdrawal)}


# ── Withdrawal Summary (live balance) ──


@bolt_view
@login_required
def withdrawal_summary(request):
    """GET /apis/withdrawals/summary/ — Get live withdrawal summary for current user.

    Returns current balance, pending amount, and total withdrawn.
    """
    from django.db.models import Sum
    from plugins.lms.models import Enrollment

    user = request.user

    # Total earned from completed enrollments
    total_earned = float(
        Enrollment.objects.filter(
            course__instructor=user,
            payment_status="completed",
        ).aggregate(
            total=Sum("amount_paid")
        )["total"] or 0
    )

    # Already withdrawn
    withdrawn_qs = Withdrawal.objects.filter(
        instructor=user,
        status__in=["approved", "processing", "completed"],
    )
    already_withdrawn = float(
        withdrawn_qs.aggregate(total=Sum("amount"))["total"] or 0
    )

    # Pending withdrawals
    pending_qs = Withdrawal.objects.filter(
        instructor=user,
        status="pending",
    )
    pending_amount = float(
        pending_qs.aggregate(total=Sum("amount"))["total"] or 0
    )

    current_balance = round(total_earned - already_withdrawn, 2)

    # Recent withdrawals
    recent = list(
        Withdrawal.objects.filter(instructor=user)
        .order_by("-created_at")[:10]
    )

    return {
        "status": "success",
        "data": {
            "current_balance": current_balance,
            "pending_amount": pending_amount,
            "total_withdrawn": already_withdrawn,
            "total_earned": total_earned,
            "pending_count": pending_qs.count(),
            "recent_withdrawals": [_serialize_withdrawal(w) for w in recent],
        },
    }


# ── Admin: Reject Withdrawal ──


@bolt_view
@login_required
def withdrawal_reject(request, pk):
    """PATCH /apis/withdrawals/<pk>/reject/ — Reject a withdrawal request (admin/staff)."""
    if not request.user.is_staff:
        return {"status": "error", "message": "Admin access required"}, 403

    body = parse_body(request)
    reason = (body or {}).get("reason", "").strip()

    withdrawal = get_object_or_404(Withdrawal, pk=pk)

    if withdrawal.status != Withdrawal.Status.PENDING:
        return {"status": "error", "message": "Only pending withdrawals can be rejected"}, 400

    withdrawal.status = Withdrawal.Status.REJECTED
    withdrawal.processed_by = request.user
    if reason:
        withdrawal.notes = reason
    withdrawal.save(update_fields=["status", "processed_by", "notes", "updated_at"])

    return {"status": "success", "data": _serialize_withdrawal(withdrawal)}
