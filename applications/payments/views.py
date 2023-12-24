from datetime import datetime
import stripe
from django.views.generic import View, TemplateView, DetailView
from django.http.response import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
# importamos los modelos
from .models import TraderPayment, VpsPayment
from applications.users.models import User
from applications.vps.models import AccountMt5
#importamos funciones
from .functions import enable_reconnection_mt5, expiration_vps
from .paypal import create_order_paypal, create_renewal_order_paypal, capture_order_paypal
from .stripe import create_order_stripe, create_renewal_order_stripe
from applications.vps.functions import active_buttons_time
from fortuna_303.settings.base import get_secret
from applications.users.function import notification_admin_by_mail, create_mail
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
            details = capture_order_paypal(token)
            if details:
                # Verificamos si es un primer pago del servicio de VPS y COPYTRADING
                if details['custom_id'] == 'first_payment':
                    User.objects.filter(id=request.user.id).update(subscriber=True)
                    payment = VpsPayment.objects.save_payment_vps(details['amount'], user, 'Paypal', details['id'])
                    messages.add_message(request=self.request, level=messages.SUCCESS, message='Su pago fue procesado exitosamente.')
                    
                    #Enviar un correo del importe al usuario cuando el pago haya sido procesado con exito.
                    mail = create_mail(user.email, f"FORTUNA 303 IMPORTE DE VPS+COPYTRADING #{payment.id}", "payments/invoice.html", {"id_payment": payment.id, "name": user.name +" "+ user.last_name, "status": payment.status, "service": "VPS+COPYTRADING", "created_date": payment.created_date, "expiration": payment.expiration, "price": payment.total})
                    mail.send(fail_silently=False)
                    #Enviar un correo de notificacion al admin cuando el pago haya sido procesado con exito.
                    affair_admin = "NUEVO PAGO DE VPS+COPYTRADING RECIBIDO."
                    message_admin = f"EL pago recibido es del usario:\n\n ID: {user.id}\n name: {user.name} {user.last_name}\n correo: {user.email}\n\nLos datos del importe:\n\n ID: {payment.id}\n Created date: {payment.created_date}\n Expiration: {payment.expiration}\n Total: {payment.total}\n Status: {payment.status}\n Method: {payment.payment_method}\n ID_Transaction: {payment.transaction_id}"
                    notification_admin_by_mail(affair_admin, message_admin)

                else:
                    # Convertimos el string del valor de custom_id a un dict
                    dictionary = eval((details['custom_id']))
                    
                    # Verificamos si es una renovacion del servicio VPS o un pago para el trader
                    if 'vps' in dictionary:
                        id_payment = dictionary['vps']
                        payment = VpsPayment.objects.update_payment_vps(id_payment, 'Paypal', details['id'])
                        messages.add_message(request=self.request, level=messages.SUCCESS, message='Su pago fue procesado exitosamente.')
                        
                        #Enviar un correo del importe al usuario cuando el pago haya sido procesado con exito.
                        mail = create_mail(user.email, f"FORTUNA 303 IMPORTE DE VPS+COPYTRADING #{payment.id}", "payments/invoice.html", {"id_payment": payment.id, "name": user.name +" "+ user.last_name, "status": payment.status, "service": "VPS+COPYTRADING", "created_date": payment.created_date, "expiration": payment.expiration, "price": payment.total})
                        mail.send(fail_silently=False)
                        #Enviar un correo de notificacion al admin cuando el pago haya sido procesado con exito.
                        affair_admin = "NUEVO PAGO DE VPS+COPYTRADING RECIBIDO."
                        message_admin = f"EL pago recibido es del usario:\n\n ID: {user.id}\n name: {user.name} {user.last_name}\n correo: {user.email}\n\nLos datos del importe:\n\n ID: {payment.id}\n Created date: {payment.created_date}\n Expiration: {payment.expiration}\n Total: {payment.total}\n Status: {payment.status}\n Method: {payment.payment_method}\n ID_Transaction: {payment.transaction_id}"
                        notification_admin_by_mail(affair_admin, message_admin)

                        # Verificamos si la cuenta esta desconectada
                        try:
                            account_mt5 = AccountMt5.objects.get(id_user=user.id)
                            if account_mt5.status == '0':
                                trader_payment = TraderPayment.objects.unpaid_trader_payments(user.id)
                                vps_payment = VpsPayment.objects.unpaid_vps_payments(user.id)
                                # Conectamos la cuenta mt5 de nuevo a metaapi en caso de que este desconectado y este al dia con los pagos
                                if trader_payment == False and vps_payment == False:
                                    enable_reconnection_mt5(user.id, self.request)
                        except Exception as err:
                            messages.add_message(request=self.request, level=messages.WARNING, message='Hubo un error al intentar habilitar la reconexión de la cuenta mt5.')
                            print("Hubo un error al intentar habilitar la reconexión de la cuenta mt5 del usuario a metaapi. ", err)

                    elif 'trader' in dictionary:
                        id_payment = dictionary['trader']
                        payment = TraderPayment.objects.update_payment_trader(id_payment, 'Paypal', details['id'])
                        messages.add_message(request=self.request, level=messages.SUCCESS, message='Su pago fue procesado exitosamente.')
                        
                        #Enviar un correo del importe al usuario cuando el pago haya sido procesado con exito.
                        mail = create_mail(user.email, f"FORTUNA 303 IMPORTE DE GESTIÓN DE CUENTAS MT5 #{payment.id}", "payments/invoice.html", {"id_payment": payment.id, "name": user.name +" "+ user.last_name, "status": payment.status, "service": "GESTIÓN DE CUENTAS MT5", "created_date": payment.created_date, "expiration": payment.expiration, "id_management": payment.id_management.id, "price": payment.total})
                        mail.send(fail_silently=False)
                        #Enviar un correo de notificacion al admin cuando el pago haya sido procesado con exito.
                        affair_admin = "NUEVO PAGO DE GESTIÓN DE CUENTAS MT5 RECIBIDO."
                        message_admin = f"EL pago recibido es del usario:\n\n ID: {user.id}\n name: {user.name} {user.last_name}\n correo: {user.email}\n\nLos datos del importe:\n\n ID: {payment.id}\n Created date: {payment.created_date}\n Expiration: {payment.expiration}\n Id_management: {payment.id_management.id}\n Total: {payment.total}\n Status: {payment.status}\n Method: {payment.payment_method}\n ID_Transaction: {payment.transaction_id}"
                        notification_admin_by_mail(affair_admin, message_admin)
                        
                        # Verificamos si la cuenta esta desconectada
                        try: 
                            account_mt5 = AccountMt5.objects.get(id_user=user.id)
                    
                            if account_mt5.status == '0':
                                trader_payment = TraderPayment.objects.unpaid_trader_payments(user.id)
                                vps_payment = VpsPayment.objects.unpaid_vps_payments(user.id)
                                # Conectamos la cuenta mt5 de nuevo a metaapi en caso de que este desconectado y este al dia con los pagos
                                if trader_payment == False and vps_payment == False:
                                    enable_reconnection_mt5(user.id, self.request)
                        except Exception as err:
                            messages.add_message(request=self.request, level=messages.WARNING, message='Hubo un error al intentar habilitar la reconexión de la cuenta mt5.')
                            print("Hubo un error al intentar habilitar la reconexión de la cuenta mt5 del usuario a metaapi. ", err)

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

        detail_payment = {
            'now': now,
            'expiration': expiration, 
            'price': price,
            'description': description,
        }
        
        context['detail_payment'] = detail_payment

        # Verificando la fecha y hora que deben estar habilitados los botones de agregar y borrar cuenta mt5
        context['active'] = active_buttons_time()
        return context 


