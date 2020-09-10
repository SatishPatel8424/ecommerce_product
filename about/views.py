from django.shortcuts import render
from django.views import generic

class about_us(generic.TemplateView):
    template_name = 'about.html'

