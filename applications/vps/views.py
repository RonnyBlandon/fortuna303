import asyncio
from datetime import datetime, date
from email.policy import default
from django.views.generic import View, TemplateView, DeleteView, FormView
# importar formularios
from .forms import CreateAccountMt5Form
#
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib import messages
#  importar modelos
from applications.vps.models import AccountMt5, AccountManagement, AccountOperation
from applications.users.models import User
from applications.payments.models import VpsPayment, TraderPayment
# imortar funciones
from .functions import trading_history, active_buttons_time
from .metaapi import create_server_mt5, configure_copyfactory, delete_server_mt5

# Create your views here.

class PanelUserView(LoginRequiredMixin, TemplateView):
    template_name = 'vps/panel-user.html'
    login_url = reverse_lazy('users_app:user_login')

    def get_context_data(self, **kwargs):
        context = super(PanelUserView, self).get_context_data(**kwargs)
        context['form_mt5'] = CreateAccountMt5Form
        context['accounts'] = AccountMt5.objects.get_account_mt5(self.request.user.id)

        # Verificando la fecha y hora que deben estar habilitados los botones de agregar y borrar cuenta mt5
        context['active'] = active_buttons_time()

        # Paginando los registros de la tabla ganancias semanales
        list_manamegent = AccountManagement.objects.get_account_management(self.request.user.id)
        paginator1 = Paginator(list_manamegent, 10)
        page = self.request.GET.get('page')
        context['profits'] = paginator1.get_page(page)
        
        # Paginando los trades de la cuenta madre
        data = trading_history()
        if data == None:
            context['operations'] = []
        else:
            list_trades = data
            paginator2 = Paginator(list_trades, 10)
            page2 = self.request.GET.get('page2')
            context['operations'] = paginator2.get_page(page2)

        # Paginando los registros de la tabla de historial de operaciones de la cuenta mt5 del usuario
        if context['accounts'].exists():
            list_operations = AccountOperation.objects.get_account_operations(context['accounts'][0].id)
            paginator3 = Paginator(list_operations, 10)
            page3 = self.request.GET.get('page3')
            context['operations2'] = paginator3.get_page(page3)
        
        return context

    # Enviamos los datos a cambiar con fecth
    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('page'):
            data = list(context['profits'].object_list.values())
            for register in data:
                register.pop('id_user_id') # borrando dato innecesario
            return JsonResponse({'profits': data})

        elif self.request.GET.get('page2'):
            data = list(context['operations'])
            return JsonResponse({'operations': data})

        elif self.request.GET.get('page3'):
            data = list(context['operations2'].object_list.values())
            for register in data:
                register.pop('id_account_mt5_id') # borrando dato innecesario
                register.pop('id') # borrando dato innecesario
            return JsonResponse({'operations2': data})
        
        else:
            response_kwargs.setdefault('content_type', self.content_type)
            return self.response_class(
                request=self.request,
                template=self.get_template_names(),
                context=context,
                using=self.template_engine,
                **response_kwargs
            )


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


class ConfirmationUnsubscribeView(LoginRequiredMixin, TemplateView):
    template_name = 'vps/confirmation-unsubscribe.html'


class UnsubscriberView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        # actualizamos el campo subscriber del usuario a False
        User.objects.filter(id=request.user.id).update(subscriber=False)

        # Borramos la cuenta en metaapi 
        accounts_mt5 = AccountMt5.objects.get_account_mt5(request.user.id)
        if accounts_mt5:
            account_mt5 = accounts_mt5[0]
            id_client_metaapi = account_mt5.id_client_metaapi

            #asyncio.run(delete_server_mt5(id_client_metaapi))

            # Borramos la cuenta mt5 en la base de datos local
            account_mt5.delete()
        
        # Actualizamos los pagos que estan en estado de "Pagar" a Cancelado
        vps_payments = VpsPayment.objects.vps_payments_by_status('Pagar')

        if vps_payments:
            vps_payments.update(status="Cancelado")

        # Redirigimos a la misma pagina de perfil de usuario
        return HttpResponseRedirect(
            reverse('vps_app:panel_user')
        )
