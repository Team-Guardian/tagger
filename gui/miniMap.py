# Math reference: http://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python/13849249#13849249

from PyQt5 import QtCore, QtGui, QtWidgets
import numpy
from math import sin, cos

from utils.geolocate import geolocateLatLonFromPixel
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

                    # Find geodetic coordinates of the four current image corners
                    (img_upper_left_lat, img_upper_left_lon) = geolocateLatLonFromPixel(img, self._current_flight.reference_altitude, 0, 0)
                    (img_upper_right_lat, img_upper_right_lon) = geolocateLatLonFromPixel(img, self._current_flight.reference_altitude, img.width, 0)
                    (img_lower_right_lat, img_lower_right_lon) = geolocateLatLonFromPixel(img, self._current_flight.reference_altitude, img.width, img.height)
                    (img_lower_left_lat, img_lower_left_lon) = geolocateLatLonFromPixel(img, self._current_flight.reference_altitude, 0, img.height)

                    # Define a vector along the width of the image in geodetic coordinates
                    width_vector_geodetic = numpy.array([[self._current_area_map.ur_lat - self._current_area_map.ul_lat],
                                                         [self._current_area_map.ur_lon - self._current_area_map.ul_lon]])
                    # Find vectors to each of the four corner points in geodetic coordinates
                    upper_left_vector_geodetic = numpy.array([[img_upper_left_lat - self._current_area_map.ul_lat],
                                                              [img_upper_left_lon - self._current_area_map.ul_lon]])
                    upper_right_vector_geodetic = numpy.array([[img_upper_right_lat - self._current_area_map.ul_lat],
                                                               [img_upper_right_lon - self._current_area_map.ul_lon]])
                    lower_right_vector_geodetic = numpy.array([[img_lower_right_lat - self._current_area_map.ul_lat],
                                                               [img_lower_right_lon - self._current_area_map.ul_lon]])
                    lower_left_vector_geodetic = numpy.array([[img_lower_left_lat - self._current_area_map.ul_lat],
                                                              [img_lower_left_lon - self._current_area_map.ul_lon]])

                    # Find lengths of the four vectors relative to the width vector (2-norm or Frobenius 'fro' norm)
                    ul_length_to_width_ratio = numpy.linalg.norm(upper_left_vector_geodetic, 'fro') / \
                                               numpy.linalg.norm(width_vector_geodetic, 'fro')
                    ur_length_to_width_ratio = numpy.linalg.norm(upper_right_vector_geodetic, 'fro') / \
                                               numpy.linalg.norm(width_vector_geodetic, 'fro')
                    lr_length_to_width_ratio = numpy.linalg.norm(lower_right_vector_geodetic, 'fro') / \
                                               numpy.linalg.norm(width_vector_geodetic, 'fro')
                    ll_length_to_width_ratio = numpy.linalg.norm(lower_left_vector_geodetic, 'fro') / \
                                               numpy.linalg.norm(width_vector_geodetic, 'fro')

                    # Find the angle between four vectors and the width vector
                    ul_angle_to_width = self.angleBetween(upper_left_vector_geodetic, width_vector_geodetic)
                    ur_angle_to_width = self.angleBetween(upper_right_vector_geodetic, width_vector_geodetic)
                    lr_angle_to_width = self.angleBetween(lower_right_vector_geodetic, width_vector_geodetic)
                    ll_angle_to_width = self.angleBetween(lower_left_vector_geodetic, width_vector_geodetic)

                    # Define a vector along the width of the image in pixel coordinates
                    width_vector_pixels = numpy.array([[self._map.boundingRect().width()],
                                                       [0]])

                    # Using ratios, find the length of the four vectors to corner points in pixel coordinates
                    upper_left_vector_pixels = numpy.array([[width_vector_pixels[0] * ul_length_to_width_ratio],
                                                                  [0]])
                    upper_right_vector_pixels = numpy.array([[width_vector_pixels[0] * ur_length_to_width_ratio],
                                                                   [0]])
                    lower_right_vector_pixels = numpy.array([[width_vector_pixels[0] * lr_length_to_width_ratio],
                                                                   [0]])
                    lower_left_vector_pixels = numpy.array([[width_vector_pixels[0] * ll_length_to_width_ratio],
                                                                  [0]])

                    # Rotate four vectors about the origin to get the X and Y coordinates of each of the four points
                    self._img_contour._topLeftX = upper_left_vector_pixels[0]*cos(ul_angle_to_width) - \
                                                  upper_left_vector_pixels[1]*sin(ul_angle_to_width)
                    self._img_contour._topLeftY = upper_left_vector_pixels[0]*sin(ul_angle_to_width) + \
                                                  upper_left_vector_pixels[1]*cos(ul_angle_to_width)

                    self._img_contour._topRightX = upper_right_vector_pixels[0]*cos(ur_angle_to_width) - \
                                                   upper_right_vector_pixels[1]*sin(ur_angle_to_width)
                    self._img_contour._topRightY = upper_right_vector_pixels[0]*sin(ur_angle_to_width) + \
                                                   upper_right_vector_pixels[1]*cos(ur_angle_to_width)

                    self._img_contour._bottomRightX = lower_right_vector_pixels[0]*cos(lr_angle_to_width) - \
                                                      lower_right_vector_pixels[1]*sin(lr_angle_to_width)
                    self._img_contour._bottomRightY = lower_right_vector_pixels[0]*sin(lr_angle_to_width) + \
                                                      lower_right_vector_pixels[1]*cos(lr_angle_to_width)

                    self._img_contour._bottomLeftX = lower_left_vector_pixels[0]*cos(ll_angle_to_width) - \
                                                     lower_left_vector_pixels[1]*sin(ll_angle_to_width)
                    self._img_contour._bottomLeftY = lower_left_vector_pixels[0]*sin(ll_angle_to_width) + \
                                                     lower_left_vector_pixels[1]*cos(ll_angle_to_width)

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

    def clearMinimap(self):
        self._original_pixmap = QtGui.QPixmap(300, 190)
        self._original_pixmap.fill(QtCore.Qt.transparent)
        self._map.setPixmap(self._original_pixmap)

    def unitVector(self, vector):
        """ Returns the unit vector of the vector.  """
        return vector / numpy.linalg.norm(vector)

    def angleBetween(self, v1, v2):
        """ Returns the angle in radians between vectors 'v1' and 'v2'"""

        v1_u = self.unitVector(v1)
        v2_u = self.unitVector(v2)
        dot_product = numpy.dot(numpy.transpose(v1_u), v2_u)
        return numpy.arccos(numpy.clip(dot_product, -1.0, 1.0))

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