from django.db import models
from applications.users.models import User
from applications.vps.models import AccountManagement
from .managers import VpsPaymentManager, TraderPaymentManager, ForexPlanPaymentManager, StockPlanPaymentManager

payment_status = (('Pagar', 'No Pagado'), ('Pagado', 'Pagado'), ('Cancelado', 'Cancelado'), ('Reembolsado', 'Reembolsado'))
payment_methods = (('Paypal', 'Paypal'), ('Stripe', 'Stripe'))
forex_plan_types = (('inicio', 'Paquete Inicio'), ('elevate', 'Paquete Elevate'))

class VpsPayment(models.Model):
    created_date = models.DateField('Fecha de creación', max_length=20)
    expiration = models.DateField('Fecha de vencimiento', max_length=20)
    total = models.DecimalField('Total', max_digits=9, decimal_places=2)
    status = models.CharField('Estado', max_length=12, choices=payment_status)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.CharField('Metodo de Pago', max_length=20, blank=True, choices=payment_methods)
    transaction_id = models.CharField('ID Transacción', max_length=50, blank=True)
    
    objects = VpsPaymentManager()

    def __str__(self):
        return str(self.id) + ' - ' +  str(self.created_date) + ' - ' + str(self.expiration) + ' - ' + self.status


class TraderPayment(models.Model):
    created_date = models.DateField('Fecha de creación')
    expiration = models.DateField('Fecha de creación')
    id_management = models.ForeignKey(AccountManagement, on_delete=models.CASCADE)
    total = models.DecimalField('Total', max_digits=9, decimal_places=2)
    status = models.CharField('Estado', max_length=12, choices=payment_status)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.CharField('Metodo de Pago', max_length=20, blank=True, choices=payment_methods)
    transaction_id = models.CharField('ID Transacción', max_length=30, blank=True)

    objects = TraderPaymentManager()

    def __str__(self):
        return str(self.id)+' - '+str(self.created_date)+' - '+str(self.expiration)+' - '+self.status+str(self.total)


class ForexPlanPayment(models.Model):
    created_date = models.DateField('Fecha de creación')
    expiration = models.DateField('Fecha de vencimiento')
    total = models.DecimalField('Total', max_digits=9, decimal_places=2)
    status = models.CharField('Estado', max_length=12, choices=payment_status)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.CharField('Metodo de Pago', max_length=20, blank=True, choices=payment_methods)
    transaction_id = models.CharField('ID Transacción', max_length=50, blank=True)
    plan_type = models.CharField('Tipo de Plan', max_length=20, choices=forex_plan_types)
    
    objects = ForexPlanPaymentManager()

    def __str__(self):
        return str(self.id) + ' - ' + str(self.created_date) + ' - ' + str(self.expiration) + ' - ' + self.status + ' - ' + self.plan_type


class StockPlanPayment(models.Model):
    created_date = models.DateField('Fecha de creación')
    expiration = models.DateField('Fecha de vencimiento')
    total = models.DecimalField('Total', max_digits=9, decimal_places=2)
    status = models.CharField('Estado', max_length=12, choices=payment_status)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.CharField('Metodo de Pago', max_length=20, blank=True, choices=payment_methods)
    transaction_id = models.CharField('ID Transacción', max_length=50, blank=True)
    
    objects = StockPlanPaymentManager()

    def __str__(self):
        return str(self.id) + ' - ' + str(self.created_date) + ' - ' + str(self.expiration) + ' - ' + self.status
