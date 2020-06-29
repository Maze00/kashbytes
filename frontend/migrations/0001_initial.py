# Generated by Django 3.0.6 on 2020-06-24 16:25

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('email', models.EmailField(max_length=30, unique=True, verbose_name='email')),
                ('username', models.CharField(max_length=30, unique=True)),
                ('last_login', models.DateField(auto_now=True, verbose_name='last login')),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('mobile_number', models.CharField(blank=True, max_length=15, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('sex', models.CharField(blank=True, max_length=12, null=True)),
                ('call_by', models.IntegerField(blank=True, null=True)),
                ('date_joined', models.DateField(default=datetime.date(2020, 6, 24))),
                ('response_count', models.BooleanField(default=False)),
                ('payment_done', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AccountActivationCoins',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coins', models.IntegerField()),
                ('activation_date', models.DateField(auto_now_add=True)),
                ('send_to', models.IntegerField()),
            ],
            options={
                'db_table': 'account_activation_coins_table',
            },
        ),
        migrations.CreateModel(
            name='HostBuyCash',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cash', models.IntegerField()),
                ('coins', models.IntegerField(default=0)),
                ('transaction_id', models.TextField()),
                ('send_to', models.IntegerField()),
                ('approve', models.BooleanField(default=False)),
                ('is_seen', models.BooleanField(default=False)),
                ('activation_date', models.DateField(auto_now_add=True)),
            ],
            options={
                'db_table': 'host_buy_cash',
            },
        ),
        migrations.CreateModel(
            name='ReceiveCoins',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coins', models.IntegerField()),
                ('receive_by', models.IntegerField()),
                ('received_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'received_coins',
            },
        ),
        migrations.CreateModel(
            name='TransferCoins',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coins', models.IntegerField()),
                ('given_by', models.IntegerField()),
                ('transfer_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'transfer_coins',
            },
        ),
        migrations.CreateModel(
            name='ReferralUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_address', models.TextField(max_length=250)),
                ('url_validity', models.BooleanField(default=0)),
                ('self_register', models.BooleanField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'refer_url_table',
            },
        ),
        migrations.CreateModel(
            name='ProfileLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pay_by_user', models.IntegerField(default=0)),
                ('coins', models.IntegerField(default=0)),
                ('user_level', models.IntegerField(default=0)),
                ('review', models.BooleanField(default=0)),
                ('transaction_id', models.CharField(blank=True, max_length=250, null=True)),
                ('has_paid', models.BooleanField(default=0)),
                ('active_with_pay', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'profile_level',
            },
        ),
        migrations.CreateModel(
            name='PersonCounter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refers', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
                'db_table': 'person_counter',
            },
        ),
        migrations.CreateModel(
            name='PasswordRecoveryUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=200)),
                ('validity', models.NullBooleanField(default=0)),
                ('created_at', models.DateField()),
                ('updated_at', models.DateField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'password_recovery_field',
            },
        ),
        migrations.CreateModel(
            name='CashOutRequestTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coins', models.IntegerField()),
                ('cash', models.IntegerField()),
                ('number', models.CharField(max_length=11)),
                ('ask_date', models.DateField(auto_now_add=True)),
                ('is_done', models.BooleanField(default=False)),
                ('is_approve', models.BooleanField(blank=True, null=True)),
                ('ask_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'cash_out_request_table',
            },
        ),
        migrations.CreateModel(
            name='CashAndCoinsTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_cash', models.IntegerField()),
                ('user_coins', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'cash_and_coins_table',
            },
        ),
    ]