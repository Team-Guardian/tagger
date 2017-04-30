import os
from db.dbHelper import create_marker, create_tag, get_all_images_for_flight
from db.models import *
from gui.tagDialog import ICON_DIRECTORY
from geographicUtilities import Point, getFrameBounds

def createNestMarkersFromCSV(path_to_file, flight):
    images = get_all_images_for_flight(flight)
    nests = []

    new_tags = []
    new_markers = []

    with open(path_to_file) as f:
        for i, line in enumerate(f):
            lat, lon, species = line.split(',')
            nests.append({'lat': lat, 'lon': lon, 'species': species})

    for nest in nests:
        tag = ensureTagExists('Nest', nest.species)
        if tag is not in new_tags:
            new_tags.append(tag)
        point = Point(nest.lat, nest.lon)
        images_containing_point = getImagesContainingPoint(images, point, flight.reference_altitude)
        if len(images_containing_point) is not 0:
            image = images_containing_point[0]
            new_markers.append(create_marker(tag, image, nest.lat, nest.lon))

    return new_tags, new_markers

def getImagesContainingPoint(images, point, reference_altitude):
    images_containing_point = []
    for image in images:
        bounds = getFrameBounds(image, reference_altitude)
        if bounds.isPointInsideBounds(point):
            images_containing_point.append(image)
    return images_containing_point

def ensureTagExists(type, subtype):
    if not Tag.objects.filter(type=type, subtype=subtype).exists():
        return create_tag(type, subtype, getUnusedTagIcons()[0])
    else:
        return Tag.objects.filter(type=type, subtype=subtype).last()

def getUnusedTagIcons():
    # get all available marker icons
    tag_icon_list = []
    for fName in os.listdir(ICON_DIRECTORY):
        if fName.endswith('.png'):
            tag_icon_list.append(fName.split('.')[0])

    # remove tag icons that are in use, but leave at least one
    unused_tag_icons = []
    for tag_icon in tag_icon_list:
        if tag_icon not in Tag.objects.values_list('symbol', flat=True):
            unused_tag_icons.append(tag_icon)

    if len(unused_tag_icons) is 0:
        unused_tag_icons.append(tag_icon_list[0])

    return unused_tag_icons