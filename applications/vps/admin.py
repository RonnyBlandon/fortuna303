from django.contrib import admin
# importando modelos de la app vps
from applications.vps.models import AccountMt5, AccountManagement, AccountOperation

# Register your models here.
class AccountMt5Admin(admin.ModelAdmin):
    list_display = ('login', 'server', 'status', 'id_user', 'reconnect')
    search_fields = ('login', 'server')
    list_filter = ('status', 'reconnect')


class AccountManagementAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_date', 'end_date', 'start_balance', 'end_balance', 'net_profit', 'id_user')
    search_fields = ('id', 'start_date', 'end_date')
    list_filter = ('end_date',)


class AccountOperationAdmin(admin.ModelAdmin):
    list_display = ('id', 'open_time', 'symbol', 'type', 'volume', 'close_time', 'commission', 'swap', 'profit', 'id_account_mt5')
    search_fields = ('id', 'open_time', 'close_time', 'symbol', 'type')


admin.site.register(AccountMt5, AccountMt5Admin)
admin.site.register(AccountManagement, AccountManagementAdmin)
admin.site.register(AccountOperation, AccountOperationAdmin)
