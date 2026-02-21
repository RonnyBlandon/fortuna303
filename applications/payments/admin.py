from django.contrib import admin
from .models import VpsPayment, TraderPayment, ForexPlanPayment, StockPlanPayment
from applications.users.function import create_mail

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_date', 'expiration', 'total', 'status', 'id_user')
    list_filter = ('status', 'payment_method', 'created_date', 'expiration')
    search_fields = ('created_date', 'expiration',)

    def resend_invoice_email(self, request, queryset):
        for invoice in queryset:
            mail = create_mail(invoice.id_user.email, f"FORTUNA 303 IMPORTE DE VPS+COPYTRADING #{invoice.id}", "payments/invoice.html", {"id_payment": invoice.id, "name": invoice.id_user.name +" "+ invoice.id_user.last_name, "status": invoice.status, "service": "VPS+COPYTRADING", "created_date": invoice.created_date, "expiration": invoice.expiration, "price": invoice.total})
            mail.send(fail_silently=False)
        
        self.message_user(request, "Los correos de las facturas se han reenviado.")
    
    actions = [resend_invoice_email]


class ForexPlanPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_date', 'expiration', 'total', 'status', 'plan_type', 'id_user')
    list_filter = ('status', 'payment_method', 'plan_type', 'created_date')
    search_fields = ('created_date', 'expiration',)


class StockPlanPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_date', 'expiration', 'total', 'status', 'id_user')
    list_filter = ('status', 'payment_method', 'created_date')
    search_fields = ('created_date', 'expiration',)


admin.site.register(VpsPayment, PaymentAdmin)
admin.site.register(TraderPayment, PaymentAdmin)
admin.site.register(ForexPlanPayment, ForexPlanPaymentAdmin)
admin.site.register(StockPlanPayment, StockPlanPaymentAdmin)
