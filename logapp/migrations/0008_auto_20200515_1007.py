# Generated by Django 3.0.5 on 2020-05-15 14:07

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('logapp', '0007_auto_20200302_1220'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usersession',
            options={'verbose_name': 'sesión de usuario', 'verbose_name_plural': 'sesiones de usuarios'},
        ),
    ]