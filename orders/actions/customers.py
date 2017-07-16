from Foodhubinit.models import Profile
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
import stripe
from django.conf import settings
from . import invoices

def get_customer_for_user(user):
    return next(iter(User.objects.filter(email=user.email)), None)

def create(user,token,plan=settings.STRIPE_DEFAULT_PLAN,charge_immediately=True):
	print("email here:",user.email)
	stripe_customer = stripe.Customer.create(
	email=user.email,
	source=token,
	)
	try:
		with transaction.atomic():
			user.profile.stripe_id = stripe_customer["id"]
			user.save()

	except IntegrityError:
		# There is already a Customer object for this user
		stripe.Customer.retrieve(stripe_customer["id"]).delete()
		return User.objects.get(email=user.email) 

	if plan and charge_immediately:
		invoices.create_and_pay(user)



