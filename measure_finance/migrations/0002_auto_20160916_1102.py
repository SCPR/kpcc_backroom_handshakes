# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-16 18:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('measure_finance', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='measuretotal',
            name='finance_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name=b''),
        ),
    ]
