import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings.settings")
django.setup()
from db.models import * # Must go after django.setup()

# Flight

# Image

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
