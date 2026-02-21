from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import stripe
from django.views.generic import View, TemplateView
from django.http.response import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from .models import TraderPayment, VpsPayment, ForexPlanPayment, StockPlanPayment
from applications.users.models import User
from applications.vps.models import AccountMt5
from .functions import enable_reconnection_mt5, expiration_vps
from .paypal import create_order_paypal, create_renewal_order_paypal, capture_order_paypal
from .stripe import create_order_stripe, create_renewal_order_stripe
from fortuna_303.settings.base import get_secret
from applications.users.function import notification_admin_by_mail, create_mail


PAYMENT_CONFIG = {
    'first-payment': {
        'title': 'Detalles de pago - VPS + Copytrading',
        'price_source': 'level',
        'description': 'Servicio mensual vps para metatrader 5 y uso del sistema copytrading.',
        'expiration_type': 'monthly',
        'custom_id': 'first_payment',
        'requires_model': False,
    },
    'renewal-vps': {
        'title': 'Detalles de pago - Renovacion VPS',
        'model': VpsPayment,
        'price_source': 'payment',
        'description': 'Renovacion mensual - VPS + Copytrading',
        'custom_id_prefix': 'vps',
    },
    'renewal-trader': {
        'title': 'Detalles de pago - Gestion MT5',
        'model': TraderPayment,
        'price_source': 'payment',
        'custom_id_prefix': 'trader',
    },
    'forex-plan': {
        'title': 'Detalles de pago - Plan Forex',
        'price_source': 'plan_type',
        'prices': {'inicio': 87, 'elevate': 97},
        'descriptions': {
            'inicio': 'Paquete Inicio - Senales automatizadas generadas por bot de trading.',
            'elevate': 'Paquete Elevate - Senales enviadas por trader profesional.'
        },
        'expiration_type': 'monthly',
        'custom_id': 'forex',
    },
    'stock-plan': {
        'title': 'Detalles de pago - Plan Bolsa de Valores',
        'price_source': 'fixed',
        'price': 797,
        'description': 'Paquete Anual - Servicio anual de senales para bolsa de valores.',
        'expiration_type': 'yearly',
        'custom_id': 'stock',
        'requires_model': False,
    },
    'renewal-forex': {
        'title': 'Detalles de pago - Renovacion Plan Forex',
        'model': ForexPlanPayment,
        'price_source': 'payment',
        'custom_id_prefix': 'forex',
        'descriptions': {
            'inicio': 'Renovacion mensual - Plan Forex Inicio',
            'elevate': 'Renovacion mensual - Plan Forex Elevate'
        }
    },
    'renewal-stock': {
        'title': 'Detalles de pago - Renovacion Plan Stock',
        'model': StockPlanPayment,
        'price_source': 'payment',
        'custom_id_prefix': 'stock',
        'description': 'Renovacion anual - Plan Stock',
    },
}


