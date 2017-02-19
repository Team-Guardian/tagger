from django.db import models


# Create your models here.

class Flight(models.Model):
    location = models.CharField(max_length=30)
    reference_altitude = models.IntegerField()
    date = models.DateField(auto_now=True)
    img_path = models.CharField(max_length=100, default='')
    intrinsic_matrix = models.CharField(max_length=100, default='')


class Image(models.Model):
    filename = models.CharField(max_length=255, unique=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    altitude = models.FloatField()
    longitude = models.FloatField()
    latitude = models.FloatField()
    roll = models.FloatField()
    pitch = models.FloatField()
    yaw = models.FloatField()
    is_reviewed = models.BooleanField(default=False)

class Tag(models.Model):
    type = models.CharField(max_length=30)
    subtype = models.CharField(max_length=30, unique=True)
    symbol = models.CharField(max_length=1)
    num_occurrences = models.IntegerField(default=0)

class Marker(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()




