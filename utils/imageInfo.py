from math import degrees
import pyexiv2


# sets telemetry info on Image from the file's EXIF tags
def loadExif(img):
    path = img.filename
    exif = pyexiv2.ImageMetadata(path)
    exif.read()
    telemetry = exif['Exif.Photo.UserComment'].raw_value.split()
    img.latitude, img.longitude, img.altitude = [float(x) for x in telemetry[0:3]]
    img.pitch, img.roll, img.yaw = [degrees(float(x)) for x in telemetry[3:]]