class PaymentsView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/payments.html'
    login_url = reverse_lazy('users_app:user_login')

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        token = self.request.GET.get('token')
        
        if token:
            details = capture_order_paypal(token)
            if details:
                self._process_paypal_payment(details, user)
        
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def _process_paypal_payment(self, details, user):
        custom_id = details['custom_id']
        
        if custom_id == 'first_payment':
            self._process_first_payment(details, user)
        else:
            try:
                dictionary = eval(custom_id)
                if 'vps' in dictionary:
                    self._process_vps_renewal(dictionary, details, user)
                elif 'trader' in dictionary:
                    self._process_trader_payment(dictionary, details, user)
                elif 'forex' in dictionary:
                    self._process_forex_payment(dictionary, details, user)
                elif 'stock' in dictionary:
                    self._process_stock_payment(dictionary, details, user)
            except:
                pass

    def _process_first_payment(self, details, user):
        User.objects.filter(id=user.id).update(subscriber=True)
        payment = VpsPayment.objects.save_payment_vps(details['amount'], user, 'Paypal', details['id'])
        messages.add_message(request=self.request, level=messages.SUCCESS, message='Su pago fue procesado exitosamente.')
        self._send_payment_emails(user, payment, 'VPS+COPYTRADING', 'VPS+COPYTRADING')

    def _process_vps_renewal(self, dictionary, details, user):
        id_payment = dictionary['vps']
        payment = VpsPayment.objects.update_payment_vps(id_payment, 'Paypal', details['id'])
        messages.add_message(request=self.request, level=messages.SUCCESS, message='Su pago fue procesado exitosamente.')
        self._send_payment_emails(user, payment, 'VPS+COPYTRADING', 'VPS+COPYTRADING')
        self._check_mt5_reconnection(user)

    def _process_trader_payment(self, dictionary, details, user):
        id_payment = dictionary['trader']
        payment = TraderPayment.objects.update_payment_trader(id_payment, 'Paypal', details['id'])
        messages.add_message(request=self.request, level=messages.SUCCESS, message='Su pago fue procesado exitosamente.')
        self._send_payment_emails(user, payment, 'GESTION DE CUENTAS MT5', 'GESTION DE CUENTAS MT5', include_management=True)
        self._check_mt5_reconnection(user)

    def _process_forex_payment(self, dictionary, details, user):
        forex_value = dictionary.get('forex')
        plan_name = "Paquete Inicio"
        
        if forex_value is True:
            plan_type = dictionary.get('plan_type', 'inicio')
            plan_name = "Paquete Inicio" if plan_type == 'inicio' else "Paquete Elevate"
            payment = ForexPlanPayment.objects.save_payment_forex(details['amount'], user, 'Paypal', details['id'], plan_type)
        else:
            id_payment = int(forex_value)
            payment = ForexPlanPayment.objects.update_payment_forex(id_payment, 'Paypal', details['id'])
            plan_name = "Paquete Inicio" if payment.plan_type == 'inicio' else "Paquete Elevate"
        
        messages.add_message(request=self.request, level=messages.SUCCESS, message='Su pago fue procesado exitosamente.')
        self._send_payment_emails(user, payment, f'FOREX PLAN - {plan_name}', f'FOREX PLAN - {plan_name}')

    def _process_stock_payment(self, dictionary, details, user):
        stock_value = dictionary.get('stock')
        
        if stock_value is True:
            payment = StockPlanPayment.objects.save_payment_stock(details['amount'], user, 'Paypal', details['id'])
        else:
            id_payment = int(stock_value)
            payment = StockPlanPayment.objects.update_payment_stock(id_payment, 'Paypal', details['id'])
        
        messages.add_message(request=self.request, level=messages.SUCCESS, message='Su pago fue procesado exitosamente.')
        self._send_payment_emails(user, payment, 'STOCK PLAN - PAQUETE ANUAL', 'STOCK PLAN - PAQUETE ANUAL')

    def _send_payment_emails(self, user, payment, service_name, service_admin, include_management=False):
        context = {
            "id_payment": payment.id,
            "name": user.name + " " + user.last_name,
            "status": payment.status,
            "service": service_name,
            "created_date": payment.created_date,
            "expiration": payment.expiration,
            "price": payment.total
        }
        if include_management:
            context["id_management"] = payment.id_management.id
            
        mail = create_mail(user.email, f"FORTUNA 303 IMPORTE DE {service_name} #{payment.id}", "payments/invoice.html", context)
        mail.send(fail_silently=False)
        
        affair_admin = f"NUEVO PAGO DE {service_admin} RECIBIDO."
        message_admin = f"EL pago recibido es del usario:\n\n ID: {user.id}\n name: {user.name} {user.last_name}\n correo: {user.email}\n\nLos datos del importe:\n\n ID: {payment.id}\n Created date: {payment.created_date}\n Expiration: {payment.expiration}\n Total: {payment.total}\n Status: {payment.status}\n Method: {payment.payment_method}\n ID_Transaction: {payment.transaction_id}"
        notification_admin_by_mail(affair_admin, message_admin)

    def _check_mt5_reconnection(self, user):
        try:
            account_mt5 = AccountMt5.objects.get(id_user=user.id)
            if account_mt5.status == '0':
                trader_payment = TraderPayment.objects.unpaid_trader_payments(user.id)
                vps_payment = VpsPayment.objects.unpaid_vps_payments(user.id)
                if trader_payment == False and vps_payment == False:
                    enable_reconnection_mt5(user.id, self.request)
        except Exception as err:
            messages.add_message(request=self.request, level=messages.WARNING, message='Hubo un error al intentar habilitar la reconexion de la cuenta mt5.')
            print("Hubo un error al intentar habilitar la reconexion de la cuenta mt5 del usuario a metaapi. ", err)

    def get_context_data(self, **kwargs):
        context = super(PaymentsView, self).get_context_data(**kwargs)
        id_user = self.request.user.id

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

        forex_payments = ForexPlanPayment.objects.forex_payments_by_user(id_user)
        stock_payments = StockPlanPayment.objects.stock_payments_by_user(id_user)

        additional_payments = []
        for payment in forex_payments:
            additional_payments.append({
                'id': payment.id,
                'plan_type': payment.get_plan_type_display(),
                'created_date': payment.created_date,
                'expiration': payment.expiration,
                'total': payment.total,
                'status': payment.status,
                'payment_type': 'forex'
            })
        for payment in stock_payments:
            additional_payments.append({
                'id': payment.id,
                'plan_type': 'Paquete Anual',
                'created_date': payment.created_date,
                'expiration': payment.expiration,
                'total': payment.total,
                'status': payment.status,
                'payment_type': 'stock'
            })

        additional_payments.sort(key=lambda x: x['created_date'], reverse=True)
        paginator3 = Paginator(additional_payments, 10)
        page3 = self.request.GET.get('page3')
        context['additional_payments'] = paginator3.get_page(page3)
        context['additional_payments_pages'] = paginator3.num_pages
        context['range'] = range(1, 9)

        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('page'):
            data = list(context['vps_payments'].object_list.values())
            for register in data:
                register.pop('id_user_id')
                register.pop('transaction_id')
                register.pop('payment_method')
            return JsonResponse({'vps_payments': data, 'total_pages': context['vps_payments_pages']})

        elif self.request.GET.get('page2'):
            data = list(context['trader_payments'].object_list.values())
            for register in data:
                register.pop('id_user_id')
                register.pop('transaction_id')
                register.pop('payment_method')
            return JsonResponse({'trader_payments': data, 'total_pages': context['trader_payments_pages']})

        elif self.request.GET.get('page3'):
            data = []
            for payment in context['additional_payments'].object_list:
                data.append({
                    'id': payment['id'],
                    'plan_type': payment['plan_type'],
                    'created_date': str(payment['created_date']),
                    'expiration': str(payment['expiration']),
                    'total': str(payment['total']),
                    'status': payment['status'],
                    'payment_type': payment['payment_type']
                })
            return JsonResponse({'additional_payments': data, 'total_pages': context['additional_payments_pages']})
        
        else:
            response_kwargs.setdefault('content_type', self.content_type)
            return self.response_class(
                request=self.request,
                template=self.get_template_names(),
                context=context,
                using=self.template_engine,
                **response_kwargs
            )


