import os
import django
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings.settings")
django.setup()
from db.models import * # Must go after django.setup()

# Flight
def create_flight(location, reference_altitude, intrinsic_matrix, date=datetime.datetime.now().date()):
    img_path = '{} - {}'.format(location, date)
    f = Flight(location=location, reference_altitude=reference_altitude, date=date, img_path=img_path, intrinsic_matrix=intrinsic_matrix)
    f.save()
    return f

def delete_flight(flight):
    flight.delete()

# Image
def create_image(flight, filename, latitude, longitude, altitude, roll, pitch, yaw):
    i = Image(flight=flight, filename=filename, latitude=latitude, longitude=longitude, altitude=altitude, roll=roll, pitch=pitch, yaw=yaw)
    i.save()
    return i

def delete_image(image):
    image.delete()

def get_all_images():
    list = []
    for l in Image.objects.all():
        list.append(l)
    return list

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

if __name__=="__main__":

    # Usage example
    my_tags = get_all_tags()
    print my_tags
    #
    # f = create_flight('SFU Surrey', 123, 'my_matrix')
    # print f.__dict__
    #
    #
    # create_image(f, '20160430_111051_217148.jpg', 49.908254, -98.276356, 462.350000, 0.021058, 0.014051, -0.416897)
    # create_image(f, '20160430_111116_587485.jpg', 49.910539, -98.281069, 469.460000, -0.086662, -0.503747, -1.800234)
    #
    #
