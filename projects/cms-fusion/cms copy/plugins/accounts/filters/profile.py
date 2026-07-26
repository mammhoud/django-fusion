import django_filters

from ..models import (
    Profile,
)


class ProfileFilter(django_filters.FilterSet):
    class Meta:
        app_label = "accounts"
        model = Profile
        fields = {
            "account": ["exact"],
            "bio": ["icontains"],
            "birth_date": ["exact", "year__gt", "year__lt"],
            "phone_number": ["exact", "icontains"],
            "address__city__name": ["exact", "icontains"],
            "address__city__country__name": ["exact", "icontains"],
        }


def get_profiles(filters=None):
    qs = Profile.objects.all()
    if filters:
        qs = filters.qs
    return qs
