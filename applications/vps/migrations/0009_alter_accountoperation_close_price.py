# Generated by Django 4.1.3 on 2022-12-06 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vps', '0008_alter_accountoperation_open_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountoperation',
            name='close_price',
            field=models.FloatField(verbose_name='Precio Cierre'),
        ),
    ]
