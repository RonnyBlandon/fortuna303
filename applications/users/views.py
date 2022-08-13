from email import message
from urllib import request
from django.core.mail import send_mail
# importamos las vistas genericas
from django.views.generic import View
from django.views.generic.edit import FormView
# importamos las librerias de redireccion de urls
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
# importamos las librerias de autenticacion de django
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
# importamos los forms
from .forms import (
    UserRegisterForm, UserLoginForm, UpdatePasswordForm, VerificationForm, 
    EmailPasswordForm, ChangePasswordForm
)
# importamos los modelos
from .models import User
# imporatmos function.py
from .function import code_generator


class UserRegisterView(FormView):
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('users_app:user_login')

    def form_valid(self, form):
        # Generamos el codigo de verificacion de correo al usuario recien registrado
        codigo = code_generator()

        usuario = User.objects.create_user(
            form.cleaned_data['name'],
            form.cleaned_data['last_name'],
            form.cleaned_data['email'],
            form.cleaned_data['password1'],
            validation_code=codigo
        )

        # Enviamos el codigo al email del usuario
        asunto = 'Confirmacion de Correo Electronico'
        mensaje = 'Codigo de Verificación: ' + codigo
        email_remitente = 'ronnyblandon2015@gmail.com'
        send_mail(asunto, mensaje, email_remitente, [form.cleaned_data['email'],])

        # Redirigimos a pantalla de verificacion al usuario
        return HttpResponseRedirect(
            reverse('users_app:user_verification', kwargs={'pk': usuario.id})
        )


class UserLoginView(FormView):
    template_name = 'users/login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('vps_app:panel_user')

    def form_valid(self, form):
        user = authenticate(
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password']
        )
        login(self.request, user)

        return super(UserLoginView, self).form_valid(form)


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(
            reverse('users_app:user_login')
        )

# esta vista es para cambiar la contraseña de los usuarios logueados
class UpdatePasswordView(LoginRequiredMixin, FormView):
    template_name = 'users/update-password.html'
    form_class = UpdatePasswordForm
    success_url = reverse_lazy('users_app:user_login')
    login_url = reverse_lazy('users_app:user_login')

    def get_form_kwargs(self):
        kwargs = super(UpdatePasswordView, self).get_form_kwargs()
        kwargs.update({
            'email': self.request.user.email
        })
        return kwargs

    def form_valid(self, form):

        usuario = self.request.user
        user = authenticate(
            email=usuario.email,
            password=form.cleaned_data['password3']
        )

        if user:
            new_password = form.cleaned_data['password1']
            usuario.set_password(new_password)
            usuario.save()

        logout(self.request)

        return super(UpdatePasswordView, self).form_valid(form)


class CodeVerificationView(FormView):
    template_name = 'users/code-verification.html'
    form_class = VerificationForm
    success_url = reverse_lazy('users_app:user_login')

    # Reescribimos esta funcion para pasarle el pk al Formulario desde la View
    def get_form_kwargs(self):
        kwargs = super(CodeVerificationView, self).get_form_kwargs()
        kwargs.update({
            'pk': self.kwargs['pk']
        })
        return kwargs

    def form_valid(self, form):

        User.objects.filter(
            id=self.kwargs['pk']
        ).update(is_active=True)

        return super(CodeVerificationView, self).form_valid(form)


class RecoverAccountView(FormView):
    template_name = 'users/forgot-password.html'
    form_class = EmailPasswordForm
    success_url = reverse_lazy('users_app:user_change_password')

    def get_queryset(self):
        queryset = super(RecoverAccountView, self).get_queryset()
        queryset = queryset.id
        return queryset

    def form_valid(self, form):
        # Generamos el codigo de verificacion al correo del usuario que olvido su contraseña
        codigo = code_generator()

        # El metodo form.cleaned_data no recibe el dato por lo que usamos el self.request.POST.get
        email = form.cleaned_data['email']

        # Actualizamos el nuevo codigo al usuario en la base de datos
        user = User.objects.filter(email=email)
        user.update(validation_code=codigo)
        id_user = user.get().id # obtenemos el id del usuario

        # Enviamos el codigo al correo
        asunto = 'Recuperación de cuenta'
        mensaje = 'Codigo de Verificación: ' + codigo + '\nNecesita este código para cambiar su contraseña.'
        email_remitente = 'ronnyblandon2015@gmail.com'
        send_mail(asunto, mensaje, email_remitente, [email,])

        # Redirigimos a pantalla de verificacion al usuario para cambiar contraseña
        return HttpResponseRedirect(
            reverse('users_app:user_change_password', kwargs={'pk': id_user})
        )


# esta vista es para cambiar la contraseña de los usuarios que no estan logueados
class ChangePasswordView(FormView):
    template_name = 'users/change-password.html'
    form_class = ChangePasswordForm
    success_url = reverse_lazy('users_app:user_login')

    # Reescribimos esta funcion para pasarle el pk al Formulario desde la View
    def get_form_kwargs(self):
        kwargs = super(ChangePasswordView, self).get_form_kwargs()
        kwargs.update({
            'pk': self.kwargs['pk']
        })
        return kwargs

    def form_valid(self, form):
        
        user = User.objects.filter(validation_code=form.cleaned_data['validation_code'])
        user = user.get()
        print('Esto es lo que contiene user en cambio de contraseña: ', user)
        new_password = self.request.POST.get('password2')
        user.set_password(new_password)
        user.save()

        return super(ChangePasswordView, self).form_valid(form)
        