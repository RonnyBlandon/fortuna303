# Generated by Django 4.1 on 2022-09-18 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vps', '0003_accountmt5_access_token_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountmt5',
            name='user_account',
            field=models.CharField(max_length=20, verbose_name='Usuario'),
        ),
    ]
