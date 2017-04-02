# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Tag = apps.get_model("db", "Tag")
    Marker = apps.get_model("db", "Marker")

    db_alias = schema_editor.connection.alias

    Marker.objects.using(db_alias).all().delete()
    Tag.objects.using(db_alias).all().delete()

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('db', '0008_auto_20170325_0520'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]