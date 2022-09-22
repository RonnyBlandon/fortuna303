from calendar import c
from django.db import models
#Importamos los modelos
from applications.users.models import User
from applications.vps.models import AccountMt5, AccountManagement

# creamos una tupla con los estados de pago para el atributo status
payment_status = (('0', 'No Pagado'), ('1', 'Pagado'), ('2', 'Cancelado'), ('3', 'Reembolsado'))



class VpsPayment(models.Model):
    created_date = models.DateTimeField('Fecha de creación', max_length=20)
    total = models.DecimalField('Total', max_digits=10, decimal_places=2)
    status = models.CharField('Estado', max_length=1, choices=payment_status)
    id_account_mt5 = models.ForeignKey(AccountMt5, on_delete=models.CASCADE)
    transaction_id = models.CharField('ID Transacción', max_length=30)

    def __str__(self):
        return str(self.id) + ' - ' +  str(self.created_date) + ' - ' + str(self.id_user) + ' - ' + self.status


class TraderPayment(models.Model):
    created_date = models.DateTimeField('Fecha de creación', max_length=20)
    total = models.DecimalField('Total', max_digits=10, decimal_places=2)
    status = models.CharField('Estado', max_length=1, choices=payment_status)
    id_management = models.ForeignKey(AccountManagement, on_delete=models.CASCADE)
    transaction_id = models.CharField('ID Transacción', max_length=30)

    def __str__(self):
        return str(self.id) + ' - ' +  str(self.created_date) + ' - ' + str(self.id_user) + ' - ' + self.status
