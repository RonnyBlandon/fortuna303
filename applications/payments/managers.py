from datetime import date
from django.db import models
from applications.payments.functions import expiration_vps

class VpsPaymentManager(models.Manager):
    """ Procedimientos para VpsPayment """

    def save_payment_vps(self, total: float, id_user, payment_method: str, transaction_id: str):
        date_now = date.today() # Sacamos la fecha que se genero el pago
        expiration = expiration_vps(date_now)

        # guardamos en la base de datos
        payment = self.model(
            created_date=date_now,
            expiration=expiration,
            total=total,
            status='Pagado',
            id_user=id_user,
            payment_method=payment_method,
            transaction_id=transaction_id
        )
        payment.save(using=self.db)
        return payment
    
    def update_payment_vps(self, id: int, payment_method: str, transaction_id: str):
        payment = self.filter(id=id).update(
            status='Pagado',
            payment_method=payment_method,
            transaction_id=transaction_id
        )
        return payment

    def vps_payments_by_user(self, id_user: int):
        payments = self.filter(id_user=id_user).order_by('-id')
        return payments

    def unpaid_vps_payments(self, id_user: int):
        payments = self.filter(id_user=id_user, status='Pagar')
        if payments:
            return True
        else:
            return False

    def vps_payments_by_status(self, status: str):
        payments = self.filter(status=status).order_by('-id')
        return payments


class TraderPaymentManager(models.Manager):
    """ Procedimientos para TraderPayment """

    def update_payment_trader(self, id: int, payment_method: str, transaction_id: str):
        payment = self.filter(id=id).update(
            status='Pagado',
            payment_method=payment_method,
            transaction_id=transaction_id
        )
        return payment

    def trader_payments_by_management(self, id_management: int):
        payments = self.filter(id_management=id_management).order_by('-id')
        return payments

    def trader_payments_by_user(self, id_user: int):
        payments = self.filter(id_user=id_user).order_by('-id')
        return payments

    def unpaid_trader_payments(self, id_user: int):
        payments = self.filter(id_user=id_user, status='Pagar')
        if payments:
            return True
        else:
            return False

    def trader_payments_by_status(self, status: str):
        payments = self.filter(status=status).order_by('-id')
        return payments