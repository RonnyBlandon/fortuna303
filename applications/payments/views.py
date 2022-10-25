from django.shortcuts import redirect
from django.views.generic import TemplateView, View
from django.http import JsonResponse
#
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.paginator import Paginator
# importamos los modelos
from .models import TraderPayment, VpsPayment
from applications.users.models import User, Level
#importamos funciones 
from applications.payments.functions import create_order, capture_order

# Create your views here.

class PaymentsView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/payments.html'
    login_url = reverse_lazy('users_app:user_login')

    def get_context_data(self, **kwargs):
        context = super(PaymentsView, self).get_context_data(**kwargs)

        id_user = self.request.user.id # sacamos el id del usuario

        vps_payment = VpsPayment.objects.get_vps_payments(id_user)
        paginator1 = Paginator(vps_payment, 3)
        page = self.request.GET.get('page')
        context['vps_payments'] = paginator1.get_page(page)

        trader_payment = TraderPayment.objects.get_trader_payments(id_user)
        paginator2 = Paginator(trader_payment, 5)
        page2 = self.request.GET.get('page')
        context['trader_payments'] = paginator2.get_page(page2)

        # Traemos la instancia del usuario 
        user = User.objects.get(id=id_user)

        # Recogemos las variables de la url que nos devuelve paypal al cancelar o aprobar el pago
        token = self.request.GET.get('token')
        if token:
            details = capture_order(token)
            if details:
                VpsPayment.objects.save_payment_vps(details['amount'], user, details['id'])

        return context

    # Enviamos los datos a cambiar con fecth
    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('page'):
            data = list(context['vps_payments'].object_list.values())
            for register in data:
                register.pop('id_user_id') # borrando dato innecesario
                register.pop('transaction_id') # borrando dato innecesario
            return JsonResponse({'vps_payments': data})

        elif self.request.GET.get('page2'):
            data = list(context['operations'])
            return JsonResponse({'operations': data})
        
        else:
            response_kwargs.setdefault('content_type', self.content_type)
            return self.response_class(
                request=self.request,
                template=self.get_template_names(),
                context=context,
                using=self.template_engine,
                **response_kwargs
            )


class CreatePaymentView(LoginRequiredMixin, View):
    
    def get(self, request, *args, **kwargs):
        value = self.request.GET.get('value')

        if value == '1':
            amount = 10.00
            descriptio = 'Alojamiento vps de cuenta metatrader 5 y uso del sistema copytrading.'

        link = create_order(value)
        return redirect(link)

    
