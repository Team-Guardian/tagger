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

# load geotiff data and convert image from tiff to png
def loadGeotiff(img):
    ul_lat, ul_lon = 49.922492, -98.312083
    lr_lat, lr_lon = 49.886744, -98.233800
    return ul_lat, ul_lon, lr_lat, lr_lon