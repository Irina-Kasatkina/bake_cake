from django.contrib import admin

from .models import Cake, Client, Order

class CakeInline(admin.TabularInline):
    model = Cake
    extra = 0


@admin.register(Cake)
class Cake(admin.ModelAdmin):
    pass


@admin.register(Client)
class Client(admin.ModelAdmin):
    list_display = [
        'name',
        'phone',
        'email',
    ]
    search_fields = [
        'name',
        'address',
        'phone',
        'email',
    ]


@admin.register(Order)
class Order(admin.ModelAdmin):
    list_display = [
        'id',
        'get_name',
        'status',
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