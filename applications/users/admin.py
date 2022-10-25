from django.contrib import admin
# Importando modelos
from .models import User, Level
# Register your models here.


class User_Admin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'last_name',
        'email'
    )

    # Agregamos un buscador por nombr
    search_fields = ['name', 'last_name']

admin.site.register(User, User_Admin)
admin.site.register(Level)
