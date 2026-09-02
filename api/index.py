import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()

if os.getenv('VERCEL'):
	call_command('migrate', interactive=False, verbosity=0)