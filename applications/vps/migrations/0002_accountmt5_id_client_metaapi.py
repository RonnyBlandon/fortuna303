# Generated by Django 4.1 on 2022-09-11 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vps', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountmt5',
            name='id_client_metaapi',
            field=models.CharField(default=1, max_length=50, verbose_name='ID de cuenta Metaapi'),
            preserve_default=False,
        ),
    ]
