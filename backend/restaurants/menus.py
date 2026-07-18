"""Cuisine-based menu generation.

No free API provides restaurant menus (that was EatStreet's moat, and it's
gone). Real restaurant identities come from OpenStreetMap; menus are
generated from per-cuisine templates with lightly randomized prices so
every restaurant is orderable end-to-end.
"""
import random

MENU_TEMPLATES = {
    "italian": {
        "Antipasti": [("Bruschetta", "Grilled bread, tomato, basil, olive oil", 8),
                      ("Burrata", "Creamy burrata, heirloom tomato, balsamic", 13),
                      ("Calamari Fritti", "Crispy squid, lemon aioli", 12)],
        "Pasta": [("Spaghetti Carbonara", "Guanciale, egg, pecorino, black pepper", 17),
                  ("Rigatoni alla Vodka", "Tomato cream, chili, parmesan", 16),
                  ("Lasagna della Casa", "Beef ragù, béchamel, mozzarella", 18)],
        "Pizza": [("Margherita", "San Marzano tomato, fior di latte, basil", 15),
                  ("Diavola", "Spicy salami, chili honey", 17)],
        "Dolci": [("Tiramisu", "Espresso-soaked ladyfingers, mascarpone", 9)],
    },
    "mexican": {
        "Starters": [("Chips & Guacamole", "Hand-smashed avocado, lime, cilantro", 9),
                     ("Queso Fundido", "Melted chihuahua cheese, chorizo", 11)],
        "Tacos": [("Al Pastor", "Spit-roasted pork, pineapple, onion", 12),
                  ("Carne Asada", "Grilled steak, salsa verde", 13),
                  ("Baja Fish", "Beer-battered cod, chipotle crema", 12)],
        "Platos": [("Enchiladas Rojas", "Chicken, red chile sauce, crema", 15),
                   ("Carnitas Bowl", "Slow-cooked pork, rice, beans, pico", 14)],
        "Postres": [("Churros", "Cinnamon sugar, chocolate dip", 7)],
    },
    "indian": {
        "Starters": [("Samosa", "Crisp pastry, spiced potato and peas", 7),
                     ("Chicken 65", "Fried chicken, curry leaf, chili", 11)],
        "Mains": [("Butter Chicken", "Tomato-fenugreek cream sauce", 17),
                  ("Chana Masala", "Chickpeas, onion-tomato gravy", 14),
                  ("Lamb Rogan Josh", "Kashmiri chili, yogurt, ginger", 19),
                  ("Palak Paneer", "Spinach, house-made paneer", 15)],
        "Breads & Rice": [("Garlic Naan", "Tandoor-baked, garlic butter", 5),
                          ("Chicken Biryani", "Saffron basmati, fried onion, raita", 17)],
        "Desserts": [("Gulab Jamun", "Rose syrup, cardamom", 6)],
    },
    "chinese": {
        "Appetizers": [("Pork Dumplings", "Pan-fried, black vinegar", 9),
                       ("Scallion Pancake", "Crispy, flaky, soy-ginger dip", 8)],
        "Entrees": [("Mapo Tofu", "Silken tofu, Sichuan peppercorn, pork", 14),
                    ("Kung Pao Chicken", "Peanuts, dried chili, scallion", 15),
                    ("Beef Chow Fun", "Wide rice noodles, wok hei", 16)],
        "Rice & Noodles": [("Yangzhou Fried Rice", "Shrimp, char siu, egg", 13),
                           ("Dan Dan Noodles", "Sesame, chili oil, minced pork", 13)],
    },
    "japanese": {
        "Small Plates": [("Edamame", "Sea salt", 6),
                         ("Gyoza", "Pork dumplings, ponzu", 9),
                         ("Agedashi Tofu", "Dashi broth, bonito", 8)],
        "Sushi & Rolls": [("Salmon Nigiri (2pc)", "Scottish salmon", 8),
                          ("Spicy Tuna Roll", "Tuna, sriracha mayo, cucumber", 11),
                          ("Dragon Roll", "Eel, avocado, tobiko", 16)],
        "Mains": [("Chicken Katsu Curry", "Panko cutlet, Japanese curry", 16),
                  ("Tonkotsu Ramen", "Pork bone broth, chashu, ajitama", 17)],
    },
    "thai": {
        "Starters": [("Spring Rolls", "Vegetables, sweet chili sauce", 8),
                     ("Chicken Satay", "Peanut sauce, cucumber relish", 10)],
        "Mains": [("Pad Thai", "Rice noodles, tamarind, peanuts", 15),
                  ("Green Curry", "Coconut milk, Thai basil, bamboo", 16),
                  ("Basil Fried Rice", "Thai chili, holy basil, fried egg", 14)],
        "Desserts": [("Mango Sticky Rice", "Coconut cream, sesame", 8)],
    },
    "american": {
        "Starters": [("Buffalo Wings", "Blue cheese, celery", 12),
                     ("Loaded Fries", "Cheddar, bacon, scallion ranch", 10)],
        "Burgers & Sandwiches": [("Classic Smash Burger", "Two patties, American cheese, pickles", 14),
                                 ("Fried Chicken Sandwich", "Buttermilk brine, slaw, hot honey", 14),
                                 ("BLT", "Thick-cut bacon, heirloom tomato, aioli", 12)],
        "Mains": [("BBQ Ribs (Half Rack)", "House rub, cornbread", 21),
                  ("Mac & Cheese", "Three-cheese blend, toasted crumbs", 13)],
        "Desserts": [("Chocolate Brownie Sundae", "Vanilla ice cream, hot fudge", 8)],
    },
    "pizza": {
        "Pizzas": [("Cheese", "Tomato, mozzarella", 13),
                   ("Pepperoni", "Cup-and-char pepperoni, hot honey", 16),
                   ("Veggie Supreme", "Peppers, mushroom, olive, red onion", 16),
                   ("Meat Lovers", "Sausage, pepperoni, bacon", 18)],
        "Sides": [("Garlic Knots", "Parmesan, parsley butter", 7),
                  ("Caesar Salad", "Romaine, croutons, shaved parm", 10)],
    },
    "mediterranean": {
        "Mezze": [("Hummus", "Tahini, olive oil, warm pita", 8),
                  ("Falafel (5pc)", "Herbed chickpea fritters, tahini", 9)],
        "Plates": [("Chicken Shawarma Plate", "Garlic sauce, rice, salad", 16),
                   ("Lamb Kofta", "Grilled skewers, tzatziki", 18),
                   ("Gyro Wrap", "Beef-lamb blend, tomato, onion", 13)],
        "Desserts": [("Baklava", "Pistachio, honey syrup", 6)],
    },
}

