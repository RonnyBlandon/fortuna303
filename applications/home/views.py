from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.contrib import messages
# Importamos los formularios
from .forms import ContactForm
# Create your views here.

class HomeTemplateView(TemplateView):
    template_name  = 'home/home.html'


class ContactView(FormView):
    template_name = 'home/contact.html'
    form_class = ContactForm
    success_url = '.'

    def form_valid(self, form):

        # Enviamos el mensaje al correo para de soporte
        name = form.cleaned_data['name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        affair = form.cleaned_data['affair']
        mensaje = 'PAGINA DE CONTACTO' + '\n\n' + 'Mi nombre es: ' + name + ' ' + last_name + '\n' + 'Mi correo es: ' + email + '\n\n' +form.cleaned_data['message']
        email_remitente = 'fortuna303.com@gmail.com'
        send_mail(affair, mensaje, email_remitente, [email_remitente,])

        messages.add_message(request=self.request, level=messages.SUCCESS, message='Su mensaje fue enviado con exito. Muy pronto recibira respuesta en su correo.')

        # Redirigimos a la misma pagina de contacto
        return HttpResponseRedirect(
            reverse('home_app:contact')
        )


class HowDoesItWorkView(TemplateView):
    template_name = 'home/how-work.html'


class TermsTemplateView(TemplateView):
    template_name = 'home/terms.html'


class PrivacyPolicyTemplatesView(TemplateView):
    template_name = 'home/privacy-policy.html'


class Error404View(TemplateView):
    template_name = "home/error_404.html"
    