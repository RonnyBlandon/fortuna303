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

   def update_status_account_mt5(self, id: int, status: str, id_client_metaapi: str):
      account = self.filter(id=id)
      account.update(status=status, id_client_metaapi=id_client_metaapi)
      return account

   def get_account_mt5(self, id):
      account = self.filter(id_user=id)
      return account


class AccountManagementManager(models.Manager):
   """ Procedimientos para AccountManagement """

   def get_account_management(self, id_user):
      management = self.filter(id_user=id_user).order_by('-id')
      return management

   def last_management_by_user(self, id_user):
      management = self.filter(id_user=id_user).last()
      if management:
         return management[0]
      else:
         return None

class AccountOperationManager(models.Manager):
   """ Procedimientos para AccountManagement """

   def get_account_operations(self, id):
      operations = self.filter(id_account_mt5=id).order_by('-id')
      return operations
