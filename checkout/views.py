from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
import sweetify
from django.utils.decorators import method_decorator
from django.views import generic
from cart.views import empty_cart_modal
from cart.contexts import cart_contents
from products.models import Product
from .forms import CustomerShippingForm, PaymentForm
from .models import CustomerShipping, OrderDetail
import stripe

stripe.api_key = settings.STRIPE_SECRET
# decorators = [login_required]

# @method_decorator(login_required, name='dispatch')
class checkout_shipping_address_view(LoginRequiredMixin,generic.FormView):
    form_class = CustomerShippingForm
    template_name = 'checkout_shipping_address.html'

    def get_initial(self):
        if not self.request.session.get("cart"):
            empty_cart_modal(self.request)
            return redirect("products")
        return self.initial.copy()

    def form_valid(self, form):
        form = self.form_class(self.request.POST)
        shipping = form.save(commit=False)
        shipping.customer = self.request.user
        shipping.save()
        return redirect("payment")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        form = self.form_class()
        return self.render_to_response(self.get_context_data(form=form))



# @method_decorator(login_required, name='dispatch')
class checkout_payment(LoginRequiredMixin,generic.FormView):
    form_class = PaymentForm
    template_name = 'checkout_payment.html'


    def form_valid(self, form):
        if self.request.method == "POST":
            # payment_form = PaymentForm(request.POST)
            form = self.form_class(self.request.POST)
            if form.is_valid():
                cart = self.request.session.get("cart", {})
                cart_total = cart_contents(self.request)["total"]
                try:
                    stripe.Charge.create(
                        amount=int(cart_total * 100),
                        currency="GBP",
                        description=self.request.user.email,
                        card=form.cleaned_data["stripe_id"]
                    )
                except stripe.error.CardError:
                    sweetify.error(
                        self.request,
                        title="Payment error occurred, please retry with valid credentials.",
                        text="If error persists, contact site owner.",
                        icon="error"
                    )
                except stripe.error.InvalidRequestError:
                    sweetify.error(
                        self.request,
                        title="A payment error has occurred.",
                        text="An item may have gone out of stock during checkout.",
                        icon="error"
                    )
                    return redirect("profile")
                except stripe.error.APIConnectionError:
                    sweetify.error(
                        self.request,
                        title="A payment error has occurred.",
                        text="Connection to payment handler has failed, please retry later.",
                        icon="error"
                    )
                    return redirect("profile")
                else:
                    sweetify.success(
                        self.request,
                        title="Payment successful, thank you for your purchase.",
                        icon="success"
                    )
                    create_order_product_records(self.request, cart)
                    del self.request.session["cart"]
                    return redirect(reverse("profile"))
                return JsonResponse({"success": True}, status=200)


    def form_invalid(self, form):
        form = self.form_class()
        return JsonResponse({"success": False, "errors": form.errors}, status=400)

def create_order_product_records(request, cart):
    """Creates the product order record in the database.

    The product's available stock is decreased by the purchased quantity.
    """
    for item, quantity in cart.items():
        product = get_object_or_404(Product, pk=item)
        product_total = quantity * product.price
        product.stock_available -= quantity
        product.save()
        order_detail = OrderDetail(
            shipping=CustomerShipping.objects.filter(
                customer=request.user).last(),
            product=product,
            quantity=quantity,
            total=product_total,
        )
        order_detail.save()
