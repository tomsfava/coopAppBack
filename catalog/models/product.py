from django.db import models

from users.models import User


class ActiveProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class Unit(models.Model):
    name = models.CharField(max_length=125, unique=True, null=False)
    symbol = models.CharField(max_length=10, unique=True, null=False)

    def __str__(self):
        return f'{self.name} ({self.symbol})'


class Product(models.Model):
    name = models.CharField(max_length=125, null=False)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)
    production_time = models.IntegerField(null=False, blank=False)
    default_purchase_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False
    )
    shelf_life = models.IntegerField(null=False, blank=False)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='created_products'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='updated_products'
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveProductManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
