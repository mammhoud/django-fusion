"""
POS Full — HR & finance managed models.

Django ORM models (app_label="pos_full") for payroll, employee schedules,
and tax reports.  Managed alongside the POS core models in the same database.
"""

from __future__ import annotations

from django.db import models


class Payroll(models.Model):
    """Employee payroll record for a given pay period."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("calculated", "Calculated"),
        ("approved", "Approved"),
        ("paid", "Paid"),
    ]

    employee = models.ForeignKey(
        "Employee", on_delete=models.CASCADE, related_name="payroll_records",
    )
    period_start = models.DateField()
    period_end = models.DateField()
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "pos_full"
        db_table = "full_payroll"
        ordering = ["-period_start", "employee__last_name"]

    def __str__(self) -> str:
        return f"Payroll #{self.id} — {self.employee} ({self.period_start}–{self.period_end})"


class EmployeeSchedule(models.Model):
    """Weekly shift schedule for an employee."""

    DAY_CHOICES = [
        ("monday", "Monday"), ("tuesday", "Tuesday"), ("wednesday", "Wednesday"),
        ("thursday", "Thursday"), ("friday", "Friday"), ("saturday", "Saturday"),
        ("sunday", "Sunday"),
    ]
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"), ("confirmed", "Confirmed"),
        ("completed", "Completed"), ("absent", "Absent"),
    ]

    employee = models.ForeignKey(
        "Employee", on_delete=models.CASCADE, related_name="schedules",
    )
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "pos_full"
        db_table = "full_employee_schedules"
        ordering = ["employee__last_name", "day_of_week", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "day_of_week"],
                name="unique_employee_schedule_per_day",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.employee} — {self.get_day_of_week_display()} ({self.start_time}–{self.end_time})"


class TaxReport(models.Model):
    """Periodic tax summary report generated from sales data."""

    PERIOD_CHOICES = [
        ("daily", "Daily"), ("weekly", "Weekly"),
        ("monthly", "Monthly"), ("quarterly", "Quarterly"),
        ("yearly", "Yearly"),
    ]

    report_type = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    total_sales = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_tax = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    transaction_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default="draft")
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "pos_full"
        db_table = "full_tax_reports"
        ordering = ["-period_start"]

    def __str__(self) -> str:
        return f"Tax Report ({self.get_report_type_display()}) {self.period_start}–{self.period_end}"