class PaymentFormView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/payment-form.html'
    login_url = reverse_lazy('users_app:user_login')

    def get_context_data(self, **kwargs):
        context = super(PaymentFormView, self).get_context_data(**kwargs)
        payment_type = self.kwargs.get('payment_type')
        pk = self.kwargs.get('pk')
        plan_type = self.request.GET.get('plan', 'inicio')
        
        config = PAYMENT_CONFIG.get(payment_type)
        if not config:
            return context

        context['title'] = config['title']
        context['payment_type'] = payment_type
        context['date'] = datetime.now()

        if pk and 'model' in config:
            payment = config['model'].objects.get(id=pk)
            context['price'] = payment.total
            context['expiration'] = payment.expiration
            context['payment_id'] = pk
            
            if payment_type == 'renewal-trader':
                context['description'] = f"Gestion de cuenta de metatrader5 del {payment.created_date} al {payment.expiration}"
            elif payment_type == 'renewal-vps':
                context['description'] = config.get('description', 'Renovacion mensual - VPS + Copytrading')
            elif payment_type == 'renewal-forex':
                plan_descriptions = config.get('descriptions', {})
                context['description'] = plan_descriptions.get(payment.plan_type, 'Renovacion mensual - Plan Forex')
                context['plan_type'] = payment.plan_type
            elif payment_type == 'renewal-stock':
                context['description'] = config.get('description', 'Renovacion anual - Plan Stock')
            else:
                context['description'] = config.get('description', 'Renovacion de servicio')
        else:
            if config['price_source'] == 'level':
                level = User.objects.get(id=self.request.user.id).level
                context['price'] = level.price
            elif config['price_source'] == 'plan_type':
                context['price'] = config['prices'].get(plan_type, 87)
                context['description'] = config['descriptions'].get(plan_type, config['descriptions']['inicio'])
                context['plan_type'] = plan_type
            elif config['price_source'] == 'fixed':
                context['price'] = config['price']
            
            if 'description' not in context:
                context['description'] = config.get('description', '')

            if config.get('expiration_type') == 'monthly':
                context['expiration'] = (datetime.now() + relativedelta(months=1)).date()
            elif config.get('expiration_type') == 'yearly':
                context['expiration'] = (datetime.now() + relativedelta(years=1)).date()
            else:
                context['expiration'] = expiration_vps(datetime.now())

        return context


