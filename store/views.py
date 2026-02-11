from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
from .models import Product, Order, OrderItem
from .cart import Cart, CartItem
from yookassa import Configuration, Payment
from django.conf import settings
import uuid
from django.http import JsonResponse

Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

def remove_from_cart(request, product_id):
    pass


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()   # ❗ вызов метода
            login(request, user)
            return redirect('product_list')
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {
        'products': products
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {
        'product': product
    })


def about(request):
    return render(request, 'store/about.html')


@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    items = cart.items.all()

    total_price = sum(item.get_total_price() for item in items)

    context = {
        'cart': cart,
        'items': items,
        'total_price': total_price,
    }

    return render(request, 'cart/cart.html', context)


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        CartItem.objects.create(cart=cart, product=product, quantity=1)

    return redirect('view_cart')

def update_cart_item(request):
    return JsonResponse({'status': 'ok'})

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product, Cart, Order
import uuid

@login_required
def create_payment(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total_price = sum(item.get_total_price() for item in items)

    payment = Payment.create({
        "amount": {
            "value": str(total_price),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "http://127.0.0.1:8000/payment-success/"
        },
        "capture": True,
        "description": f"Оплата {product.name}"
    }, str(uuid.uuid4()))

    Order.objects.create(
        product=product,
        user=request.user,
        payment_id=payment.id,
        status="pending"
    )

    return redirect(payment.confirmation.confirmation_url)


def payment_success(request):
    return render(request, "payment_success.html")
