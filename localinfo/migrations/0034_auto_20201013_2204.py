# Generated by Django 3.1 on 2020-10-13 22:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('localinfo', '0033_auto_20200921_1726'),
    ]

    operations = [
        migrations.AddField(
            model_name='opdictionary',
            name='op_program',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='localinfo.opprogram', verbose_name='Programa de operación'),
            preserve_default=False,
        ),
    ]