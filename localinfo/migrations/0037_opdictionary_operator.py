# Generated by Django 3.2.20 on 2023-08-22 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('localinfo', '0036_remove_opdictionary_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='opdictionary',
            name='operator',
            field=models.IntegerField(default=1, null=True),
        ),
    ]