# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-14 05:40
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='status',
        ),
        migrations.RemoveField(
            model_name='order',
            name='updated',
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_address',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='order',
            name='order_Desc',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.jsonb.JSONField(), default=list, null=True, size=None),
        ),
        migrations.AddField(
            model_name='order',
            name='order_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
