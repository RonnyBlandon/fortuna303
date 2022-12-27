# Generated by Django 4.1.4 on 2022-12-19 17:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountMt5',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login', models.CharField(max_length=20, verbose_name='Usuario')),
                ('password', models.CharField(max_length=128, verbose_name='Password')),
                ('server', models.CharField(max_length=30, verbose_name='Servidor')),
                ('id_client_metaapi', models.CharField(max_length=50, verbose_name='ID de cuenta MetaApi')),
                ('status', models.CharField(choices=[('0', 'Desconectado'), ('1', 'Conectado'), ('2', 'Error')], max_length=1, verbose_name='Estado')),
                ('id_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AccountOperation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('open_time', models.DateTimeField(max_length=20, verbose_name='Fecha Apertura')),
                ('open_price', models.FloatField(verbose_name='Precio Apertura')),
                ('symbol', models.CharField(max_length=10, verbose_name='Par')),
                ('type', models.CharField(max_length=6, verbose_name='Tipo')),
                ('volume', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Lotaje')),
                ('close_time', models.DateTimeField(max_length=20, verbose_name='Fecha Cierre')),
                ('close_price', models.CharField(max_length=10, verbose_name='Precio Cierre')),
                ('commission', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Comisiones')),
                ('swap', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Swap')),
                ('profit', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Beneficio')),
                ('id_account_mt5', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vps.accountmt5')),
            ],
        ),
        migrations.CreateModel(
            name='AccountManagement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(verbose_name='Fecha Inicial')),
                ('end_date', models.DateField(verbose_name='Fecha Final')),
                ('start_balance', models.DecimalField(decimal_places=2, max_digits=9, verbose_name='Balance Inicial')),
                ('withdraw_deposit', models.DecimalField(decimal_places=2, default=0.0, max_digits=9, verbose_name='Retiro/Deposito')),
                ('end_balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=9, verbose_name='Balance Final')),
                ('gross_profit', models.DecimalField(decimal_places=2, default=0.0, max_digits=9, verbose_name='Ganancia Bruta')),
                ('commission', models.DecimalField(decimal_places=2, default=0.0, max_digits=6, verbose_name='Comisiones')),
                ('swap', models.DecimalField(decimal_places=2, default=0.0, max_digits=6, verbose_name='Swap')),
                ('net_profit', models.DecimalField(decimal_places=2, default=0.0, max_digits=9, verbose_name='Ganancia Neta')),
                ('id_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