class CheckoutSessionView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        if 'payment-method' not in request.POST or 'terms-and-conditions' not in request.POST:
            return self._handle_missing_fields(request)
        
        payment_type = request.POST['type']
        payment_method = request.POST['payment-method']
        plan_type = request.POST.get('plan-type', 'inicio')
        id_payment = request.POST.get('id-payment')
        
        price, description, custom_id, metadata = self._get_payment_details(payment_type, plan_type, id_payment, request)
        
        if price is None:
            return HttpResponseRedirect(reverse('payments_app:payments'))

        if payment_method == 'paypal':
            link_payment = create_renewal_order_paypal(amount=price, description=description, custom_id=custom_id)
        elif payment_method == 'stripe':
            link_payment = create_renewal_order_stripe(id_user=request.user.id, amount=price, description=description, metadata=metadata)
        else:
            return HttpResponseRedirect(reverse('payments_app:payments'))

        return HttpResponseRedirect(link_payment)

    def _get_payment_details(self, payment_type, plan_type, id_payment, request):
        config = PAYMENT_CONFIG.get(payment_type)
        if not config:
            return None, None, None, None

        price = None
        description = ''
        custom_id = ''
        metadata = {'custom_id': '', 'id_user': request.user.id}

        if payment_type == 'first-payment':
            level = User.objects.get(id=request.user.id).level
            price = level.price
            description = config['description']
            custom_id = 'first_payment'
            metadata['custom_id'] = 'first_payment'

        elif payment_type in ['renewal-vps', 'renewal-trader', 'renewal-forex', 'renewal-stock']:
            model = config['model']
            payment = model.objects.get(id=id_payment)
            if payment.id_user.id != request.user.id or payment.status != 'Pagar':
                return None, None, None, None
            
            price = payment.total
            
            if payment_type == 'renewal-trader':
                description = f"Gestion de cuenta de metatrader5 del {payment.created_date} al {payment.expiration}"
            elif payment_type == 'renewal-vps':
                description = config.get('description', 'Renovacion mensual - VPS + Copytrading')
            elif payment_type == 'renewal-forex':
                plan_descriptions = config.get('descriptions', {})
                description = plan_descriptions.get(payment.plan_type, 'Renovacion mensual - Plan Forex')
            elif payment_type == 'renewal-stock':
                description = config.get('description', 'Renovacion anual - Plan Stock')
            else:
                description = config.get('description', 'Renovacion de servicio')
            
            custom_id = str({config['custom_id_prefix']: int(id_payment)})
            metadata['custom_id'] = config['custom_id_prefix']
            metadata['payment_id'] = id_payment
            
            if payment_type == 'renewal-forex':
                metadata['plan_type'] = payment.plan_type

        elif payment_type == 'forex-plan':
            price = config['prices'].get(plan_type, 87)
            description = config['descriptions'].get(plan_type, config['descriptions']['inicio'])
            custom_id = str({'forex': True, 'plan_type': plan_type})
            metadata['custom_id'] = 'forex'
            metadata['plan_type'] = plan_type

        elif payment_type == 'stock-plan':
            price = config['price']
            description = config['description']
            custom_id = str({'stock': True})
            metadata['custom_id'] = 'stock'

        return price, description, custom_id, metadata

    def _handle_missing_fields(self, request):
        payment_type = request.POST.get('type', '')
        messages.add_message(request=request, level=messages.ERROR, message='Debe elegir un metodo de pago y aceptar los terminos y condiciones.')
        
        if payment_type in ['renewal-vps', 'renewal-trader', 'renewal-forex', 'renewal-stock']:
            pk = request.POST.get('id-payment')
            return HttpResponseRedirect(reverse('payments_app:payment_renewal', kwargs={'payment_type': payment_type, 'pk': pk}))
        else:
            return HttpResponseRedirect(reverse('payments_app:payment_form', kwargs={'payment_type': payment_type}))


