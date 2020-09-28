from django.urls import path
from .views import checkout_shipping_address_view, checkout_payment
from checkout import views as check1
from checkout import views as contact1

urlpatterns = [
    path("shipping/", contact1.checkout_shipping_address_view.as_view(), name="shipping"),
    path("payment/", contact1.checkout_payment.as_view(), name="payment"),
    # path('shipping/', check1.checkout_shipping_address_view.as_view(), name="shipping")
]
