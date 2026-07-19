"""
Cloud CRM API URL configuration.

@tested pos-portal/full/cloud - CRM API URLs
"""

from __future__ import annotations

from django.urls import path

from . import api

urlpatterns = [
    path("dashboard/", api.dashboard, name="crm-dashboard"),
    path("companies/", api.list_companies, name="crm-companies-list"),
    path("companies/create/", api.create_company, name="crm-companies-create"),
    path("contacts/", api.list_contacts, name="crm-contacts-list"),
    path("contacts/create/", api.create_contact, name="crm-contacts-create"),
    path("deals/", api.list_deals, name="crm-deals-list"),
    path("deals/create/", api.create_deal, name="crm-deals-create"),
]
