from django.contrib import admin
# Importando modelos
from .models import User, Level
# Register your models here.


class User_Admin(admin.ModelAdmin):
    list_display = (
        'id',
        'Nombre_Completo',
        'email',
        'is_active',
        'subscriber',
        'due_payments',
    )
    # función para mostrar el nombre completo en una sola columna de la tabla users llamada full_name
    def Nombre_Completo(self, obj):
        return obj.name + ' ' + obj.last_name

    # Agregamos un buscador por nombre , apellido y correo electronico
    search_fields = ['name', 'last_name', 'email']
    list_filter = ('is_active', 'subscriber', 'due_payments')

admin.site.register(User, User_Admin)
admin.site.register(Level)
