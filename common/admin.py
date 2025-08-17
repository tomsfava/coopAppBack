from django.contrib import admin

from .models import Macroregion, MacroregionAffinity, Region


@admin.register(Macroregion)
class MacroregionAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_regions', 'display_affinities']
    search_fields = ['name']

    def display_regions(self, obj):
        return ', '.join([region.name for region in obj.regions.all()])

    display_regions.short_description = 'Regiões'

    def display_affinities(self, obj):
        affinities_as_source = obj.affinities_as_source.all()
        affinities_as_target = obj.affinities_as_target.all()
        unique_affinities = set()
        for aff in affinities_as_source:
            unique_affinities.add(f'{aff.macroregion2.name}: {aff.value}')
        for aff in affinities_as_target:
            unique_affinities.add(f'{aff.macroregion1.name}: {aff.value}')
        return ', '.join(sorted(list(unique_affinities)))

    display_affinities.short_description = 'Afinidades'


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'macroregion']
    list_filter = ['macroregion']
    search_fields = ['name']


@admin.register(MacroregionAffinity)
class MacroregionAffinityAdmin(admin.ModelAdmin):
    list_display = ['name', 'macroregion1', 'macroregion2', 'value']
    list_filter = ['macroregion1', 'macroregion2']
