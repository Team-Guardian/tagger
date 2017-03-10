from math import degrees
from osgeo import gdal
import re
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
def loadGeotiff(img_path):
    metadata = gdal.Info(img_path + '.tif') # read GeoTIFF metadata from the given image in *.tif* format
    ul, ur, lr, ll = None # create empty fields for the metadata we are searching for

    # find lines containing geo-information in metadata
    ul = re.match("(Upper Left).+$", metadata, flags=re.MULTILINE)
    # ur = re.match("(Upper Right).+$", metadata, flags=re.MULTILINE)
    lr = re.match("(Lower Right).+$", metadata, flags=re.MULTILINE)
    # ll = re.match("(Lower Left).+$", metadata, flags=re.MULTILINE)

    # parse the strings to get geodetic coordinates in DMS
    ul_dms_lon = re.findall("(\d+(?=d)|\d+(?=\')|\d+\.\d+(?=\"))(?=.*[W|E])", ul.group(0))
    ul_dms_lat = re.findall("(\d+(?=d)|\d+(?=\')|\d+\.\d+(?=\"))(?=.*[N|S])", ul.group(0))

    # ur_dms_lon = re.findall("(\d+(?=d)|\d+(?=\')|\d+\.\d+(?=\"))(?=.*[W|E])", ur.group(0))
    # ur_dms_lat = re.findall("(\d+(?=d)|\d+(?=\')|\d+\.\d+(?=\"))(?=.*[N|S])", ur.group(0))

    lr_dms_lon = re.findall("(\d+(?=d)|\d+(?=\')|\d+\.\d+(?=\"))(?=.*[W|E])", lr.group(0))
    lr_dms_lat = re.findall("(\d+(?=d)|\d+(?=\')|\d+\.\d+(?=\"))(?=.*[N|S])", lr.group(0))

    # ll_dms_lon = re.findall("(\d+(?=d)|\d+(?=\')|\d+\.\d+(?=\"))(?=.*[W|E])", ll.group(0))
    # ll_dms_lat = re.findall("(\d+(?=d)|\d+(?=\')|\d+\.\d+(?=\"))(?=.*[N|S])", ll.group(0))

    return ul_lat, ul_lon, lr_lat, lr_lon

def convertDmsToDecimal(dms_coords):

