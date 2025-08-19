from django.contrib import admin

from .distribution import Distribution
from .offer import Offer
from .order import Order


class DistributionInline(admin.TabularInline):
    """Mostra distribuições diretamente no admin de Order ou Offer."""

    model = Distribution
    extra = 0
    fields = ('offer', 'quantity', 'source', 'created_by', 'updated_by', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('offer', 'created_by', 'updated_by')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'client',
        'product',
        'quantity',
        'status',
        'delivery_date',
        'created_by',
        'created_at',
    )
    list_filter = ('status', 'delivery_date', 'product')
    search_fields = ('client__name', 'product__name')
    date_hierarchy = 'delivery_date'
    inlines = [DistributionInline]
    autocomplete_fields = ('client', 'product', 'created_by', 'updated_by')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'product',
        'cooperated',
        'quantity',
        'status',
        'start_date',
        'end_date',
        'created_by',
    )
    list_filter = ('status', 'product', 'start_date', 'end_date')
    search_fields = ('product__name', 'cooperated__full_name')
    date_hierarchy = 'start_date'
    inlines = [DistributionInline]
    autocomplete_fields = ('product', 'cooperated', 'created_by', 'updated_by')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Distribution)
class DistributionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'order',
        'offer',
        'quantity',
        'source',
        'created_by',
        'created_at',
        'updated_by',
        'updated_at',
    )
    list_filter = ('source', 'order__status', 'offer__status')
    search_fields = (
        'order__client__full_name',
        'order__product__name',
        'offer__product__name',
        'offer__cooperated__full_name',
    )
    autocomplete_fields = ('order', 'offer', 'created_by', 'updated_by')
    readonly_fields = ('created_at', 'updated_at')
