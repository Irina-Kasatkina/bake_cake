from datetime import datetime

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from shop.models import Cake, Client, Order


def index(request):
    print([f'{client.name} {client.phone}' for client in Client.objects.all()])
    context = {
    }
    return render(request, 'index.html', context)


@require_http_methods(['POST'])
def login(request):
    print('Это login')
    return render(request, 'index.html', {})


def calculate_price(payload):
    return 1000


@require_http_methods(['POST'])
def payment(request):
    
    payload = dict(request.POST.items())
    
    price = calculate_price(payload)
    
    client, created = Client.objects.get_or_create(
        phone = payload['PHONE'],
        defaults={
            'name': payload['NAME'],
            'email': payload['EMAIL'],
            'address': payload['ADDRESS'],
        },
    )
    
    order = Order.objects.create(
        client = client,
        date = datetime.strptime(payload['DATE'], '%Y-%m-%d').date(),
        time = datetime.strptime(payload['TIME'], '%H:%M').time(),
        comment = payload['DELIVCOMMENTS'],
        cost = price,
    )
    
    Cake.objects.create(
        order=order,
        lvls=payload['LEVELS'],
        form=payload['FORM'],
        topping=payload['TOPPING'],
        berries=payload['BERRIES'],
        decor=payload['DECOR'],
        words=payload['WORDS'],
        comment=payload['COMMENTS'],
    )

    context = {'price': price}
    
    return render(request, 'payment.html', context)


@require_http_methods(['POST'])
def lk(request):
    context = {}
    return render(request, 'lk.html', context)
