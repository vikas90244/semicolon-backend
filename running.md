# Running commands

Use these commands to start Redis and Celery for the backend.

```powershell
docker run -d --name redis -p 6379:6379 redis:7
python -m celery -A core worker --loglevel=info
python -m celery -A core beat --loglevel=info
```
