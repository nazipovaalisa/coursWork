from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import (BaseView, FilmDetailView, SeansDetailView, SeansListView, RegistrationView, LoginPostView, RegistrationPostView,
                    LoginView, AccountView, CartView, AddToCartView, DeleteFromCartView, CheckOrder, MakeOrderView, CheckOutView, EmailVerifyView)

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<int:ticket_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('delete-from-cart/<int:ticket_id>/', DeleteFromCartView.as_view(), name='delete_from_cart'),
    path('', BaseView.as_view(), name='base'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('verify_email/<uidb64>/<token>', EmailVerifyView.as_view(), name='verify_email'),
    path('account/', AccountView.as_view(), name='account'),
    path('checkorder/', CheckOrder.as_view(), name='checkorder'),
    path('login-post/', LoginPostView.as_view(), name='login_post' ),
    path('registration_post/', RegistrationPostView.as_view(), name='registration_post'),
    path('checkout/', CheckOutView.as_view(), name='checkout'),
    path('make-order/', MakeOrderView.as_view(), name='make_order'),
    path('<str:film_slug>/', FilmDetailView.as_view(), name='film_detail'),
    path('<str:film_slug>/<str:date_seans>/', SeansListView.as_view(), name='seans_list'),
    path('<str:film_slug>/<str:date_seans>/<slug:seans_slug>/', SeansDetailView.as_view(), name='seans_detail'),
]
