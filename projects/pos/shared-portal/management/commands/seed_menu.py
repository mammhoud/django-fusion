"""
Management command to seed sample menu data for testing the portal.

Usage:
    python manage.py seed_menu

@tested pos-portal/vresume - Seed data for menu portal testing
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from shared.models import Category, MenuItem, Menu


class Command(BaseCommand):
    """Seed sample menu items and categories for the POS Portal."""

    help = "Seed sample menu data for the POS Portal"

    def handle(self, *args, **options):
        self.stdout.write("Seeding menu data...")

        # Create categories
        categories = {
            "appetizers": Category.objects.get_or_create(
                slug="appetizers",
                defaults={
                    "name": "Appetizers",
                    "description": "Start your meal with these light bites",
                    "display_order": 0,
                },
            )[0],
            "main-course": Category.objects.get_or_create(
                slug="main-course",
                defaults={
                    "name": "Main Course",
                    "description": "Hearty main dishes",
                    "display_order": 1,
                },
            )[0],
            "desserts": Category.objects.get_or_create(
                slug="desserts",
                defaults={
                    "name": "Desserts",
                    "description": "Sweet treats to finish your meal",
                    "display_order": 2,
                },
            )[0],
            "drinks": Category.objects.get_or_create(
                slug="drinks",
                defaults={
                    "name": "Beverages",
                    "description": "Refreshing drinks and beverages",
                    "display_order": 3,
                },
            )[0],
        }

        # Create menu items
        items_data = [
            # (name, slug, category, price, description, prep_time, featured)
            ("Bruschetta", "bruschetta", "appetizers", 8.99,
             "Toasted bread topped with fresh tomatoes, basil, and mozzarella", 10, True),
            ("Garlic Bread", "garlic-bread", "appetizers", 5.99,
             "Crispy bread with garlic butter and herbs", 8, False),
            ("Caesar Salad", "caesar-salad", "appetizers", 9.99,
             "Romaine lettuce with Caesar dressing, croutons, and parmesan", 12, True),
            ("Margherita Pizza", "margherita-pizza", "main-course", 14.99,
             "Classic pizza with tomato sauce, mozzarella, and basil", 20, True),
            ("Grilled Salmon", "grilled-salmon", "main-course", 22.99,
             "Atlantic salmon with lemon butter sauce and seasonal vegetables", 25, True),
            ("Pasta Carbonara", "pasta-carbonara", "main-course", 15.99,
             "Spaghetti with pancetta, egg, and parmesan cheese", 18, False),
            ("Beef Burger", "beef-burger", "main-course", 13.99,
             "Angus beef patty with lettuce, tomato, and special sauce", 15, True),
            ("Chocolate Lava Cake", "chocolate-lava-cake", "desserts", 8.99,
             "Warm chocolate cake with a molten center, served with vanilla ice cream", 15, True),
            ("Tiramisu", "tiramisu", "desserts", 7.99,
             "Classic Italian coffee-flavored dessert", 5, False),
            ("Fresh Orange Juice", "fresh-orange-juice", "drinks", 4.99,
             "Freshly squeezed orange juice", 3, False),
            ("Espresso", "espresso", "drinks", 2.99,
             "Double shot of premium espresso", 2, True),
            ("Mint Lemonade", "mint-lemonade", "drinks", 3.99,
             "Refreshing lemonade with fresh mint", 3, False),
        ]

        for name, slug, cat_key, price, desc, prep, featured in items_data:
            MenuItem.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "category": categories[cat_key],
                    "price": price,
                    "description": desc,
                    "preparation_time": prep,
                    "is_featured": featured,
                    "is_available": True,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(items_data)} menu items across {len(categories)} categories"
        ))
