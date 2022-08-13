from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
#
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

# Create your views here.

class PanelUserView(LoginRequiredMixin,TemplateView):
    template_name = 'vps/panel-user.html'
    login_url = reverse_lazy('users_app:user_login')


class SistemaFacturacionView(LoginRequiredMixin, TemplateView):
    template_name = 'vps/facturacion.html'
    login_url = reverse_lazy('users_app:user_login')
