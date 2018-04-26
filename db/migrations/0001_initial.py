# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-12 05:10


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=30)),
                ('reference_altitude', models.IntegerField()),
                ('date', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=255, unique=True)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('roll', models.FloatField()),
                ('pitch', models.FloatField()),
                ('yaw', models.FloatField()),
                ('is_reviewed', models.BooleanField(default=False)),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='db.Flight')),
            ],
        ),
        migrations.CreateModel(
            name='Marker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='db.Image')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=30, unique=True)),
                ('subtype', models.CharField(max_length=30, unique=True)),
                ('symbol', models.CharField(max_length=1)),
                ('num_occurrences', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='marker',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='db.Tag'),
        ),
    ]
