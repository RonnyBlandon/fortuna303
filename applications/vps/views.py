import asyncio
from email import message
from django.views.generic import TemplateView, DeleteView, FormView
# importar formularios
from .forms import CreateAccountMt5Form
#
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
#  importar modelos
from applications.vps.models import AccountMt5, AccountManagement
# imortar funciones
from .functions import trading_history
from .metaapi import create_server_mt5, configure_copyfactory, delete_server_mt5

# Create your views here.

class PanelUserView(LoginRequiredMixin, TemplateView):
    template_name = 'vps/panel-user.html'
    paginate_by = 10
    ordering = 'id'
    login_url = reverse_lazy('users_app:user_login')

    def get_context_data(self, **kwargs):
        context = super(PanelUserView, self).get_context_data(**kwargs)
        context['accounts'] = AccountMt5.objects.get_account_mt5(self.request.user.id)
        context['profit'] = AccountManagement.objects.all()
        context['form_mt5'] = CreateAccountMt5Form
        
        data = trading_history()
        if data == None:
            context['operations'] = []
        else:
            context['operations'] = data
        
        return context


class CreateAccounMt5View(LoginRequiredMixin, FormView):
    form_class = CreateAccountMt5Form
    success_url = reverse_lazy('vps_app:panel_user')

    def form_valid(self, form):
        id_user = self.request.user
        name = self.request.user.name
        last_name = self.request.user.last_name
        login = form.cleaned_data['login']
        password = form.cleaned_data['password']
        server = form.cleaned_data['server']
        full_name = name + ' ' + last_name
        # creamos el servidor y suscribimos la nueva cuenta en MetaApi
        account = asyncio.run(create_server_mt5(full_name, login, password, server))
        # Guardar en la base de datos local luego de confirmar la creacion y suscripcion de la nueva cuenta.
        if account:
            suscriber = asyncio.run(configure_copyfactory(account['id']))

            if suscriber.status_code == 204:
                status = '1'
                AccountMt5.objects.create_account_mt5(
                    login,
                    password,
                    server,
                    account['id'],
                    account['access_token'],
                    status,
                    id_user
                )
            messages.add_message(request=self.request, level=messages.SUCCESS, message='La cuenta ha sido creada y conectada con éxito.')
        else:
            messages.add_message(request=self.request, level=messages.ERROR, message='Fallo en la creación y conexión de la cuenta, los datos ingresados son incorrectos.')
            HttpResponseRedirect(
                reverse('vps_app:panel_user')
            )

        return super(CreateAccounMt5View, self).form_valid(form)


class DeleteAccountMt5View(LoginRequiredMixin, DeleteView):
    template_name = 'vps/delete-account-mt5.html'
    model = AccountMt5
    success_url = reverse_lazy('vps_app:panel_user')
    
    def post(self, request, *args, **kwargs):
        accounts_mt5 = AccountMt5.objects.get_account_mt5(self.request.user.id)
        account_mt5 = accounts_mt5[0]
        id_client_metaapi = account_mt5.id_client_metaapi

        asyncio.run(delete_server_mt5(id_client_metaapi))

        messages.add_message(request=self.request, level=messages.SUCCESS, message='La cuenta se ha eliminado con éxito.')

        return super(DeleteAccountMt5View, self).post(request, *args, **kwargs)