class WebhookStripeView(View):
    
    def post(self, request, *args, **kwargs):
        endpoint_secret = get_secret('STRIPE_ENDPOINT_SECRET')
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)
        except Exception as err:
            print("Error proveniente de stripe.Webhook.construct_event(): ", err)
            return HttpResponse(status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            self._process_stripe_payment(session)

        return HttpResponse(status=200)

    def _process_stripe_payment(self, session):
        price = session["amount_total"] / 100
        transaction_id = session["payment_intent"]
        id_user = session["metadata"]["id_user"]
        custom_id = session["metadata"]["custom_id"]
        user = User.objects.get(id=id_user)
        
        if custom_id == 'first_payment':
            User.objects.filter(id=id_user).update(subscriber=True)
            payment = VpsPayment.objects.save_payment_vps(price, user, 'Stripe', transaction_id)
            self._send_emails(user, payment, 'VPS+COPYTRADING', 'VPS+COPYTRADING')
        
        elif custom_id == 'vps':
            id_payment = session["metadata"]["payment_id"]
            payment = VpsPayment.objects.update_payment_vps(id_payment, 'Stripe', transaction_id)
            self._send_emails(user, payment, 'VPS+COPYTRADING', 'VPS+COPYTRADING')
            self._check_reconnection(id_user)

        elif custom_id == 'trader':
            id_payment = session["metadata"]["payment_id"]
            payment = TraderPayment.objects.update_payment_trader(id_payment, 'Stripe', transaction_id)
            self._send_emails(user, payment, 'GESTION DE CUENTAS MT5', 'GESTION DE CUENTAS MT5', include_management=True)
            self._check_reconnection(id_user)

        elif custom_id == 'forex':
            plan_type = session["metadata"].get("plan_type", "inicio")
            plan_name = "Paquete Inicio" if plan_type == 'inicio' else "Paquete Elevate"
            
            if "payment_id" in session["metadata"]:
                id_payment = session["metadata"]["payment_id"]
                payment = ForexPlanPayment.objects.update_payment_forex(id_payment, 'Stripe', transaction_id)
            else:
                payment = ForexPlanPayment.objects.save_payment_forex(price, user, 'Stripe', transaction_id, plan_type)
            
            self._send_emails(user, payment, f'FOREX PLAN - {plan_name}', f'FOREX PLAN - {plan_name}')

        elif custom_id == 'stock':
            if "payment_id" in session["metadata"]:
                id_payment = session["metadata"]["payment_id"]
                payment = StockPlanPayment.objects.update_payment_stock(id_payment, 'Stripe', transaction_id)
            else:
                payment = StockPlanPayment.objects.save_payment_stock(price, user, 'Stripe', transaction_id)
            
            self._send_emails(user, payment, 'STOCK PLAN - PAQUETE ANUAL', 'STOCK PLAN - PAQUETE ANUAL')

    def _send_emails(self, user, payment, service_name, service_admin, include_management=False):
        context = {
            "id_payment": payment.id,
            "name": user.name + " " + user.last_name,
            "status": payment.status,
            "service": service_name,
            "created_date": payment.created_date,
            "expiration": payment.expiration,
            "price": payment.total
        }
        if include_management:
            context["id_management"] = payment.id_management.id
            
        mail = create_mail(user.email, f"FORTUNA 303 IMPORTE DE {service_name} #{payment.id}", "payments/invoice.html", context)
        mail.send(fail_silently=False)
        
        affair_admin = f"NUEVO PAGO DE {service_admin} RECIBIDO."
        message_admin = f"EL pago recibido es del usario:\n\n ID: {user.id}\n name: {user.name} {user.last_name}\n correo: {user.email}\n\nLos datos del importe:\n\n ID: {payment.id}\n Created date: {payment.created_date}\n Expiration: {payment.expiration}\n Total: {payment.total}\n Status: {payment.status}\n Method: {payment.payment_method}\n ID_Transaction: {payment.transaction_id}"
        notification_admin_by_mail(affair_admin, message_admin)

    def _check_reconnection(self, id_user):
        try:
            account_mt5 = AccountMt5.objects.get(id_user=id_user)
            if account_mt5.status == '0':
                trader_payment = TraderPayment.objects.unpaid_trader_payments(id_user)
                vps_payment = VpsPayment.objects.unpaid_vps_payments(id_user)
                if trader_payment == False and vps_payment == False:
                    enable_reconnection_mt5(id_user, None)
        except Exception as err:
            print("Hubo un error al intentar habilitar la reconexion de la cuenta mt5 del usuario a metaapi. ", err)
