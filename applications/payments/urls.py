from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views
from .views import WebhookStripeView

app_name = 'payments_app'

urlpatterns = [
    path('payments/', views.PaymentsView.as_view(), name='payments'),
    path('payment/<str:payment_type>/', views.PaymentFormView.as_view(), name='payment_form'),
    path('payment/<str:payment_type>/<int:pk>/', views.PaymentFormView.as_view(), name='payment_renewal'),
    path('checkout-session/', views.CheckoutSessionView.as_view(), name='checkout_session'),
    path('webhook-stripe/', csrf_exempt(WebhookStripeView.as_view()), name='webhook_stripe'),
]
