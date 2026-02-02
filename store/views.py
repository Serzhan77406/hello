from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
from .models import Product
from .Cart import Cart,Cartitem

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

@login_required

def view_cart(request):
    if not request.user.is_authenticated:
        return redirest('login')
    
    cart, created = Cart.obgects.get_or_create(user=request.user)    

    items = cart.items.all()

    total_price = 0
    for item in items:
        total_price += item.get_total_price()

    context ={
        'cart' : cart,
        'items' : items,
        'total_price' : total_price,
    }    

    return render(request, 'cart.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(product, id=product_id)
     cart,_ = Cart.object.get_or_create(user=request.user)
    
try:    

    cart_item = Cartitem.objects.get(cart=cart, product=product)
    cart_item.quantity +=1
    cart_item.save()
except Cartitem.doesNotExist:
    Cartitem.objects.create(cart=cart, product=product, quantity=1) 

return redirect('vieq_cart')   



