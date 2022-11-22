from datetime import datetime
import asyncio
from django.views.generic import TemplateView, DetailView
from django.http import JsonResponse
#
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.paginator import Paginator
# importamos los modelos
from .models import TraderPayment, VpsPayment
from applications.users.models import User
from applications.vps.models import AccountMt5
#importamos funciones 
from applications.payments.functions import (create_order, create_renewal_order, capture_order, 
expiration_vps, reconnect_mt5_account)
# Create your views here.

class PaymentsView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/payments.html'
    login_url = reverse_lazy('users_app:user_login')

    def get(self, request, *args, **kwargs):
        # Traemos la instancia del usuario relacionado a la nueva factura
        user = User.objects.get(id=request.user.id)

        # Recogemos las variables de la url que nos devuelve paypal al cancelar o aprobar el pago
        token = self.request.GET.get('token')
        if token:
            details = capture_order(token)
            if details:
                # Verificamos si es un primer pago del servicio de VPS y COPYTRADING
                if details['custom_id'] == 'first_payment':
                    User.objects.filter(id=request.user.id).update(subscriber=True)
                    VpsPayment.objects.save_payment_vps(details['amount'], user, 'Paypal', details['id'])
                else:
                    # Convertimos el string del valor de custom_id a un dict
                    dictionary = eval((details['custom_id']))
                    
                    # Verificamos si es una renovacion del servicio VPS o un pago para el trader
                    if 'vps' in dictionary:
                        id_payment = dictionary['vps']
                        VpsPayment.objects.update_payment_vps(id_payment, 'Paypal', details['id'])
                        # Verificamos si la cuenta esta desconectada
                        account_mt5 = AccountMt5.objects.get(id_user=user.id)
                        if account_mt5.status == '0':
                            trader_payment = TraderPayment.objects.unpaid_trader_payments(user.id)
                            vps_payment = VpsPayment.objects.unpaid_vps_payments(user.id)
                            # Conectamos la cuenta mt5 de nuevo a metaapi en caso de que este desconectado y este al dia con los pagos
                            if trader_payment == False and vps_payment == False:
                                reconnect_mt5_account(user.id, self.request)

                    elif 'trader' in dictionary:
                        id_payment = dictionary['trader']
                        TraderPayment.objects.update_payment_trader(id_payment, 'Paypal', details['id'])
                        # Verificamos si la cuenta esta desconectada
                        account_mt5 = AccountMt5.objects.get(id_user=user.id)
                        if account_mt5.status == '0':
                            trader_payment = TraderPayment.objects.unpaid_trader_payments(user.id)
                            vps_payment = VpsPayment.objects.unpaid_vps_payments(user.id)
                            # Conectamos la cuenta mt5 de nuevo a metaapi en caso de que este desconectado y este al dia con los pagos
                            if trader_payment == False and vps_payment == False:
                                reconnect_mt5_account(user.id, self.request)

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


    def get_context_data(self, **kwargs):
        context = super(PaymentsView, self).get_context_data(**kwargs)

        id_user = self.request.user.id # sacamos el id del usuario

        vps_payment = VpsPayment.objects.vps_payments_by_user(id_user)
        paginator1 = Paginator(vps_payment, 10)
        page = self.request.GET.get('page')
        context['vps_payments'] = paginator1.get_page(page)
        context['vps_payments_pages'] = paginator1.num_pages

        trader_payment = TraderPayment.objects.trader_payments_by_user(id_user)
        paginator2 = Paginator(trader_payment, 10)
        page2 = self.request.GET.get('page2')
        context['trader_payments'] = paginator2.get_page(page2)
        context['trader_payments_pages'] = paginator2.num_pages

        # Agregamos un range para que se muestre una cantidad especifica de botones en el paginador en html.
        context['range'] = range(1, 9)

        return context

    # Enviamos los datos a cambiar con fecth
    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('page'):
            data = list(context['vps_payments'].object_list.values())
            for register in data:
                register.pop('id_user_id') # borrando dato innecesario
                register.pop('transaction_id') # borrando dato innecesario
                register.pop('payment_method') # borrando dato innecesario
            return JsonResponse({'vps_payments': data, 'total_pages': context['vps_payments_pages']})

        elif self.request.GET.get('page2'):
            data = list(context['trader_payments'].object_list.values())
            for register in data:
                register.pop('id_user_id') # borrando dato innecesario
                register.pop('transaction_id') # borrando dato innecesario
                register.pop('payment_method') # borrando dato innecesario
            return JsonResponse({'trader_payments': data, 'total_pages': context['trader_payments_pages']})
        
        else:
            response_kwargs.setdefault('content_type', self.content_type)
            return self.response_class(
                request=self.request,
                template=self.get_template_names(),
                context=context,
                using=self.template_engine,
                **response_kwargs
            )


class FirstPaymentView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/first-payment.html'

    def get_context_data(self, **kwargs):
        context = super(FirstPaymentView, self).get_context_data(**kwargs)
        now = datetime.now()
        expiration = expiration_vps(now)
        level = User.objects.get(id=self.request.user.id).level
        price = level.price

        description = "Servicio mensual vps para metatrader 5 y uso del sistema copytrading."

        link = create_order(amount=price, description=description)

        detail_payment = {'now': now, 'expiration': expiration, 'price': price, 'link_payment': link}
        context['detail_payment'] = detail_payment
        return context 


class VpsPaymentRenewalView(LoginRequiredMixin, DetailView):
    template_name = 'payments/vps-payment-renewal.html'
    model = VpsPayment
    context_object_name = 'detail_payment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        id_payment = self.kwargs['pk']
        register = VpsPayment.objects.filter(id=id_payment)
        amount = register[0].total
        description = "Renovación del servicio mensual de vps para metarader 5 y uso del sistema copytrading."
        
        link = create_renewal_order(case="vps", payment_id=id_payment, amount=amount, description=description)
        context['link_payment'] = link

        return context


class TraderPaymentRenewalView(LoginRequiredMixin, DetailView):
    template_name = 'payments/trader-method-payment.html'
    model = TraderPayment
    context_object_name = 'detail_payment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        id_payment = self.kwargs['pk']
        register = TraderPayment.objects.filter(id=id_payment)
        amount = register[0].total
        description = f"Gestión de cuenta de metatrader5 del {register[0].created_date} al {register[0].expiration}"
        
        link = create_renewal_order(case="trader", payment_id=id_payment, amount=amount, description=description)
        context['link_payment'] = link

        return context
