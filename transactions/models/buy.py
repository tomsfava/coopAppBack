from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from catalog.models import Product
from operations.models import Distribution
from users.models import User


class BuyQuerySet(models.QuerySet):
    def by_cooperated(self, user):
        return self.filter(distribution__offer__cooperated=user)


class Buy(models.Model):
    """Representa o quanto foi efetivamente comprado pela cooperativa das mãos do cooperado.
    Deve ser cadastrado no momento da pesagem da distribuição entregue.
    distribution pode ser nulo para o caso de entregas que não foram previamente cadastradas
    nesse caso, product e cooperated devem ser preenchidos
    """

    distribution = models.ForeignKey(
        Distribution, on_delete=models.PROTECT, null=True, blank=True
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)
    cooperated = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    quantity_received = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    excess_quantity = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    missing_quantity = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    unity_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    total_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=True
    )
    delivery_date = models.DateField(null=False)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True, related_name='created_buys'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True, related_name='updated_buys'
    )
    updated_at = models.DateTimeField(auto_now=True)
    objects = BuyQuerySet.as_manager()

    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'

    def __str__(self):
        if self.distribution:
            return (
                f'{self.quantity_received} {self.distribution.offer.product.name} '
                f'recebido de {self.distribution.offer.cooperated.full_name}'
            )
        else:
            return (
                f'{self.quantity_received} {self.product.name} '
                f'recebido de {self.cooperated.full_name}'
            )

    def clean(self):
        super().clean()

        # Validar quantidade
        if self.quantity_received <= 0:
            raise ValidationError('A quantidade deve ser maior que zero.')

        # Lógica do Buy Distribuido
        if self.distribution:
            self.total_value = self.quantity_received * self.unity_price

            distribution_quantity = self.distribution.quantity
            if self.quantity_received > distribution_quantity:
                self.excess_quantity = self.quantity_received - distribution_quantity
                self.missing_quantity = Decimal(0)
            elif self.quantity_received < distribution_quantity:
                self.missing_quantity = distribution_quantity - self.quantity_received
                self.excess_quantity = Decimal(0)
            else:
                self.missing_quantity = Decimal(0)
                self.excess_quantity = Decimal(0)

        # Lógica do Buy Avulso
        elif not self.distribution:
            # Validar que Product e Cooperated foram preenchidos
            if not self.product or not self.cooperated:
                raise ValidationError(
                    'Para compra avulsa,Product e Cooperated devem ser preenchidos.'
                )
            # Calcula e atribui valores para Buy Avulso
            self.total_value = self.quantity_received * self.unity_price
            self.excess_quantity = Decimal(0)
            self.missing_quantity = Decimal(0)
