import os
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views import generic

from .forms import ContactForm


class contact_us(generic.FormView):
    form_class = ContactForm
    template_name = "contact.html"
    success_url = 'success/'

    def get(self, *args, **kwargs):
        form = self.form_class()
        current_user = self.request.user
        if str(current_user) != "AnonymousUser":
            form.fields["email"].widget.attrs.update({
                "value": current_user.email
            })
        return render(self.request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            customer_email_address = form.cleaned_data["email"]
            contact_message = customer_email_address + " - " + \
                              form.cleaned_data["contact_message"]
            try:
                send_mail(subject, contact_message, customer_email_address, [
                    os.environ.get("EMAIL_RECIPIENT")], True)
            except BadHeaderError:
                # Prevents header injection.
                return HttpResponse("Invalid header found.")
            return JsonResponse({"success": True}, status=200)
        return JsonResponse({"success": False, "errors": form.errors}, status=400)


