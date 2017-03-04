from math import degrees
import pyexiv2
from db.models import Image


# sets telemetry info on Image from the file's EXIF tags
def loadImageWithExif(path, flight):
    if not flight:
        raise Exception("Need a flight to load an image")

    exif = pyexiv2.ImageMetadata(path)
    exif.read()
    telemetry = exif['Exif.Photo.UserComment'].raw_value.split()
    latitude, longitude, altitude = [float(x) for x in telemetry[0:3]]
    pitch, roll, yaw = [degrees(float(x)) for x in telemetry[3:]]
    return Image(filename=path, flight=flight,
                 latitude=latitude, longitude=longitude, altitude=altitude,
                 roll=roll, pitch=pitch, yaw=yaw)