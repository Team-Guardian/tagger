# loadGeotiff(...): http://gis.stackexchange.com/questions/57834/how-to-get-raster-corner-coordinates-using-python-gdal-bindings/57837#57837

from math import degrees
from osgeo import gdal, osr
import pyexiv2
from db.dbHelper import create_image


# reads EXIF from file on disk and returns new Image in DB
def createImageWithExif(path, flight):
    if not flight:
        raise Exception("Need a flight to load an image")

    exif = pyexiv2.ImageMetadata(path)
    exif.read()
    width, height = exif.dimensions
    telemetry = exif['Exif.Photo.UserComment'].raw_value.split()
    # degrees, degrees, metres
    latitude, longitude, altitude = [float(x) for x in telemetry[0:3]]
    # store as degrees, but exif has radians
    pitch, roll, yaw = [degrees(float(x)) for x in telemetry[3:]]
    return create_image(filename=path, width=width, height=height, flight=flight,
                        latitude=latitude, longitude=longitude, altitude=altitude,
                        roll=roll, pitch=pitch, yaw=yaw)

def loadGeotiff(img_path):
    raster=img_path + '.tif'
    ds=gdal.Open(raster)

    gt=ds.GetGeoTransform()
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    ext=GetExtent(gt,cols,rows)

    src_srs=osr.SpatialReference()
    src_srs.ImportFromWkt(ds.GetProjection())
    #tgt_srs=osr.SpatialReference()
    #tgt_srs.ImportFromEPSG(4326)
    tgt_srs = src_srs.CloneGeogCS()

    geo_ext=ReprojectCoords(ext,src_srs,tgt_srs)
    return geo_ext

def GetExtent(gt,cols,rows):
    ''' Return list of corner coordinates from a geotransform

        @type gt:   C{tuple/list}
        @param gt: geotransform
        @type cols:   C{int}
        @param cols: number of columns in the dataset
        @type rows:   C{int}
        @param rows: number of rows in the dataset
        @rtype:    C{[float,...,float]}
        @return:   coordinates of each corner
    '''
    ext=[]
    xarr=[0,cols]
    yarr=[0,rows]

    for px in xarr:
        for py in yarr:
            x=gt[0]+(px*gt[1])+(py*gt[2])
            y=gt[3]+(px*gt[4])+(py*gt[5])
            ext.append([x,y])
        yarr.reverse()
    return ext

def ReprojectCoords(coords,src_srs,tgt_srs):
    ''' Reproject a list of x,y coordinates.

        @type geom:     C{tuple/list}
        @param geom:    List of [[x,y],...[x,y]] coordinates
        @type src_srs:  C{osr.SpatialReference}
        @param src_srs: OSR SpatialReference object
        @type tgt_srs:  C{osr.SpatialReference}
        @param tgt_srs: OSR SpatialReference object
        @rtype:         C{tuple/list}
        @return:        List of transformed [[x,y],...[x,y]] coordinates
    '''
    trans_coords=[]
    transform = osr.CoordinateTransformation(src_srs, tgt_srs)
    for x,y in coords:
        x,y,z = transform.TransformPoint(x,y)
        trans_coords.append([x,y])
    return trans_coords