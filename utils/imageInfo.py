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

    # find lines containing geo-information in metadata
    ul = re.search("(Upper Left).+$", metadata, flags=re.MULTILINE)
    # ur = re.match("(Upper Right).+$", metadata, flags=re.MULTILINE)
    lr = re.search("(Lower Right).+$", metadata, flags=re.MULTILINE)
    # ll = re.match("(Lower Left).+$", metadata, flags=re.MULTILINE)

    lon_pattern = re.compile("\d+(?=d.*[W|E])|\d+(?=\'.*[W|E])|\d+\.\d+(?=\"[W|E])|[W|E]")
    lat_pattern = re.compile("\d+(?!.*[W|E])(?=d.*[N|S])|\d+(?!.*[W|E])(?=\'.*[N|S])|\d+\.\d+(?!.*[W|E])(?=\"[N|S])|[N|S]")

    # parse the strings to get geodetic coordinates in DMS
    ul_dms_lon = lon_pattern.findall(ul.group(0))
    ul_dms_lat = lat_pattern.findall(ul.group(0))

    # ur_dms_lon = re.findall("(\d+(?=d)|\d+(?=\')|\d+\.\d+(?=\"))(?=.*[W|E])", ur.group(0))
    # ur_dms_lat = re.findall("(\d+(?=d)|\d+(?=\')|\d+\.\d+(?=\"))(?=.*[N|S])", ur.group(0))

    lr_dms_lon = lon_pattern.findall(lr.group(0))
    lr_dms_lat = lat_pattern.findall(lr.group(0))

    # ll_dms_lon = re.findall("(\d+(?=d)|\d+(?=\')|\d+\.\d+(?=\"))(?=.*[W|E])", ll.group(0))
    # ll_dms_lat = re.findall("(\d+(?=d)|\d+(?=\')|\d+\.\d+(?=\"))(?=.*[N|S])", ll.group(0))

    ul_lat = convertDmsToDecimal(ul_dms_lat)
    ul_lon = convertDmsToDecimal(ul_dms_lon)
    lr_lat = convertDmsToDecimal(lr_dms_lat)
    lr_lon = convertDmsToDecimal(lr_dms_lon)

    return ul_lat, ul_lon, lr_lat, lr_lon

# data is fed in as a list of strings of form [d, m, s, hemisphere]
def convertDmsToDecimal(dms_coords):
    degree_coords = float(dms_coords[0]) + ((float(dms_coords[1]) + (float(dms_coords[2])/60) )/60)
    if dms_coords[3] == 'S' or dms_coords[3] == 'W':
        degree_coords = -degree_coords
    return degree_coords