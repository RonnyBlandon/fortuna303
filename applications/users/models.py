from django.db import models
# importamos las librerias para el control de usuarios
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .managers import UserManager

# Create your models here.

class User(AbstractBaseUser, PermissionsMixin):
    
    name = models.CharField('Nombre', max_length=20)
    last_name = models.CharField('Apellido', max_length=20)
    email = models.EmailField('Correo Electronico', unique=True)
    validation_code = models.CharField(max_length=6)
    # creamos la columna staff en modelo para la creacion de superusuarios
    is_staff = models.BooleanField(default=False)
    # nueva columna para verificar si el correo es real
    is_active = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return str(self.id) + ' - ' + self.name + ' ' + self.last_name + ' - ' + self.email

    def get_full_name(self):
        return self.first_name + " " + self.last_name

    # Para extraerlo en los views
    def get_id(self):
        return self.id
