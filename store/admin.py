from django.contrib import admin
from .models import Product
from .cart import Cart, CartItem


admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)





