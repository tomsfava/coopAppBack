from django.db import models

from users.models import User


class ActiveClientManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class Client(models.Model):
    name = models.CharField(max_length=199, unique=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='created_clients'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='updated_clients'
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveClientManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
