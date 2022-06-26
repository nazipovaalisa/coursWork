from decimal import Decimal

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django import views
from django.contrib.auth import login, authenticate, get_user_model
from django.http import HttpResponseRedirect
from django.db import transaction
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator as token_generator

from .models import Film, Customer, Bron, Seans, Ticket, Cart
from .forms import LoginForm, RegistrationForm, OrderForm
from .mixins import CartMixin
from utils import recalc_cart

from datetime import date, datetime, timedelta

from .utils import send_email_verify

User=get_user_model()

def get_dates(): #получить даты на неделю вперед, начиная с сегодняшнего дня
    startdate = date.today()
    date_list = [startdate+timedelta(days=x) for x in range(7)]
    return date_list

class BaseView( views.View): #рендеринг главной страницы

    def get(self, request, *args, **kwargs):
        films = Film.objects.filter(is_posted = True).order_by('-date_of_release')
        context = {
            'films': films,
        }
        return render(request, 'base.html', context)

class FilmDetailView(views.generic.DetailView): #Детальная информация о фильме

    model = Film
    template_name = 'film/film_detail.html' #указываем шаблон
    slug_url_kwarg = 'film_slug'
    context_object_name = 'film'

    def get_context_data(self, *, object_list=None, **kwargs): #в контектсе передаем список дат
        context = super().get_context_data(**kwargs)
        context['dates'] = get_dates() #
        return context

class SeansDetailView(CartMixin,views.generic.DetailView):

    model = Seans
    template_name = 'seans/seans_detail.html'
    slug_url_kwarg = 'seans_slug'
    context_object_name = 'seans'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['number'] = list(range(1, 8))
        context['cart'] = self.cart
        context['tickets'] = Ticket.objects.filter(seans__slug=self.kwargs['seans_slug'])
        return context

class SeansListView(views.generic.ListView):

    model = Seans
    template_name = 'seans/seans_list.html'
    context_object_name = 'seans_all'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['film'] = Film.objects.get(slug=self.kwargs['film_slug'])
        context['dates'] = get_dates()
        return context

    def get_queryset(self):
        return Seans.objects.filter(film__slug=self.kwargs['film_slug'],
                                    date_seans=datetime.strptime(self.kwargs['date_seans'], "%Y-%m-%d").date())

class LoginView(views.View):

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {
            'form': form
        }
        return render(request, 'login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                customer = Customer.objects.get(user=user)
                if not customer.is_active:
                    message = 'Подтвердите вашу учетную запись!'
                    messages.add_message(request, messages.INFO, message)
                    return HttpResponseRedirect('/')
                login(request, user)
                return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        return render(request, 'login.html', context)

class LoginPostView(CartMixin, views.View):

    def post(self, request, *args, **kwargs):
        formlogin = LoginForm(request.POST or None)
        formregistr = RegistrationForm(request.POST or None)
        if formlogin.is_valid():
            username = formlogin.cleaned_data['username']
            password = formlogin.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                customer = Customer.objects.get(user=request.user)
                self.cart = Cart.objects.create(owner=customer)
                self.cart.save()
                cart = Cart.objects.filter(for_anonymous_user=True, in_order = False).first()
                for item in cart.tickets.all():
                    item.user = customer
                    item.cart = self.cart
                    item.save()
                    self.cart.tickets.add(item)
                    recalc_cart(self.cart)
                    self.cart.save()
                cart.delete()
                context = {
                    'cart': self.cart,
                    'formlogin': formlogin,
                    'formregistr': formregistr,
                }
                return render(request, 'checkorder.html', context)
        context = {
            'cart': self.cart,
            'formlogin': formlogin,
            'formregistr': formregistr,
        }
        return render(request, 'checkorder.html', context)

class RegistrationView(views.View):

    def get(self, request, *args, **kwargs):
        form =RegistrationForm(request.POST or None)
        context = {
            'form': form
        }
        return render(request, 'registration.html', context)

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Customer.objects.create(
                user=new_user,
                phone=form.cleaned_data['phone']
            )
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            send_email_verify(request, user)
            return render(request, 'confirm_email.html')
        context = {
            'form': form
        }
        return render(request, 'registration.html', context)



class RegistrationPostView(CartMixin, views.View):

    def post(self, request, *args, **kwargs):
        formlogin = LoginForm(request.POST or None)
        formregistr = RegistrationForm(request.POST or None)
        if formregistr.is_valid():
            new_user = formregistr.save(commit = False)
            new_user.username = formregistr.cleaned_data['username']
            new_user.email = formregistr.cleaned_data['email']
            new_user.first_name = formregistr.cleaned_data['first_name']
            new_user.last_name = formregistr.cleaned_data['last_name']
            new_user.save()
            new_user.set_password(formregistr.cleaned_data['password'])
            new_user.save()
            Customer.objects.create(
                user=new_user,
                phone=formregistr.cleaned_data['phone']
            )
            user = authenticate(username=formregistr.cleaned_data['username'], password=formregistr.cleaned_data['password'])
            login(request, user)
            customer = Customer.objects.get(user=request.user)
            self.cart = Cart.objects.create(owner=customer)
            self.cart.save()
            cart = Cart.objects.filter(for_anonymous_user=True, in_order = False).first()
            for item in cart.tickets.all():
                item.user = customer
                item.cart = self.cart
                item.save()
                self.cart.tickets.add(item)
                recalc_cart(self.cart)
                self.cart.save()
            cart.delete()
            context = {
                'cart': self.cart,
                'formlogin': formlogin,
                'formregistr': formregistr,
            }
            return render(request, 'checkorder.html', context)
        context = {
            'cart': self.cart,
            'formlogin': formlogin,
            'formregistr': formregistr,
        }
        return render(request, 'checkorder.html', context)

class EmailVerifyView(views.View):

    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)
        if user is not None and token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            customer = Customer.objects.get(user=user)
            customer.is_active = True
            customer.save()
            login(request, user)
            return render(request, 'success_registration.html', context={'user': user})
        return render(request, 'invalid_verify.html')

    @staticmethod
    def get_user(uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError,
                User.DoesNotExist, ValidationError):
            user = None
        return user



