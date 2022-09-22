from django.shortcuts import render
from django.views.generic import ListView, TemplateView, View

#
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
# importamos los modelos
from .models import TraderPayment, VpsPayment

# Create your views here.

class PaymentsView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/payments.html'
    login_url = reverse_lazy('users_app:user_login')
    paginate_by = 10
    ordering = 'id'
    context_object_name = 'lista-pagos'
    model = VpsPayment, TraderPayment

