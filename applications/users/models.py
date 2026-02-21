from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
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
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    class Meta:
        unique_together = ('email',)
    
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return str(self.id) + ' - ' + self.name + ' ' + self.last_name + ' - ' + self.email

    def get_full_name(self):
        return self.name + " " + self.last_name

    @property
    def has_active_forex(self):
        from applications.payments.models import ForexPlanPayment
        from datetime import date
        last_payment = ForexPlanPayment.objects.filter(
            id_user=self.id,
            status='Pagado'
        ).order_by('-expiration').first()
        if last_payment:
            return last_payment.expiration >= date.today()
        return False

    @property
    def forex_plan_info(self):
        from applications.payments.models import ForexPlanPayment
        from datetime import date
        payments = ForexPlanPayment.objects.filter(
            id_user=self.id
        ).order_by('-created_date')
        
        result = []
        seen_plans = set()
        
        for payment in payments:
            if payment.plan_type not in seen_plans:
                seen_plans.add(payment.plan_type)
                result.append({
                    'id': payment.id,
                    'plan_type': payment.plan_type,
                    'plan_name': payment.get_plan_type_display(),
                    'expiration': payment.expiration,
                    'status': payment.status,
                    'is_active': payment.status == 'Pagado' and payment.expiration >= date.today(),
                    'needs_renewal': payment.status == 'Pagar'
                })
        
        return result if result else None

    @property
    def has_forex_inicio_active(self):
        from applications.payments.models import ForexPlanPayment
        return ForexPlanPayment.objects.filter(
            id_user=self.id,
            plan_type='inicio'
        ).exclude(status='Cancelado').exists()

    @property
    def has_forex_elevate_active(self):
        from applications.payments.models import ForexPlanPayment
        return ForexPlanPayment.objects.filter(
            id_user=self.id,
            plan_type='elevate'
        ).exclude(status='Cancelado').exists()

    @property
    def has_stock_active(self):
        from applications.payments.models import StockPlanPayment
        return StockPlanPayment.objects.filter(
            id_user=self.id
        ).exclude(status='Cancelado').exists()

    @property
    def stock_plan_info(self):
        from applications.payments.models import StockPlanPayment
        from datetime import date
        last_payment = StockPlanPayment.objects.filter(
            id_user=self.id
        ).order_by('-created_date').first()
        if last_payment:
            return {
                'id': last_payment.id,
                'expiration': last_payment.expiration,
                'status': last_payment.status,
                'is_active': last_payment.status == 'Pagado' and last_payment.expiration >= date.today(),
                'needs_renewal': last_payment.status == 'Pagar'
            }
        return None
