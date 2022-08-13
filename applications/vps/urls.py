from django import views
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'vps_app'

urlpatterns = [
    path('panel-user/', views.PanelUserView.as_view(), name='panel_user'),
    path('facturation-system/', views.SistemaFacturacionView.as_view(), name='billing'),
]
