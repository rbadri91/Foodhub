from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from localflavor.us.forms import USPhoneNumberField
from django.contrib.postgres.fields import ArrayField
import stripe
from orders.models import StripeObject

# Create your models here.default
class Profile(StripeObject):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    phone_no = USPhoneNumberField(required=False, label="Phone")
    addresses = ArrayField(models.CharField(max_length=200, blank=True),default=list, null=True)

    @property
    def stripe_customer(self):
    	print("stripe id here:",self.stripe_id)
    	if self.stripe_id is not None:
    		return stripe.Customer.retrieve(self.stripe_id)
    	else:
    		return None	
    @property
    def user_email(self):
    	return User.email
    		

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
