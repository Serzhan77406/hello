from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterForm, LoginForm
from .models import Product

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
    return render(request, "accounts/register.html",{'form':form})



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user
            login(request, user)          
            
            return redirect('product_list')
    else:
        form = LoginForm()
    return render(request, "accounts/login.html",{'form':form})

def Logout_viev(request):
    logout(request)
    return redirect('login')


def product_list(request):
    products = Product.objects.all() # берём все товары
    return render(request, 'store/product_list.html', {
    'products': products
    })

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'store/product_detail.html', {
        'product': product
    })

def about(request):
    return render(request, 'store/about.html')

