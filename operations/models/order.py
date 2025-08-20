from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from catalog.models import Client, Product
from users.models import User


class OrderQuerySet(models.QuerySet):
    def open(self):
        return self.filter(status=Order.OrderStatus.OPEN)

    def partial(self):
        return self.filter(status=Order.OrderStatus.PARTIAL)

    def filled(self):
        return self.filter(status=Order.OrderStatus.FILLED)

    def closed(self):
        return self.filter(
            status__in=[
                Order.OrderStatus.CLOSED_PARTIAL,
                Order.OrderStatus.CLOSED_FILLED,
            ]
        )

    def cancelled(self):
        return self.filter(status=Order.OrderStatus.CANCELLED)

    def pending(self):
        return self.filter(
            status__in=[
                Order.OrderStatus.OPEN,
                Order.OrderStatus.PARTIAL,
                Order.OrderStatus.FILLED,
            ]
        )


class Order(models.Model):
    """Modelo de Pedidos cadastrados pelos Admin de acordo com pedido de Clientes."""

    class OrderStatus(models.TextChoices):
        OPEN = 'OPEN', 'Aberto'
        PARTIAL = 'PARTIAL', 'Parcialmente Distribuído'
        FILLED = 'FILLED', 'Distribuído (100%)'
        CLOSED_PARTIAL = 'CLOSED_PARTIAL', 'Encerrado (Parcial)'
        CLOSED_FILLED = 'CLOSED_FILLED', 'Encerrado (Completo)'
        CANCELLED = 'CANCELLED', 'Cancelado'

    client = models.ForeignKey(
        Client, on_delete=models.PROTECT, null=False, related_name='orders'
    )

    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, null=False, related_name='orders'
    )

    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=False)

    delivery_date = models.DateField(null=False)

    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.OPEN
    )

    notes = models.TextField(null=True, blank=True)
    # Audit fields
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True, related_name='created_orders'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True, related_name='updated_orders'
    )

    updated_at = models.DateTimeField(auto_now=True)

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['delivery_date']

    def __str__(self):
        return f'Pedido #{self.pk}:{self.client}-{self.product}:{self.delivery_date}'

    def clean(self):
        super().clean()
        if self.quantity <= 0:
            raise ValidationError('A quantidade deve ser maior que zero.')

        if self.delivery_date < timezone.now().date():
            raise ValidationError('A data de entrega deve ser no futuro.')

    @property
    def is_closed(self):
        return self.status in [
            Order.OrderStatus.CLOSED_PARTIAL,
            Order.OrderStatus.CLOSED_FILLED,
        ]

    @property
    def days_to_delivery(self):
        return (self.delivery_date - timezone.now().date()).days

    @property
    def allocated_quantity(self):
        return self.distributions.aggregate(total=models.Sum('quantity'))['total'] or 0

    @property
    def remaining_quantity(self):
        return self.quantity - self.allocated_quantity
