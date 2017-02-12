from __future__ import unicode_literals
from django.db import models


# Create your models here.

class Flight(models.Model):
    location = models.CharField(max_length=30)
    reference_altitude = models.IntegerField()
    date = models.DateField(auto_now=True)


class Image(models.Model):
    filename = models.CharField(max_length=255, unique=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    roll = models.FloatField()
    pitch = models.FloatField()
    yaw = models.FloatField()
    is_reviewed = models.BooleanField(default=False)

class Tag(models.Model):
    type = models.CharField(max_length=30, unique=True)
    subtype = models.CharField(max_length=30, unique=True)
    symbol = models.CharField(max_length=1)
    num_occurrences = models.IntegerField(default=0)

class Marker(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()




