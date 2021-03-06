# Generated by Django 3.0.5 on 2020-08-03 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('localinfo', '0029_auto_20200618_1439'),
    ]

    operations = [
        migrations.AddField(
            model_name='opdictionary',
            name='created_at',
            field=models.DateTimeField(null=True, verbose_name='Fecha de creación'),
        ),
        migrations.AddField(
            model_name='opdictionary',
            name='route_type',
            field=models.CharField(max_length=30, null=True, verbose_name='Tipo de ruta'),
        ),
        migrations.AddField(
            model_name='opdictionary',
            name='updated_at',
            field=models.DateTimeField(null=True, verbose_name='Fecha de última modificación'),
        ),
        migrations.AddField(
            model_name='opdictionary',
            name='user_route_code',
            field=models.CharField(max_length=30, null=True, verbose_name='Código de usuario'),
        ),
    ]
