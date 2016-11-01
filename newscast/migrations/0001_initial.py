# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-10-28 05:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ballot_box', '0001_initial'),
        ('election_registrar', '0002_election_election_caveats'),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topicname', models.CharField(blank=True, db_index=True, max_length=255, null=True, unique=True, verbose_name='Topic Name')),
                ('topicslug', models.SlugField(blank=True, max_length=255, null=True, unique=True, verbose_name='Topic Slug')),
                ('description', models.TextField(blank=True, null=True, verbose_name='About This Topic')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Date Modified')),
                ('contest', models.ManyToManyField(to='ballot_box.Contest')),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='election_registrar.Election')),
            ],
        ),
    ]