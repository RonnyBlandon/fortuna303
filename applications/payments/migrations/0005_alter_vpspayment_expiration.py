# Generated by Django 4.1.1 on 2022-10-14 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_traderpayment_payment_method_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vpspayment',
            name='expiration',
            field=models.DateField(max_length=20, verbose_name='Fecha de vencimiento'),
        ),
    ]