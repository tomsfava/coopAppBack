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
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, related_name='created_distributions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, related_name='updated_distributions'
    )
    updated_at = models.DateTimeField(auto_now=True)

    objects = DistributionQuerySet.as_manager()

    class Meta:
        verbose_name = 'Distribuição'
        verbose_name_plural = 'Distribuições'
        constraints = [
            models.UniqueConstraint(fields=['order', 'offer'], name='order_offer_unique')
        ]

    def __str__(self):
        return (
            f'Distribuição #{self.pk}:Pd:{self.order_id}-Of:{self.offer_id}-{self.quantity}'
        )

    def clean(self):
        super().clean()
        if self.order.product != self.offer.product:
            raise ValidationError('O pedido e oferta devem ser do mesmo produto.')
        if self.quantity <= 0:
            raise ValidationError('A quantidade deve ser maior que zero.')
        if self.quantity > self.offer.quantity:
            raise ValidationError('A distribuição nao pode ser maior que a oferta.')
        if self.quantity > self.order.quantity:
            raise ValidationError('A distribuição nao pode ser maior que o pedido.')
        if self.order.status == Order.OrderStatus.CANCELLED:
            raise ValidationError('O pedido foi cancelado.')
        if self.order.status in [
            Order.OrderStatus.CLOSED_PARTIAL,
            Order.OrderStatus.CLOSED_FILLED,
        ]:
            raise ValidationError('O pedido foi encerrado.')
        if self.offer.status == Offer.OfferStatus.CANCELLED:
            raise ValidationError('A oferta foi cancelada.')
        if self.offer.status == Offer.OfferStatus.DELIVERED:
            raise ValidationError('A oferta foi entregue.')

    @property
    def cooperated(self):
        return self.offer.cooperated
