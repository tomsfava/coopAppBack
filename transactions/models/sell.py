from django.db import models

from operations.models import Order
from users.models import User


class SellQuerySet(models.QuerySet):
    def by_client(self, client):
        return self.filter(order__client=client)


class Sell(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, null=False, related_name='sell'
    )
    quantity_delivered = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    missing_quantity = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    delivery_date = models.DateField(null=False)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True, related_name='created_sells'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True, related_name='updated_sells'
    )
    updated_at = models.DateTimeField(auto_now=True)
    objects = SellQuerySet.as_manager()

    def __str__(self):
        return f'{self.quantity_delivered}{self.order.product.name}'
        f'entregue para {self.order.client.name}'
