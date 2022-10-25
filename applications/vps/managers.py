from django.db import models
from .functions import encrypt_password

class AccountMt5Manager(models.Manager):
   """ Procedimientos para cuentas mt5 """

   def create_account_mt5(self, login, password, server, id_client_metaapi, status, id_user):
      encrypted = encrypt_password(password=password)

      account = self.model(
         login=login,
         password=encrypted,
         server=server,
         id_client_metaapi=id_client_metaapi,
         status=status,
         id_user=id_user
      )
      account.save(using=self.db)
      return account
     

   def get_account_mt5(self, id):
      account = self.filter(id_user=id)
      return account


class AccountManagementManager(models.Manager):
   """ Procedimientos para AccountManagement """

   def get_account_management(self, id):
      management = self.filter(id_user=id).order_by('-id')
      return management


class AccountOperationManager(models.Manager):
   """ Procedimientos para AccountManagement """

   def get_account_operations(self, id):
      operations = self.filter(id_account_mt5=id).order_by('-id')
      return operations
