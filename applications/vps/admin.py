from django.contrib import admin
# importando modelos de la app vps
from applications.vps.models import AccountMt5, AccountManagement, AccountOperation

# Register your models here.

admin.site.register(AccountMt5)
admin.site.register(AccountManagement)
admin.site.register(AccountOperation)