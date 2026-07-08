"""Minimal fake accounts models for testing django-fusion in isolation."""
from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        app_label = "accounts"


class PrivacyPolicy(models.Model):
    class Meta:
        app_label = "accounts"


class PrivacyConsent(models.Model):
    class Meta:
        app_label = "accounts"


class TermsOfService(models.Model):
    class Meta:
        app_label = "accounts"


class TermsConsent(models.Model):
    class Meta:
        app_label = "accounts"
