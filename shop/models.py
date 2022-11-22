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
    comment = models.TextField(
        'Комментарий курьеру',
        null=True,
        blank=True
    )
    cost = models.IntegerField()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'Заказ №{self.id}'


class Cake(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name='заказ',
        related_name='cake',
        on_delete=models.CASCADE
    )

    class Level(models.TextChoices):
        one_level = '1', '1'
        two_levels = '2', '2'
        three_levels = '3', '3'
    lvls = models.CharField(
        'уровни',
        max_length=1,
        choices=Level.choices,
    )

    class Shape(models.TextChoices):
        CIRCLE = 'CI', 'круг'
        SQUARE = 'SQ', 'квадрат'
        RECTANGLE = 'RE', 'прямоугольник'
    form = models.CharField(
        'форма',
        max_length=2,
        choices=Shape.choices,
    )

    class Topping(models.TextChoices):
        nothing = 'NN', 'Без топпинга'
        white_sauce = 'WS', 'Белый соус'
        caramel = 'CA', 'Карамельный'
        maple = 'MA' , 'Кленовый'
        bilberry = 'BI', 'Черничный'
        milk_chocolate = 'MC', 'Молочный шоколад'
        strawberry = 'ST', 'Клубничный'
    topping = models.CharField(
        'топпинг',
        max_length=2,
        choices=Topping.choices,
    )

    class Berry(models.TextChoices):
        nothing = 'NN', 'Без ягод'
        blackberry = 'BK', 'Ежевика'
        raspberry = 'RA', 'Малина'
        blueberry = 'BL', 'Голубика'
        strawberry = 'ST', 'Клубника'
    berries = models.CharField(
        'ягоды',
        max_length=2,
        choices=Berry.choices,
        default='NN'
    )

    class Decor(models.TextChoices):
        nothing = 'NN', 'Без декора'
        pistachios = 'PS', 'Фисташки'
        meringue = 'ME', 'Безе'
        hazelnut = 'HA', 'Фундук'
        pecan = 'PE', 'Пекан'
        marshmallow = 'MR', 'Маршмеллоу'
        marzipan = 'MZ', 'Марципан'
    decor = models.CharField(
        'декор',
        max_length=2,
        choices=Decor.choices,
        default='NN'
    )

    words = models.CharField(
        'надпись',
        max_length=50,
        null=True,
        blank=True,
    )

    comment = models.TextField(
        'комментарий',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'торт'
        verbose_name_plural = 'торты'

    def __str__(self):
        return f'Торт №{self.id}'
