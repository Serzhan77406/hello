from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
import uuid

# формы
from .forms import RegisterForm, LoginForm

# модели
from .models import Product, Order, OrderItem

# корзина
from .cart import Cart, CartItem

# YooKassa
from yookassa import Configuration, Payment

# Настройка YooKassa
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


# --- Аккаунт ---
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
            user = form.get_user()
            login(request, user)
            return redirect('product_list')
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# --- Продукты ---
def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})


def about(request):
    return render(request, 'store/about.html')


# --- Корзина ---
@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total_price = sum(item.get_total_price() for item in items)
    return render(request, 'cart/cart.html', {
        'cart': cart,
        'items': items,
        'total_price': total_price,
    })


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


@login_required
def remove_from_cart(request, product_id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    try:
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    return redirect('view_cart')


def update_cart_item(request):
    return JsonResponse({'status': 'ok'})


# --- Платежи ---
@login_required
def create_payment(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Создаём заказ
    order = Order.objects.create(
        user=request.user,
        total_price=product.price,  # цена всего заказа (здесь один продукт)
        payment_id='temp',          # временно, потом заменим на payment.id
        status='pending'
    )

    # Создаём элемент заказа
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1
    )

    # Создаём платеж в YooKassa
    payment = Payment.create({
        "amount": {
            "value": str(order.total_price),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "http://127.0.0.1:8000/payment-success/"
        },
        "capture": True,
        "description": f"Оплата {product.name}"
    }, str(uuid.uuid4()))

    # Сохраняем реальный payment_id
    order.payment_id = payment.id
    order.save()

    # Редирект на оплату
    return redirect(payment.confirmation.confirmation_url)

def payment_success(request):
    return render(request, "payment_success.html")