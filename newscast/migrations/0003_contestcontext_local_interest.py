# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-05 21:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newscast', '0002_contestcontext'),
    ]

    operations = [
        migrations.AddField(
            model_name='contestcontext',
            name='local_interest',
            field=models.BooleanField(default=False, verbose_name="We're Interested In This?"),
        ),
    ]