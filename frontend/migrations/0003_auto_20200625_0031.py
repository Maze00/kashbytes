# Generated by Django 3.0.6 on 2020-06-24 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0002_receivecoins3daysoffer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receivecoins3daysoffer',
            name='gained_offer',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
