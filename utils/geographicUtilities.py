from geolocate import geolocateLatLonFromPixel

# Definitions and utilities for performing geographic operations.

import sys, os
import pyexiv2
from db.models import Image

# Combine a point with an existing average of points.
# Don't use for distances spanning many km
def addToAverage(count, average, new):
    average.lat = (average.lat * count + new.lat) / (count + 1)
    average.long = (average.long * count + new.long) / (count + 1)

def exportAllTelemetry(flight, filename):
    out = open(filename, 'w')
    out.write('name,latitude,longitude,altitude,pitch,roll,yaw\n')

    for img in Image.objects.filter(flight=flight):
        telemetry = [img.filename,
                     img.latitude, img.longitude,
                     img.altitude - flight.reference_altitude,
                     img.pitch, img.roll, img.yaw]
        out.write(str.join(",", [str(val) for val in telemetry]) + "\n")

    out.close()

# Get geographic bounds for any frame - can be an entire image or a subset
def getFrameBounds(image, reference_altitude, top_left_pixel=None, bottom_right_pixel=None):
    bounds = PolygonBounds()
    if top_left_pixel and bottom_right_pixel:
        bounds.addVertex(Point(*geolocateLatLonFromPixel(image, reference_altitude, top_left_pixel.x(),
                                            top_left_pixel.y())))
        bounds.addVertex(Point(*geolocateLatLonFromPixel(image, reference_altitude, bottom_right_pixel.x(),
                                            top_left_pixel.y())))
        bounds.addVertex(Point(*geolocateLatLonFromPixel(image, reference_altitude, bottom_right_pixel.x(),
                                            bottom_right_pixel.y())))
        bounds.addVertex(Point(*geolocateLatLonFromPixel(image, reference_altitude, top_left_pixel.x(),
                                            bottom_right_pixel.y())))
    else:
        bounds.addVertex(Point(*geolocateLatLonFromPixel(image, reference_altitude, 0, 0)))
        bounds.addVertex(Point(*geolocateLatLonFromPixel(image, reference_altitude, image.width, 0)))
        bounds.addVertex(Point(*geolocateLatLonFromPixel(image, reference_altitude, image.width, image.height)))
        bounds.addVertex(Point(*geolocateLatLonFromPixel(image, reference_altitude, 0, image.height)))
    return bounds


class Point(object):
    def __init__(self, lat, lon):
        self.lat = lat
        self.long = lon

# a simple container for the geographic corners of a geotagged image
class PolygonBounds(object):
    def __init__(self):
        # Point objects
        self.vertices = []

        # axis-aligned bounding box, i.e. extents
        self.minLat = 0.0
        self.maxLat = 0.0
        self.minLong = 0.0
        self.maxLong = 0.0

    def addVertex(self, vertex):
        self.vertices.append(vertex)
        self.updateExtents()

    def updateVertex(self, index, vertex):
        if index >= len(self.vertices):
            raise IndexError("Attempted to update vertex " + str(index) + " with only " + str(len(self.vertices)) + " defined.")

        self.vertices[index] = vertex
        self.updateExtents()

    def updateExtents(self):
        lats = [p.lat for p in self.vertices]
        self.minLat = min(lats)
        self.maxLat = max(lats)

        longs = [p.long for p in self.vertices]
        self.minLong = min(longs)
        self.maxLong = max(longs)

    # Simple bounds checking. Will become inaccurate when polygon edges span large (many km) distances
    def isPointInsideBounds(self, point):
        # fail fast by checking extents
        if point.lat < self.minLat or \
                point.lat > self.maxLat or \
                point.long < self.minLong or \
                point.long > self.maxLong:
            return False

        # adapted from http://web.archive.org/web/20161116163747/https://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html

        # start with last vertex to get edge between last and first
        v1 = self.vertices[-1]
        sides = len(self.vertices)
        inside = False

        for v2 in self.vertices:
            # is point within range of latitudes on this edge and can intersect it?
            if (point.lat < v2.lat) != (point.lat < v1.lat):
                # does ray from point to east intersect current edge?
                if point.long < (v1.long - v2.long) * (point.lat - v2.lat) / (v1.lat - v2.lat) + v2.long:
                    # crossed an edge, change status
                    inside = not inside

            # move follower forward
            v1 = v2

        return inside

