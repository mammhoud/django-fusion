"""Concrete Certificate model — inherits fields from AbstractCertificate."""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_fusion.models.base import BaseModel as DefaultBase
from django_fusion.models.certificate import AbstractCertificate
from django_fusion.models.tags import *


class Certificate(AbstractCertificate, DefaultBase):
    """Concrete Certificate model for storing certification records."""

    class Meta(AbstractCertificate.Meta):
        abstract = False
        verbose_name = _("Certificate")
        verbose_name_plural = _("Certificates")
