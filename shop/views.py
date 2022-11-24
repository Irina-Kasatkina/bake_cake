from datetime import datetime

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from rest_framework.serializers import Serializer, ModelSerializer

from shop.models import Cake, Client, Order

class ClientSerializer(ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        exclude = ['client',]


class CakeSerializer(ModelSerializer):
    class Meta:
        model = Cake
        exclude = ['order',]


def index(request):
    print([f'{client.name} {client.phone}' for client in Client.objects.all()])
    context = {
    }
    return render(request, 'index.html', context)


@require_http_methods(['POST'])
def login(request):
    print('Это login')
    return render(request, 'index.html', {})


def calculate_price(lvls, form, topping, berries, decor, words):
    lvl_costs = (400, 750, 1100)
    form_costs = (600, 400, 1000)
    topping_costs = (0, 200, 180, 200, 300, 350, 200)
    berries_costs = (0, 400, 300, 450, 500)
    decor_costs = (0, 300, 400, 350, 300, 200, 280)

    price = lvl_costs[lvls - 1] + form_costs[form - 1] + topping_costs[topping - 1] \
            + berries_costs[berries - 1] + decor_costs[decor - 1]
    if words:
        price += 500
    return price


@require_http_methods(['POST'])
def payment(request):
    payload = dict(request.POST.items())

    client_serializer = ClientSerializer(data=payload)
    order_serializer = OrderSerializer(data=payload)
    cake_serializer = CakeSerializer(data=payload)
    client_serializer.is_valid(raise_exception=True)
    order_serializer.is_valid(raise_exception=True)
    cake_serializer.is_valid(raise_exception=True)
    
    client, created = Client.objects.get_or_create(
        phone = client_serializer.validated_data['phone'],
        defaults={
            'name': client_serializer.validated_data['name'],
            'email': client_serializer.validated_data['email'],
            'address': client_serializer.validated_data['address'],
        },
    )
    
    order = Order.objects.create(
        client = client,
        date = order_serializer.validated_data['date'],
        time = order_serializer.validated_data['time'],
        delivcomments = order_serializer.validated_data['delivcomments'],
    )
    
    cake = Cake.objects.create(
        order=order,
        lvls=cake_serializer.validated_data['lvls'],
        form=cake_serializer.validated_data['form'],
        topping=cake_serializer.validated_data['topping'],
        berries=cake_serializer.validated_data.get('berries', 0),
        decor=cake_serializer.validated_data.get('decor', 0),
        words=cake_serializer.validated_data.get('words', ''),
        comments=cake_serializer.validated_data.get('comments', ''),
    )

    price = calculate_price(
        lvls=cake.lvls,
        form=cake.form,
        topping=cake.topping,
        berries=cake.berries,
        decor=cake.decor,
        words=cake.words
    )

    order.cost = price
    order.save()

    context = {'price': price}
    
    return render(request, 'payment.html', context)
