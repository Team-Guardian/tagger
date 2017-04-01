from PyQt5 import QtCore, QtGui, QtWidgets

import utils.geolocate
from contour import Contour
from observer import *
from db.models import *

class MiniMap(QtWidgets.QGraphicsView, Observer):
    def __init__(self, parent):
        super(MiniMap, self).__init__(parent)

        # Initialize Minimap and scene objects
        self._scene = QtWidgets.QGraphicsScene(self)
        self._map = QtWidgets.QGraphicsPixmapItem()
        # Create the contour for the currently displayed image
        self._minimap_contour = QtWidgets.QGraphicsPolygonItem()
        self._img_contour = Contour(self._minimap_contour)

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

        # Populate the scene with items and show
        self.addItemsToScene()
        self.setScene(self._scene)

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
                    self.findImageCornerPixelCoordinates(img)
                    self._img_contour.updatePolygon()
                else:
                    print "Error! Selected image does not exist in the database"
                    return

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

    def removeContour(self):
        scene_objects = self._scene.items()
        for item in scene_objects:
            if type(item) is Contour:
                self._scene.removeItem(item)

    def addItemsToScene(self):
        self._scene.addItem(self._map)
        self._scene.addItem(self._img_contour)

    def restoreOriginalPixmap(self):
        self._map.setPixmap(self._original_pixmap)
        self.fitInView()

    def fitInView(self):
        rect = QtCore.QRectF(self._map.pixmap().rect())
        if not rect.isNull():
            viewrect = self.viewport().rect()
            self._map.setPixmap(self._map.pixmap().scaled(viewrect.width(), viewrect.height(), QtCore.Qt.KeepAspectRatio))
            self.centerOn(self._map.pixmap().rect().center())

    def clearMinimap(self):
        for item in self._scene.items(): # clear the bounding box
            if type(item) == QtWidgets.QGraphicsLineItem:
                self._scene.removeItem(item)
        self._original_pixmap = QtGui.QPixmap(300, 190)
        self._original_pixmap.fill(QtCore.Qt.transparent)
        self._map.setPixmap(self._original_pixmap)
