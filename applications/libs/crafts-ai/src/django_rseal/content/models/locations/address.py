from django.db import models
from django.utils.translation import gettext_lazy as _


class Address(models.Model):
    city = models.ForeignKey("City", on_delete=models.CASCADE)
    street = models.CharField(max_length=100, verbose_name=_("Street"))
    building = models.CharField(max_length=100, verbose_name=_("Building"))
    apartment = models.CharField(max_length=100, verbose_name=_("Apartment"))
    postal_code = models.CharField(max_length=100, verbose_name=_("Postal Code"))

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        ordering = ["city"]
        db_table = "Addresses"
