# Generated by Django 3.2 on 2021-05-24 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consistencychecker', '0002_consistency_authority_period_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='consistency',
            name='authority_period_index_version',
            field=models.CharField(default=1, max_length=10),
        ),
    ]
