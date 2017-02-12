import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings.settings")

django.setup()

from db.models import *

if __name__=="__main__":
    print 'Debug Point'





