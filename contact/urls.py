from django.urls import path
# from .views import contact_us, contact_success
from contact import views
from contact import views as contact1


urlpatterns = [
    # path("", contact_us, name="contact"),
    # path("success/", contact_success, name="contact_success")
    path('', contact1.contact_us.as_view(), name="contact"),
]
