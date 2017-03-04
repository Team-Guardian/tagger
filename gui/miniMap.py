from PyQt5 import QtCore, QtGui, QtWidgets

import utils.geolocate
from observer import *
from db.models import *

class MiniMap(QtWidgets.QGraphicsView, Observer):
    def __init__(self, parent):
        super(MiniMap, self).__init__(parent)

        # initialize objects
        self._scene = QtWidgets.QGraphicsScene(self)
        self._map = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._map)
        self.setScene(self._scene)
        self._img_contour = Contour()

        # construct an empty pixmap object placeholder and show it
        # self._original_pixmap = QtGui.QPixmap(self._map.boundingRect().width(), self._map.boundingRect().height())
        self._original_pixmap = QtGui.QPixmap(300, 190)
        self._original_pixmap.fill(QtCore.Qt.transparent)
        self._map.setPixmap(self._original_pixmap)

        # configure MiniMap to be an observer of TaggingTab
        self.window().addObserver(self)

        # create null objects
        self._current_area_map = None
        self._current_flight = None

    # show the original minimap after flight has been selected
    def setMinimap(self, flight):
        self._current_flight = flight
        self._current_area_map = flight.area_map

        self._map_full_filepath = "./area_maps/" + flight.area_map.filename
        self._original_pixmap = QtGui.QPixmap(self._map_full_filepath)
        self._map.setPixmap(self._original_pixmap)
        self.fitInView()

    def notify(self, event, id, data):
        if event is "CURRENT_IMG_CHANGED":
            if self._current_area_map is not None:
                # try to retrieve full image object from DB
                if Image.objects.filter(filename=data).exists():
                    img = Image.objects.filter(filename=data).last()
                    map_dims = self._map.boundingRect()

                    site_elevation = img.flight.reference_altitude
                    (img_upper_left_lat, img_upper_left_lon) = utils.geolocate.geolocate_pixel(img, site_elevation, 0, 0)
                    (img_upper_right_lat, img_upper_right_lon) = utils.geolocate.geolocate_pixel(img, site_elevation,
                                                                                                 map_dims.width(), 0)
                    (img_lower_right_lat, img_lower_right_lon) = utils.geolocate.geolocate_pixel(img, site_elevation,
                                                                                                 map_dims.width(), map_dims.height())
                    (img_lower_left_lat, img_lower_left_lon) = utils.geolocate.geolocate_pixel(img, site_elevation,
                                                                                               0, map_dims.height())

                    # interpolate the location of the image on the minimap (in px)
                    self._img_contour._topLeftX = ((img_upper_left_lon - self._current_area_map.ul_lon) / (
                    self._current_area_map.lr_lon - self._current_area_map.ul_lon)) * map_dims.width()
                    self._img_contour._topLeftY = ((img_upper_left_lat - self._current_area_map.ul_lat) / (
                    self._current_area_map.lr_lat - self._current_area_map.ul_lat)) * map_dims.height()

                    self._img_contour._topRightX = ((img_upper_right_lon - self._current_area_map.ul_lon) / (
                    self._current_area_map.lr_lon - self._current_area_map.ul_lon)) * map_dims.width()
                    self._img_contour._topRightY = ((img_upper_right_lat - self._current_area_map.ul_lat) / (
                    self._current_area_map.lr_lat - self._current_area_map.ul_lat)) * map_dims.height()

                    self._img_contour._bottomRightX = ((img_lower_right_lon - self._current_area_map.ul_lon) / (
                    self._current_area_map.lr_lon - self._current_area_map.ul_lon)) * map_dims.width()
                    self._img_contour._bottomRightY = ((img_lower_right_lat - self._current_area_map.ul_lat) / (
                    self._current_area_map.lr_lat - self._current_area_map.ul_lat)) * map_dims.height()

                    self._img_contour._bottomLeftX = ((img_lower_left_lon - self._current_area_map.ul_lon) / (
                    self._current_area_map.lr_lon - self._current_area_map.ul_lon)) * map_dims.width()
                    self._img_contour._bottomLeftY = ((img_lower_left_lat - self._current_area_map.ul_lat) / (
                    self._current_area_map.lr_lat - self._current_area_map.ul_lat)) * map_dims.height()

                    self.showImageContourOnMinimap(self._img_contour)
                else:
                    print "Error! Selected image does not exist in the database"
                    return

    def restoreOriginalPixmap(self):
        self._map.setPixmap(self._original_pixmap)
        self.fitInView()

    def fitInView(self):
        rect = QtCore.QRectF(self._map.pixmap().rect())
        if not rect.isNull():
            viewrect = self.viewport().rect()
            self._map.setPixmap(self._map.pixmap().scaled(viewrect.width(), viewrect.height(), QtCore.Qt.KeepAspectRatio))
            self.centerOn(self._map.pixmap().rect().center())

    def showImageContourOnMinimap(self, contour_coords):

        line_item1 = QtWidgets.QGraphicsLineItem(contour_coords._topLeftX, contour_coords._topLeftY,
                                                 contour_coords._topRightX, contour_coords._topRightY)
        line_item2 = QtWidgets.QGraphicsLineItem(contour_coords._topRightX, contour_coords._topRightY,
                                                 contour_coords._bottomRightX, contour_coords._bottomRightY)
        line_item3 = QtWidgets.QGraphicsLineItem(contour_coords._bottomRightX, contour_coords._bottomRightY,
                                                 contour_coords._bottomLeftX, contour_coords._bottomLeftY)
        line_item4 = QtWidgets.QGraphicsLineItem(contour_coords._bottomLeftX, contour_coords._bottomLeftY,
                                                 contour_coords._topLeftX, contour_coords._topLeftY)

        pen = QtGui.QPen()
        pen.setColor(QtCore.Qt.red)
        pen.setWidth(2)
        line_item1.setPen(pen)
        line_item2.setPen(pen)
        line_item3.setPen(pen)
        line_item4.setPen(pen)

        self._scene.addItem(line_item1)
        self._scene.addItem(line_item2)
        self._scene.addItem(line_item3)
        self._scene.addItem(line_item4)

# utility class to hold and access current image corner coordinates in a
class Contour():
    def __init__(self):
        self._topLeftX = 0
        self._topLeftY = 0

        self._topRightX = 0
        self._topRightY = 0

        self._bottomRightX = 0
        self._bottomRightY = 0

        self._bottomLeftX = 0
        self._bottomLeftY = 0
