from math import radians, degrees
from utils.geolocationUtilities import *

class Geolocator:
    def __init__(self):

        # Initialize variables that will be changed once an image becomes available
        self._intrinsic_matrix = numpy.array([[3446.85229, 0, 1477.50261],
                                              [0, 3431.11804, 1002.49563],
                                              [0, 0, 1]], dtype=numpy.float64)
        self._intrinsic_matrix_inverse = numpy.linalg.inv(self._intrinsic_matrix)

        self._current_image = None
        self._lat_img = None
        self._lon_img = None
        self._roll_img = None
        self._pitch_img = None
        self._yaw_img = None
        self._altitude = None
        self._site_elevation = None
        self._scaling_factor = None

        # Current flight will update once a flight is selected
        self._current_flight = None

        # Initialize empty matrices
        self._reference_ecef = None
        self._aircraft_ecef = None
        self._aircraft_ned = None
        self._rotation_camera_to_ned = None
        self._rotation_ned_to_camera = None
        self._origin_of_ned_to_camera = None


        # Select a reference point for geolocation operations
        self._lat_ref = radians(49.903867) # TODO: generalize
        self._lon_ref = radians(-98.273483)

    def setCurrentImage(self, image):
        self._current_image = image
        self.updateCurrentImageParameters(image)

    # Running the update methods for the first time will create local variables
    def updateCurrentImageParameters(self, image):
        self._lat_img = radians(image.latitude)
        self._lon_img = radians(image.longitude)
        self._roll_img = radians(image.roll)
        self._pitch_img = radians(image.pitch)
        self._yaw_img = radians(image.yaw)
        self._altitude = image.altitude

        # Update common matrices with recent changes
        self.updateMatrices()

    def setCurrentFlightAndSiteElevation(self, flight=None):
        if flight is not None:
            self._current_flight = flight
            self.setSiteElevation(flight.reference_altitude)
        else:
            print "Error! Invalid flight passed, current flight and site elevation were not changed"

    def setSiteElevation(self, site_elevation):
        self._site_elevation = site_elevation

    def updateMatrices(self):
        self._reference_ecef = geodeticToEcef(self._lat_ref, self._lon_ref, self._site_elevation)
        self._aircraft_ecef = geodeticToEcef(self._lat_img, self._lon_img, self._site_elevation)
        self._aircraft_ned = transformEcefToNed(self._lat_img, self._lon_img, self._reference_ecef, self._aircraft_ecef)
        self._origin_of_ned_to_camera = numpy.array([[self._aircraft_ned[0]],
                                                     [self._aircraft_ned[1]],
                                                     [self._site_elevation - self._altitude]], dtype=numpy.float64)
        self._rotation_camera_to_ned = createRotationCameraToNed(self._pitch_img, self._roll_img, self._yaw_img)
        self._rotation_ned_to_camera = numpy.linalg.inv(self._rotation_camera_to_ned)

    def getPixelFromLatLon(self, pixel_lat, pixel_lon):
        pixel_projection_ecef = geodeticToEcef(radians(pixel_lat), radians(pixel_lon), self._site_elevation)
        pixel_projection_ned = transformEcefToNed(radians(pixel_lat), radians(pixel_lon), self._reference_ecef,
                                                  pixel_projection_ecef)
        scaled_pixel_location = numpy.dot(numpy.dot(self._intrinsic_matrix, self._rotation_ned_to_camera), pixel_projection_ned) - \
                                numpy.dot(numpy.dot(self._intrinsic_matrix, self._rotation_ned_to_camera), self._origin_of_ned_to_camera)
        scaling_factor = scaled_pixel_location[2]
        x_pixel_coordinate = scaled_pixel_location[0] / scaling_factor
        y_pixel_coordinate = scaled_pixel_location[1] / scaling_factor

        return x_pixel_coordinate, y_pixel_coordinate

    def getLatLonFromPixel(self, x_pixel_coord, y_pixel_coord):
        image_point = numpy.array([[x_pixel_coord],
                                   [y_pixel_coord],
                                   [1]], dtype=numpy.float64)

        ray_orientation = numpy.dot((numpy.dot(self._rotation_camera_to_ned, self._intrinsic_matrix_inverse)), image_point)
        scaling_factor = -1*( self._origin_of_ned_to_camera[2] / ray_orientation[2] )

        x_ned_coord = self._origin_of_ned_to_camera[0] + scaling_factor*ray_orientation[0]
        y_ned_coord = self._origin_of_ned_to_camera[1] + scaling_factor*ray_orientation[1]

        pixel_coords_in_ned = numpy.array([[x_ned_coord],
                                           [y_ned_coord],
                                           [0]], dtype=numpy.float64)
        pixel_coords_in_ecef = transformNedToEcef(self._lat_img, self._lon_img, self._reference_ecef, pixel_coords_in_ned)
        pixel_coords_in_geodetic = ecefToGeodetic(pixel_coords_in_ecef)

        pixel_latitude_degrees = degrees(pixel_coords_in_geodetic[0])
        pixel_longitude_degrees = degrees(pixel_coords_in_geodetic[1])

        return pixel_latitude_degrees, pixel_longitude_degrees
