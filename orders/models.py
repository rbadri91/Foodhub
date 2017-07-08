from django.db import models
import uuid

STATUS_CHOICES = (
		("Started", "Started"),
		("Abandoned", "Abandoned"),
		("Finished", "Finished"),
	)

# Create your models here.
class Order(models.Model):
	order_id = models.CharField(max_length=120, default=uuid.uuid4, unique=True, primary_key=True)
	status = models.CharField(max_length=120, choices=STATUS_CHOICES, default="Started")
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated = models.DateTimeField(auto_now_add=False, auto_now=True)
