from PyQt5 import QtWidgets, QtGui
from ui.ui_mapTab import Ui_MapTab
from gui.imageListItem import ImageListItem
from utils.geographicUtilities import Point, PolygonBounds
from utils.geolocator import Geolocator


class MapTab(QtWidgets.QWidget, Ui_MapTab):
    def __init__(self):
        super(MapTab, self).__init__()
        self.setupUi(self)
        self.currentFlight = None
        self.currentImage = None

        self.button_search.clicked.connect(self.search)
        self.list_allImages.currentItemChanged.connect(self.currentImageChanged)

        self.geolocator = Geolocator()

    def addImageToUi(self, image):
        item = ImageListItem(image.filename, image)
        self.list_allImages.addItem(item)

    def currentImageChanged(self, current, _):
        self.currentImage = current.getImage()
        self.geolocator.setCurrentImage(self.currentImage)
        self.openImage(self.currentImage.filename, self.viewer_map)

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
            bounds.addVertex(Point(*self.geolocator.getLatLonFromPixel(0, 0)))
            bounds.addVertex(Point(*self.geolocator.getLatLonFromPixel(img.width, 0)))
            bounds.addVertex(Point(*self.geolocator.getLatLonFromPixel(img.width, img.height)))
            bounds.addVertex(Point(*self.geolocator.getLatLonFromPixel(0, img.height)))
            if bounds.isPointInsideBounds(p):
                item.setHidden(False)

    def getCurrentImage(self):
        return self.currentImage

    def getCurrentFlight(self):
        return self.currentFlight

    def resetTab(self):
        pass # TODO
