from django.urls import path
from .views import products_view, product_detail_view, product_search
from products import views

urlpatterns = [

    path('', views.products_view.as_view(), name='products'),

    path('product/<int:pk>', views.product_detail_view.as_view(), name='product_detail'),
    path('search', views.product_search.as_view(), name='product_search'),


]
