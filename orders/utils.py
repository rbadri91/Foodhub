from django.utils import timezone
from django.conf import settings
import datetime
from decimal import Decimal

ZERO_DECIMAL_CURRENCIES = [
    "bif", "clp", "djf", "gnf", "jpy", "kmf", "krw",
    "mga", "pyg", "rwf", "vuv", "xaf", "xof", "xpf",
]

def convert_tstamp(response, field_name=None):
    tz = timezone.utc if settings.USE_TZ else None

    if field_name and response.get(field_name):
        return datetime.datetime.fromtimestamp(
            response[field_name],
            tz
        )
    if response is not None and not field_name:
        return datetime.datetime.fromtimestamp(
            response,
            tz
        )

def convert_amount_for_api(amount, currency="usd"):
    if currency is None:
        currency = "usd"
    return int(amount * 100) if currency.lower() not in ZERO_DECIMAL_CURRENCIES else int(amount)

def convert_amount_for_db(amount, currency="usd"):
    if currency is None:  # @@@ not sure if this is right; find out what we should do when API returns null for currency
        currency = "usd"
    return (amount / Decimal("100")) if currency.lower() not in ZERO_DECIMAL_CURRENCIES else Decimal(amount)