from math import cos, sin, sqrt, radians, degrees
from math import acos, asin, atan2
import utils.xmlParser
import numpy

def getPixelFromLatLon(image, image_width, image_height, site_elevation, pixel_lat, pixel_lon): #TODO: test

    lat_img = radians(image.latitude)
    lon_img = radians(image.longitude)

    intrinsic_matrix = utils.xmlParser.getIntrinsicMatrix(image.flight.intrinsic_matrix)

    # choose a reference location inside flight area
    lat_ref = radians(49.903867)
    lon_ref = radians(-98.273483)

    reference_ecef = geodeticToEcef(lat_ref, lon_ref, site_elevation)

    aircraft_ecef = geodeticToEcef(lat_img, lon_img, site_elevation)
    aircraft_ned = transformEcefToNed(lat_img, lon_img, reference_ecef, aircraft_ecef)

    pixel_projection_ecef = geodeticToEcef(radians(pixel_lat), radians(pixel_lon), site_elevation)
    pixel_projection_ned = transformEcefToNed(radians(pixel_lat), radians(pixel_lon), reference_ecef, pixel_projection_ecef)

    rotation_camera_to_ned = createRotationCameraToNed(radians(image.pitch), radians(image.roll), radians(image.yaw))
    rotation_ned_to_camera = numpy.linalg.inv(rotation_camera_to_ned)
    zNedToCam = (site_elevation - image.altitude) # z-axis is pointing down
    yNedToCam = aircraft_ned[1]
    xNedToCam = aircraft_ned[0]
    ned_origin_to_camera = numpy.array([[xNedToCam],
                                        [yNedToCam],
                                        [zNedToCam]], dtype=numpy.float64)

    scaled_pixel_location = numpy.dot(numpy.dot(intrinsic_matrix, rotation_ned_to_camera),pixel_projection_ned) - numpy.dot(numpy.dot(intrinsic_matrix, rotation_ned_to_camera), ned_origin_to_camera)
    scaling_factor = scaled_pixel_location[2]
    x = scaled_pixel_location[0]/scaling_factor
    y = scaled_pixel_location[1]/scaling_factor

    return x, y

def geolocateLatLonFromPixelOnImage(img, site_elevation, pu, pv):
    lat = radians(img.latitude)
    lon = radians(img.longitude)
    # maybe these can be useful - no idea what these do
    #orig_roll = roll
    #roll = atan(cos(img.pitch)*tan(orig_roll))#RMissue:8, corrects roll for img.pitched axis

    site_elevation = img.flight.reference_altitude

    # choose a reference location inside flight area
    latRef = radians(49.903867)
    lonRef = radians(-98.273483)

    # get the coordinates of reference location in ECEF
    ecefRef = selectEcefRef(latRef, lonRef, site_elevation)
    # get coordinates of the plane in ECEF
    groundEcef = geodeticToEcef(lat, lon, site_elevation)
    # get the coordinates of the plane in NED
    vehicleNed = transformEcefToNed(lat, lon, ecefRef, groundEcef)

    rotationCameraToNed = createRotationCameraToNed(radians(img.pitch), radians(img.roll), radians(img.yaw))

    intrinsicMatrix = utils.xmlParser.getIntrinsicMatrix(img.flight.intrinsic_matrix)

    # image frame (pixel location) column vector
    imagePoint = numpy.array([[pu],
                              [pv],
                               [1]], dtype=numpy.float64)

    zNedToCam = (site_elevation - img.altitude) # z-axis is pointing down
    yNedToCam = vehicleNed[1]
    xNedToCam = vehicleNed[0]
    posVectorNedToCamera = numpy.array([[xNedToCam],
                                        [yNedToCam],
                                        [zNedToCam]], dtype=numpy.float64)

    intrinsicMatrixInverse = numpy.linalg.inv(intrinsicMatrix)
    rotationCameraToNedInverse = numpy.linalg.inv(rotationCameraToNed)

    # the collection of all points that map to (pu, pv) lies on a 3D "ray" coming out of the camera
    rayOrientation = numpy.dot((numpy.dot(rotationCameraToNed, intrinsicMatrixInverse)), imagePoint) # (R^-1*A^-1)*p
    scalingFactor = -1*posVectorNedToCamera[2]/rayOrientation[2]

    Xm = posVectorNedToCamera[0] + scalingFactor*rayOrientation[0]
    Ym = posVectorNedToCamera[1] + scalingFactor*rayOrientation[1]
    Zm = 0 # the entire solution rests on the assumptions that we are shooting objects at the ground level, flush with NED's xy-plane, such that Zned = Zm = 0

    pixelNed = numpy.array([[Xm], 
                            [Ym], 
                            [Zm]], dtype=numpy.float64) 

    pixelEcef = transformNedToEcef(lat, lon, ecefRef, pixelNed)
    pixelGeodetic = ecefToGeodetic(pixelEcef)

    dLat = degrees(pixelGeodetic[0])
    dLon = degrees(pixelGeodetic[1])

    return dLat, dLon

