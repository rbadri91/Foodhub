# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-15 00:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Foodhubinit', '0004_auto_20170714_0201'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='profile',
            name='stripe_id',
            field=models.CharField(max_length=255, null=True, unique=True),
        ),
    ]
