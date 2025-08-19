from django.core.exceptions import ValidationError
from django.db import models

from catalog.models import Product
from users.models import User


class OfferQuerySet(models.QuerySet):
    def distribution_priority(self):
        """Ofertas prioritárias para distribuição."""
        return self.filter(
            status__in=[
                Offer.OfferStatus.NOT_ALLOCATED,
                Offer.OfferStatus.PARTIALLY_ALLOCATED,
            ]
        )

    def fully_allocated(self):
        """Ofertas totalmente distribuídas."""
        return self.filter(status=Offer.OfferStatus.ALLOCATED)

    def active(self):
        """Ofertas ativas que podem ser usadas na distribuição."""
        return self.filter(
            status__in=[
                Offer.OfferStatus.NOT_ALLOCATED,
                Offer.OfferStatus.PARTIALLY_ALLOCATED,
                Offer.OfferStatus.ALLOCATED,
            ]
        )

    def by_cooperated(self, cooperated):
        return self.filter(cooperated=cooperated)

    def by_product(self, product):
        return self.filter(product=product)


class Offer(models.Model):
    """Modelo de ofertas cadastradas por Admins para os cooperados."""

    class OfferStatus(models.TextChoices):
        NOT_ALLOCATED = 'NOT_ALLOCATED', 'Disponível'
        PARTIALLY_ALLOCATED = 'PARTIALLY_ALLOCATED', 'Parcialmente distribuída'
        ALLOCATED = 'ALLOCATED', 'Totalmente Distribuída'
        DELIVERED = 'DELIVERED', 'Entregue'
        CANCELLED = 'CANCELLED', 'Cancelada'

    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, null=False, related_name='offers'
    )
    cooperated = models.ForeignKey(
        User, on_delete=models.PROTECT, null=False, related_name='offers'
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    status = models.CharField(
        max_length=20, choices=OfferStatus.choices, default=OfferStatus.NOT_ALLOCATED
    )
    notes = models.TextField(null=True, blank=True)
    # Audit fields
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, related_name='created_offers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, related_name='updated_offers'
    )
    updated_at = models.DateTimeField(auto_now=True)

    objects = OfferQuerySet.as_manager()

    class Meta:
        verbose_name = 'Oferta'
        verbose_name_plural = 'Ofertas'

    def __str__(self):
        return f'Oferta #{self.pk}:{self.product}-{self.cooperated}-{self.quantity}'

    def clean(self):
        super().clean()
        if self.quantity <= 0:
            raise ValidationError('A quantidade deve ser maior que zero.')
        if self.end_date < self.start_date:
            raise ValidationError('A data final deve ser posterior à inicial')
