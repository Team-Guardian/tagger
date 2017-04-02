from PyQt5 import QtCore, QtGui, QtWidgets

import utils.geolocate
from contour import Contour
from observer import *
from db.models import *

class MiniMap(QtWidgets.QGraphicsView):
    def __init__(self, parent):
        super(MiniMap, self).__init__(parent)

        # Initialize Minimap and scene objects
        self._scene = QtWidgets.QGraphicsScene(self)
        self._map = QtWidgets.QGraphicsPixmapItem()
        # Create the contour for the currently displayed image
        self._minimap_contour = QtWidgets.QGraphicsPolygonItem()
        self._img_contour = Contour(self._minimap_contour)

        # construct an empty pixmap object placeholder and show it
        self._map.setPixmap(self.generatePlaceholderPixmap())

        # create null objects
        self._current_area_map = None
        self._current_flight = None

        self.addItemsToScene()
        self.setScene(self._scene)

    # show the original minimap after flight has been selected
    def setMinimap(self, flight):
        self.clearScene()
        self._current_flight = flight
        self._current_area_map = flight.area_map
        map_full_filepath = "./area_maps/{}".format(flight.area_map.filename)
        areamap_pixmap = QtGui.QPixmap(map_full_filepath)
        self._map.setPixmap(areamap_pixmap)
        self.fitInView()
        self.addItemsToScene()

    def updateContourOnImageChange(self, image):
        if self._current_area_map is not None:
            self.findImageCornerPixelCoordinates(image)
            self._img_contour.updatePolygon()
        else:
            print "This flight does not have an associated areamap."

    def findImageCornerPixelCoordinates(self, img):
        map_dims = self._map.boundingRect()
        site_elevation = img.flight.reference_altitude
        (img_upper_left_lat, img_upper_left_lon) = utils.geolocate.geolocateLatLonFromPixel(img, site_elevation, 0, 0)
        (img_upper_right_lat, img_upper_right_lon) = utils.geolocate.geolocateLatLonFromPixel(img, site_elevation,
                                                                                              img.width, 0)
        (img_lower_right_lat, img_lower_right_lon) = utils.geolocate.geolocateLatLonFromPixel(img, site_elevation,
                                                                                              img.width,
                                                                                              img.height)
        (img_lower_left_lat, img_lower_left_lon) = utils.geolocate.geolocateLatLonFromPixel(img, site_elevation,
                                                                                            0, img.height)

        # interpolate the location of the image on the minimap (in px)
        self._img_contour._topLeft.setX(((img_upper_left_lon - self._current_area_map.ul_lon) /
                                (self._current_area_map.lr_lon - self._current_area_map.ul_lon)) * map_dims.width())
        self._img_contour._topLeft.setY(((img_upper_left_lat - self._current_area_map.ul_lat) /
                                (self._current_area_map.lr_lat - self._current_area_map.ul_lat)) * map_dims.height())

        self._img_contour._topRight.setX(((img_upper_right_lon - self._current_area_map.ul_lon) /
                                (self._current_area_map.lr_lon - self._current_area_map.ul_lon)) * map_dims.width())
        self._img_contour._topRight.setY(((img_upper_right_lat - self._current_area_map.ul_lat) /
                                (self._current_area_map.lr_lat - self._current_area_map.ul_lat)) * map_dims.height())

        self._img_contour._bottomRight.setX(((img_lower_right_lon - self._current_area_map.ul_lon) /
                                (self._current_area_map.lr_lon - self._current_area_map.ul_lon)) * map_dims.width())
        self._img_contour._bottomRight.setY(((img_lower_right_lat - self._current_area_map.ul_lat) /
                                (self._current_area_map.lr_lat - self._current_area_map.ul_lat)) * map_dims.height())

        self._img_contour._bottomLeft.setX(((img_lower_left_lon - self._current_area_map.ul_lon) /
                                (self._current_area_map.lr_lon - self._current_area_map.ul_lon)) * map_dims.width())
        self._img_contour._bottomLeft.setY(((img_lower_left_lat - self._current_area_map.ul_lat) /
                                (self._current_area_map.lr_lat - self._current_area_map.ul_lat)) * map_dims.height())

    def addItemsToScene(self):
        self._scene.addItem(self._map)
        self._scene.addItem(self._img_contour)

    def clearScene(self):
        for item in  self._scene.items():
            self._scene.removeItem(item)
        self._img_contour.deleteOldPointsFromPolygon()

    def fitInView(self):
        rect = QtCore.QRectF(self._map.pixmap().rect())
        if not rect.isNull():
            viewrect = self.viewport().rect()
            self._map.setPixmap(self._map.pixmap().scaled(viewrect.width(), viewrect.height(), QtCore.Qt.KeepAspectRatio))
            self.centerOn(self.viewport().rect().center())

    def setPlaceholderPixmap(self):
        self._map.setPixmap(self.generatePlaceholderPixmap())

    def generatePlaceholderPixmap(self):
        placeholder_pixmap = QtGui.QPixmap(300, 190)
        placeholder_pixmap.fill(QtCore.Qt.transparent)
        return placeholder_pixmap

    def reset(self):
        self._img_contour.reset()
        self.clearScene()
        self.setPlaceholderPixmap()
