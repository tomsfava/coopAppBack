from django.core.exceptions import ValidationError
from django.db import models

from users.models import User

from .offer import Offer
from .order import Order


class DistributionQuerySet(models.QuerySet):
    def by_order(self, order):
        return self.filter(order=order)

    def by_offer(self, offer):
        return self.filter(offer=offer)

    def by_cooperated(self, user):
        return self.filter(offer__cooperated=user)

    def auto_generated(self):
        return self.filter(source=Distribution.DistributionSource.AUTO)

    def manual(self):
        return self.filter(source=Distribution.DistributionSource.MANUAL)

    def semi_auto(self):
        return self.filter(source=Distribution.DistributionSource.SEMI_AUTO)

    def needs_recalculation(self, order):
        return self.filter(
            order=order,
            source__in=[
                Distribution.DistributionSource.AUTO,
                Distribution.DistributionSource.SEMI_AUTO,
            ],
        )

    def updated_by_user(self, user):
        return self.filter(updated_by=user)

    def manually_updated_by_user(self, user):
        return self.filter(updated_by=user, source=Distribution.DistributionSource.MANUAL)

    def recalculated_by_user(self, user):
        return self.filter(
            updated_by=user, source=Distribution.DistributionSource.SEMI_AUTO
        )


class Distribution(models.Model):
    class DistributionSource(models.TextChoices):
        AUTO = 'AUTO', 'Automática'
        MANUAL = 'MANUAL', 'Manual'
        SEMI_AUTO = 'SEMI_AUTO', 'Semi-Automática'

    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, null=False, related_name='distributions'
    )
    offer = models.ForeignKey(
        Offer, on_delete=models.PROTECT, null=False, related_name='distributions'
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    source = models.CharField(
        max_length=10, choices=DistributionSource.choices, default=DistributionSource.AUTO
    )
    notes = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='created_distributions',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='updated_distributions',
    )
    updated_at = models.DateTimeField(auto_now=True)

    objects = DistributionQuerySet.as_manager()

    class Meta:
        verbose_name = 'Distribuição'
        verbose_name_plural = 'Distribuições'
        constraints = [
            models.UniqueConstraint(fields=['order', 'offer'], name='order_offer_unique')
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_quantity = self.quantity or 0

    def __str__(self):
        return (
            f'Distribuição de {self.quantity} {self.offer.product.name} '
            f'do cooperado {self.offer.cooperated.full_name} '
            f'para o pedido #{self.order.id} '
        )

    def clean(self):
        super().clean()
        # Produtos devem ser iguais
        if self.order.product != self.offer.product:
            raise ValidationError('O pedido e a oferta devem ser do mesmo produto.')
        # Quantidade deve ser positiva
        if self.quantity <= 0:
            raise ValidationError('A quantidade deve ser maior que zero.')
        # Verifica se excede o limite do pedido
        if (
            self.order.allocated_quantity - self._original_quantity + self.quantity
        ) > self.order.quantity:
            raise ValidationError('A soma das distribuições excede a quantidade do pedido.')
        # Verifica se excede o limite da oferta
        if (
            self.offer.allocated_quantity - self._original_quantity + self.quantity
        ) > self.offer.quantity:
            raise ValidationError('A soma das distribuições excede a quantidade da oferta.')
        # Status inválidos para distribuir
        if self.order.status in [
            Order.OrderStatus.CANCELLED,
            Order.OrderStatus.CLOSED_PARTIAL,
            Order.OrderStatus.CLOSED_FILLED,
        ]:
            raise ValidationError(
                'Não é possível distribuir em pedidos cancelados ou encerrados.'
            )
        if self.offer.status in [
            Offer.OfferStatus.CANCELLED,
            Offer.OfferStatus.DELIVERED,
        ]:
            raise ValidationError(
                'Não é possível distribuir a partir de ofertas canceladas ou entregues.'
            )

    @property
    def cooperated(self):
        return self.offer.cooperated

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._original_quantity = instance.quantity
        return instance
