# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-10 22:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ballot_box', '0005_auto_20160506_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultsource',
            name='source_active',
            field=models.BooleanField(default=False, verbose_name='Active Data Source?'),
        ),
        migrations.AlterField(
            model_name='resultsource',
            name='source_name',
            field=models.CharField(db_index=True, max_length=255, unique=True, verbose_name='Name Of Data Source'),
        ),
        migrations.AlterField(
            model_name='resultsource',
            name='source_short',
            field=models.CharField(max_length=5, verbose_name='Shortname Of Data Source'),
        ),
        migrations.AlterField(
            model_name='resultsource',
            name='source_slug',
            field=models.SlugField(blank=True, max_length=255, null=True, unique=True, verbose_name='Slugged Data Soure'),
        ),
        migrations.AlterField(
            model_name='resultsource',
            name='source_type',
            field=models.CharField(max_length=255, verbose_name='Ext Of File Or Type Of Source'),
        ),
        migrations.AlterField(
            model_name='resultsource',
            name='source_url',
            field=models.URLField(blank=True, max_length=1024, null=True, verbose_name='Url To Data Source'),
        ),
    ]