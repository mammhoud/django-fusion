# Django ORM models mirroring Rust/Diesel schema (managed=True for Solo, app_label="posapp")

from django.db import models

from models.core import EmployeeType


class Employee(models.Model):
    """Staff members."""
    name = models.TextField()
    phone = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    employee_type = models.ForeignKey(EmployeeType, on_delete=models.CASCADE, db_column="employee_type_id")
    salary = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    joined_at = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded = models.BooleanField(default=False)

    class Meta:
        app_label = "posapp"
        db_table = "employees"
        managed = True
        ordering = ["name"]

    def __str__(self):
        return self.name


class EmployeeSchedule(models.Model):
    """Employee shift schedules."""
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("absent", "Absent"),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column="employee_id")
    shift_start = models.DateTimeField()
    shift_end = models.DateTimeField()
    status = models.TextField(default="scheduled", choices=STATUS_CHOICES)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "posapp"
        db_table = "employee_schedules"
        managed = True
        ordering = ["-shift_start"]


class Payroll(models.Model):
    """Employee payslips."""
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("approved", "Approved"),
        ("paid", "Paid"),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column="employee_id")
    period_start = models.TextField()
    period_end = models.TextField()
    regular_hours = models.FloatField()
    overtime_hours = models.FloatField()
    total_pay = models.FloatField()
    status = models.TextField(default="draft", choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "posapp"
        db_table = "payrolls"
        managed = True
        ordering = ["-period_start"]


class User(models.Model):
    """POS user accounts."""
    email = models.TextField(unique=True)
    password_hash = models.TextField()
    name = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "posapp"
        db_table = "users"
        managed = True
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} <{self.email}>"


class Role(models.Model):
    """RBAC roles with JSON permission sets."""
    name = models.TextField(unique=True)
    permissions = models.TextField(default="[]")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "posapp"
        db_table = "roles"
        managed = True
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserRole(models.Model):
    """Many-to-many join: users ↔ roles."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column="role_id")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "posapp"
        db_table = "user_roles"
        managed = True
        unique_together = [("user_id", "role_id")]
