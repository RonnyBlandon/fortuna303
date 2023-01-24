from django.db import models
# importamos las librerias para el control de usuarios
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
# imporatmos managers
from .managers import UserManager

class Level(models.Model):
    account_level = models.CharField('Nivel', max_length=20)
    min_balance = models.DecimalField('Balance Minimo', max_digits=10, decimal_places=2)
    max_balance = models.DecimalField('Balance Maximo', max_digits=10, decimal_places=2)
    price = models.DecimalField('Precio', max_digits=6, decimal_places=2)

    def __str__(self):
        return str(self.id) + ' - ' + self.account_level + ' ' + str(self.max_balance) + ' - ' + str(self.price)


class User(AbstractBaseUser, PermissionsMixin):
    
    name = models.CharField('Nombre', max_length=20)
    last_name = models.CharField('Apellido', max_length=20)
    email = models.EmailField('Correo Electronico', max_length=60, unique=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    subscriber = models.BooleanField('Suscriptor')
    due_payments = models.BooleanField('¿Tiene pagos vencidos?')
    id_customer_stripe = models.CharField('ID customer stripe', max_length=25, blank=True, null=True)
    validation_code = models.CharField(max_length=6)
    # creamos la columna staff en modelo para la creacion de superusuarios
    is_staff = models.BooleanField(default=False)
    # nueva columna para verificar si el correo es real
    is_active = models.BooleanField(default=False)

    class Meta:
        unique_together = ('email',)
    
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return str(self.id) + ' - ' + self.name + ' ' + self.last_name + ' - ' + self.email

    def get_full_name(self):
        return self.first_name + " " + self.last_name
