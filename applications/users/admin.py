from django.contrib import admin
# Importando modelos de la app user
from .models import User
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