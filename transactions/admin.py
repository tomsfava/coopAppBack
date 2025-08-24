from django.contrib import admin

from .models import Buy, Sell


@admin.register(Sell)
class SellAdmin(admin.ModelAdmin):
    list_display = [
        'sell_display',
        'order',
        'quantity_delivered',
        'delivery_date',
        'created_at',
    ]
    list_filter = ['delivery_date', 'created_at']
    search_fields = ['order__client__name', 'order__product__name']

    def sell_display(self, obj):
        return f'Venda #{obj.id} - {obj.order.product.name} para {obj.order.client.name}'

    sell_display.short_description = 'Venda'
    sell_display.admin_order_field = 'id'

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        if change:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Buy)
class BuyAdmin(admin.ModelAdmin):
    list_display = [
        'buy_display',
        'get_product_name',
        'get_cooperated_name',
        'quantity_received',
        'delivery_date',
        'created_at',
    ]
    list_filter = ['delivery_date', 'created_at']
    search_fields = [
        'distribution__offer__product__name',
        'distribution__offer__cooperated__full_name',
        'product__name',
        'cooperated__full_name',
    ]

    def buy_display(self, obj):
        if obj.distribution:
            return f'Compra #{obj.id} - {obj.quantity_received} {obj.distribution.offer.product.name} de {obj.distribution.offer.cooperated.full_name}'  # noqa: E501
        else:
            return f'Compra Avulsa #{obj.id} - {obj.quantity_received} {obj.product.name} de {obj.cooperated.full_name}'  # noqa: E501

    buy_display.short_description = 'Compra'
    buy_display.admin_order_field = 'id'

    def get_product_name(self, obj):
        if obj.distribution:
            return obj.distribution.offer.product.name
        elif obj.product:
            return obj.product.name
        return 'N/A'

    get_product_name.short_description = 'Produto'

    def get_cooperated_name(self, obj):
        if obj.distribution:
            return obj.distribution.offer.cooperated.full_name
        elif obj.cooperated:
            return obj.cooperated.full_name
        return 'N/A'

    get_cooperated_name.short_description = 'Cooperado'

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        if change:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)
