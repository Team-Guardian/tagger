from PyQt5 import QtCore, QtGui, QtWidgets

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

        # construct an empty pixmap object placeholder and show it
        self.createAndSetPlaceholderPixmap()

        # create null objects
        self._current_flight = None

        self.addMapToScene()
        self.setScene(self._scene)

    # show the original minimap after flight has been selected
    def setMinimap(self, flight):
        self.clearScene()
        self._current_flight = flight
        self.loadAndSetFlightAreaPixmap()

        # initialize contour
        self._img_contour = Contour(self._minimap_contour)

        self.fitInView()
        self.addMapToScene()

    def updateContourOnImageChange(self, image):
        if self._current_flight.area_map is not None:
            self.removeContourFromScene()
            self.findImageCornerPixelCoordinates(image)
            self._img_contour.updatePolygon()
            self.addContourToScene()
        else:
            print "This flight does not have an associated areamap."

    def findImageCornerPixelCoordinates(self, img):
        map_dims = self._map.boundingRect()

        current_area_map = self._current_flight.area_map

        site_elevation = img.flight.reference_altitude
        (img_upper_left_lat, img_upper_left_lon) = self.window().taggingTab.geolocator.getLatLonFromPixel(0, 0)
        (img_upper_right_lat, img_upper_right_lon) = self.window().taggingTab.geolocator.getLatLonFromPixel(img.width, 0)
        (img_lower_right_lat, img_lower_right_lon) = self.window().taggingTab.geolocator.getLatLonFromPixel(img.width, img.height)
        (img_lower_left_lat, img_lower_left_lon) = self.window().taggingTab.geolocator.getLatLonFromPixel(0, img.height)

        # interpolate the location of the image on the minimap (in px)
        self._img_contour._topLeft.setX(((img_upper_left_lon - current_area_map.ul_lon) /
                                (current_area_map.lr_lon - current_area_map.ul_lon)) * map_dims.width())
        self._img_contour._topLeft.setY(((img_upper_left_lat - current_area_map.ul_lat) /
                                (current_area_map.lr_lat - current_area_map.ul_lat)) * map_dims.height())

        self._img_contour._topRight.setX(((img_upper_right_lon - current_area_map.ul_lon) /
                                (current_area_map.lr_lon - current_area_map.ul_lon)) * map_dims.width())
        self._img_contour._topRight.setY(((img_upper_right_lat - current_area_map.ul_lat) /
                                (current_area_map.lr_lat - current_area_map.ul_lat)) * map_dims.height())

        self._img_contour._bottomRight.setX(((img_lower_right_lon - current_area_map.ul_lon) /
                                (current_area_map.lr_lon - current_area_map.ul_lon)) * map_dims.width())
        self._img_contour._bottomRight.setY(((img_lower_right_lat - current_area_map.ul_lat) /
                                (current_area_map.lr_lat - current_area_map.ul_lat)) * map_dims.height())

        self._img_contour._bottomLeft.setX(((img_lower_left_lon - current_area_map.ul_lon) /
                                (current_area_map.lr_lon - current_area_map.ul_lon)) * map_dims.width())
        self._img_contour._bottomLeft.setY(((img_lower_left_lat - current_area_map.ul_lat) /
                                (current_area_map.lr_lat - current_area_map.ul_lat)) * map_dims.height())

    def addMapToScene(self):
        self._scene.addItem(self._map)

    def addContourToScene(self):
        self._scene.addItem(self._img_contour)

    def removeContourFromScene(self):
        for item in  self._scene.items():
            if type(item) is Contour:
                self._scene.removeItem(item)

    def clearScene(self):
        for item in  self._scene.items():
            self._scene.removeItem(item)

    def fitInView(self):
        rect = QtCore.QRectF(self._map.pixmap().rect())
        if not rect.isNull():
            viewrect = self.viewport().rect()
            self._map.setPixmap(self._map.pixmap().scaled(viewrect.width(), viewrect.height(), QtCore.Qt.KeepAspectRatio))
            self.centerOn(self.viewport().rect().center())

    def createAndSetPlaceholderPixmap(self):
        self._map.setPixmap(self.generatePlaceholderPixmap())

    def generatePlaceholderPixmap(self):
        placeholder_pixmap = QtGui.QPixmap(300, 190)
        placeholder_pixmap.fill(QtCore.Qt.transparent)
        return placeholder_pixmap

    def loadAndSetFlightAreaPixmap(self):
        map_full_filepath = "./area_maps/{}".format(self._current_flight.area_map.filename)
        self._map.setPixmap(QtGui.QPixmap(map_full_filepath))

    def reset(self):
        self.clearScene()
        self.createAndSetPlaceholderPixmap()
