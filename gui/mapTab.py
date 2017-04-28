from PyQt5 import QtWidgets, QtGui, QtCore
from contour import Contour
from ui.ui_mapTab import Ui_MapTab
from gui.imageListItem import ImageListItem
from utils.geographicUtilities import Point, PolygonBounds, getFrameBounds
from utils.geolocate import geolocateLatLonFromPixel
from mapContextMenu import MapContextMenu
from observer import *


class MapTab(QtWidgets.QWidget, Ui_MapTab, Observer):
    def __init__(self):
        super(MapTab, self).__init__()
        Observer.__init__(self)

        self.setupUi(self)

        # Current flight will be set once loaded
        self.current_flight = None
        # Current image will be set based on the user selecting an image from the list
        self.current_image = None
        self.current_contour = None

        # Parent QGraphicsPolygonItem to create contour classes
        self.parent_polygon = QtWidgets.QGraphicsPolygonItem()

        # Create a list to hold contour objects for all listed images
        self.image_list_contour_and_item_dict = {}

        # Sets a transparent pixmap to initialize the size of the PhotoViewer
        self.createAndSetPlaceholderAreaPixmap()

        self.map_context_menu = MapContextMenu()
        self.viewer_map._photo.setTabContextMenu(self.map_context_menu)

        # Connect tab buttons and clickable items to event handlers
        self.button_search.clicked.connect(self.search)
        self.list_allImages.currentItemChanged.connect(self.currentImageChanged)

        self.viewer_map.getPhotoItem().addObserver(self)

    def notify(self, event, id, data):
        if event is "FIND_IMAGES":
            point_pixel_x_coord = self.map_context_menu.pixel_x_invocation_coord
            point_pixel_y_coord = self.map_context_menu.pixel_y_invocation_coord
            point_lat, point_lon = self.geolocatePoint(point_pixel_x_coord, point_pixel_y_coord)
            self.findImagesContainingPoint(point_lat, point_lon)

        elif event is "COPY_LAT_LON":
            point_pixel_x_coord = self.map_context_menu.pixel_x_invocation_coord
            point_pixel_y_coord = self.map_context_menu.pixel_y_invocation_coord
            point_lat, point_lon = self.geolocatePoint(point_pixel_x_coord, point_pixel_y_coord)
            self.copyPointLatLonToClipboard(point_lat, point_lon)

        elif event is "RESET_FILTERS":
            self.clearLatLonInputFields()
            self.unhideAllImages()

    def geolocatePoint(self, x, y):
        map_width, map_height = self.viewer_map._photo.boundingRect().getRect()[2:]
        lat, lon = geolocateLatLonFromPixel(self.current_flight.area_map, map_width, map_height, x, y)
        return lat, lon

    def findImagesContainingPoint(self, lat, lon):
        self.line_latitude.setText('{}'.format(lat))
        self.line_longitude.setText('{}'.format(lon))
        self.search()

    # Tab setup functions
    def setMap(self, flight):
        self.clearScene()
        self.current_flight = flight
        self.loadAndSetFlightAreaPixmap()

        self.addMapToScene()

    def loadAndSetFlightAreaPixmap(self):
        areamap_full_filepath = "./area_maps/{}".format(self.current_flight.area_map.filename)
        self.viewer_map.setPhoto(QtGui.QPixmap(areamap_full_filepath))
        # self.viewer_map.centerOn(self.viewer_map._photo.pixmap().rect().center())

    def addMapToScene(self):
        self.viewer_map._scene.addItem(self.viewer_map._photo)

    def createAndSetPlaceholderAreaPixmap(self):
        self.viewer_map._photo.setPixmap(self.generatePlaceholderPixmap())

    def generatePlaceholderPixmap(self):
        placeholder_pixmap = QtGui.QPixmap(1220, 846)
        placeholder_pixmap.fill(QtCore.Qt.transparent)
        return placeholder_pixmap

    # Images list manipulation and interaction functions
    def addImageToUi(self, image):
        item = ImageListItem(image.filename, image)
        if not image.is_reviewed:
            font = item.font()
            font.setBold(True)
            item.setFont(font)
        self.list_allImages.addItem(item)

        # create a new contour for current image
        contour = self.createImageContour(image)
        # pair contour and corresponding image in a dict
        self.image_list_contour_and_item_dict[image] = [item, contour]

        self.updateAndShowContoursOnAreamap(contour)

    def currentImageChanged(self, current, _):
        if self.current_contour:
            self.removeCurrentContourFromScene()

        # update currentImage with selected item
        self.current_image = current.getImage()

        self.current_contour = self.createImageContour(self.current_image)
        self.updateAndShowContoursOnAreamap(self.current_contour)
        self.highlightCurrentImageContour()


    # Class utility functions
    def search(self):
        if len(self.line_latitude.text()) == 0 and len(self.line_longitude.text()) == 0:
            self.unhideAllImages()
            return

        # both are required
        if len(self.line_latitude.text()) == 0 or len(self.line_longitude.text()) == 0:
            return

        # hide all
        self.hideAllImages()

        try:
            lat = float(self.line_latitude.text())
        except ValueError:
            print 'Latitude is not a float'
            self.clearLatLonInputFields()
            self.unhideAllImages()
            return
        try:
            lon = float(self.line_longitude.text())
        except ValueError:
            print 'Longitude is not a float'
            self.clearLatLonInputFields()
            self.unhideAllImages()
            return

        p = Point(lat, lon)
        for i in range(self.list_allImages.count()):
            item = self.list_allImages.item(i)
            img = item.getImage()
            bounds = getFrameBounds(img, self.current_flight.reference_altitude)
            if bounds.isPointInsideBounds(p):
                item.setHidden(False)

    def copyPointLatLonToClipboard(self, lat, lon):
        QtWidgets.QApplication.clipboard().setText('{}, {}'.format(lat, lon))

    def hideAllImages(self):
        for i in range(self.list_allImages.count()):
            self.list_allImages.item(i).setHidden(True)

    def unhideAllImages(self):
        for i in range(self.list_allImages.count()):
            self.list_allImages.item(i).setHidden(False)

    def clearLatLonInputFields(self):
        self.line_latitude.setText('')
        self.line_longitude.setText('')

    def createImageContour(self, image):
        contour = Contour(self.parent_polygon)

        map_dims = self.viewer_map._photo.boundingRect()

        current_area_map = self.current_flight.area_map

        site_elevation = image.flight.reference_altitude
        (img_upper_left_lat, img_upper_left_lon) = geolocateLatLonFromPixel(image, site_elevation, 0, 0)
        (img_upper_right_lat, img_upper_right_lon) = geolocateLatLonFromPixel(image, site_elevation,
                                                                              image.width, 0)
        (img_lower_right_lat, img_lower_right_lon) = geolocateLatLonFromPixel(image, site_elevation,
                                                                              image.width,
                                                                              image.height)
        (img_lower_left_lat, img_lower_left_lon) = geolocateLatLonFromPixel(image, site_elevation,
                                                                                            0, image.height)

        # interpolate the location of the image on the minimap (in px)
        contour._topLeft.setX(((img_upper_left_lon - current_area_map.ul_lon) /
                                (current_area_map.lr_lon - current_area_map.ul_lon)) * map_dims.width())
        contour._topLeft.setY(((img_upper_left_lat - current_area_map.ul_lat) /
                                (current_area_map.lr_lat - current_area_map.ul_lat)) * map_dims.height())

        contour._topRight.setX(((img_upper_right_lon - current_area_map.ul_lon) /
                                (current_area_map.lr_lon - current_area_map.ul_lon)) * map_dims.width())
        contour._topRight.setY(((img_upper_right_lat - current_area_map.ul_lat) /
                                (current_area_map.lr_lat - current_area_map.ul_lat)) * map_dims.height())

        contour._bottomRight.setX(((img_lower_right_lon - current_area_map.ul_lon) /
                                (current_area_map.lr_lon - current_area_map.ul_lon)) * map_dims.width())
        contour._bottomRight.setY(((img_lower_right_lat - current_area_map.ul_lat) /
                                (current_area_map.lr_lat - current_area_map.ul_lat)) * map_dims.height())

        contour._bottomLeft.setX(((img_lower_left_lon - current_area_map.ul_lon) /
                                (current_area_map.lr_lon - current_area_map.ul_lon)) * map_dims.width())
        contour._bottomLeft.setY(((img_lower_left_lat - current_area_map.ul_lat) /
                                (current_area_map.lr_lat - current_area_map.ul_lat)) * map_dims.height())

        return contour

    def updateAndShowContoursOnAreamap(self, contour):
        contour.updatePolygon()
        self.addContourToScene(contour)

    def removeOldContourHighlight(self):
        if self.current_image is not None:
            # extract the contour from dictionary (don't care about the current item)
            _, current_contour = self.image_list_contour_and_item_dict[self.current_image]
            current_contour.removePolygonHighlight()

    def highlightCurrentImageContour(self):
        self.current_contour.highlightPolygon()

    # Clear and reset routines
    def clearScene(self):
        for item in self.viewer_map._scene.items():
            self.viewer_map._scene.removeItem(item)

    def removeCurrentContourFromScene(self):
        self.viewer_map._scene.removeItem(self.current_contour)

    def removeContoursFromScene(self):
        for item in  self.viewer_map._scene.items():
            if type(item) is Contour:
                self.viewer_map._scene.removeItem(item)

    def addContourToScene(self, contour):
        self.viewer_map._scene.addItem(contour)

    def disableCurrentImageChangedEvent(self):
        self.list_allImages.currentItemChanged.disconnect(self.currentImageChanged)

    def enableCurrentItemChangedEvent(self):
        self.list_allImages.currentItemChanged.connect(self.currentImageChanged)

    def resetTab(self):
        self.image_list_contour_and_item_dict = {}
        self.current_flight = None
        self.current_image = None

        self.disableCurrentImageChangedEvent()  # disconnect signal to avoid triggering an event
        self.list_allImages.clear()
        self.enableCurrentItemChangedEvent()  # re-enable the event

        self.clearScene()

    # Accessors and mutators of the class variables
    def getCurrentImage(self):
        return self.current_image

    def getCurrentFlight(self):
        return self.current_flight
