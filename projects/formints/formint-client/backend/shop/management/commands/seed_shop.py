"""Seed the FormintC purchase app with the Formint Café catalog + demo users."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from shop.models import Category, Order, OrderItem, Product

CATALOG = [
    {
        "name": "Coffee",
        "slug": "coffee",
        "glyph": "cup",
        "description": "Single-origin beans, roasted weekly.",
        "products": [
            {
                "name": "Espresso",
                "price": "3.50",
                "unit": "cup",
                "tags": ["strong", "double-shot"],
                "description": "A 28 g double shot pulled to a honey-thick crema.",
                "image_url": "https://images.unsplash.com/photo-1510707577719-ae7c14805e3a?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "Flat White",
                "price": "4.80",
                "unit": "cup",
                "tags": ["velvety"],
                "description": "Double ristretto under a thin layer of micro-foam.",
                "image_url": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "Pour Over — Yirgacheffe",
                "price": "5.90",
                "unit": "cup",
                "tags": ["single-origin", "floral"],
                "description": "Ethiopian beans, 4:6 method, jasmine + bergamot.",
                "image_url": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "Cold Brew Tonic",
                "price": "6.40",
                "compare_at_price": "7.00",
                "unit": "glass",
                "tags": ["refreshing", "sparkling"],
                "description": "18-hour steep over soda water with an orange twist.",
                "image_url": "https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "Mocha",
                "price": "5.20",
                "compare_at_price": "5.80",
                "unit": "cup",
                "tags": ["sweet", "classic"],
                "description": "Double espresso, single-origin cocoa, steamed milk.",
                "image_url": "https://images.unsplash.com/photo-1541167760496-1628856ab772?auto=format&fit=crop&w=600&q=80",
            },
        ],
    },
    {
        "name": "Pastries",
        "slug": "pastries",
        "glyph": "cake",
        "description": "Baked in-house before sunrise.",
        "products": [
            {
                "name": "Almond Croissant",
                "price": "4.20",
                "unit": "each",
                "tags": ["buttery", "laminated"],
                "description": "72-hour laminated dough, frangipane centre.",
                "image_url": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "Cinnamon Knot",
                "price": "3.90",
                "unit": "each",
                "tags": ["spiced"],
                "description": "Knot of brioche, Saigon cinnamon, vanilla glaze.",
                "image_url": "https://images.unsplash.com/photo-1509365465985-25d11c17e812?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "Cardamom Bun",
                "price": "4.40",
                "unit": "each",
                "tags": ["aromatic"],
                "description": "Swedish-style with crushed cardamom in the dough.",
                "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80",
            },
        ],
    },
    {
        "name": "Breakfast",
        "slug": "breakfast",
        "glyph": "sun",
        "description": "Served until 12:30 every day.",
        "products": [
            {
                "name": "Shakshuka",
                "price": "9.80",
                "unit": "plate",
                "tags": ["hearty"],
                "description": "Slow eggs in spiced tomato-pepper stew, sourdough.",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Shakshuka_%28Unsplash%29.jpg/960px-Shakshuka_%28Unsplash%29.jpg",
            },
            {
                "name": "Avocado Smash",
                "price": "8.60",
                "unit": "plate",
                "tags": ["veggie"],
                "description": "Pea-topped smashed avocado on seeded toast.",
                "image_url": "https://images.unsplash.com/photo-1541519227354-08fa5d50c44d?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "French Toast Brioche",
                "price": "7.90",
                "unit": "plate",
                "tags": ["sweet"],
                "description": "Brioche, crème anglaise, roasted plum compote.",
                "image_url": "https://images.unsplash.com/photo-1484723091739-30a097e8f929?auto=format&fit=crop&w=600&q=80",
            },
        ],
    },
    {
        "name": "Lunch",
        "slug": "lunch",
        "glyph": "bowl",
        "description": "Light plates from noon until close.",
        "products": [
            {
                "name": "Harissa Chicken Bowl",
                "price": "12.40",
                "unit": "bowl",
                "tags": ["protein"],
                "description": "Grilled harissa chicken, freekeh, pickled onion.",
                "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "Roasted Tomato Soup",
                "price": "6.20",
                "unit": "bowl",
                "tags": ["comfort"],
                "description": "Charred tomatoes, basil oil, grilled cheese crouton.",
                "image_url": "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "Halloumi Sourdough",
                "price": "10.10",
                "unit": "plate",
                "tags": ["veggie"],
                "description": "Seared halloumi, chilli honey, rocket on sourdough.",
                "image_url": "https://images.unsplash.com/photo-1553909489-cd47e0907980?auto=format&fit=crop&w=600&q=80",
            },
        ],
    },
    {
        "name": "Tea",
        "slug": "tea",
        "glyph": "leaf",
        "description": "Loose-leaf and ceremonial-grade brews.",
        "products": [
            {
                "name": "Matcha Latte",
                "price": "4.90",
                "compare_at_price": "5.50",
                "unit": "cup",
                "tags": ["matcha", "creamy"],
                "description": "Ceremonial-grade matcha, oat milk, fine sugar.",
                "image_url": "https://images.unsplash.com/photo-1515823064-d6e0c04616a7?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "Earl Grey",
                "price": "3.80",
                "unit": "cup",
                "tags": ["classic", "bergamot"],
                "description": "A bold Ceylon black scented with bergamot.",
                "image_url": "https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "Chai Latte",
                "price": "4.60",
                "unit": "cup",
                "tags": ["spiced", "creamy"],
                "description": "Masala chai concentrate, steamed milk, honey.",
                "image_url": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "Jasmine Green",
                "price": "3.90",
                "unit": "pot",
                "tags": ["floral", "delicate"],
                "description": "Jasmine-scented green buds, brewed to order.",
                "image_url": "https://images.unsplash.com/photo-1571934811356-5cc061b6821f?auto=format&fit=crop&w=600&q=80",
            },
        ],
    },
    {
        "name": "Smoothies",
        "slug": "smoothies",
        "glyph": "blend",
        "description": "Cold-pressed fruit, blended on demand.",
        "products": [
            {
                "name": "Mango Tango",
                "price": "6.90",
                "unit": "glass",
                "tags": ["tropical", "vegan"],
                "description": "Alphonso mango, passion fruit, coconut water.",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Fresh-mango-smoothie_01.jpg/960px-Fresh-mango-smoothie_01.jpg",
            },
            {
                "name": "Berry Blast",
                "price": "6.50",
                "unit": "glass",
                "tags": ["berry", "antioxidant"],
                "description": "Strawberry, blueberry, blackberry, Greek yoghurt.",
                "image_url": "https://images.unsplash.com/photo-1505252585461-04db1eb84625?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "Green Detox",
                "price": "7.20",
                "unit": "glass",
                "tags": ["green", "fresh"],
                "description": "Spinach, green apple, cucumber, ginger, lime.",
                "image_url": "https://images.unsplash.com/photo-1553530666-ba11a7da3888?auto=format&fit=crop&w=600&q=80",
            },
        ],
    },
    {
        "name": "Desserts",
        "slug": "desserts",
        "glyph": "slice",
        "description": "From the pastry case, all day.",
        "products": [
            {
                "name": "Basque Cheesecake",
                "price": "6.80",
                "compare_at_price": "7.50",
                "unit": "slice",
                "tags": ["burnt-top", "creamy"],
                "description": "Caramelised surface, molten centre, sea salt.",
                "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "Tiramisu Pot",
                "price": "5.90",
                "unit": "pot",
                "tags": ["coffee", "mascarpone"],
                "description": "Espresso-soaked savoiardi, whipped mascarpone.",
                "image_url": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "Salted Brownie",
                "price": "4.50",
                "unit": "each",
                "tags": ["fudgy", "salty"],
                "description": "Dark chocolate, caramel ripple, flaky salt.",
                "image_url": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=600&q=80",
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Seed the Formint Café catalog (idempotent) + demo customer/staff users."

    def handle(self, *args, **options):
        for cat in CATALOG:
            category, created = Category.objects.get_or_create(
                slug=cat["slug"],
                defaults={
                    "name": cat["name"],
                    "glyph": cat["glyph"],
                    "description": cat["description"],
                },
            )
            for i, prod in enumerate(cat["products"]):
                Product.objects.update_or_create(
                    slug=prod["name"].lower().replace(" ", "-").replace("—", "-"),
                    defaults={
                        "category": category,
                        "name": prod["name"],
                        "description": prod.get("description", ""),
                        "price": prod["price"],
                        "compare_at_price": prod.get("compare_at_price"),
                        "image_url": prod.get("image_url", ""),
                        "unit": prod.get("unit", "each"),
                        "tags": prod.get("tags", []),
                        "is_available": True,
                        "is_featured": i < 2,
                        "sort_order": i,
                    },
                )
            self.stdout.write(self.style.SUCCESS(f"  ✓ {category.name} ({len(cat['products'])} products)"))

        # Demo users — customer + employee (staff). Legacy demo users from the
        # pre-rebrand seed (dailygrind) are removed so a re-seed converges.
        User = get_user_model()
        User.objects.filter(
            email__in=["customer@dailygrind.example", "barista@dailygrind.example"]
        ).delete()
        customer, _ = User.objects.get_or_create(
            email="customer@formintcafe.example",
            defaults={"is_active": True, "username": "customer_formintcafe"},
        )
        # Force the demo password on every run so `make seed` converges to the
        # documented credentials (a stray signup or re-seed must not drift them).
        customer.set_password("coffee123")
        customer.save()
        staff, _ = User.objects.get_or_create(
            email="barista@formintcafe.example",
            defaults={"is_active": True, "is_staff": True, "username": "barista_formintcafe"},
        )
        staff.set_password("coffee123")
        staff.save()

        self.stdout.write(self.style.SUCCESS("  ✓ demo users: customer@formintcafe.example / barista@formintcafe.example (pw: coffee123)"))

        # Demo orders — a few recent transactions so the POS Orders view has
        # live data. Created only when the ledger is empty (idempotent).
        if not Order.objects.exists():
            by_slug = {p.slug: p for p in Product.objects.all()}
            demo_orders = [
                {
                    "customer_name": "Amira Haddad",
                    "customer_email": "amira@example.com",
                    "order_type": Order.OrderType.DINE_IN,
                    "status": Order.Status.COMPLETED,
                    "items": [
                        ("Espresso", by_slug.get("espresso"), 2, "3.50"),
                        ("Almond Croissant", by_slug.get("almond-croissant"), 1, "4.20"),
                    ],
                    "hours_ago": 4,
                },
                {
                    "customer_name": "Jonas Weber",
                    "customer_email": "jonas@example.com",
                    "order_type": Order.OrderType.TAKEAWAY,
                    "status": Order.Status.READY,
                    "items": [("Matcha Latte", by_slug.get("matcha-latte"), 1, "4.90")],
                    "hours_ago": 2,
                },
                {
                    "customer_name": "Sofia Reyes",
                    "customer_email": "sofia@example.com",
                    "order_type": Order.OrderType.DELIVERY,
                    "status": Order.Status.PREPARING,
                    "items": [
                        ("Espresso", by_slug.get("espresso"), 1, "3.50"),
                        ("Matcha Latte", by_slug.get("matcha-latte"), 1, "4.90"),
                    ],
                    "hours_ago": 0,
                },
            ]
            for spec in demo_orders:
                order = Order.objects.create(
                    customer_name=spec["customer_name"],
                    customer_email=spec["customer_email"],
                    order_type=spec["order_type"],
                    status=spec["status"],
                )
                subtotal = Decimal("0")
                for name, product, qty, price in spec["items"]:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=name,
                        unit_price=price,
                        quantity=qty,
                    )
                    subtotal += Decimal(price) * qty
                tax = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))
                Order.objects.filter(pk=order.pk).update(
                    subtotal=subtotal,
                    tax=tax,
                    total=subtotal + tax,
                    created_at=timezone.now() - timezone.timedelta(hours=spec["hours_ago"]),
                )
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ {len(demo_orders)} demo orders")
            )

        self.stdout.write(self.style.SUCCESS("Seed complete."))
