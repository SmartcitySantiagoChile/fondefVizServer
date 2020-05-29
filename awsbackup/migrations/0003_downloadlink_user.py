# Generated by Django 3.0.5 on 2020-05-15 21:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('awsbackup', '0002_downloadlink_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='downloadlink',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to=settings.AUTH_USER_MODEL, verbose_name='Usuario'),
        ),
    ]
