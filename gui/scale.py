from PyQt5 import QtCore, QtGui, QtWidgets
from observer import Observer
from utils.geolocate import geolocateLatLonFromPixel
from math import cos, asin, sqrt

HEIGHT_OFFSET = 70
WIDTH_OFFSET = 70
DEFAULT_WIDTH = 300
ROUNDING_FACTOR = 2

class Scale(Observer):
    def __init__(self):
        # lines that make up the scale
        self.horizontal_line = QtWidgets.QGraphicsLineItem()
        self.vertical_line_start = QtWidgets.QGraphicsLineItem()
        self.vertical_line_end = QtWidgets.QGraphicsLineItem()

        # text box to show distance that scale represents
        self.distance_text_box = QtWidgets.QGraphicsTextItem()

        # apply style to the scale lines
        self.setScalePen()

        # create an empty graphics view object
        self.graphics_view = None

        # current image
        self.current_image = None

    def setGraphicsView(self, photoviewer_graphics_view):
        self.graphics_view = photoviewer_graphics_view

    def setCurrentImage(self, image):
        self.current_image = image

    def setScalePen(self):
        pen = QtGui.QPen()
        pen.setColor(QtCore.Qt.red)
        pen.setWidth(6)
        self.horizontal_line.setPen(pen)
        self.vertical_line_start.setPen(pen)
        self.vertical_line_end.setPen(pen)

        text_font = QtGui.QFont()
        text_font.setPointSize(20)
        self.distance_text_box.setDefaultTextColor(QtCore.Qt.red)
        self.distance_text_box.setFont(text_font)

    def updateScale(self):
        scene_point, scale_width_in_pixels = self.calculateScaleWidth()

        if scene_point == 0 and scale_width_in_pixels == 0:
            return
        else:
            self.paintScale(scene_point, scale_width_in_pixels)

    def calculateScaleWidth(self):
        if self.current_image is not None:
            scene_point = self.getSceneCoordinatesForScale()
            x_start = scene_point.x()
            y_start = scene_point.y()
            x_end = x_start - DEFAULT_WIDTH
            y_end = y_start

            # Find geodetic coordinates of two points on the image
            lat_start, lon_start = geolocateLatLonFromPixel(self.current_image, self.current_image.flight.reference_altitude, x_start, y_start)
            lat_end, lon_end = geolocateLatLonFromPixel(self.current_image, self.current_image.flight.reference_altitude, x_end, y_end)

            # Find ground distance between two points
            distance_in_meters = self.distanceBetweenGeodeticCoordinates(lat_start, lon_start, lat_end, lon_end)
            # Find the nearest "pretty" number to display on scale
            reduced_distance_in_meters = distance_in_meters - (distance_in_meters % ROUNDING_FACTOR)

            # Using proportions, find the width of the scale that will correspond to the "pretty" distance
            scale_width_in_pixels = DEFAULT_WIDTH * (reduced_distance_in_meters / distance_in_meters)

            self.distance_text_box.setHtml('{} m'.format(reduced_distance_in_meters))

            return scene_point, scale_width_in_pixels
        else:
            return 0, 0

    # Finding the distance between two lat, lon points:
    # http://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula
    def distanceBetweenGeodeticCoordinates(self, lat1, lon1, lat2, lon2):
        p = 0.017453292519943295  # Pi/180
        a = 0.5 - cos((lat2 - lat1) * p) / 2.0 + cos(lat1 * p) * cos(lat2 * p) * (1.0 - cos((lon2 - lon1) * p)) / 2.0
        return 12742 * asin(sqrt(a)) * 1000 # convert to meters

    def paintScale(self, scene_point, scale_width):
        self.deleteScaleFromScene()

        x_pos = scene_point.x()
        y_pos = scene_point.y()

        self.horizontal_line.setLine(x_pos, y_pos , x_pos - scale_width, y_pos)
        self.vertical_line_start.setLine(x_pos, y_pos, x_pos, y_pos - 10)
        self.vertical_line_end.setLine(x_pos - scale_width, y_pos, x_pos - scale_width, y_pos - 10)
        self.distance_text_box.setPos(x_pos - scale_width, y_pos - 70)
        self.addScaleToScene()

    def deleteScaleFromScene(self):
        for item in self.graphics_view.getScene().items():
            if item == self.horizontal_line or item == self.vertical_line_start or item == self.vertical_line_end or item == self.distance_text_box:
                self.graphics_view.getScene().removeItem(item)

    def addScaleToScene(self):
        self.graphics_view.getScene().addItem(self.horizontal_line)
        self.graphics_view.getScene().addItem(self.vertical_line_start)
        self.graphics_view.getScene().addItem(self.vertical_line_end)
        self.graphics_view.getScene().addItem(self.distance_text_box)

    def getSceneCoordinatesForScale(self):
        x_coord_in_viewport = self.graphics_view.viewport().size().width() - WIDTH_OFFSET
        y_coord_in_viewport = self.graphics_view.viewport().size().height() - HEIGHT_OFFSET
        scene_point = self.graphics_view.mapToScene(x_coord_in_viewport, y_coord_in_viewport)
        return scene_point