def geolocateLatLonFromPixelOnAreamap(area_map, area_map_pixel_width, area_map_pixel_height, x, y):
    lat = (y/area_map_pixel_height)*(area_map.ll_lat - area_map.ul_lat) + area_map.ul_lat
    lon = (x/area_map_pixel_width) * (area_map.ur_lon - area_map.ul_lon) + area_map.ul_lon
    return lat, lon

#
# Location-specific ECEF reference that serves as unique NED origin
#
def selectEcefRef( latRef, lonRef, altRef):
    ecefRef = geodeticToEcef(latRef, lonRef, altRef)

    return ecefRef
#
# A pair of functions to go between geodetic coordinates and ECEF
#
def geodeticToEcef( lat, lon, elevation):
    # semi-major earth axis [m]
    a = 6378137
    # semi-minor earth axis [m]
    b = 6356752.3142
    # flattening factor
    f = (a - b) / a
    # first eccentricity, squared
    e2 = (2 * f) - (f * f)
    # meridian radius of curvature
    #M = (a * (1 - e2)) / sqrt(1 - e2 * sin(lat) ** 2) ** 3
    # prime vertical radius of curvature: http://clynchg3c.com/Technote/geodesy/radiigeo.pdf
    N = a / sqrt(1 - e2 * sin(lat) ** 2)

    # Earth Centered Earth Fixed aircraft coordinates
    # using altitude from sea level for 3D position around the Earth
    # https://en.wikipedia.org/wiki/Geographic_coordinate_conversion#From_geodetic_to_ECEF_coordinates
    #Xe = (N + alt) * cos(lat) * cos(lon)
    #Ye = (N + alt) * cos(lat) * sin(lon)
    # equivalency: 1 - e2 = b^2/a^2
    #Ze = (N * (1 - e2) + alt) * sin(lat)
    # column vector
    #vehicleEcef = numpy.array([[Xe], [Ye], [Ze]])

    # Earth Centered Earth Fixed ground coordinates directly below the aircraft
    # use site elevation as ground altitude
    Xe = (N + elevation) * cos(lat) * cos(lon)
    Ye = (N + elevation) * cos(lat) * sin(lon)
    Ze = (N * (1 - e2) + elevation) * sin(lat)
    ecefCoords = numpy.array([[Xe], [Ye], [Ze]])

    return ecefCoords

def ecefToGeodetic( ecef):

    # WGS-84 ellipsoid parameters
    a = 6378137
    f = 1 / 298.257223563
     
    # Derived parameters
    e2 = f * (2 - f)
    a1 = a * e2
    a2 = a1 * a1
    a3 = a1 * e2 / 2
    a4 = 2.5 * a2
    a5 = a1 + a3
    a6 = 1 - e2
    """Convert ECEF (meters) to LLA (radians and meters).
    """
    # Olson, D. K., Converting Earth-Centered, Earth-Fixed Coordinates to
    # Geodetic Coordinates, IEEE Transactions on Aerospace and Electronic
    # Systems, 32 (1996) 473-476.
    w = sqrt(ecef[0] * ecef[0] + ecef[1] * ecef[1])
    z = ecef[2]
    zp = abs(z)
    w2 = w * w
    r2 = z * z + w2
    r  = sqrt(r2)
    s2 = z * z / r2
    c2 = w2 / r2
    u = a2 / r
    v = a3 - a4 / r
    if c2 > 0.3:
        s = (zp / r) * (1 + c2 * (a1 + u + s2 * v) / r)
        lat = asin(s)
        ss = s * s
        c = sqrt(1 - ss)
    else:
        c = (w / r) * (1 - s2 * (a5 - u - c2 * v) / r)
        lat = acos(c)
        ss = 1 - c * c
        s = sqrt(ss)
    g = 1 - e2 * ss
    rg = a / sqrt(g)
    rf = a6 * rg
    u = w - rg * c
    v = zp - rf * s
    f = c * u + s * v
    m = c * v - s * u
    p = m / (rf / g + f)
    lat = lat + p
    if z < 0:
        lat = -lat

    geodeticCoords = numpy.array([                    [lat], 
                                  [atan2(ecef[1], ecef[0])], 
                                            [f + m * p / 2]], dtype=numpy.float64)

    return geodeticCoords

