from django.contrib import admin
# import the models
from .models import VpsPayment, TraderPayment
# Register your models here.

admin.site.register(VpsPayment)
admin.site.register(TraderPayment)
