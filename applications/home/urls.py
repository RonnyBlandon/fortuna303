from django import views
from django.urls import path
from . import views

app_name = 'home_app'

urlpatterns = [
    path('', views.HomeTemplateView.as_view(), name='home'),
    path('terms/', views.TermsTemplateView.as_view(), name='terms'),
    path('privacy-policy/', views.PrivacyPolicyTemplatesView.as_view(), name='privacy_policy'),
    path('contact/', views.ContactoTemplateView.as_view(), name='contact'),
]