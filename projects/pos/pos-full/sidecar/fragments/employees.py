"""
POS Full — EmployeesFragment.

Employee statistics grouped by role for the employees page.

Fragment name: ``pos.employees``

Template context::

    {
        "total_employees": 12,
        "active_employees": 10,
        "by_role": {"cashier": 4, "server": 3, "manager": 2, ...},
        "today_scheduled": 6,
        "roles": ["cashier", "server", "manager", "admin", "kitchen"],
    }
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from django.utils import timezone

from fragments import FragmentComponent, register


@register
class EmployeesFragment(FragmentComponent):
    """Employee stats by role and schedule."""

    fragment_name = "pos.employees"

    def get_context(self, **kwargs: Any) -> dict[str, Any]:
        from models.pos import Employee
        from models.hr import EmployeeSchedule

        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(is_active=True).count()

        # Count by role
        role_counts = Counter(
            Employee.objects.filter(is_active=True).values_list("role", flat=True)
        )

        # Today's scheduled employees
        today_name = timezone.now().strftime("%A").lower()
        today_scheduled = EmployeeSchedule.objects.filter(
            day_of_week=today_name,
            employee__is_active=True,
        ).count()

        return {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "by_role": dict(role_counts),
            "today_scheduled": today_scheduled,
            "roles": [role for role, _ in Employee.ROLES],
        }