class VpsPaymentRenewalView(LoginRequiredMixin, DetailView):
    template_name = 'payments/vps-payment-renewal.html'
    model = VpsPayment
    context_object_name = 'detail_payment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        id_payment = self.kwargs['pk']
        context['id_payment'] = id_payment
        return context


class TraderPaymentRenewalView(LoginRequiredMixin, DetailView):
    template_name = 'payments/trader-method-payment.html'
    model = TraderPayment
    context_object_name = 'detail_payment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        id_payment = self.kwargs['pk']
        context['id_payment'] = id_payment
        return context


class CheckoutSessionView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):

        if 'payment-method' in request.POST and 'terms-and-conditions' in request.POST:
            type = request.POST['type']
            payment_method = request.POST['payment-method']
            level = User.objects.get(id=request.user.id).level
            price = level.price
            if type == 'first-payment':
                description = "Servicio mensual vps para metatrader 5 y uso del sistema copytrading."
            
                if payment_method == 'paypal':
                    link_payment = create_order_paypal(amount=price, description=description)
                elif payment_method == 'stripe':
                    link_payment = create_order_stripe(id_user=request.user.id, amount=price, description=description)

            elif type == 'renewal-vps':
                id_payment = request.POST['id-payment']
                # validamos el id_pyment para evitar equivocaciones
                register = VpsPayment.objects.filter(id=id_payment)
                if register[0].id_user.id == request.user.id:
                    if register[0].status == 'Pagar':
                        amount = register[0].total
                        description = f"Renovación del servicio mensual de vps para metarader 5 y uso del sistema copytrading."

                if payment_method == 'paypal':
                    link_payment = create_renewal_order_paypal(case="vps", payment_id=id_payment, amount=amount, description=description)
                elif payment_method == 'stripe':
                    link_payment = create_renewal_order_stripe(id_user=request.user.id, case="vps", payment_id=id_payment, amount=amount, description=description)

            elif type == 'renewal-trader':
                id_payment = request.POST['id-payment']
                # validamos el id_pyment para evitar equivocaciones
                register = TraderPayment.objects.filter(id=id_payment)
                if register[0].id_user.id == request.user.id:
                    if register[0].status == 'Pagar':
                        amount = register[0].total
                        description = f"Gestión de cuenta de metatrader5 del {register[0].created_date} al {register[0].expiration}"

                if payment_method == 'paypal':
                    link_payment = create_renewal_order_paypal(case="trader", payment_id=id_payment, amount=amount, description=description)
                elif payment_method == 'stripe':
                    link_payment = create_renewal_order_stripe(id_user=request.user.id, case="trader", payment_id=id_payment, amount=amount, description=description)

            return HttpResponseRedirect(link_payment)
        else:
            match request.POST['type']:
                case 'first-payment':
                    messages.add_message(request=self.request, level=messages.ERROR, message='Debe elegir un método de pago y aceptar los términos y condiciones.')
                    return HttpResponseRedirect(reverse('payments_app:first_payment'))
                case 'renewal-vps':
                    id_payment = request.POST['id-payment']
                    messages.add_message(request=self.request, level=messages.ERROR, message='Debe elegir un método de pago y aceptar los términos y condiciones.')
                    return HttpResponseRedirect(reverse('payments_app:vps_payment_renewal', kwargs={'pk':id_payment}))
                case 'renewal-trader':
                    id_payment = request.POST['id-payment']
                    messages.add_message(request=self.request, level=messages.ERROR, message='Debe elegir un método de pago y aceptar los términos y condiciones.')
                    return HttpResponseRedirect(reverse('payments_app:trader_payment', kwargs={'pk':id_payment}))


