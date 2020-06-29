# Generated by Django 3.0.6 on 2020-06-24 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReceiveCoins3daysOffer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coins', models.IntegerField()),
                ('gained_offer', models.BooleanField(default=False)),
                ('receive_by', models.IntegerField()),
                ('received_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'received_coins_3_days',
            },
        ),
    ]