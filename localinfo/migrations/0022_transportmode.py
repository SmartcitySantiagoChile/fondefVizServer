# Generated by Django 1.11.6 on 2018-03-31 21:22


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('localinfo', '0021_remove_operator_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransportMode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('esId', models.IntegerField(unique=True, verbose_name='Identificador')),
                ('name', models.CharField(max_length=50, verbose_name='Nombre')),
            ],
            options={
                'verbose_name': 'Modo de transporte',
                'verbose_name_plural': 'Modos de transporte',
            },
        ),
    ]
