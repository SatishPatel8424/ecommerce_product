from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import sweetify
from django.utils.decorators import method_decorator
from django.views import generic

from checkout.models import OrderDetail
from .forms import UserRegisterForm, UserCredentialsUpdateForm

decorators = [login_required]

@login_required
def logout(request):
    """Log the user out."""
    auth.logout(request)
    sweetify.success(
        request,
        title="You have been successfully logged out.",
        icon="success"
    )
    return redirect(reverse("home"))

class registration(generic.FormView):
    form_class = UserRegisterForm
    template_name = 'register.html'

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("profile")
        previous_page = request.META.get("HTTP_REFERER")
        form = self.form_class(self.request.POST)
        if previous_page:
            if "next" in previous_page:
                marker_index = previous_page.index("next")
                string_length = len(previous_page)
                redirect_string = previous_page[marker_index + 5:string_length]
                request.session["redirect_target"] = redirect_string
        if request.method == "POST":
            if form.is_valid():
                form.save()
                sweetify.success(
                    request,
                    title="Account created successfully.",
                    icon="success"
                )
                user = auth.authenticate(
                    request,
                    username=form.cleaned_data.get("username"),
                    password=form.cleaned_data.get("password1")
                )
                if user is not None:
                    auth.login(request, user)
                    if request.session.get("redirect_target"):
                        return HttpResponseRedirect(
                            request.session["redirect_target"]
                        )
                    return redirect("profile")
        else:
            # form = UserRegisterForm()
            form = self.form_class()
            return JsonResponse({"success": True}, status=200)
        return JsonResponse({"success": False, "errors": form.errors}, status=400)


@method_decorator(login_required, name='dispatch')
class profile(generic.FormView):
    form_class = UserCredentialsUpdateForm
    template_name = 'profile.html'

    def post(self, request, *args, **kwargs):
        previous_page = request.META.get("HTTP_REFERER")
        if previous_page:
            if previous_page.endswith("login"):
                sweetify.success(
                    request,
                    title="Login successful.",
                    icon="success",
                )
        user = User.objects.get(username=request.user)
        user_orders = OrderDetail.objects.filter(
            shipping__customer_id=user.id).order_by("-purchase_date")
        if request.method == "POST":
            form = UserCredentialsUpdateForm(request.POST, instance=user)
            if form.is_valid():
                new_credentials = form.save(commit=False)
                hashed_password = make_password(form.cleaned_data["password"])
                new_credentials.password = hashed_password
                new_credentials.save()
                sweetify.success(
                    request,
                    "Your credentials have been updated, please login."
                )
                return redirect("login")
        else:
            form = UserCredentialsUpdateForm(instance=user)
            return JsonResponse({"success": True}, status=200)
        return JsonResponse({"success": False, "errors": form.errors}, status=400)


