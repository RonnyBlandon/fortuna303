from django.contrib import admin
# import the models
from .models import VpsPayment, TraderPayment
# Register your models here.

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_date', 'expiration', 'total', 'status', 'id_user')
    list_filter = ('status', 'payment_method', 'created_date', 'expiration')
    search_fields = ('created_date', 'expiration',)


admin.site.register(VpsPayment, PaymentAdmin)
admin.site.register(TraderPayment, PaymentAdmin)
