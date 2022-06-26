from django import views

from .models import Cart, Customer
#Класс для создания покупателя и корзины
class CartMixin(views.generic.detail.SingleObjectMixin, views.View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated: #если пользователь авторизован
            customer = Customer.objects.filter(user=request.user).first()
            if not customer:
                customer = Customer.objects.create(user=request.user)
            cart = Cart.objects.filter(owner=customer, in_order=False).last()
            if not cart:
                cart = Cart.objects.create(owner=customer)
        else:
            customer = Customer.objects.filter(user_id=2).first()
            if not customer:
                customer = Customer.objects.create(user_id=2)
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart:
                cart = Cart.objects.create(owner=customer, for_anonymous_user=True)
        self.cart = cart
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context