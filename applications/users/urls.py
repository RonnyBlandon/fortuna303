from django import views
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'users_app'

urlpatterns = [
    path(
        'user-register/', 
        views.UserRegisterView.as_view(), 
        name='user_register'
        ),
    path(
        'user-login/', 
        views.UserLoginView.as_view(), 
        name='user_login'
        ),
    path(
        'logout/', 
        views.LogoutView.as_view(), 
        name='user_logout'
        ),
    path(
        'update-password/', 
        views.UpdatePasswordView.as_view(), 
        name='update_password'
        ),
    path(
        'code-verification/<pk>/', 
        views.CodeVerificationView.as_view(), 
        name='user_verification'
        ),
    path('email-password/', 
        views.RecoverAccountView.as_view(), 
        name='user_email_password'
        ),
    path(
        'change-password/<pk>/', 
        views.ChangePasswordView.as_view(), 
        name='user_change_password'
        ),
]
