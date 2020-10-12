import random
from django.shortcuts import render
from django.views import generic

from products.models import Product

# home view
class home(generic.ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'

    def get_queryset(self):
        showcase_products = Product.objects.filter(
            showcase_product=True)
        products = []
        total_showcase_products = showcase_products.count()
        if total_showcase_products > 3:
            random_indices = random.Random().sample(
                range(0, total_showcase_products), 3
            )
            for index in random_indices:
                products.append(showcase_products.all()[index])
        elif total_showcase_products == 3:
            products = showcase_products
        return products