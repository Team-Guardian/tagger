import os
import django
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings.settings")
django.setup()
from db.models import * # Must go after django.setup()

# AreaMap
def create_areamap(name, filename, ul_lat, ul_lon, ll_lat, ll_lon, lr_lat, lr_lon, ur_lat, ur_lon):
    am = AreaMap(name=name, filename=filename, ul_lat=ul_lat, ul_lon=ul_lon, ll_lat=ll_lat, ll_lon=ll_lon, lr_lat=lr_lat, lr_lon=lr_lon, ur_lat=ur_lat, ur_lon=ur_lon)
    am.save()
    return am

# Flight
def create_flight(location, reference_altitude, intrinsic_matrix, date=datetime.datetime.now().date(), area_map=None):
    img_path = '{} - {}'.format(location, date)
    f = Flight(location=location, reference_altitude=reference_altitude, date=date, img_path=img_path, intrinsic_matrix=intrinsic_matrix, area_map=area_map)
    f.save()
    return f

def delete_flight(flight):
    flight.delete()

def get_all_flights():
    flights = {}
    for f in Flight.objects.all():
        flights[f.location + " " + str(f.date)] = f
    return flights

# Image
def create_image(flight, width, height, filename, latitude, longitude, altitude, roll, pitch, yaw):
    i = Image(flight=flight, width=width, height=height, filename=filename, latitude=latitude, longitude=longitude, altitude=altitude, roll=roll, pitch=pitch, yaw=yaw)
    i.save()
    return i

def delete_image(image):
    image.delete()

def get_all_images():
    images = []
    for i in Image.objects.all():
        images.append(i)
    return images

def get_all_images_for_flight(flight):
    images = []
    result = Image.objects.filter(flight=flight)
    if result.exists():
        for i in result:
            images.append(i)
    return images

# Tag
def create_tag(type, subtype, symbol, num_occurrences=0):
    t = Tag(type=type, subtype=subtype, symbol=symbol, num_occurrences=num_occurrences)
    t.save()
    return t

def delete_tag(tag):
    tag.delete()

def get_all_tags():
    list = []
    for t in Tag.objects.all():
        list.append(t)
    return list

# Marker
def create_marker(tag, image, latitude, longitude):
    m = Marker(tag=tag, image=image, latitude=latitude, longitude=longitude)
    m.save()
    return m

def delete_marker(marker):
    marker.delete()

def get_all_markers():
    list = []
    for m in Marker.objects.all():
        list.append(m)
    return list

if __name__=="__main__":

    # Usage example
    my_tags = get_all_tags()
    print my_tags

    f = create_flight('SFU Surrey', 123, 'my_matrix')
    print f.__dict__
    delete_flight(f)