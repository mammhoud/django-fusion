from django.db import models
from django.utils.translation import gettext_lazy as _


class Country(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Name"))

    def get_cities(self):
        return [city.name for city in self.cities.all()]  # type: ignore

    @staticmethod
    def get_countries_cities_dict():
        countries = Country.objects.all()
        return {country.name: country.get_cities() for country in countries}

    class Meta:
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")
        ordering = ["name"]
        db_table = "Countries"

    def __str__(self):
        return f"{self.name}"


class City(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    country = models.ForeignKey(("Country"), related_name="cities", on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
        ordering = ["name"]
        db_table = "Cities"
