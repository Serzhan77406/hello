from django.urls import path
from .views import product_list, register_view, login_view
from . import views


urlpatterns = [
    path('', product_list, name='product_list'),
    path('about/', views.about, name='about'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login')
]