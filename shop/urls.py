from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    if request.user.is_authehticated:
        return HttpResponse(f'привет {request.user.username}')
    return HttpResponse('Вы вoшли')


urlpatterns = [
path('admin/', admin.site.urls),
path('', include('store.urls')),
]