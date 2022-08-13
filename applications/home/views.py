from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.

class HomeTemplateView(TemplateView):
    template_name  = 'home/home.html'


class ContactoTemplateView(TemplateView):
    template_name = 'home/contact.html'


class TermsTemplateView(TemplateView):
    template_name = 'home/terms.html'


class PrivacyPolicyTemplatesView(TemplateView):
    template_name = 'home/privacy-policy.html'