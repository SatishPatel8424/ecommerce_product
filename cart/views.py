import json
from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse, HttpResponseRedirect
import sweetify
from django.views import generic

def empty_cart_modal(request):
    """Modal shown when cart page accessed with empty cart."""
    sweetify.error(
        request,
        "Your cart is empty.",
        text="Add products to your cart.",
        timer=4000,
        timerProgressBar=True,
        button=True
    )
    return request


class cart_view(generic.TemplateView):
    template_name = 'cart.html'
    context_object_name = 'cart_items'


    def get(self, request, *args, **kwargs):
        if not request.session.get("cart"):
            empty_cart_modal(request)
            return redirect(reverse("products"))
        return render(self.request, self.template_name)

    def post(self, request, *args, **kwargs):
        if request.headers["Identifying-Header"] == "quantityValidationFetch":
            custom_fetch_request = json.loads(request.body)
            response = validate_item_quantity_change(
                request, custom_fetch_request)
            return JsonResponse(response)
        if request.headers["Identifying-Header"] == "removeCartItemFetch":
            custom_fetch_request = json.loads(request.body)
            cart = request.session["cart"]
            target_product = custom_fetch_request["itemId"]
            del cart[target_product]
            request.session["cart"] = cart
            return JsonResponse({"success": True}, status=200)
        return JsonResponse({"success": False, }, status=400)

def add_to_cart(request, id):
    """Adds the required quantity of a product to session variable."""
    quantity = int(request.POST.get("quantity"))
    cart = request.session.get("cart", {})
    if id in cart:
        cart[id] = int(cart[id]) + quantity
    else:
        cart[id] = cart.get(id, quantity)

    request.session["cart"] = cart
    return redirect(reverse("cart_view"))

def adjust_cart(request, id):
    """Alters existing product quantity, removes if quantity less than 1."""
    quantity = int(request.POST.get("quantity"))
    cart = request.session.get("cart", {})
    if quantity > 0:
        cart[id] = quantity
    else:
        cart.pop(id)
    request.session["cart"] = cart
    return redirect(reverse("cart_view"))


def validate_item_quantity_change(request, custom_fetch_request):
    item_id = custom_fetch_request["itemId"]
    cart = request.session["cart"]
    old_item_quantity = int((cart[item_id]))
    new_item_quantity = int(custom_fetch_request["newItemQuantity"])
    response = {
        "itemId": item_id,
        "newItemQuantity": new_item_quantity,
        "updatedQuantity": False
    }
    if old_item_quantity != new_item_quantity:
        response["updatedQuantity"] = True
    return response
