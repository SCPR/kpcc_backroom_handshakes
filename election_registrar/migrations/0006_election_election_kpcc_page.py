# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-03-07 20:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('election_registrar', '0005_auto_20170307_1104'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='election_kpcc_page',
            field=models.URLField(blank=True, max_length=1024, null=True, verbose_name=b'URL on KPCC.org hosting results'),
        ),
    ]
