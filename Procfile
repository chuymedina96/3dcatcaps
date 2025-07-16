web: gunicorn backend.wsgi --log-file -
release: python manage.py makemigrations
release: python manage.py migrate