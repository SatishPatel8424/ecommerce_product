from django.urls import path
from . import views
from .views import about_us

urlpatterns = [
    path("", views.about_us.as_view(), name="about"),


]
