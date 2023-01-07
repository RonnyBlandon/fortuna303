from django.db import models
from applications.users.models import User
# Managers
from .managers import AccountMt5Manager, AccountManagementManager, AccountOperationManager
# Create your models here.

Status = (('0', 'Desconectado'), ('1', 'Conectado'), ('2', 'Error'))

# Create your models here.

class AccountMt5(models.Model):
    login = models.CharField('Usuario', max_length=20)
    password = models.CharField('Password', max_length=128)
    server = models.CharField('Servidor', max_length=30)
    id_client_metaapi = models.CharField('ID de cuenta MetaApi', max_length=50)
    status = models.CharField('Estado', max_length=1, choices=Status)
    reconnect = models.BooleanField('Reconexión hablitada')
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = AccountMt5Manager()

    def __str__(self):
        return  str(self.id) + ' - ' + str(self.login) + ' - ' + self.password +' - ' + str(self.server) + ' - ' + str(self.id_user)


class AccountManagement(models.Model):
    start_date = models.DateField('Fecha Inicial')
    end_date = models.DateField('Fecha Final')
    start_balance = models.DecimalField('Balance Inicial', max_digits=9, decimal_places=2)
    withdraw_deposit = models.DecimalField('Retiro/Deposito', max_digits=9, decimal_places=2, default=0.00)
    end_balance = models.DecimalField('Balance Final', max_digits=9, decimal_places=2, default=0.00)
    gross_profit = models.DecimalField('Ganancia Bruta', max_digits=9, decimal_places=2, default=0.00)
    commission = models.DecimalField('Comisiones', max_digits=6, decimal_places=2, default=0.00)
    swap = models.DecimalField('Swap', max_digits=6, decimal_places=2, default=0.00)
    net_profit = models.DecimalField('Ganancia Neta', max_digits=9, decimal_places=2, default=0.00)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = AccountManagementManager()

    def __str__(self):
        return  str(self.id) + ' - ' + str(self.start_date) +' - ' + str(self.end_date) + ' - ' + str(self.id_user)


class AccountOperation(models.Model):
    open_time = models.DateTimeField('Fecha Apertura', max_length=20)
    open_price = models.FloatField('Precio Apertura')
    symbol = models.CharField('Par', max_length=10)
    type = models.CharField('Tipo', max_length=6)
    volume = models.DecimalField('Lotaje', max_digits=5, decimal_places=2)
    close_time = models.DateTimeField('Fecha Cierre', max_length=20)
    close_price = models.CharField('Precio Cierre', max_length=10)
    commission = models.DecimalField('Comisiones', max_digits=6, decimal_places=2)
    swap = models.DecimalField('Swap', max_digits=6, decimal_places=2)
    profit = models.DecimalField('Beneficio', max_digits=8, decimal_places=2)
    id_account_mt5 = models.ForeignKey(AccountMt5, on_delete=models.CASCADE)

    objects = AccountOperationManager()

    def __str__(self):
        return  str(self.id) + ' - ' + str(self.close_time) +' - ' + str(self.profit) + ' - ' + str(self.id_account_mt5)
