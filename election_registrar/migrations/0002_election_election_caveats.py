# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-10-27 21:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('election_registrar', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='election_caveats',
            field=models.TextField(blank=True, null=True, verbose_name=b'Audience-facing display of election status'),
        ),
    ]