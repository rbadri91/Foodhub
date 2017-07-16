from django.db import models

class ChargeManager(models.Manager):

    def during(self, year, month):
        return self.filter(
            charge_created__year=year,
            charge_created__month=month
        )

    def paid_totals_for(self, year, month):
        return self.during(year, month).filter(
            paid=True
        ).aggregate(
            total_amount=models.Sum("amount"),
            total_refunded=models.Sum("amount_refunded")
        )