release: python manage.py migrate --noinput
web: gunicorn bookstore.wsgi --access-logfile - --error-logfile -