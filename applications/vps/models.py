from django.db import models
from applications.users.models import User
# Managers
from .managers import AccountMt5Manager
# Create your models here.

Status = (('0', 'Desconectado'), ('1', 'Conectado'), ('2', 'Error'))
class AccountMt5(models.Model):
    login = models.CharField('Usuario', max_length=20)
    password = models.CharField('Password', max_length=128)
    server = models.CharField('Servidor', max_length=30)
    id_client_metaapi = models.CharField('ID de cuenta MetaApi', max_length=50)
    access_token = models.CharField('Token de cuenta MetaApi', max_length=100)
    status = models.CharField('Estado', max_length=1, choices=Status)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = AccountMt5Manager()

    def __str__(self):
        return  str(self.login) + ' - ' + self.password +' - ' + str(self.server) + ' - ' + str(self.id_user)


class AccountManagement(models.Model):
    start_date = models.DateField('Fecha Inicial')
    end_date = models.DateField('Fecha Final')
    start_balance = models.DecimalField('Balance Inicial', max_digits=9, decimal_places=2)
    withdraw_deposit = models.DecimalField('Retiro/Deposito', max_digits=9, decimal_places=2, default=0.00)
    end_balance = models.DecimalField('Balance Final', max_digits=9, decimal_places=2, default=0.00)
    gross_profit = models.DecimalField('Ganancia Bruta', max_digits=9, decimal_places=2, default=0.00)
    net_profit = models.DecimalField('Ganancia Neta', max_digits=9, decimal_places=2, default=0.00)
    id_account_mt5 = models.ForeignKey(AccountMt5, on_delete=models.CASCADE)

    def __str__(self):
        return  self.user + ' - ' + self.password +' - ' + str(self.server) + ' - ' + str(self.id_user)