# 
# A pair of transformation functions to go between ECEF and NED
#
def transformEcefToNed( lat, lon, ecefRef, vectorWrtEcef):
    # Todo: Add error detection mechanism if input vector 'vectorWrtEcef' is not 3x1

    vectorWrtEcefFromEcefRefToVehicle = vectorWrtEcef - ecefRef

    rotationEcefToNed = numpy.array([
        [-sin(lat)*cos(lon), -sin(lat)*sin(lon),  cos(lat)],
        [         -sin(lon),           cos(lon),         0],
        [-cos(lat)*cos(lon), -cos(lat)*sin(lon), -sin(lat)]
    ])

    vectorWrtNed = numpy.dot(rotationEcefToNed, vectorWrtEcefFromEcefRefToVehicle)

    return vectorWrtNed

def transformNedToEcef( lat, lon, ecefRef, vectorWrtNed):

    # the order of operations is reversed compared to "transformEcefToNed"
    rotationNedToEcef = numpy.array([
            [-sin(lat)*cos(lon), -sin(lon), -cos(lat)*cos(lon)],
            [-sin(lat)*sin(lon),  cos(lon), -cos(lat)*sin(lon)],
            [          cos(lat),         0,          -sin(lat)]
        ])

    rotatedVectorWrtNed = numpy.dot(rotationNedToEcef, vectorWrtNed)
    vectorWrtEcef = rotatedVectorWrtNed + ecefRef

    return vectorWrtEcef

# 
# [Insert descriptive comment here]
#
def createTransformationCameraToNed( vehicleNed, posVectorCameraToNed, rotationCameraToNed):

    cameraPositionWrtRefNed = numpy.dot(rotationCameraToNed, posVectorCameraToNed)

    # if Zm = 0, then we can safely discard the third column of the rotation matrix
    reducedRotationNedToCamera = rotationNedToCamera[:, [0, 1]]
    transformCameraToNed = numpy.concatenate((reducedRotationNedToCamera, nedOriginPosWrtCamera), axis=1) 

    return transformCameraToNed

def createRotationCameraToNed( pitch, roll, yaw):
    # transformation between body frame and navigation frame
    rotationNedToBody = numpy.array([
       [                                cos(pitch)*cos(yaw),                                 cos(pitch)*sin(yaw),          -sin(pitch)],
       [-cos(roll)*sin(yaw) + sin(roll)*sin(pitch)*cos(yaw),  cos(roll)*cos(yaw) + sin(roll)*sin(pitch)*sin(yaw), sin(roll)*cos(pitch)],
       [ sin(roll)*sin(yaw) + cos(roll)*sin(pitch)*cos(yaw), -sin(roll)*cos(yaw) + cos(roll)*sin(pitch)*sin(yaw), cos(roll)*cos(pitch)]
    ])

    # camera orientation (parallel to aircraft z axis)
    rotationBodyToCamera = numpy.array([[ 0, 1, 0],
                                        [-1, 0, 0],
                                        [ 0, 0, 1]], dtype=numpy.float64)

    # rotation between camera frame - mapping (NED) frame
    rotationNedToCamera = numpy.dot(rotationNedToBody, rotationBodyToCamera)
    rotationCameraToNed = numpy.linalg.inv(rotationNedToCamera) # Important! - when code is verified, just rewrite the matrix at the definition command

    return rotationCameraToNed