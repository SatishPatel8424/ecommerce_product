from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.views import generic
from django.views.generic.base import View
from .models import Product

# product view
class products_view(generic.ListView):
    model = Product
    template_name = 'productslist.html'
    context_object_name = 'product'
    paginate_by = 15

    def get_paginate_by(self, queryset):
        queryset = Product.objects.filter(active_product=True)

# product detail view
class product_detail_view(generic.DetailView):
    model = Product
    template_name = "productdetail.html"
    context_object_name = 'product'

# product search view
class product_search(generic.ListView):
    model = Product
    template_name = 'productslist.html'
    context_object_name = 'product'

    def get_queryset(self):  # new
        # query = self.request.GET.get('q')
        search_query = self.request.GET.get("search_query")
        search_query_list = search_query.split(" ")
        q_object = Q(name__icontains=search_query_list[0]) | Q(
            description__icontains=search_query_list[0])
        for term in search_query_list:
            q_object.add((Q(name__icontains=term) | Q(
                description__icontains=term)), q_object.connector)
        products = Product.objects.filter(q_object, active_product=True)

        return products


