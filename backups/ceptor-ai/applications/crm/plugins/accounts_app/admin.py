from django.contrib import admin
from .models import Customer, StaffProfile, Vendor


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "status", "email")
    list_filter = ("role", "status")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("get_full_name", "email", "phone", "loyalty_points")
    search_fields = ("first_name", "last_name", "email")


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("name", "phone_number", "address")
    search_fields = ("name",)
