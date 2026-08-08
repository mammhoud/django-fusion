"""Shop domain models — categories, products, session cart and orders."""
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

# ── Catalog ────────────────────────────────────────────────────────────────


class Category(models.Model):
    """A menu group (Coffee, Pastries, Breakfast, etc.)."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    # A short remix-style glyph label ("cup", "mug", "cake", ...) shown as a
    # soft icon chip on the storefront — no emoji, no binary assets.
    glyph = models.CharField(max_length=24, blank=True, help_text="Short glyph label, e.g. cup / mug / cake")
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """A sellable menu item."""

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Old price for a strikethrough promo badge, when set.
    compare_at_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    image_url = models.URLField(blank=True)
    unit = models.CharField(max_length=32, default="each")
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    # Optional flavour-tag chips ("oat", "decaf", "spicy", ...)
    tags = models.JSONField(default=list, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            n = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("shop:product", args=[self.slug])


# ── Cart (session-scoped) ──────────────────────────────────────────────────


class Cart(models.Model):
    """A shopping cart keyed by Django session (optionally linked to a user)."""

    session_key = models.CharField(max_length=64, unique=True, blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carts",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        owner = self.user.email if self.user else (self.session_key or "guest")
        return f"Cart({owner})"

    @property
    def item_count(self):
        return sum(i.quantity for i in self.items.all())

    @property
    def subtotal(self):
        return sum(i.line_total for i in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    # unit price snapshot so later price edits do not rewrite open carts
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(fields=["cart", "product"], name="uniq_cart_product")
        ]

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    @property
    def line_total(self):
        return self.quantity * self.unit_price


# ── Orders ─────────────────────────────────────────────────────────────────


class Order(models.Model):
    """A placed order — converted from a cart at checkout."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PREPARING = "preparing", "Preparing"
        READY = "ready", "Ready"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class OrderType(models.TextChoices):
        DINE_IN = "dine_in", "Dine in"
        TAKEAWAY = "takeaway", "Takeaway"
        DELIVERY = "delivery", "Delivery"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
    )
    customer_name = models.CharField(max_length=160)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=40, blank=True)
    order_type = models.CharField(
        max_length=16, choices=OrderType.choices, default=OrderType.TAKEAWAY
    )
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    reference = models.CharField(max_length=12, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.reference or self.pk}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._next_reference()
        super().save(*args, **kwargs)

    def _next_reference(self):
        import random
        import string

        alphabet = string.ascii_uppercase + string.digits
        for _ in range(32):
            ref = "".join(random.choices(alphabet, k=6))
            if not Order.objects.filter(reference=ref).exists():
                return ref
        return f"ORD{self.pk or '000000'}"

    @property
    def item_count(self):
        return sum(i.quantity for i in self.items.all())

    def status_badge(self):
        return {
            "pending": "amber",
            "confirmed": "sky",
            "preparing": "violet",
            "ready": "emerald",
            "completed": "zinc",
            "cancelled": "rose",
        }.get(self.status, "zinc")


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True
    )
    product_name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} × {self.product_name}"

    @property
    def line_total(self):
        return self.quantity * self.unit_price
