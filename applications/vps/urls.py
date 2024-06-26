from django import views
from django.urls import path
from . import views

app_name = 'vps_app'

urlpatterns = [
    path('panel-user/', views.PanelUserView.as_view(), name='panel_user'),
    path('add-account-mt5/', views.CreateAccounMt5View.as_view(), name='add_account_mt5'),
    path('delete-account-mt5/<pk>', views.DeleteAccountMt5View.as_view(), name='delete_account_mt5'),
    path('reconnect-account-mt5/>', views.ReconnectMt5Account.as_view(), name='reconnect_account_mt5'),
    path('confirmation-unsubscribe/', views.ConfirmationUnsubscribeView.as_view(), name='confirmation_unsubscribe'),
    path('unsubscribe/', views.UnsubscriberView.as_view(), name='unsubscribe'),
]
