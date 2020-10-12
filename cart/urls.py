import view
from django.urls import path, re_path
from .views import cart_view, add_to_cart, adjust_cart

from cart import views


urlpatterns = [
    path("", views.cart_view.as_view(), name="cart_view"),
    re_path(r"add/(?P<id>\d+)", views.add_to_cart, name="add_to_cart"),
    re_path(r"adjust/(?P<id>\d+)", views.adjust_cart, name="adjust_cart"),

]
