from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User


class Client(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
    )
    name = models.CharField(
        'Имя',
        blank=True,
        null=True,
        max_length=50
    )
    phone = PhoneNumberField(
        'Телефон',
        db_index=True,
    )
    email = models.EmailField(
        'Почта',
        blank=True,
        max_length=100,
        null=True,
        db_index=True,
    )
    address = models.TextField(
        'Адрес',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'

    def __str__(self):
        return f'{self.name}'


class Order(models.Model):
    client = models.ForeignKey(
        Client,
        verbose_name='клиент',
        related_name='client_orders',
        on_delete=models.CASCADE
    )

    date = models.DateField('Дата доставки')
    time = models.TimeField('Время доставки')
    delivcomments = models.TextField(
        'Комментарий курьеру',
        blank=True
    )
    cost = models.IntegerField(
        'Цена заказа',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'Заказ №{self.id}'


LEVEL_CHOICES = [
    (1, '1'),
    (2, '2'),
    (3, '3'),
]

SHAPE_CHOICES = [
    (1, 'Круг'),
    (2, 'Квадрат'),
    (3, 'Прямоугольник'),
]

TOPPING_CHOICES = [
    (1, 'Без'),
    (2, 'Белый соус'),
    (3, 'Карамельный'),
    (4, 'Кленовый'),
    (5, 'Черничный'),
    (6, 'Молочный шоколад'),
    (7, 'Клубничный'),
]

BERRY_CHOICES = [
    (1, 'нет'),
    (2, 'Ежевика'),
    (3, 'Малина'),
    (4, 'Голубика'),
    (5, 'Клубника'),
]

DECOR_CHOICES = [
    (1, 'нет'),
    (2, 'Фисташки'),
    (3, 'Безе'),
    (4, 'Фундук'),
    (5, 'Пекан'),
    (6, 'Маршмеллоу'),
    (7, 'Марципан'),
]


class Cake(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name='заказ',
        related_name='cake',
        on_delete=models.CASCADE
    )
    lvls = models.CharField(
        'уровни',
        max_length=1,
        choices=LEVEL_CHOICES,
    )
    form = models.CharField(
        'форма',
        max_length=2,
        choices=SHAPE_CHOICES,
    )
    topping = models.CharField(
        'топпинг',
        max_length=2,
        choices=TOPPING_CHOICES,
    )
    berries = models.CharField(
        'ягоды',
        max_length=2,
        choices=BERRY_CHOICES,
        default=('0', 'нет'),
    )
    decor = models.CharField(
        'декор',
        max_length=2,
        choices=DECOR_CHOICES,
        default=('0', 'нет'),
    )

    words = models.CharField(
        'надпись',
        max_length=50,
        blank=True,
    )

    comments = models.TextField(
        'комментарий',
        blank=True
    )

    class Meta:
        verbose_name = 'торт'
        verbose_name_plural = 'торты'

    def __str__(self):
        return f'Торт №{self.id}'
