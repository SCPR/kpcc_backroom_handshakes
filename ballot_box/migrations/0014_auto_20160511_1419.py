# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-11 21:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ballot_box', '0013_auto_20160511_1043'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contest',
            old_name='contesttype',
            new_name='office',
        ),
        migrations.AlterField(
            model_name='candidate',
            name='candidateid',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Candidate ID'),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='fullname',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name="Candidate's Full Name"),
        ),
    ]
