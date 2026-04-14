from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

from core.CI.models.cart import CartItem


class CourseCartItem(CartItem):
    """
    Specialized cart item for course purchases
    """

    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, verbose_name=_("Course")
    )
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, editable=False
    )
    object_id = models.CharField(max_length=255, editable=False)
    content_object = GenericForeignKey()

    class Meta:
        verbose_name = _("Course Cart Item")
        verbose_name_plural = _("Course Cart Items")
        # unique_together = ("cart", "polymorphic_ctype", "object_id")

    def save(self, *args, **kwargs):
        # Automatically set generic relation fields
        self.content_type = ContentType.objects.get_for_model(self.course)
        self.object_id = str(self.course.id)
        # Use Decimal for exact precision
        self.price = Decimal(str(self.course.price)).quantize(Decimal('0.01'))
        self.full_clean()
        super().save(*args, **kwargs)

    # def delete(self, *args, **kwargs):
    #     # Delete the course item from the cart
    #     self.course = None
    #     self.content_type = None
    #     self.object_id = None
    #     self.full_clean()
    #     super().save(*args, **kwargs)
