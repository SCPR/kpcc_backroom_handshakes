# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-13 22:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ballot_box', '0016_auto_20160511_1530'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ballotmeasure',
            old_name='name',
            new_name='fullname',
        ),
        migrations.AlterField(
            model_name='ballotmeasure',
            name='measureid',
            field=models.CharField(max_length=255, verbose_name='Measure ID'),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='party',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Political Party'),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='votecount',
            field=models.IntegerField(blank=True, null=True, verbose_name='Votes Received'),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='votepct',
            field=models.FloatField(blank=True, null=True, verbose_name='Percent Of Total Votes'),
        ),
        migrations.AlterField(
            model_name='contest',
            name='contestname',
            field=models.CharField(max_length=255, verbose_name='Display Reference To This Contest'),
        ),
        migrations.AlterField(
            model_name='contest',
            name='precinctsreporting',
            field=models.IntegerField(blank=True, null=True, verbose_name='Number Of Precincts Reporting Votes'),
        ),
        migrations.AlterField(
            model_name='contest',
            name='votersturnout',
            field=models.FloatField(blank=True, null=True, verbose_name='Percent Voters Who Cast Ballots'),
        ),
    ]
