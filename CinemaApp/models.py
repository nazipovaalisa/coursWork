from datetime import datetime, date

from django.conf import settings

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

#Таблица Жанры
class Genre(models.Model):

    name = models.CharField(max_length=50, verbose_name='Жанр')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

#Таблица Фильмы
class Film (models.Model):

    name = models.CharField(max_length=100, verbose_name = 'Название фильма')
    slug = models.SlugField(verbose_name='URL')
    country = models.CharField(max_length=50, verbose_name = 'Страна производства')
    date_of_release = models.DateField(verbose_name = 'Старт проката')
    genre = models.ManyToManyField(Genre, verbose_name = 'Жанр', related_name='film')
    description = models.TextField(verbose_name ='Описание', blank = True, default = 'Описание будет позже')
    image = models.ImageField(upload_to="images/", height_field="image_height", width_field="image_width",
                              verbose_name = 'Изображение')
    image_height = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,
        default="525"
    )
    image_width = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,
        default="260"
    )
    is_posted=models.BooleanField(verbose_name = 'Опубликовано', default='True')

    def __str__(self):
        return self.name

    #получение абсолютной ссылки объекта
    def get_absolute_url(self):
        return reverse('film_detail', kwargs={'film_slug': self.slug})

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural ='Фильмы'

#Таблица Залы
class Hall (models.Model):

    type_comfort = 'comfort'
    type_standart = 'standart'

    choice_of_type = (
        (type_comfort, 'Комфорт'),
        (type_standart, 'Стандарт')
    )

    hall_id = models.IntegerField(verbose_name='Номер зала')
    type = models.CharField(max_length=100, verbose_name = 'Тип зала', choices = choice_of_type, default = type_standart)

    def __str__(self):
        return f"{self.hall_id} | {self.type}"

    class Meta:
        verbose_name = 'Зал'
        verbose_name_plural = 'Залы'

#Таблица Сеансы
class Seans (models.Model):

    slug = models.SlugField(verbose_name='URL', blank=True, null=True)
    date_seans = models.DateField(verbose_name='Дата сеанса')
    time_seans = models.TimeField(verbose_name='Время сеанса')
    film = models.ForeignKey(Film, on_delete=models.CASCADE, verbose_name='Фильм')
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, verbose_name='Зал')
    price = models. DecimalField(max_digits = 9, decimal_places=2, verbose_name='Цена')

    def __str__(self):
        return f"{self.film.name} | {self.date_seans} | {self.time_seans}"

    #метод возвращает true - если сеанс в прошлом времени
    @property
    def is_past(self):
        current_day = datetime.now()
        current_time = current_day.time()
        return (date.today() == self.date_seans) and (current_time > self.time_seans)

    # определяем автоматически слаг
    def save(self, *args, **kwargs):
        super(Seans, self).save(*args, **kwargs)
        self.slug = f"seans-{self.id}"
        super().save(*args, **kwargs)

    #абсолютная ссылка на объект
    def get_absolute_url(self, *args, **kwargs):
        return reverse('seans_detail', kwargs={'film_slug':self.film.slug, 'date_seans':self.date_seans, 'seans_slug':self.slug})

    class Meta:
        ordering=['date_seans','time_seans']
        verbose_name = 'Сеанс'
        verbose_name_plural = 'Сеансы'

#Таблица Билеты
class Ticket (models.Model):
    row = models.IntegerField(verbose_name='Ряд')
    seat = models.IntegerField (verbose_name='Место')
    price = models. DecimalField(max_digits = 9, decimal_places=2, verbose_name = 'Цена', null = True)
    seans = models.ForeignKey(Seans, on_delete=models.CASCADE, verbose_name='Сеанс')
    reserved = models.BooleanField(verbose_name='Забронирован', default=False )
    bought = models.BooleanField(verbose_name='Куплен', default=False)

    def __str__(self):
        return f"{self.seans} | ряд: {self.row} | место: {self.seat}"

    class Meta:
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'

#Промежуточная таблица забронированных билетов
class Bron(models.Model):

    user = models.ForeignKey('Customer', verbose_name = 'Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name = 'Корзина', on_delete=models.CASCADE, blank = True)
    ticket = models.ForeignKey(Ticket, blank = True, verbose_name='Забронированный билет', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена', blank = True)

    def __str__(self):
        return f"Бронирование: {self.ticket}"

    # переопредедляем save для заполнения цены забронированного билета
    def save(self, *args, **kwargs):
        self.price = self.ticket.price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'

#Таблица Корзины
class Cart(models.Model):

    owner = models.ForeignKey('Customer', verbose_name = 'Покупатель', on_delete=models.CASCADE)
    tickets = models.ManyToManyField(Bron, blank = True, related_name = 'related_cart', verbose_name='Забронированные билеты')
    count = models.IntegerField(verbose_name='Количество билетов', default=0)
    sum = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Сумма', blank = True, null=True, default=0)
    in_order = models.BooleanField(default= False)
    for_anonymous_user = models.BooleanField(default = False)
    
    def __str__(self):
        return {self.id}

    #Метод для получения билетов в корзине
    def tickets_in_cart(self):
        return [b.ticket for b in self.tickets.all()]

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

#Таблица Заказа
class Order(models.Model):

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name = 'orders' ,verbose_name = 'Покупатель')
    phone = models.CharField(max_length=11, verbose_name='Номер телефона')
    email = models.CharField(max_length=100, verbose_name='Электронная почта')
    created_at = models.DateField(verbose_name='Дата заказа', auto_now=True)
    cart = models.ForeignKey(Cart, verbose_name='Корзина',  null=True, blank=True, related_name='related_cart', on_delete=models.CASCADE)
    use_bonuses = models.BooleanField(verbose_name='Списать бонусы', default=False)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name='Заказ'
        verbose_name_plural = 'Заказы'

#Таблица Покупатели
class Customer(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name = 'Пользователь', on_delete=models.CASCADE)
    is_active=models.BooleanField(default=False)
    cutomer_orders = models.ManyToManyField(Order,blank=True, verbose_name = 'Заказы покупателя', related_name = 'related_customer')
    phone = models.CharField(max_length=20, verbose_name = 'Номер телефона')
    bonuses = models.IntegerField(verbose_name='Бонусы', blank=True, null=True, default=0)


    def __str__(self):
        return f"{self.user.username}"

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'

#Сигнал, срабатывающий после сохранения cеанса для создания или изменения билетов
@receiver(post_save, sender = Seans)
def create_or_update_ticket(sender, instance, **kwargs):
    for i in range(1, 8): #7 рядов
        for j in range(1, 15): #в каждом ряду 14 мест
            ticket, created = Ticket.objects.get_or_create(seans=instance, row=i, seat=j)
            ticket.price = instance.price
            ticket.save()
