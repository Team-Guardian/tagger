from PyQt5 import QtWidgets, QtGui, QtCore
from contour import Contour
from ui.ui_mapTab import Ui_MapTab
from gui.imageListItem import ImageListItem
from utils.geographicUtilities import Point, PolygonBounds
from utils.geolocate import geolocateLatLonFromPixel


class MapTab(QtWidgets.QWidget, Ui_MapTab):
    def __init__(self):
        super(MapTab, self).__init__()

        self.setupUi(self)

        # Current flight will be set once loaded
        self.current_flight = None
        # Current image will be set based on the user selecting an image from the list
        self.current_image = None

        # Sets a transparent pixmap to initialize the size of the PhotoViewer
        self.createAndSetPlaceholderAreaPixmap()

        # Connect tab buttons and clickable items to event handlers
        self.button_search.clicked.connect(self.search)
        self.list_allImages.currentItemChanged.connect(self.currentImageChanged)

    # Tab setup functions
    def setMap(self, flight):
        self.clearScene()
        self.current_flight = flight
        self.loadAndSetFlightAreaPixmap()

        self.addMapToScene()

    def loadAndSetFlightAreaPixmap(self):
        areamap_full_filepath = "./area_maps/{}".format(self.current_flight.area_map.filename)
        self.viewer_map._photo.setPixmap(QtGui.QPixmap(areamap_full_filepath))
        self.viewer_map.centerOn(self.viewer_map._photo.pixmap().rect().center())

    def addMapToScene(self):
        self.viewer_map._scene.addItem(self.viewer_map._photo)

    def createAndSetPlaceholderAreaPixmap(self):
        self.viewer_map._photo.setPixmap(self.generatePlaceholderPixmap())

    def generatePlaceholderPixmap(self):
        placeholder_pixmap = QtGui.QPixmap(1000, 1000)
        placeholder_pixmap.fill(QtCore.Qt.transparent)
        return placeholder_pixmap

    # Images list manipulation and interaction functions
    def addImageToUi(self, image):
        item = ImageListItem(image.filename, image)
        self.list_allImages.addItem(item)

    def currentImageChanged(self, current, _):
        self.current_image = current.getImage()

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
            bounds.addVertex(Point(*geolocateLatLonFromPixel(img, self.current_flight.reference_altitude, 0, 0)))
            bounds.addVertex(Point(*geolocateLatLonFromPixel(img, self.current_flight.reference_altitude, img.width, 0)))
            bounds.addVertex(Point(*geolocateLatLonFromPixel(img, self.current_flight.reference_altitude, img.width, img.height)))
            bounds.addVertex(Point(*geolocateLatLonFromPixel(img, self.current_flight.reference_altitude, 0, img.height)))
            if bounds.isPointInsideBounds(p):
                item.setHidden(False)

    # Clear and reset routines
    def clearScene(self):
        for item in self.viewer_map._scene.items():
            self.viewer_map._scene.removeItem(item)

    def resetTab(self):
        self.clearScene()

    # Accessors and mutators of the class variables
    def getCurrentImage(self):
        return self.current_image

    def getCurrentFlight(self):
        return self.current_flight
