from math import cos, sin, sqrt, acos, asin, atan2
import numpy as np


def convertGeodeticToEcef(lat, lon, elevation):
    # semi-major earth axis [m]
    a = 6378137.0
    # semi-minor earth axis [m]
    b = 6356752.3142
    # flattening factor
    f = (a - b) / a
    # first eccentricity, squared
    e2 = (2 * f) - (f * f)
    # meridian radius of curvature
    # M = (a * (1 - e2)) / sqrt(1 - e2 * sin(lat) ** 2) ** 3
    # prime vertical radius of curvature: http://clynchg3c.com/Technote/geodesy/radiigeo.pdf
    N = a / sqrt(1 - e2 * sin(lat) ** 2)

    # Earth Centered Earth Fixed aircraft coordinates
    # using altitude from sea level for 3D position around the Earth
    # https://en.wikipedia.org/wiki/Geographic_coordinate_conversion#From_geodetic_to_ECEF_coordinates
    # Xe = (N + alt) * cos(lat) * cos(lon)
    # Ye = (N + alt) * cos(lat) * sin(lon)
    # equivalency: 1 - e2 = b^2/a^2
    # Ze = (N * (1 - e2) + alt) * sin(lat)
    # column vector
    # vehicleEcef = np.array([[Xe], [Ye], [Ze]])

    # Earth Centered Earth Fixed ground coordinates directly below the aircraft
    # use site elevation as ground altitude
    Xe = (N + elevation) * cos(lat) * cos(lon)
    Ye = (N + elevation) * cos(lat) * sin(lon)
    Ze = (N * (1 - e2) + elevation) * sin(lat)
    ecefCoords = np.array([[Xe], [Ye], [Ze]])

    return ecefCoords


def convertEcefToGeodetic(ecef):
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
    r = sqrt(r2)
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

    geodeticCoords = np.array([[lat],
                               [atan2(ecef[1], ecef[0])],
                               [f + m * p / 2]], dtype=np.float64)

    return geodeticCoords


#
# A pair of transformation functions to go between ECEF and NED
#
def homogenousTransformFromEcefToNed(lat, lon, ecef_ref_vector, vector_in_ecef_from_ecef_origin_to_point):
    # Todo: Add error detection mechanism if input vector 'vectorWrtEcef' is not 3x1

    vector_in_ecef_from_ecef_ref_to_body = vector_in_ecef_from_ecef_origin_to_point - ecef_ref_vector

    rotation_ecef_to_ned = np.array([
        [-sin(lat)*cos(lon), -sin(lat)*sin(lon),  cos(lat)],
        [-sin(lon),                    cos(lon),         0],
        [-cos(lat)*cos(lon), -cos(lat)*sin(lon), -sin(lat)]
    ])

    vector_from_ned_origin_to_point = np.dot(rotation_ecef_to_ned, vector_in_ecef_from_ecef_ref_to_body)

    return vector_from_ned_origin_to_point


def homogenousTransformFromNedToEcef(lat, lon, ecef_ref_vector, vector_from_ned_origin_to_point):

    rotation_ned_to_ecef = np.array([
        [-sin(lat)*cos(lon), -sin(lon), -cos(lat)*cos(lon)],
        [-sin(lat)*sin(lon),  cos(lon), -cos(lat)*sin(lon)],
        [cos(lat),                   0,          -sin(lat)]
    ])

    vector_in_ecef_from_ecef_ref_to_point = np.dot(rotation_ned_to_ecef, vector_from_ned_origin_to_point)
    vector_in_ecef_from_ecef_origin_to_point = vector_in_ecef_from_ecef_ref_to_point + ecef_ref_vector

    return vector_in_ecef_from_ecef_origin_to_point

def createRotationCameraToNed(pitch, roll, yaw):
    # transformation between body frame and navigation frame
    rotation_ned_to_body = np.array([
        [                                cos(pitch)*cos(yaw),                                 cos(pitch)*sin(yaw),          -sin(pitch)],
        [-cos(roll)*sin(yaw) + sin(roll)*sin(pitch)*cos(yaw),  cos(roll)*cos(yaw) + sin(roll)*sin(pitch)*sin(yaw), sin(roll)*cos(pitch)],
        [ sin(roll)*sin(yaw) + cos(roll)*sin(pitch)*cos(yaw), -sin(roll)*cos(yaw) + cos(roll)*sin(pitch)*sin(yaw), cos(roll)*cos(pitch)]
    ])

    # camera orientation (parallel to aircraft z axis)
    rotation_body_to_camera = np.array([[0, 1, 0],
                                        [-1, 0, 0],
                                        [0, 0, 1]], dtype=np.float64)

    # rotation between camera frame - mapping (NED) frame
    rotation_ned_to_camera = np.dot(rotation_ned_to_body, rotation_body_to_camera)
    rotation_camera_to_ned = np.linalg.inv(rotation_ned_to_camera)  # Important! - when code is verified, just rewrite the matrix at the definition command

    return rotation_camera_to_ned