class AccountView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        customer = Customer.objects.filter(user=request.user).first()
        context = {
            'customer': customer,
            'cart': self.cart
        }
        return render(request, 'account.html', context)


class CartView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        return render(request, 'cart.html', {"cart": self.cart})

#добавление в корзину
class AddToCartView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        ticket_id = kwargs.get('ticket_id')
        ticket = Ticket.objects.get(id=ticket_id)
        bron_ticket, created = Bron.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, ticket=ticket
        )
        if created:
            self.cart.tickets.add(bron_ticket)
            ticket.reserved = True
            ticket.save()
        recalc_cart(self.cart)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class DeleteFromCartView(CartMixin, views.View): #удаление из корзины

    def get(self, request, *args, **kwargs):
        ticket_id = kwargs.get('ticket_id')
        ticket = Ticket.objects.get(id=ticket_id)
        bron_ticket = Bron.objects.get(
            user=self.cart.owner, cart=self.cart, ticket=ticket
        )
        self.cart.tickets.remove(bron_ticket)
        bron_ticket.delete()
        recalc_cart(self.cart)
        ticket.reserved = False
        ticket.save()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class CheckOrder(CartMixin, views.View): #рендер страницы проверки заказа

    def get(self, request, *args, **kwargs):
        formlogin = LoginForm(request.POST or None)
        formregistr = RegistrationForm(request.POST or None)
        context = {
            'cart': self.cart,
            'formlogin': formlogin,
            'formregistr': formregistr,
        }
        return render(request, 'checkorder.html', context)

class CheckOutView(CartMixin, views.View): #рендер страницы формирования заказа

    def get(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        context = {
            'form': form,
            'cart': self.cart,
        }
        return render(request, 'checkout.html', context)

class MakeOrderView(CartMixin, views.View): #создание заказа

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        if not request.user.is_authenticated: #если пользователь не авторизован
            customer = Customer.objects.filter(user_id=2).last() #находим покупателя с анонимным id
        else:
            customer = Customer.objects.get(user=request.user) #находим покупателя с текущим пользователем
        if form.is_valid():
            new_order = form.save(commit=False) #создаем новый заказ
            new_order.customer = customer
            new_order.phone = form.cleaned_data['phone']
            new_order.email = form.cleaned_data['email']
            new_order.use_bonuses = form.cleaned_data['use_bonuses']
            new_order.save()

            bonuses = customer.bonuses  # сохраняем текущие бонусы

            if not self.cart.for_anonymous_user: #начисляем за покупку бонусы
                customer.bonuses += int(self.cart.sum * Decimal("0.05"))
                customer.save()

            self.cart.in_order = True
            if new_order.use_bonuses: #если выбрано списание бонусов
                if bonuses > int(self.cart.sum): #если бонусов больше суммы заказа
                    bonuses = int(self.cart.sum) #списываем сумму заказа, то есть скидка будет 100%
                self.cart.sum -= bonuses #уменьшаем сумму корзины
                customer.bonuses -= bonuses #списываем бонусы
                customer.save()
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.orders.add(new_order)

            for bron in self.cart.tickets.all():
                bron.ticket.bought = True
                bron.ticket.save()
            context = {'cart': self.cart}
            return render(request, 'success.html', context)
        for bron in self.cart.tickets.all():
            bron.ticket.reserved = False
            bron.ticket.save()
            self.cart.tickets.remove(bron)
            bron.delete()
            recalc_cart(self.cart)
        return HttpResponseRedirect('/checkout/')