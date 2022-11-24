import requests
import base64

from django.urls import reverse

from environs import Env

env = Env()
env.read_env()

from datetime import datetime

from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from rest_framework.serializers import Serializer, ModelSerializer
from django.contrib.sites.models import Site

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
    # Client.objects.filter(phone='+79095916079').delete()
    # print([f'{client.name} {client.phone}' for client in Client.objects.all()])
    print(settings.DEBUG)
    context = {
        'is_debug': settings.DEBUG,
    }
    return render(request, 'index.html', context)


@require_http_methods(['POST'])
def login(request):
    payload = dict(request.POST.items())
    client_serializer = ClientSerializer(data=payload)
    client_serializer.is_valid(raise_exception=True)
    client, created = Client.objects.get_or_create(
        phone = client_serializer.validated_data['phone'],
        defaults={
            'name': '',
            'email': '',
            'address': '',
        },
    )
    context = {'phone': client.phone,
        'name': client.name or '',
        'email': client.email,
        'address': client.address,
    }
    return render(request, 'lk.html', context)


def calculate_price(lvls, form, topping, berries=0, decor=0, words=''):
    lvl_costs = (400, 750, 1100)
    form_costs = (600, 400, 1000)
    topping_costs = (0, 200, 180, 200, 300, 350, 200)
    berries_costs = (0, 400, 300, 450, 500)
    decor_costs = (0, 300, 400, 350, 300, 200, 280)

    price = (lvl_costs[lvls - 1] + form_costs[form - 1] + topping_costs[topping - 1] +
             berries_costs[berries] + decor_costs[decor])
    if words:
        price += 500
    return price


def check_dellivery_time(date, time):
    delivery_datetime = datetime.combine(date, time)
    order_datetime  = datetime.now()
    time_delta = delivery_datetime - order_datetime
    return time_delta.days < 1


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

    if check_dellivery_time(order.date, order.time):
        fast_delivery_coefficient = 1.2
        price *= fast_delivery_coefficient
    order.cost = price
    order.save()
    
    domain = env.list('ALLOWED_HOSTS', ['127.0.0.1', 'localhost'])[0]

    success_url = 'http://{domain}:8000{path}'.format(domain=domain, path=reverse('lk'))
    data = {    
        'merchantId': env('KASSA_LOGIN'),
        'amount': price*100,
        'successUrl': success_url,
        'returnUrl': success_url,
        'description': 'Test payment for {}'.format(client.email),
        'demo': True,
    }
    
    login_pass = '{}:{}'.format(env('KASSA_LOGIN'), env('KASSA_PASSWORD'))
    
    token = base64.b64encode(str.encode(login_pass)).decode('utf-8')
    headers = {'Authorization': f'Basic {token}'}

    response = requests.post(
        'https://ecommerce.pult24.kz/payment/create',
        headers=headers,
        json=data,
    )
    response.raise_for_status()
    
    return redirect(
        to=response.json()['url'],
    )


def lk(request):
    context = {
    }
    return render(request, 'lk.html', context)
