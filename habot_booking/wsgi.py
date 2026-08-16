"""
WSGI config for habot_booking project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habot_booking.settings')

application = get_wsgi_application()
