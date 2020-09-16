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


    def get_initial(self):
        form = self.form_class()
        if self.request.GET:
            initial = self.request.GET.dict()
            current_user = self.request.user
            if str(current_user) != "AnonymousUser":
                form.fields["email"].widget.attrs.update({
                    "value": current_user.email
                })
            return initial
        else:
            return super(contact_us, self).get_initial()

    def form_valid(self, form):
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
        return super().form_valid(subject)

class contact_success(generic.TemplateView):
    template_name = 'contact_success.html'
