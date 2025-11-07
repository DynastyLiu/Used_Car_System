"""
WSGI config for usedcar_system project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'usedcar_system.settings')

application = get_wsgi_application()

