from PyQt5 import QtCore, QtGui, QtWidgets
from observer import Observer
from utils.geolocate import geolocateLatLonFromPixel
from math import cos, asin, sqrt

# offset of the scale in viewport coordinates
HEIGHT_OFFSET = 70
WIDTH_OFFSET = 70

# default starting values
DEFAULT_SCALE_WIDTH_FRACTION = 0.15
DEFAULT_FONT_POINT_SIZE = 25
DEFAULT_PEN_WIDTH = 6

ROUNDING_FACTOR = 2

class Scale(Observer):
    def __init__(self):
        # lines that make up the scale
        self.horizontal_line = QtWidgets.QGraphicsLineItem()
        self.vertical_line_start = QtWidgets.QGraphicsLineItem()
        self.vertical_line_middle = QtWidgets.QGraphicsLineItem()
        self.vertical_line_end = QtWidgets.QGraphicsLineItem()

        # text box to show distance that scale represents
        self.distance_text_box = QtWidgets.QGraphicsTextItem()

        # empty graphics view object to be filled by PhotoViewer
        self.graphics_view = None

        # current image, changes on every image change event
        self.current_image = None

        # apply style to the scale lines
        self.setScaleStyle()

    # class setters
    def setGraphicsView(self, photoviewer_graphics_view):
        self.graphics_view = photoviewer_graphics_view

    def setCurrentImage(self, image):
        self.current_image = image

    # create and apply style to the scale
    def setScaleStyle(self):
        pen = QtGui.QPen()
        pen.setColor(QtCore.Qt.red)
        self.adjustScalePenThickness(pen)
        self.setPenToGraphicsItems(pen)

        text_font = QtGui.QFont()
        text_font.setPointSize(DEFAULT_FONT_POINT_SIZE)
        self.distance_text_box.setDefaultTextColor(QtCore.Qt.red)
        self.distance_text_box.setFont(text_font)

    def adjustScalePenThickness(self, current_pen):
        if self.graphics_view is not None:
            current_pen.setWidth(self.getVisibleImageRegionHeight() * 0.00175)
        return current_pen

    def adjustScaleTextBoxFontSize(self, current_font):
        if self.graphics_view is not None:
            current_font.setPointSize(self.getVisibleImageRegionHeight() * 0.015)
        return current_font

    def setPenToGraphicsItems(self, pen):
        self.horizontal_line.setPen(pen)
        self.vertical_line_start.setPen(pen)
        self.vertical_line_middle.setPen(pen)
        self.vertical_line_end.setPen(pen)

    # public API to update the scale when view changes
    def updateScale(self):
        scene_point, scale_width_in_pixels = self.calculateScaleWidth()
        if scene_point == 0 and scale_width_in_pixels == 0:
            return
        else:
            self.paintScale(scene_point, scale_width_in_pixels)

    def calculateScaleWidth(self):
        if self.current_image is not None:
            scene_point_start, scene_point_default_end = self.getSceneCoordinatesForScale()
            x_start = scene_point_start.x()
            y_start = scene_point_start.y()
            default_x_end = scene_point_default_end.x()
            default_y_end = scene_point_default_end.y()

            # Find geodetic coordinates of two points on the image
            lat_start, lon_start = geolocateLatLonFromPixel(self.current_image, self.current_image.flight.reference_altitude, x_start, y_start)
            lat_end, lon_end = geolocateLatLonFromPixel(self.current_image, self.current_image.flight.reference_altitude, default_x_end, default_y_end)

            # Find ground distance between two points
            distance_in_meters = self.distanceBetweenGeodeticCoordinates(lat_start, lon_start, lat_end, lon_end)
            # Find the nearest "pretty" number to display on scale
            reduced_distance_in_meters = distance_in_meters - (distance_in_meters % ROUNDING_FACTOR)

            # Using proportions, find the width of the scale that will correspond to the "pretty" distance
            scale_width_in_pixels = (x_start - default_x_end) * (reduced_distance_in_meters / distance_in_meters)

            self.distance_text_box.setHtml('{} m'.format(reduced_distance_in_meters))

            return scene_point_start, scale_width_in_pixels
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

        self.horizontal_line.setLine(*self.getHorizontalLineCoordinates(x_pos, y_pos, scale_width))
        self.vertical_line_start.setLine(*self.getStartVerticalLineCoordinates(x_pos, y_pos, scale_width))
        self.vertical_line_middle.setLine(*self.getMiddleLineCoordinates(x_pos, y_pos, scale_width))
        self.vertical_line_end.setLine(*self.getEndVerticalLineCoordinates(x_pos, y_pos, scale_width))
        self.distance_text_box.setPos(*self.getTextboxOffset(x_pos, y_pos, scale_width))

        updated_pen = self.adjustScalePenThickness(self.horizontal_line.pen())
        updated_font = self.adjustScaleTextBoxFontSize(self.distance_text_box.font())
        self.setPenToGraphicsItems(updated_pen)
        self.distance_text_box.setFont(updated_font)

        self.addScaleToScene()

    def getHorizontalLineCoordinates(self, x_pos, y_pos, scale_width):
        x_start = x_pos
        y_start = y_pos
        x_end = x_start - scale_width
        y_end = y_start
        return x_start, y_start, x_end, y_end

    def getStartVerticalLineCoordinates(self, x_pos, y_pos, scale_width):
        x_start = x_pos
        y_start = y_pos
        x_end = x_start
        y_end = y_pos - (self.getVisibleImageRegionHeight() * 0.011)
        return x_start, y_start, x_end, y_end

    def getEndVerticalLineCoordinates(self, x_pos, y_pos, scale_width):
        x_start = x_pos - scale_width
        y_start = y_pos
        x_end = x_start
        y_end = y_pos - (self.getVisibleImageRegionHeight() * 0.011)
        return x_start, y_start, x_end, y_end

    def getMiddleLineCoordinates(self, x_pos, y_pos, scale_width):
        x_start = x_pos - (scale_width/2)
        y_start = y_pos
        x_end = x_start
        y_end = y_pos - (self.getVisibleImageRegionHeight() * 0.006)
        return x_start, y_start, x_end, y_end

    def getTextboxOffset(self, x_pos, y_pos, scale_width):
        x = x_pos - scale_width
        y = y_pos - (self.getVisibleImageRegionHeight() * 0.055)
        return x, y

    def getVisibleImageRegionHeight(self):
        return (self.graphics_view.mapToScene(0, self.graphics_view.viewport().size().height()).y() -
                                      self.graphics_view.mapToScene(0, 0).y())

    # loop through all items shown in the scene and delete items that belong to Scale class
    def deleteScaleFromScene(self):
        for item in self.graphics_view.getScene().items():
            # TODO: add these items to the group and delete based on group attribute
            if item == self.horizontal_line or item == self.vertical_line_start or item == self.vertical_line_end or item == self.vertical_line_middle or item == self.distance_text_box:
                self.graphics_view.getScene().removeItem(item)

    def addScaleToScene(self):
        self.graphics_view.getScene().addItem(self.horizontal_line)
        self.graphics_view.getScene().addItem(self.vertical_line_start)
        self.graphics_view.getScene().addItem(self.vertical_line_middle)
        self.graphics_view.getScene().addItem(self.vertical_line_end)
        self.graphics_view.getScene().addItem(self.distance_text_box)

    # maps viewport coordinates to scene coordinates to geolocate correct pixel points
    def getSceneCoordinatesForScale(self):
        x_start_coord_in_viewport = self.graphics_view.viewport().size().width() - WIDTH_OFFSET
        y_start_coord_in_viewport = self.graphics_view.viewport().size().height() - HEIGHT_OFFSET
        scene_point_start = self.graphics_view.mapToScene(x_start_coord_in_viewport, y_start_coord_in_viewport)
        # 10 % of viewport width always
        x_end_coord_in_viewport = x_start_coord_in_viewport - (self.graphics_view.viewport().size().width() * DEFAULT_SCALE_WIDTH_FRACTION)
        y_end_coord_in_viewport = y_start_coord_in_viewport
        scene_point_default_end = self.graphics_view.mapToScene(x_end_coord_in_viewport, y_end_coord_in_viewport)
        return scene_point_start, scene_point_default_end
