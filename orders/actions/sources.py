from .. import models
import stripe
from . import customers

def create_card(customer, token):
    if customer.profile.stripe_customer is not None:
        source = customer.profile.stripe_customer.sources.create(source=token)
    else:
        source = customers.create(customer,token)
            
    return sync_card(customer, source)

def sync_card(customer, source):

    defaults = dict(
        customer=customer,
        name=source["name"] or "",
        address_line_1=source["address_line1"] or "",
        address_line_1_check=source["address_line1_check"] or "",
        address_line_2=source["address_line2"] or "",
        address_city=source["address_city"] or "",
        address_state=source["address_state"] or "",
        address_country=source["address_country"] or "",
        address_zip=source["address_zip"] or "",
        address_zip_check=source["address_zip_check"] or "",
        country=source["country"] or "",
        cvc_check=source["cvc_check"] or "",
        dynamic_last4=source["dynamic_last4"] or "",
        exp_month=source["exp_month"],
        exp_year=source["exp_year"]
    )

    card, created = models.Card.objects.get_or_create(
        stripe_id=source["id"],
        defaults=defaults
    )



    

