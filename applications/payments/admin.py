from django.contrib import admin
# import the models
from .models import VpsPayment, TraderPayment
# import functions
from applications.users.function import create_mail
# Register your models here.

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_date', 'expiration', 'total', 'status', 'id_user')
    list_filter = ('status', 'payment_method', 'created_date', 'expiration')
    search_fields = ('created_date', 'expiration',)

    def resend_invoice_email(self, request, queryset):
        for invoice in queryset:
            # Reenviar un correo del importe al usuario.
            mail = create_mail(invoice.id_user.email, f"FORTUNA 303 IMPORTE DE VPS+COPYTRADING #{invoice.id}", "payments/invoice.html", {"id_payment": invoice.id, "name": invoice.id_user.name +" "+ invoice.id_user.last_name, "status": invoice.status, "service": "VPS+COPYTRADING", "created_date": invoice.created_date, "expiration": invoice.expiration, "price": invoice.total})
            mail.send(fail_silently=False)
        
        self.message_user(request, "Los correos de las facturas se han reenviado.")
    
    actions = [resend_invoice_email]


admin.site.register(VpsPayment, PaymentAdmin)
admin.site.register(TraderPayment, PaymentAdmin)
