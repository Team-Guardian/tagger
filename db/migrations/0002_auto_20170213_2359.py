# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-13 23:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='type',
            field=models.CharField(max_length=30),
        ),
    ]
