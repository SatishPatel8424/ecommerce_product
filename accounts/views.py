from django.contrib.auth.mixins import LoginRequiredMixin
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

# decorators = [login_required]

# logout view
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

# registration view
class registration(generic.FormView):
    form_class = UserRegisterForm
    template_name = 'register.html'

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_initial(self):
        if self.request.user.is_authenticated:
            return redirect("profile")
        previous_page = self.request.META.get("HTTP_REFERER")
        form = self.form_class(self.request.POST)
        if previous_page:
            if "next" in previous_page:
                marker_index = previous_page.index("next")
                string_length = len(previous_page)
                redirect_string = previous_page[marker_index + 5:string_length]
                self.request.session["redirect_target"] = redirect_string
        return self.initial.copy()

    def form_valid(self, form):
        form.save()
        sweetify.success(
            self.request,
            title="Account created successfully.",
            icon="success"
        )
        user = auth.authenticate(
            self.request,
            username=form.cleaned_data.get("username"),
            password=form.cleaned_data.get("password1")
        )
        if user is not None:
            auth.login(self.request, user)
            if self.request.session.get("redirect_target"):
                return HttpResponseRedirect(
                    self.request.session["redirect_target"]
                )
            return redirect("profile")
        return HttpResponseRedirect(self.get_success_url())

# profile view
# @method_decorator(login_required, name='dispatch')
class profile(LoginRequiredMixin,generic.FormView):
    form_class = UserCredentialsUpdateForm
    template_name = 'profile.html'


    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_initial(self):
        previous_page = self.request.META.get("HTTP_REFERER")
        if previous_page:
            if previous_page.endswith("login"):
                sweetify.success(
                    self.request,
                    title="Login successful.",
                    icon="success",
                )
        return self.initial.copy()

    def form_valid(self, form):
        user = User.objects.get(username=self.request.user)
        user_orders = OrderDetail.objects.filter(
            shipping__customer_id=user.id).order_by("-purchase_date")
        form = UserCredentialsUpdateForm(self.request.POST, instance=user)
        new_credentials = form.save(commit=False)
        hashed_password = make_password(form.cleaned_data["password"])
        new_credentials.password = hashed_password
        new_credentials.save()
        sweetify.success(
            self.request,
            "Your credentials have been updated, please login."
        )
        return redirect("login")
        return HttpResponseRedirect(self.get_success_url())




