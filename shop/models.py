from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Client(models.Model):
    name = models.CharField(
        'Имя',
        max_length=50
    )
    phone = PhoneNumberField(
        'Телефон',
        db_index=True,
    )
    email = models.EmailField(
        'Почта',
        max_length=100,
        db_index=True,
    )
    address = models.TextField('Адрес')

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
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
]

SHAPE_CHOICES = [
    ('1', 'Круг'),
    ('2', 'Квадрат'),
    ('3', 'Прямоугольник'),
]

TOPPING_CHOICES = [
    ('0', 'Без'),
    ('1', 'Белый соус'),
    ('2', 'Карамельный'),
    ('3', 'Кленовый'),
    ('4', 'Черничный'),
    ('5', 'Молочный шоколад'),
    ('6', 'Клубничный'),
]

BERRY_CHOICES = [
    ('0', 'нет'),
    ('1', 'Ежевика'),
    ('2', 'Малина'),
    ('3', 'Голубика'),
    ('4', 'Клубника'),
]

DECOR_CHOICES = [
    ('0', 'нет'),
    ('1', 'Фисташки'),
    ('2', 'Безе'),
    ('3', 'Фундук'),
    ('4', 'Пекан'),
    ('5', 'Маршмеллоу'),
    ('6', 'Марципан'),
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
