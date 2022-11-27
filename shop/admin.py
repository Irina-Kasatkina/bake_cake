from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ExportMixin

from .models import Cake, Client, Order, Source


class OrderResource(resources.ModelResource):
    
    class Meta:
        model = Order
        fields = ('id', 'client__name', 'client__phone', 'date', 'address', 'time', 'cost',)
        export_order = ('id', 'client__name', 'client__phone', 'date', 'address', 'time', 'cost',)


class CakeInline(admin.TabularInline):
    model = Cake
    extra = 0


@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    pass


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'phone',
        'email',
        'address',
    ]
    search_fields = [
        'name',
        'address',
        'phone',
        'email',
    ]


@admin.register(Order)

class Order(ExportMixin, admin.ModelAdmin):
    ExportMixin.to_encoding = 'utf-8-sig'
    resource_classes = [OrderResource]
    list_display = [
        'id',
        'get_name',
        'get_status_display',
        'address',
        'get_phone',
    ]
    @admin.display(ordering='client__name', description='Name')
    def get_name(self, obj):
        return obj.client.name

    @admin.display(ordering='client__phone', description='Phone')
    def get_phone(self, obj):
        return obj.client.phone

    search_fields = [
        'client__name',
        'client__address',
        'client__phone',
    ]

    inlines = [CakeInline]

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = [
        'source_name',
        'count',
    ]