class WebhookStripeView(View):
    
    def post(self, request, *args, **kwargs):
        endpoint_secret = get_secret('STRIPE_ENDPOINT_SECRET')
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)
        except Exception as err:
            # cualquier error
            print("Error proveniente de stripe.Webhook.construct_event(): ", err)
            return HttpResponse(status=400)

        # Handle the checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            # creamos el importe del primer pago vps con la informacion relevante
            price = session["amount_total"] / 100
            transaction_id = session["payment_intent"]
            id_user = session["metadata"]["id_user"]
            custom_id = session["metadata"]["custom_id"]
            user = User.objects.get(id=id_user)
            
            # Verificamos si es un primer pago del servicio de VPS y COPYTRADING
            if custom_id == 'first_payment':
                User.objects.filter(id=id_user).update(subscriber=True)
                payment = VpsPayment.objects.save_payment_vps(price, user, 'Stripe', transaction_id)
                messages.add_message(request=self.request, level=messages.SUCCESS, message='Su pago fue procesado exitosamente.')
                #Enviar un correo del importe al usuario cuando el pago haya sido procesado con exito.
                mail = create_mail(user.email, f"FORTUNA 303 IMPORTE DE VPS+COPYTRADING #{payment.id}", "payments/invoice.html", {"id_payment": payment.id, "name": user.name +" "+ user.last_name, "status": payment.status, "service": "VPS+COPYTRADING", "created_date": payment.created_date, "expiration": payment.expiration, "price": payment.total})
                mail.send(fail_silently=False)
                #Enviar un correo de notificacion al admin cuando el pago haya sido procesado con exito.
                affair_admin = "NUEVO PAGO DE VPS+COPYTRADING RECIBIDO."
                message_admin = f"EL pago recibido es del usario:\n\n ID: {user.id}\n name: {user.name} {user.last_name}\n correo: {user.email}\n\nLos datos del importe:\n\n ID: {payment.id}\n Created date: {payment.created_date}\n Expiration: {payment.expiration}\n Total: {payment.total}\n Status: {payment.status}\n Method: {payment.payment_method}\n ID_Transaction: {payment.transaction_id}"
                notification_admin_by_mail(affair_admin, message_admin)           
            
            # Verificamos si es una renovacion del servicio VPS o un pago para el trader
            elif custom_id == 'vps':
                id_payment = session["metadata"]["payment_id"]

                payment = VpsPayment.objects.update_payment_vps(id_payment, 'Stripe', transaction_id)
                messages.add_message(request=self.request, level=messages.SUCCESS, message='Su pago fue procesado exitosamente.')
                
                #Enviar un correo del importe al usuario cuando el pago haya sido procesado con exito.
                mail = create_mail(user.email, f"FORTUNA 303 IMPORTE DE VPS+COPYTRADING #{payment.id}", "payments/invoice.html", {"id_payment": payment.id, "name": user.name +" "+ user.last_name, "status": payment.status, "service": "VPS+COPYTRADING", "created_date": payment.created_date, "expiration": payment.expiration, "price": payment.total})
                mail.send(fail_silently=False)
                #Enviar un correo de notificacion al admin cuando el pago haya sido procesado con exito.
                affair_admin = "NUEVO PAGO DE VPS+COPYTRADING RECIBIDO."
                message_admin = f"EL pago recibido es del usario:\n\n ID: {user.id}\n name: {user.name} {user.last_name}\n correo: {user.email}\n\nLos datos del importe:\n\n ID: {payment.id}\n Created date: {payment.created_date}\n Expiration: {payment.expiration}\n Total: {payment.total}\n Status: {payment.status}\n Method: {payment.payment_method}\n ID_Transaction: {payment.transaction_id}"
                notification_admin_by_mail(affair_admin, message_admin)
                
                # Verificamos si la cuenta esta desconectada
                try:
                    account_mt5 = AccountMt5.objects.get(id_user=id_user)
                    if account_mt5.status == '0':
                        trader_payment = TraderPayment.objects.unpaid_trader_payments(id_user)
                        vps_payment = VpsPayment.objects.unpaid_vps_payments(id_user)

                        # Habilitamos la reconexión de la cuenta mt5 a metaapi en caso de que este desconectado y este al dia con los pagos.
                        if trader_payment == False and vps_payment == False:
                            enable_reconnection_mt5(id_user, self.request)
                except Exception as err:
                    messages.add_message(request=self.request, level=messages.WARNING, message='Hubo un error al intentar habilitar la reconexión de la cuenta mt5.')
                    print("Hubo un error al intentar habilitar la reconexión de la cuenta mt5 del usuario a metaapi. ", err)

            elif custom_id == 'trader':
                id_payment = session["metadata"]["payment_id"]
                payment = TraderPayment.objects.update_payment_trader(id_payment, 'Stripe', transaction_id)
                messages.add_message(request=self.request, level=messages.SUCCESS, message='Su pago fue procesado exitosamente.')
                
                #Enviar un correo del importe al usuario cuando el pago haya sido procesado con exito.
                mail = create_mail(user.email, f"FORTUNA 303 IMPORTE DE GESTIÓN DE CUENTAS MT5 #{payment.id}", "payments/invoice.html", {"id_payment": payment.id, "name": user.name +" "+ user.last_name, "status": payment.status, "service": "GESTIÓN DE CUENTAS MT5", "created_date": payment.created_date, "expiration": payment.expiration, "id_management": payment.id_management.id, "price": payment.total})
                mail.send(fail_silently=False)
                #Enviar un correo de notificacion al admin cuando el pago haya sido procesado con exito.
                affair_admin = "NUEVO PAGO DE GESTIÓN DE CUENTAS MT5 RECIBIDO."
                message_admin = f"EL pago recibido es del usario:\n\n ID: {user.id}\n name: {user.name} {user.last_name}\n correo: {user.email}\n\nLos datos del importe:\n\n ID: {payment.id}\n Created date: {payment.created_date}\n Expiration: {payment.expiration}\n Id_management: {payment.id_management.id}\n Total: {payment.total}\n Status: {payment.status}\n Method: {payment.payment_method}\n ID_Transaction: {payment.transaction_id}"
                notification_admin_by_mail(affair_admin, message_admin)
                
                # Verificamos si la cuenta esta desconectada
                try: 
                    account_mt5 = AccountMt5.objects.get(id_user=id_user)
                    if account_mt5.status == '0':
                        trader_payment = TraderPayment.objects.unpaid_trader_payments(id_user)
                        vps_payment = VpsPayment.objects.unpaid_vps_payments(id_user)

                        # Habilitamos la reconexión de la cuenta mt5 a metaapi en caso de que este desconectado y este al dia con los pagos.
                        if trader_payment == False and vps_payment == False:
                            enable_reconnection_mt5(id_user, self.request)
                except Exception as err:
                    messages.add_message(request=self.request, level=messages.WARNING, message='Hubo un error al intentar habilitar la reconexión de la cuenta mt5.')
                    print("Hubo un error al intentar habilitar la reconexión de la cuenta mt5 del usuario a metaapi. ", err)

        return HttpResponse(status=200)