DEFAULT_CUISINE = "american"

_CUISINE_ALIASES = {
    "burger": "american", "bbq": "american", "sandwich": "american",
    "diner": "american", "chicken": "american", "steak_house": "american",
    "tex-mex": "mexican", "taco": "mexican",
    "sushi": "japanese", "ramen": "japanese",
    "noodle": "chinese", "asian": "chinese",
    "greek": "mediterranean", "turkish": "mediterranean",
    "lebanese": "mediterranean", "middle_eastern": "mediterranean",
    "vietnamese": "thai",  # closest template on hand
}


def resolve_cuisine(raw: str) -> str:
    """Map a free-form OSM cuisine tag to one of our menu templates."""
    if not raw:
        return DEFAULT_CUISINE
    key = raw.lower().split(";")[0].strip()
    if key in MENU_TEMPLATES:
        return key
    return _CUISINE_ALIASES.get(key, DEFAULT_CUISINE)


def build_menu(restaurant, rng: random.Random | None = None) -> int:
    """Create menu sections/items for a restaurant. Returns item count.

    Prices vary ±20% around the template baseline so restaurants don't
    all look identical. A per-restaurant seed keeps output deterministic.
    """
    from .models import MenuItem, MenuSection

    rng = rng or random.Random(str(restaurant.id))
    template = MENU_TEMPLATES[resolve_cuisine(restaurant.cuisine)]
    count = 0
    for position, (section_name, items) in enumerate(template.items()):
        section, _ = MenuSection.objects.get_or_create(
            restaurant=restaurant, name=section_name, defaults={"position": position}
        )
        for name, description, base_dollars in items:
            price = int(base_dollars * 100 * rng.uniform(0.8, 1.2))
            price = (price // 25) * 25 + 24  # e.g. 1349, 1574 — menu-ish prices
            MenuItem.objects.get_or_create(
                section=section,
                name=name,
                defaults={"description": description, "price_cents": price},
            )
            count += 1
    return count
