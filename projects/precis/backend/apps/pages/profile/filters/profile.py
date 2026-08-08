import django_filters

# The profile model lives in the domain app as ``Person`` — it was renamed
# from ``Profile`` during the fusion consolidation. Keep the ``Profile``
# alias so callers (``get_profiles``, filtersets) stay stable.
from apps.domain.models.users.users import Person as Profile


class ProfileFilter(django_filters.FilterSet):
    """Filter Person/Profile rows by the fields the model actually carries.

    Fields were realigned to the ``Person`` model after the fusion
    consolidation (legacy ``account``/``address__city__…`` lookups came from
    an older profile schema and broke FilterSet validation).
    """

    class Meta:
        model = Profile
        fields = {
            "user": ["exact"],
            "bio": ["icontains"],
            "first_name": ["icontains"],
            "last_name": ["icontains"],
            "email": ["exact", "icontains"],
            "birth_date": ["exact", "year__gt", "year__lt"],
            "phone_number": ["exact", "icontains"],
            "country": ["exact", "icontains"],
            "city": ["exact", "icontains"],
        }


def get_profiles(filters=None):
    qs = Profile.objects.all()
    if filters:
        qs = filters.qs
    return qs
