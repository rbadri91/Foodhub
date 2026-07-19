"""AI assistant for restaurant discovery.

Answers "who has the food I want" and per-restaurant questions by giving
Claude the live catalog (restaurants + menus) as grounded context. The
catalog is serialized deterministically and placed in a cached system
block so repeated questions reuse the prompt-cache prefix.
"""
import anthropic
from django.conf import settings

from .models import Restaurant

MODEL = "claude-haiku-4-5"
MAX_HISTORY = 10
MAX_MESSAGE_CHARS = 500

INSTRUCTIONS = """\
You are FoodHub's ordering assistant. Help users find which restaurant has
the food they're craving, and answer questions about specific restaurants
(menu, prices, rating, delivery/pickup, address).

Rules:
- Answer only from the catalog below. If something isn't in it, say so —
  never invent restaurants or dishes.
- When recommending, name the restaurant, the matching dishes, and their
  prices. Prefer 1-3 best matches over exhaustive lists.
- Prices in the catalog are US dollars.
- Be concise and friendly; this renders in a small chat widget.
"""


def is_configured() -> bool:
    return bool(settings.ANTHROPIC_API_KEY)


def _catalog() -> str:
    """Deterministic text catalog — stable ordering keeps the cache warm."""
    lines = []
    restaurants = (
        Restaurant.objects.filter(is_active=True)
        .order_by("name")
        .prefetch_related("sections__items")
    )
    for r in restaurants:
        lines.append(
            f"## {r.name} ({r.cuisine}) — {r.address or ''} {r.city}, {r.state}\n"
            f"rating {r.rating}/5, price level {r.price_level}/4, "
            f"delivery: {'yes' if r.supports_delivery else 'no'}, "
            f"pickup: {'yes' if r.supports_pickup else 'no'}"
        )
        for section in r.sections.all():
            for item in section.items.all():
                if not item.is_available:
                    continue
                desc = f" — {item.description}" if item.description else ""
                lines.append(
                    f"- [{section.name}] {item.name}: ${item.price_cents / 100:.2f}{desc}"
                )
        lines.append("")
    return "\n".join(lines)


def ask_assistant(message: str, history: list[dict]) -> str:
    """One chat turn. `history` is prior [{role, content}] turns from the client."""
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    messages = [
        {"role": h["role"], "content": h["content"]}
        for h in history[-MAX_HISTORY:]
    ]
    messages.append({"role": "user", "content": message})

    # No thinking config: Haiku 4.5 doesn't support adaptive thinking, and
    # grounded menu Q&A doesn't need extended reasoning.
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=[
            {"type": "text", "text": INSTRUCTIONS},
            {
                "type": "text",
                "text": f"# Restaurant catalog\n\n{_catalog()}",
                "cache_control": {"type": "ephemeral"},
            },
        ],
        messages=messages,
    )
    return "".join(block.text for block in response.content if block.type == "text")
