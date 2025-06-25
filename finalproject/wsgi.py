"""
WSGI config for finalproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys

path = '/home/Kalyankumar5951/finalproject'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finalproject.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

