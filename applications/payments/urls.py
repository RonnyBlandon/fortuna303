from django import views
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'payments_app'

urlpatterns = [
    path('payments/', views.PaymentsView.as_view(), name='payments'),
    path('first-payment/', views.FirstPaymentView.as_view(), name='first_payment'),
    path('renewal-payment/<pk>/', views.VpsPaymentRenewalView.as_view(), name='vps_payment_renewal'),
    path('trader-payment/<pk>/', views.TraderPaymentRenewalView.as_view(), name='trader_payment'),
]
