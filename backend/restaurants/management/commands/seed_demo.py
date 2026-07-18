"""Seed a fully offline demo dataset — no network required.

    python manage.py seed_demo
"""
import random

from django.core.management.base import BaseCommand

from restaurants.menus import MENU_TEMPLATES, build_menu
from restaurants.models import Restaurant

DEMO = [
    ("Nonna Lucia's", "italian"), ("Trattoria del Sole", "italian"),
    ("La Taqueria Norteña", "mexican"), ("Casa Verde", "mexican"),
    ("Saffron & Clove", "indian"), ("Bombay Junction", "indian"),
    ("Golden Wok", "chinese"), ("Sichuan House", "chinese"),
    ("Izakaya Kōji", "japanese"), ("Tsukiji Sushi Bar", "japanese"),
    ("Bangkok Basil", "thai"),
    ("The Smokehouse", "american"), ("Maple & Main Diner", "american"),
    ("Brick Oven Co.", "pizza"), ("Slice Society", "pizza"),
    ("Olive & Thyme", "mediterranean"),
]


class Command(BaseCommand):
    help = "Create demo restaurants with menus (offline, deterministic)."

    def add_arguments(self, parser):
        parser.add_argument("--city", default="Dallas")
        parser.add_argument("--state", default="TX")

    def handle(self, *args, **opts):
        rng = random.Random("foodhub-demo")
        created = 0
        for name, cuisine in DEMO:
            restaurant, was_created = Restaurant.objects.get_or_create(
                name=name,
                city=opts["city"],
                defaults={
                    "cuisine": cuisine,
                    "state": opts["state"],
                    "address": f"{rng.randint(100, 9900)} {rng.choice(['Main St', 'Elm St', 'Oak Ave', 'Commerce St', 'Greenville Ave'])}",
                    "price_level": rng.randint(1, 3),
                    "rating": round(rng.uniform(3.6, 4.9), 1),
                },
            )
            if was_created:
                build_menu(restaurant)
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} demo restaurants."))
