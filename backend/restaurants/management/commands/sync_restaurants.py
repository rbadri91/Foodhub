"""Sync real restaurants for a city from OpenStreetMap's Overpass API.

Overpass is free and keyless — no billing account, no quota anxiety,
no API key to leak. Usage:

    python manage.py sync_restaurants --city "Dallas" --state "TX" --limit 40
"""
import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from restaurants.menus import build_menu, resolve_cuisine
from restaurants.models import Restaurant

QUERY = """
[out:json][timeout:30];
area["name"="{city}"]["boundary"="administrative"]->.a;
(
  node["amenity"~"restaurant|fast_food"]["name"](area.a);
);
out body {limit};
"""


class Command(BaseCommand):
    help = "Import restaurants for a city from OpenStreetMap (Overpass API)."

    def add_arguments(self, parser):
        parser.add_argument("--city", required=True)
        parser.add_argument("--state", default="")
        parser.add_argument("--limit", type=int, default=40)

    def handle(self, *args, **opts):
        query = QUERY.format(city=opts["city"], limit=opts["limit"])
        try:
            resp = requests.post(settings.OVERPASS_URL, data={"data": query}, timeout=60)
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise CommandError(
                f"Overpass request failed ({exc}). Try again shortly, or use "
                "`python manage.py seed_demo` for offline demo data."
            ) from exc

        elements = resp.json().get("elements", [])
        created = 0
        for el in elements:
            tags = el.get("tags", {})
            name = tags.get("name")
            if not name:
                continue
            addr = ", ".join(
                filter(None, [tags.get("addr:housenumber", ""), tags.get("addr:street", "")])
            )
            restaurant, was_created = Restaurant.objects.update_or_create(
                osm_id=el["id"],
                defaults={
                    "name": name[:200],
                    "cuisine": resolve_cuisine(tags.get("cuisine", "")),
                    "address": addr[:300],
                    "city": opts["city"],
                    "state": opts["state"],
                    "latitude": el.get("lat"),
                    "longitude": el.get("lon"),
                },
            )
            if was_created:
                build_menu(restaurant)
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Synced {len(elements)} OSM elements; created {created} new restaurants with menus."
        ))
