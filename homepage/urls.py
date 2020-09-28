from django.urls import path
from . views import home
from homepage import views

urlpatterns = [
    path('', views.home.as_view(), name='home'),
]
