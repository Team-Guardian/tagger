from PyQt5 import QtWidgets, QtGui
from ui.ui_mapTab import Ui_MapTab
from gui.imageListItem import ImageListItem
from utils.geographicUtilities import Point, PolygonBounds
from utils.geolocate import geolocateLatLonFromPixel
from observer import *


class MapTab(QtWidgets.QWidget, Ui_MapTab, Observer):
    def __init__(self):
        super(MapTab, self).__init__()
        Observer.__init__(self)

        self.setupUi(self)
        self.currentFlight = None
        self.currentImage = None

        self.button_search.clicked.connect(self.search)
        self.list_allImages.currentItemChanged.connect(self.currentImageChanged)

        self.viewer_map.getPhotoItem().addObserver(self)

    def notify(self, event, id, data):
        if event is "FIND_IMAGES":
            point_pixel_x_coord = self.viewer_map.getPhotoItem().map_context_menu.pixel_x_invocation_coord
            point_pixel_y_coord = self.viewer_map.getPhotoItem().map_context_menu.pixel_y_invocation_coord
            point_lat, point_lon = geolocateLatLonFromPixel(self.currentImage, self.currentFlight.reference_altitude,
                                                point_pixel_x_coord, point_pixel_y_coord)
            self.line_latitude.setText('{}'.format(point_lat))
            self.line_longitude.setText('{}'.format(point_lon))
            self.search()
        elif event is "COPY_LAT_LON":
            point_pixel_x_coord = self.viewer_map.getPhotoItem().map_context_menu.pixel_x_invocation_coord
            point_pixel_y_coord = self.viewer_map.getPhotoItem().map_context_menu.pixel_y_invocation_coord
            lat, lon = geolocateLatLonFromPixel(self.currentImage, self.currentFlight.reference_altitude, point_pixel_x_coord, point_pixel_y_coord)
            QtWidgets.QApplication.clipboard().setText('{}, {}'.format(lat, lon))
        elif event is "RESET_FILTERS":
            self.line_latitude.setText('')
            self.line_longitude.setText('')
            # unhide all
            for i in range(self.list_allImages.count()):
                self.list_allImages.item(i).setHidden(False)
            return

    def addImageToUi(self, image):
        item = ImageListItem(image.filename, image)
        self.list_allImages.addItem(item)

    def currentImageChanged(self, current, _):
        self.currentImage = current.getImage()
        self.openImage('./flights/{}/{}'.format(self.currentFlight.img_path, self.currentImage.filename), self.viewer_map)

    def openImage(self, path, viewer):
        viewer.setPhoto(QtGui.QPixmap(path))

    def search(self):
        if len(self.line_latitude.text()) == 0 and len(self.line_longitude.text()) == 0:
            # unhide all
            for i in range(self.list_allImages.count()):
                self.list_allImages.item(i).setHidden(False)
            return

        # both are required
        if len(self.line_latitude.text()) == 0 or len(self.line_longitude.text()) == 0:
            return

        # hide all
        for i in range(self.list_allImages.count()):
            self.list_allImages.item(i).setHidden(True)

        lat = float(self.line_latitude.text())
        lon = float(self.line_longitude.text())
        p = Point(lat, lon)
        for i in range(self.list_allImages.count()):
            item = self.list_allImages.item(i)
            img = item.getImage()
            bounds = PolygonBounds()
            bounds.addVertex(Point(*geolocateLatLonFromPixel(img, self.currentFlight.reference_altitude, 0, 0)))
            bounds.addVertex(Point(*geolocateLatLonFromPixel(img, self.currentFlight.reference_altitude, img.width, 0)))
            bounds.addVertex(Point(*geolocateLatLonFromPixel(img, self.currentFlight.reference_altitude, img.width, img.height)))
            bounds.addVertex(Point(*geolocateLatLonFromPixel(img, self.currentFlight.reference_altitude, 0, img.height)))
            if bounds.isPointInsideBounds(p):
                item.setHidden(False)

    def copyPointLatLonToClipboard(self):
        pass

    def getCurrentImage(self):
        return self.currentImage

    def getCurrentFlight(self):
        return self.currentFlight

    def resetTab(self):
        pass # TODO
