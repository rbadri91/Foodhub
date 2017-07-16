# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-15 02:22
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0003_card'),
    ]

    operations = [
        migrations.CreateModel(
            name='Charge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_id', models.CharField(max_length=255, null=True, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('source', models.CharField(max_length=100)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=9, null=True)),
                ('amount_refunded', models.DecimalField(decimal_places=2, max_digits=9, null=True)),
                ('description', models.TextField(blank=True)),
                ('paid', models.NullBooleanField()),
                ('disputed', models.NullBooleanField()),
                ('refunded', models.NullBooleanField()),
                ('captured', models.NullBooleanField()),
                ('receipt_sent', models.BooleanField(default=False)),
                ('charge_created', models.DateTimeField(blank=True, null=True)),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='charges', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_id', models.CharField(max_length=255, null=True, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('amount_due', models.DecimalField(decimal_places=2, max_digits=9)),
                ('attempted', models.NullBooleanField()),
                ('attempt_count', models.PositiveIntegerField(null=True)),
                ('statement_descriptor', models.TextField(blank=True)),
                ('closed', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True)),
                ('paid', models.BooleanField(default=False)),
                ('receipt_number', models.TextField(blank=True)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=9)),
                ('tax', models.DecimalField(decimal_places=2, max_digits=9, null=True)),
                ('tax_percent', models.DecimalField(decimal_places=2, max_digits=9, null=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=9)),
                ('date', models.DateTimeField()),
                ('charge', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='orders.Charge')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='charge',
            name='invoice',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='charges', to='orders.Invoice'),
        ),
    ]