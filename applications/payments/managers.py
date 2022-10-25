import decimal
from django.db import models
from datetime import date, timedelta
from calendar import isleap, monthrange

class VpsPaymentManager(models.Manager):
    """ Procedimientos para VpsPayment """

    def save_payment_vps(self, total: float, id_user, transaction_id: str):
        date_now = date.today()  # Sacamos la fecha que se genero el pago
        days_of_month = monthrange(date_now.year, date_now.month)[1]  # calculamos cuantos dias tiene el mes
        # Agregamos la fecha de vencimiento
        match days_of_month:
            case 31:
                if date_now.month == 1:  # Preguntando si es enero
                    if isleap(date_now.year):  # Preguntando si es año bisiesto
                        if date_now.day == 29:
                            expiration = date_now + timedelta(days=31)
                        elif date_now.day == 30:
                            expiration = date_now + timedelta(days=30)
                        elif date_now.day == 31:
                            expiration = date_now + timedelta(days=30)
                    else: 
                        if date_now.day == 29:
                            expiration = date_now + timedelta(days=31)
                        elif date_now.day == 30:
                            expiration = date_now + timedelta(days=30)
                        elif date_now.day == 31:
                            expiration = date_now + timedelta(days=29)
                else:
                    expiration = date_now + timedelta(days=31)
            case 30:
                expiration = date_now + timedelta(days=30)
            case 29:
                expiration = date_now + timedelta(days=30)
            case 28:
                expiration = date_now + timedelta(days=30)
        # guardamos en la base de datos
        payment = self.model(
            created_date=date_now,
            expiration=expiration,
            total=total,
            status='Pagado',
            id_user=id_user,
            payment_method='Paypal',
            transaction_id=transaction_id
        )
        payment.save(using=self.db)
        return payment

    def get_vps_payments(self, id):
        payments = self.filter(id_user=id).order_by('-id')
        return payments


class TraderPaymentManager(models.Manager):
    """ Procedimientos para TraderPayment """

    def get_trader_payments(self, id):
        payments = self.filter(id_management=id).order_by('-id')
        return payments
