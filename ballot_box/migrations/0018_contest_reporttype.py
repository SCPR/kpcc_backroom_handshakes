# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-14 20:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ballot_box', '0017_auto_20160513_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='reporttype',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Status of Results'),
        ),
    ]
