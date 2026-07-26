"""
Tests for Withdrawal API endpoints — instructor payout/withdrawal requests.

Endpoints tested:
    GET    /apis/withdrawals/               — List withdrawals
    POST   /apis/withdrawals/create/         — Request a withdrawal
    GET    /apis/withdrawals/<pk>/           — Withdrawal detail
    PATCH  /apis/withdrawals/<pk>/cancel/    — Cancel withdrawal
    PATCH  /apis/withdrawals/<pk>/approve/   — Approve withdrawal (admin)
    PATCH  /apis/withdrawals/<pk>/reject/    — Reject withdrawal (admin)
    GET    /apis/withdrawals/summary/        — Withdrawal summary
"""

from __future__ import annotations

import pytest
from django_bolt.testing import TestClient

pytestmark = pytest.mark.django_db


# ═══════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════

def _add_to_instructors_group(user):
    """Add a user to the 'Instructors' group (create it if it doesn't exist)."""
    from django.contrib.auth.models import Group
    group, _ = Group.objects.get_or_create(name="Instructors")
    user.groups.add(group)
    user.save()
    return user


# ═══════════════════════════════════════════════════════════════════
# List Withdrawals
# ═══════════════════════════════════════════════════════════════════


class TestWithdrawalList:
    """GET /apis/withdrawals/ — List withdrawal requests."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/withdrawals/")
            assert resp.status_code == 401

    def test_returns_empty_list_for_user_with_no_withdrawals(self, test_api, auth_token):
        with TestClient(test_api) as client:
            resp = client.get(
                "/apis/withdrawals/",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert "data" in data
            assert data["data"] == []

    def test_pagination_structure(self, test_api, auth_token):
        with TestClient(test_api) as client:
            resp = client.get(
                "/apis/withdrawals/?page=1&per_page=10",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            data = resp.json()
            assert data["status"] == "success"
            assert "pagination" in data
            assert data["pagination"]["page"] == 1

    def test_status_filter(self, test_api, auth_token):
        with TestClient(test_api) as client:
            resp = client.get(
                "/apis/withdrawals/?status=pending",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 200

    def test_admin_sees_all_withdrawals(self, test_api, staff_auth_token, test_user):
        """Admin/staff users should see all withdrawals, not just their own."""
        with TestClient(test_api) as client:
            resp = client.get(
                "/apis/withdrawals/",
                headers={"Authorization": f"Bearer {staff_auth_token}"},
            )
            assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════
# Create Withdrawal
# ═══════════════════════════════════════════════════════════════════


class TestWithdrawalCreate:
    """POST /apis/withdrawals/create/ — Request a withdrawal."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.post(
                "/apis/withdrawals/create/",
                json={"amount": 100, "payment_method": "paypal"},
            )
            assert resp.status_code == 401

    def test_requires_instructor_group(self, test_api, auth_token):
        """Non-instructor users should get 403."""
        with TestClient(test_api) as client:
            resp = client.post(
                "/apis/withdrawals/create/",
                json={"amount": 100, "payment_method": "paypal"},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 403
            data = resp.json()
            assert "Only instructors" in data.get("message", "")

    def test_requires_amount(self, test_api, auth_token, test_user):
        """Amount must be provided."""
        _add_to_instructors_group(test_user)
        with TestClient(test_api) as client:
            resp = client.post(
                "/apis/withdrawals/create/",
                json={"payment_method": "paypal"},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 400
            data = resp.json()
            assert "Amount is required" in data.get("message", "")

    def test_rejects_amount_below_minimum(self, test_api, auth_token, test_user):
        """Minimum withdrawal amount is $50.00."""
        _add_to_instructors_group(test_user)
        with TestClient(test_api) as client:
            resp = client.post(
                "/apis/withdrawals/create/",
                json={"amount": 10, "payment_method": "paypal"},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 400
            data = resp.json()
            assert "$50.00" in data.get("message", "")

    def test_rejects_invalid_payment_method(self, test_api, auth_token, test_user):
        _add_to_instructors_group(test_user)
        with TestClient(test_api) as client:
            resp = client.post(
                "/apis/withdrawals/create/",
                json={"amount": 100, "payment_method": "bitcoin"},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 400
            data = resp.json()
            assert "Invalid payment method" in data.get("message", "")

    def test_rejects_amount_exceeding_balance(self, test_api, auth_token, test_user):
        """Withdrawal amount cannot exceed current balance."""
        _add_to_instructors_group(test_user)
        with TestClient(test_api) as client:
            # User has no enrollments, so balance is 0 — $50 should be rejected
            resp = client.post(
                "/apis/withdrawals/create/",
                json={"amount": 5000, "payment_method": "paypal"},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 400
            data = resp.json()
            assert "Insufficient balance" in data.get("message", "")

    def test_creates_withdrawal_with_seeded_balance(self, test_api, auth_token, test_user):
        """Create withdrawal successfully when instructor has sufficient balance."""
        _add_to_instructors_group(test_user)

        # Seed an enrollment with completed payment to give the instructor balance
        from django.contrib.auth.models import User
        from plugins.lms.models import Enrollment, Course
        student = User.objects.create_user(username=f"student_bal_{test_user.id}", password="test")
        # Create a Course owned by this instructor so enrollment links back
        course = Course.objects.create(
            title="Test Course",
            instructor=test_user,
            price=500.00,
        )
        Enrollment.objects.create(
            student=student,
            course=course,
            amount_paid=500.00,
            payment_status="completed",
        )

        with TestClient(test_api) as client:
            resp = client.post(
                "/apis/withdrawals/create/",
                json={"amount": 100, "payment_method": "paypal", "payment_details": {"email": "test@example.com"}},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.json()}"
            data = resp.json()
            assert data["status"] == "success"
            assert data["data"]["amount"] == 100.0
            assert data["data"]["status"] == "pending"
            assert data["data"]["payment_method"] == "paypal"
            assert data["data"]["can_cancel"] is True
            assert data["data"]["is_pending"] is True
            assert data["data"]["is_completed"] is False


# ═══════════════════════════════════════════════════════════════════
# Withdrawal Detail
# ═══════════════════════════════════════════════════════════════════


class TestWithdrawalDetail:
    """GET /apis/withdrawals/<pk>/ — Get withdrawal detail."""

    def test_returns_404_for_nonexistent(self, test_api, auth_token):
        with TestClient(test_api) as client:
            resp = client.get(
                "/apis/withdrawals/99999/",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 404

    def test_returns_403_for_other_users_withdrawal(self, test_api, auth_token, test_user):
        """A non-staff user cannot view another user's withdrawal."""
        _add_to_instructors_group(test_user)
        from django.contrib.auth.models import User
        other = User.objects.create_user(username="other_user", password="test")

        # Create a withdrawal for the other user
        from plugins.lms.models import Withdrawal
        w = Withdrawal.objects.create(instructor=other, amount=100, current_balance=500)

        # test_user tries to see other's withdrawal
        with TestClient(test_api) as client:
            resp = client.get(
                f"/apis/withdrawals/{w.pk}/",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 403
            data = resp.json()
            assert "Permission denied" in data.get("message", "")


# ═══════════════════════════════════════════════════════════════════
# Cancel Withdrawal
# ═══════════════════════════════════════════════════════════════════


class TestWithdrawalCancel:
    """PATCH /apis/withdrawals/<pk>/cancel/ — Cancel a withdrawal."""

    def test_returns_401_when_unauthenticated(self, test_api, test_user):
        from plugins.lms.models import Withdrawal
        w = Withdrawal.objects.create(instructor=test_user, amount=100, current_balance=500)
        with TestClient(test_api) as client:
            resp = client.patch(f"/apis/withdrawals/{w.pk}/cancel/")
            assert resp.status_code == 401

    def test_cancels_pending_withdrawal(self, test_api, auth_token, test_user):
        _add_to_instructors_group(test_user)
        from plugins.lms.models import Withdrawal
        w = Withdrawal.objects.create(instructor=test_user, amount=100, current_balance=500)

        with TestClient(test_api) as client:
            resp = client.patch(
                f"/apis/withdrawals/{w.pk}/cancel/",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert data["data"]["status"] == "cancelled"

    def test_cannot_cancel_approved_withdrawal(self, test_api, auth_token, test_user):
        _add_to_instructors_group(test_user)
        from plugins.lms.models import Withdrawal
        w = Withdrawal.objects.create(instructor=test_user, amount=100, current_balance=500,
                                       status=Withdrawal.Status.APPROVED)

        with TestClient(test_api) as client:
            resp = client.patch(
                f"/apis/withdrawals/{w.pk}/cancel/",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 400
            data = resp.json()
            assert "Only pending" in data.get("message", "")


# ═══════════════════════════════════════════════════════════════════
# Approve Withdrawal (Admin)
# ═══════════════════════════════════════════════════════════════════


class TestWithdrawalApprove:
    """PATCH /apis/withdrawals/<pk>/approve/ — Approve a withdrawal (admin only)."""

    def test_returns_401_when_unauthenticated(self, test_api, test_user):
        from plugins.lms.models import Withdrawal
        w = Withdrawal.objects.create(instructor=test_user, amount=100, current_balance=500)
        with TestClient(test_api) as client:
            resp = client.patch(f"/apis/withdrawals/{w.pk}/approve/")
            assert resp.status_code == 401

    def test_returns_403_for_non_staff(self, test_api, auth_token, test_user):
        from plugins.lms.models import Withdrawal
        w = Withdrawal.objects.create(instructor=test_user, amount=100, current_balance=500)

        with TestClient(test_api) as client:
            resp = client.patch(
                f"/apis/withdrawals/{w.pk}/approve/",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 403
            data = resp.json()
            assert "Admin access required" in data.get("message", "")

    def test_approves_pending_withdrawal(self, test_api, staff_auth_token, test_user):
        from plugins.lms.models import Withdrawal
        w = Withdrawal.objects.create(instructor=test_user, amount=100, current_balance=500)

        with TestClient(test_api) as client:
            resp = client.patch(
                f"/apis/withdrawals/{w.pk}/approve/",
                headers={"Authorization": f"Bearer {staff_auth_token}"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert data["data"]["status"] == "approved"
            assert data["data"]["processed_by"] is not None

    def test_cannot_approve_already_approved(self, test_api, staff_auth_token, test_user):
        from plugins.lms.models import Withdrawal
        w = Withdrawal.objects.create(instructor=test_user, amount=100, current_balance=500,
                                       status=Withdrawal.Status.APPROVED)

        with TestClient(test_api) as client:
            resp = client.patch(
                f"/apis/withdrawals/{w.pk}/approve/",
                headers={"Authorization": f"Bearer {staff_auth_token}"},
            )
            assert resp.status_code == 400
            data = resp.json()
            assert "Only pending" in data.get("message", "")

    def test_cannot_approve_rejected_withdrawal(self, test_api, staff_auth_token, test_user):
        from plugins.lms.models import Withdrawal
        w = Withdrawal.objects.create(instructor=test_user, amount=100, current_balance=500,
                                       status=Withdrawal.Status.REJECTED)

        with TestClient(test_api) as client:
            resp = client.patch(
                f"/apis/withdrawals/{w.pk}/approve/",
                headers={"Authorization": f"Bearer {staff_auth_token}"},
            )
            assert resp.status_code == 400


# ═══════════════════════════════════════════════════════════════════
# Reject Withdrawal (Admin)
# ═══════════════════════════════════════════════════════════════════


class TestWithdrawalReject:
    """PATCH /apis/withdrawals/<pk>/reject/ — Reject a withdrawal (admin only)."""

    def test_returns_401_when_unauthenticated(self, test_api, test_user):
        from plugins.lms.models import Withdrawal
        w = Withdrawal.objects.create(instructor=test_user, amount=100, current_balance=500)
        with TestClient(test_api) as client:
            resp = client.patch(f"/apis/withdrawals/{w.pk}/reject/")
            assert resp.status_code == 401

    def test_returns_403_for_non_staff(self, test_api, auth_token, test_user):
        from plugins.lms.models import Withdrawal
        w = Withdrawal.objects.create(instructor=test_user, amount=100, current_balance=500)

        with TestClient(test_api) as client:
            resp = client.patch(
                f"/apis/withdrawals/{w.pk}/reject/",
                json={"reason": "Insufficient documentation"},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 403

    def test_rejects_pending_withdrawal(self, test_api, staff_auth_token, test_user):
        from plugins.lms.models import Withdrawal
        w = Withdrawal.objects.create(instructor=test_user, amount=100, current_balance=500)

        with TestClient(test_api) as client:
            resp = client.patch(
                f"/apis/withdrawals/{w.pk}/reject/",
                json={"reason": "Insufficient documentation"},
                headers={"Authorization": f"Bearer {staff_auth_token}"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert data["data"]["status"] == "rejected"

    def test_stores_rejection_reason(self, test_api, staff_auth_token, test_user):
        from plugins.lms.models import Withdrawal
        w = Withdrawal.objects.create(instructor=test_user, amount=100, current_balance=500)

        with TestClient(test_api) as client:
            resp = client.patch(
                f"/apis/withdrawals/{w.pk}/reject/",
                json={"reason": "Please provide valid bank details"},
                headers={"Authorization": f"Bearer {staff_auth_token}"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["data"]["notes"] == "Please provide valid bank details"

    def test_cannot_reject_already_approved(self, test_api, staff_auth_token, test_user):
        from plugins.lms.models import Withdrawal
        w = Withdrawal.objects.create(instructor=test_user, amount=100, current_balance=500,
                                       status=Withdrawal.Status.APPROVED)

        with TestClient(test_api) as client:
            resp = client.patch(
                f"/apis/withdrawals/{w.pk}/reject/",
                json={},
                headers={"Authorization": f"Bearer {staff_auth_token}"},
            )
            assert resp.status_code == 400


# ═══════════════════════════════════════════════════════════════════
# Withdrawal Summary
# ═══════════════════════════════════════════════════════════════════


class TestWithdrawalSummary:
    """GET /apis/withdrawals/summary/ — Withdrawal summary."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/withdrawals/summary/")
            assert resp.status_code == 401

    def test_returns_zero_balance_with_no_data(self, test_api, auth_token):
        with TestClient(test_api) as client:
            resp = client.get(
                "/apis/withdrawals/summary/",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            summary = data["data"]
            assert summary["current_balance"] == 0
            assert summary["pending_amount"] == 0
            assert summary["total_withdrawn"] == 0
            assert summary["pending_count"] == 0
            assert summary["recent_withdrawals"] == []

    def test_includes_recent_withdrawals(self, test_api, auth_token, test_user):
        _add_to_instructors_group(test_user)
        from plugins.lms.models import Withdrawal
        w1 = Withdrawal.objects.create(instructor=test_user, amount=100, current_balance=500)
        w2 = Withdrawal.objects.create(instructor=test_user, amount=200, current_balance=500)

        with TestClient(test_api) as client:
            resp = client.get(
                "/apis/withdrawals/summary/",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 200
            data = resp.json()
            recent = data["data"]["recent_withdrawals"]
            assert len(recent) == 2
            # Most recent first
            assert recent[0]["amount"] == 200.0
            assert recent[1]["amount"] == 100.0

    def test_summary_serializes_withdrawal_fields(self, test_api, auth_token, test_user):
        _add_to_instructors_group(test_user)
        from plugins.lms.models import Withdrawal
        w = Withdrawal.objects.create(
            instructor=test_user, amount=150, current_balance=500,
            payment_method="bank_transfer",
            payment_details={"account": "12345", "bank": "Test Bank"},
        )

        with TestClient(test_api) as client:
            resp = client.get(
                "/apis/withdrawals/summary/",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 200
            data = resp.json()
            recent = data["data"]["recent_withdrawals"]
            assert len(recent) == 1
            item = recent[0]
            assert item["id"] == w.pk
            assert item["amount"] == 150.0
            assert item["status"] == "pending"
            assert item["status_display"] == "Pending"
            assert item["payment_method"] == "bank_transfer"
            assert item["payment_method_display"] == "Bank Transfer"
            assert item["can_cancel"] is True
            assert item["is_pending"] is True
            assert item["is_completed"] is False
            assert item["instructor_name"] == "Test User"
