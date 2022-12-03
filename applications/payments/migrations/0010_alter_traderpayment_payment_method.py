# Generated by Django 4.1.3 on 2022-12-01 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0009_alter_traderpayment_created_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='traderpayment',
            name='payment_method',
            field=models.CharField(blank=True, choices=[('Paypal', 'Paypal'), ('Stripe', 'Stripe')], max_length=20, verbose_name='Metodo de Pago'),
        ),
    ]
