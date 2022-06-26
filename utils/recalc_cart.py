from django.db import models

def recalc_cart(cart):
    cart_data = cart.tickets.aggregate(models.Sum('price'), models.Count('id'))
    if cart_data.get('price__sum'):
        cart.sum = cart_data['price__sum']
    else:
        cart.sum = 0
    cart.count = cart_data['id__count']
    cart.save()


