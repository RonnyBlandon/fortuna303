from django.db import models
from django.contrib.auth.models import BaseUserManager
# import models

class UserManager(BaseUserManager, models.Manager):

    def _create_user(self, name, last_name, email, account_level, password, is_staff, is_superuser, is_active, **extra_fields):
        user = self.model(
            name=name,
            last_name=last_name,
            email=email,
            level=account_level,
            subscriber=False,
            due_payments=False,
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
        if account_level is None:
            # Establecer un valor predeterminado para account_level si no se proporciona
            account_level = 2
        return self._create_user(name, last_name, email, account_level, password, True, True, True, **extra_fields)


    def cod_validation(self, id_user, validation_code):
        if self.filter(id=id_user, validation_code=validation_code):
            return True
        else:
            return False


    def email_exists(self, email: str):
        if self.filter(email=email):
            return True
        else:
            return False


    def get_level_user(self, id):
        user = self.get(id=id)
        level = user.level
        return level


    def update_user_due_payments(self, id_user: int, due_payments: bool):
        user = self.filter(id=id_user)
        user.update(due_payments=due_payments)
        return user


    def get_id_customer_stripe(self, id_user: int):
        user = self.get(id=id_user)
        id_customer = user.id_customer_stripe
        if id_customer:
            return id_customer
