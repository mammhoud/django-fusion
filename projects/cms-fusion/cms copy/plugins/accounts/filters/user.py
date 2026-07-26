import django_filters
from base.shared.auth.models.user import User as Account


class AccountFilter(django_filters.FilterSet):
    class Meta:
        app_label = "accounts"
        model = Account
        fields = ("id", "email", "is_admin")
