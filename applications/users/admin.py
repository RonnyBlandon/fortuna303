from django.contrib import admin
# Importando modelos de la app user
from .models import User
# Register your models here.

admin.site.register(User)