from django import views
from django.urls import path
from . import views

app_name = 'vps_app'

urlpatterns = [
    path('panel-user/', views.PanelUserView.as_view(), name='panel_user'),
    path('add-account-mt5/', views.CreateAccounMt5View.as_view(), name='add_account_mt5'),
    path('delete-account-mt5/<pk>', views.DeleteAccountMt5View.as_view(), name='delete_account_mt5'),
]
