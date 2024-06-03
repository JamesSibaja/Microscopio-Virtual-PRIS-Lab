import os
import django
from getpass import getpass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "virtual_microscope.settings")
django.setup()

from django.contrib.auth.models import User

username = "admin"
email = "admin@example.com"
password = os.getenv("DJANGO_SUPERUSER_PASSWORD") or getpass('Enter password for superuser: ')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
else:
    print('Superuser already exists')
