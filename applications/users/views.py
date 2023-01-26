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
from django.contrib import messages
# importamos los forms
from .forms import (
    UserRegisterForm, UserLoginForm, UpdatePasswordForm, VerificationForm, 
    EmailPasswordForm, ChangePasswordForm
)
# importamos los modelos
from .models import User, Level
# imporatmos function.py
from .function import code_generator, notification_admin_by_mail, create_mail


class UserRegisterView(FormView):
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('users_app:user_login')

    def form_valid(self, form):
        # Generamos el codigo de verificacion de correo al usuario recien registrado
        codigo = code_generator()
        # este get devuelve una tupla de instancias
        level = Level.objects.get(account_level='0'), # Siempre iniciaran como nivel 0
        
        name = form.cleaned_data['name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        user = User.objects.create_user(
            name,
            last_name,
            email,
            level[0],
            form.cleaned_data['password1'],
            validation_code=codigo
        )

        # Enviamos el codigo de verificar cuenta al email del usuario
        mail = create_mail(user.email, "CÓDIGO DE VERIFICACIÓN", "users/send-verification.html", {"validation_code": codigo, "message_context": "Necesitas este código para verificar el correo electrónico."})
        mail.send(fail_silently=False)
        # Enviamos un correo notificando al email del administrador que se ha creado una cuenta de usuario.
        affair_admin = "NUEVA CUENTA DE USUARIO."
        message_admin = f"Se ha creado una nueva cuenta de usuario sin verificar. \n\n ID: {user.id} \n Name: {name} {last_name} \n Email: {email}"
        notification_admin_by_mail(affair_admin, message_admin)

        # Redirigimos a pantalla de verificacion al usuario
        return HttpResponseRedirect(
            reverse('users_app:user_verification', kwargs={'pk': user.id})
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

        messages.add_message(request=self.request, level=messages.SUCCESS, message='Se ha cambiado la contraseña, inicie sesión.')

        # Enviamos un correo notificando al email del administrador que se ha creado una cuenta de usuario.
        affair_admin = "USUARIO HA CAMBIADO SU CONTRASEÑA."
        message_admin = f"Un usuario ha cambiado su contraseña. \n\n ID: {user.id} \n Name: {user.name} {user.last_name} \n Email: {user.email}"
        notification_admin_by_mail(affair_admin, message_admin)

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

        user = User.objects.filter(
            id=self.kwargs['pk']
        )
        user.update(is_active=True)
        messages.add_message(request=self.request, level=messages.SUCCESS, message='Se ha verificado el correo electrónico, ya puede iniciar sesión.')

        # Enviamos un correo notificando al email del administrador que se ha verificado una cuenta de usuario.
        affair_admin = "SE HA VERIFICADO UNA CUENTA DE USUARIO"
        message_admin = f"Se verifico la cuenta del usuario. \n\n ID: {user[0].id} \n Name: {user[0].name} {user[0].last_name} \n Email: {user[0].email}"
        notification_admin_by_mail(affair_admin, message_admin)

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
        id_user = user[0].id # obtenemos el id del usuario

        # Enviamos el codigo de verificación para cambiar contraseña al usuario
        mail = create_mail(user[0].email, "RECUPERACIÓN DE CUENTA", "users/send-verification.html", {"validation_code": codigo, "message_context": "Necesitas este código para cambiar la contraseña."})
        mail.send(fail_silently=False)

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
        new_password = self.request.POST.get('password2')
        user.set_password(new_password)
        user.save()
        messages.add_message(request=self.request, level=messages.SUCCESS, message='Se ha cambiado la contraseña, inicie sesión.')

        # Enviamos un correo notificando al email del administrador que se ha creado una cuenta de usuario.
        affair_admin = "USUARIO HA CAMBIADO SU CONTRASEÑA."
        message_admin = f"Un usuario ha cambiado su contraseña. \n\n ID: {user.id} \n Name: {user.name} {user.last_name} \n Email: {user.email}"
        notification_admin_by_mail(affair_admin, message_admin)

        return super(ChangePasswordView, self).form_valid(form)
        