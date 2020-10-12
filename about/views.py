from django.shortcuts import render
from django.views import generic

# about us view
class about_us(generic.TemplateView):
    template_name = 'about.html'

