# Generated by Django 4.1.2 on 2022-10-30 00:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0006_traderpayment_id_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='traderpayment',
            name='created_date',
            field=models.DateTimeField(max_length=20, verbose_name='Fecha de creación'),
        ),
        migrations.AlterField(
            model_name='traderpayment',
            name='expiration',
            field=models.DateTimeField(max_length=20, verbose_name='Fecha de creación'),
        ),
    ]