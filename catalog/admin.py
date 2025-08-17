from django.contrib import admin

from .models import Client, Product, Unit


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']

    readonly_fields = ['created_by', 'created_at', 'updated_by', 'updated_at']

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'name',
                    'unit',
                    'production_time',
                    'default_purchase_value',
                    'shelf_life',
                    'is_active',
                )
            },
        ),  # noqa: E501
        ('Auditoria', {'fields': ('created_by', 'created_at', 'updated_by', 'updated_at')}),  # noqa: E501
    )

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        if change:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'is_active', 'created_at']
    list_filter = ['is_active', 'region']
    search_fields = ['name']

    readonly_fields = ['created_by', 'created_at', 'updated_by', 'updated_at']

    fieldsets = (
        (None, {'fields': ('name', 'region', 'is_active')}),
        ('Auditoria', {'fields': ('created_by', 'created_at', 'updated_by', 'updated_at')}),  # noqa: E501
    )

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        if change:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)
