from django import views
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'payments_app'

urlpatterns = [
    path('payments/', views.PaymentsView.as_view(), name='payments'),
    path('paypal-payment/', views.CreatePaymentView.as_view(), name='paypal_payment')
]
