web: gunicorn core.wsgi --bind 0.0.0.0:$PORT
worker: celery -A core worker --loglevel=info
beat: celery -A core beat --loglevel=info
