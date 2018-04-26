# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-26 22:36


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0004_image_altitude'),
    ]

    operations = [
        migrations.CreateModel(
            name='AreaMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('filename', models.CharField(max_length=100, unique=True)),
                ('ul_lat', models.FloatField()),
                ('ul_lon', models.FloatField()),
                ('lr_lat', models.FloatField()),
                ('lr_lon', models.FloatField()),
            ],
        ),
        migrations.AlterField(
            model_name='image',
            name='altitude',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='flight',
            name='area_map',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='db.AreaMap'),
        ),
    ]
