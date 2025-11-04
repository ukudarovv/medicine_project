from django.contrib import admin
from .models import (
    ServiceCategory,
    Service,
    PriceList,
    PriceItem,
    ICDCode,
    ServiceMaterial
)


class ServiceMaterialInline(admin.TabularInline):
    model = ServiceMaterial
    extra = 1
    raw_id_fields = ['material']


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'parent', 'order', 'is_active']
    search_fields = ['name', 'code']
    list_filter = ['organization', 'is_active']
    raw_id_fields = ['organization', 'parent']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'category', 'base_price', 'unit',
        'default_duration', 'is_active'
    ]
    search_fields = ['name', 'code', 'description']
    list_filter = ['organization', 'category', 'unit', 'is_active', 'is_expensive']
    raw_id_fields = ['organization', 'category']
    inlines = [ServiceMaterialInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('organization', 'category', 'code', 'name', 'description')
        }),
        ('Цены', {
            'fields': ('unit', 'base_price', 'price_min', 'price_max', 'vat_rate')
        }),
        ('Планирование', {
            'fields': ('default_duration',)
        }),
        ('Визуал', {
            'fields': ('color', 'image')
        }),
        ('Флаги', {
            'fields': ('is_expensive', 'is_active', 'show_in_online_booking', 'requires_materials', 'requires_equipment')
        }),
    )


class PriceItemInline(admin.TabularInline):
    model = PriceItem
    extra = 0
    raw_id_fields = ['service']


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = ['name', 'branch', 'start_date', 'end_date', 'is_active']
    search_fields = ['name', 'description']
    list_filter = ['organization', 'branch', 'is_active', 'start_date']
    raw_id_fields = ['organization', 'branch']
    inlines = [PriceItemInline]


@admin.register(PriceItem)
class PriceItemAdmin(admin.ModelAdmin):
    list_display = ['service', 'pricelist', 'price', 'discount_percent', 'final_price']
    search_fields = ['service__name', 'service__code']
    list_filter = ['pricelist']
    raw_id_fields = ['pricelist', 'service']


@admin.register(ICDCode)
class ICDCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'name_ru', 'parent_code', 'level', 'is_active']
    search_fields = ['code', 'name', 'name_ru']
    list_filter = ['level', 'is_active']


@admin.register(ServiceMaterial)
class ServiceMaterialAdmin(admin.ModelAdmin):
    list_display = ['service', 'material', 'quantity', 'is_optional']
    search_fields = ['service__name', 'material__name']
    raw_id_fields = ['service', 'material']

