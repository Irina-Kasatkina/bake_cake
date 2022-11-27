import base64
import requests
from contextlib import suppress
from datetime import datetime
from urllib.parse import parse_qs, urlparse

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_http_methods
from rest_framework.serializers import ModelSerializer, Serializer

from shop.models import Cake, Client, Order, Source


class ClientSerializer(ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        exclude = ['client']


class CakeSerializer(ModelSerializer):
    class Meta:
        model = Cake
        exclude = ['order']


def index(request):

    utm_source = request.GET.get('utm_source', '')
    if utm_source:
        source, created = Source.objects.get_or_create(
            source_name=utm_source
        )
        source.count += 1
        source.save()

    client, context = None, None
    phone = request.COOKIES.get('phone')
    if phone:
        with suppress(ObjectDoesNotExist):
            client = Client.objects.get(phone=phone)
    if client:
        context = get_context(client)

    return render(request, 'index.html', context)


def get_context(client):
    return {
        'is_debug': settings.DEBUG,
        'client_details': {
            'phone': str(client.phone),
            'name': client.name,
            'email': client.email,
            'address': client.address,
            'client_label': '' if (not client.name) else client.name[:1],
        },
        'orders': client.client_orders.all(),
    }


@require_http_methods(['POST'])
def login_page(request):
    payload = dict(request.POST.items())
    client_serializer = ClientSerializer(data=payload)
    client_serializer.is_valid(raise_exception=True)
    phone = client_serializer.validated_data['phone']
    user = authenticate(username=phone, password='1234')
    if not user:
        user = User.objects.create_user(
            username=phone,
            password='1234'
        )
    login(request, user)

    client, created = Client.objects.get_or_create(
        user=user,
        phone=phone,
        defaults={
            'name': '',
            'email': '',
            'address': '',
        },
    )

    response = render(request, 'lk.html', get_context(client))
    response.set_cookie('phone', str(phone))
    return response


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
    
    phone = client_serializer.validated_data['phone']
    user = authenticate(username=phone, password='1234')
    if not user:
        user = User.objects.create_user(
            username=phone,
            password='1234'
        )
    login(request, user)
    
    client, created = Client.objects.get_or_create(
        user = user,
        phone = phone,
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
    
    domain = settings.ALLOWED_HOSTS[0]    
    if settings.DEBUG:
        success_url = 'http://{domain}:8000{path}'.format(domain=domain, path=reverse('lk'))
    else:
        success_url = 'http://{domain}{path}'.format(domain=domain, path=reverse('lk'))
    
    data = {    
        'merchantId': settings.KASSA_LOGIN,
        'amount': price*100,
        'successUrl': success_url,
        'returnUrl': success_url,
        'description': 'Test payment for {}'.format(client.email),
        'demo': True,
    }

    login_pass = f'{settings.KASSA_LOGIN}:{settings.KASSA_PASSWORD}'
    
    token = base64.b64encode(str.encode(login_pass)).decode('utf-8')
    headers = {'Authorization': f'Basic {token}'}

    response = requests.post(
        'https://ecommerce.pult24.kz/payment/create',
        headers=headers,
        json=data,
    )
    response.raise_for_status()

    parsed_url = urlparse(response.json()['url'])
    payment_id = parse_qs(parsed_url.query)['id'][0]

    order.payment_id = payment_id
    order.save()
    
    return redirect(
        to=response.json()['url'],
    )


@login_required
def lk(request):
    
    payload = dict(request.GET.items())
    if payload and 'ecom_transaction_id' in payload:
        order = Order.objects.get(payment_id=payload['ecom_transaction_id'])
        print('worked!')
        if payload['status'] == 'ok':
            order.status = 1
            order.save()
    
    user = request.user
    client = Client.objects.get(user=user)
    
    if request.method == 'POST':
        payload = dict(request.POST.items())

        client_serializer = ClientSerializer(data=payload)
        client_serializer.is_valid(raise_exception=True)
        client.name = client_serializer.validated_data['name']
        client.phone = client_serializer.validated_data['phone']
        client.email = client_serializer.validated_data['email']
        client.address = client_serializer.validated_data['address']
        # if payload.get('address'):
        #     client.address = client_serializer.validated_data['address']
        client.save()

    return render(request, 'lk.html', get_context(client))
