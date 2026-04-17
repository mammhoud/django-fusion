from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

class Cart(models.Model):
    """
    Base shopping cart model that can be linked to a user or session.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        null=True,
        blank=True,
        verbose_name=_("User")
    )
    session_key = models.CharField(
        _("Session Key"),
        max_length=40,
        null=True,
        blank=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Guest Cart {self.session_key}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """
    Abstract base model for cart items.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Cart")
    )
    quantity = models.PositiveIntegerField(_("Quantity"), default=1)
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")

    @property
    def total_price(self):
        return self.price * self.quantity
