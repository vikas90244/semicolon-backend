web: gunicorn core.wsgi:application --timeout 300 --keep-alive 5
worker: celery -A core worker --loglevel=info
beat: celery -A core beat --loglevel=info
