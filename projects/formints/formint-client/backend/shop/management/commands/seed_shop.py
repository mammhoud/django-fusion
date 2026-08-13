"""Seed the FormintC purchase app with The Daily Grind catalog + demo users."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from shop.models import Category, Product

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
            },
            {
                "name": "Flat White",
                "price": "4.80",
                "unit": "cup",
                "tags": ["velvety"],
                "description": "Double ristretto under a thin layer of micro-foam.",
            },
            {
                "name": "Pour Over — Yirgacheffe",
                "price": "5.90",
                "unit": "cup",
                "tags": ["single-origin", "floral"],
                "description": "Ethiopian beans, 4:6 method, jasmine + bergamot.",
            },
            {
                "name": "Cold Brew Tonic",
                "price": "6.40",
                "unit": "glass",
                "tags": ["refreshing", "sparkling"],
                "description": "18-hour steep over soda water with an orange twist.",
            },
            {
                "name": "Mocha",
                "price": "5.20",
                "unit": "cup",
                "tags": ["sweet", "classic"],
                "description": "Double espresso, single-origin cocoa, steamed milk.",
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
            },
            {
                "name": "Cinnamon Knot",
                "price": "3.90",
                "unit": "each",
                "tags": ["spiced"],
                "description": "Knot of brioche, Saigon cinnamon, vanilla glaze.",
            },
            {
                "name": "Cardamom Bun",
                "price": "4.40",
                "unit": "each",
                "tags": ["aromatic"],
                "description": "Swedish-style with crushed cardamom in the dough.",
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
            },
            {
                "name": "Avocado Smash",
                "price": "8.60",
                "unit": "plate",
                "tags": ["veggie"],
                "description": "Pea-topped smashed avocado on seeded toast.",
            },
            {
                "name": "French Toast Brioche",
                "price": "7.90",
                "unit": "plate",
                "tags": ["sweet"],
                "description": "Brioche, crème anglaise, roasted plum compote.",
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
            },
            {
                "name": "Roasted Tomato Soup",
                "price": "6.20",
                "unit": "bowl",
                "tags": ["comfort"],
                "description": "Charred tomatoes, basil oil, grilled cheese crouton.",
            },
            {
                "name": "Halloumi Sourdough",
                "price": "10.10",
                "unit": "plate",
                "tags": ["veggie"],
                "description": "Seared halloumi, chilli honey, rocket on sourdough.",
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Seed The Daily Grind catalog (idempotent) + demo customer/staff users."

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
                        "unit": prod.get("unit", "each"),
                        "tags": prod.get("tags", []),
                        "is_available": True,
                        "is_featured": i < 2,
                        "sort_order": i,
                    },
                )
            self.stdout.write(self.style.SUCCESS(f"  ✓ {category.name} ({len(cat['products'])} products)"))

        # Demo users — customer + employee (staff).
        User = get_user_model()
        customer, _ = User.objects.get_or_create(
            email="customer@dailygrind.example",
            defaults={"is_active": True, "username": "customer_dailygrind"},
        )
        if not customer.has_usable_password():
            customer.set_password("coffee123")
            customer.save()
        staff, _ = User.objects.get_or_create(
            email="barista@dailygrind.example",
            defaults={"is_active": True, "is_staff": True, "username": "barista_dailygrind"},
        )
        if not staff.has_usable_password():
            staff.set_password("coffee123")
            staff.save()

        self.stdout.write(self.style.SUCCESS("  ✓ demo users: customer@dailygrind.example / barista@dailygrind.example (pw: coffee123)"))
        self.stdout.write(self.style.SUCCESS("Seed complete."))
