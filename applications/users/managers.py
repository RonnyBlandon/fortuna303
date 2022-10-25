from django.db import models
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager, models.Manager):

    def _create_user(self, name, last_name, email, account_level, password, is_staff, is_superuser, is_active, **extra_fields):
        user = self.model(
            name=name,
            last_name=last_name,
            email=email,
            level=account_level,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=is_active,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self.db)
        return user


    def create_user(self, name, last_name, email, account_level, password, **extra_fields):
        return self._create_user(name, last_name, email, account_level, password, False, False, False, **extra_fields)


    def create_superuser(self, name, last_name, email, account_level, password=None, **extra_fields):
        return self._create_user(name, last_name, email, account_level, password, True, True, True, **extra_fields)


    def cod_validation(self, id_user, validation_code):
        if self.filter(id=id_user, validation_code=validation_code):
            return True
        else:
            return False


    def email_exists(self, email):
        if self.filter(email=email):
            return True
        else:
            return False

    # Devido a que no funciona el authenticate de django en el forms.py creamos una funcion que lo
    # haga aqui en el managers
