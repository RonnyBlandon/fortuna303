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
    path('checkout-session/', views.CheckoutSessionView.as_view(), name='checkout_session'),
    path('webhook-stripe/', views.WebhookStripeView.as_view(), name='webhook_stripe'),
    path('payment-success/', views.SuccessPaymentView.as_view(), name='payment_success'),
    path('payment-cancel/', views.CancelPaymentView.as_view(), name='payment_cancel'),
]
