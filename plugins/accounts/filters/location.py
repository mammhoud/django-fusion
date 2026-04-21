import django_filters

from www.core.base.models.locations import *  # type: ignore


class AddressFilter(django_filters.FilterSet):
    class Meta:
        model = Address
        fields = {
            "city": ["exact"],
            "street": ["icontains"],
            "building": ["icontains"],
            "apartment": ["icontains"],
            "postal_code": ["icontains"],
        }


class CityFilter(django_filters.FilterSet):
    class Meta:
        model = City
        fields = {"name": ["exact", "icontains"], "country__name": ["exact", "icontains"]}


class CountryFilter(django_filters.FilterSet):
    class Meta:
        model = Country
        fields = {"name": ["exact", "icontains"], "region__name": ["exact", "icontains"]}


# class RegionFilter(django_filters.FilterSet):
#     class Meta:
#         model = Region
#         fields = {
#             'name': ['exact', 'icontains'],
#             'region': ['exact', 'icontains'],
#         }


def get_addresses(filters=None):
    qs = Address.objects.all()
    if filters:
        qs = filters.qs
    return qs


def get_cities(filters=None):
    qs = City.objects.all()
    if filters:
        qs = filters.qs
    return qs


def get_countries(filters=None):
    qs = Country.objects.all()
    if filters:
        qs = filters.qs
    return qs


def get_regions(filters=None):
    qs = Region.objects.all()
    if filters:
        qs = filters.qs
    return qs
