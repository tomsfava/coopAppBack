from django.db import models

from operations.models import Order


class Sell(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, null=False, related_name='sell'
    )
    quantity_delivered = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    missing_quantity = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
