web: gunicorn run_server:weisaw_app
worker: celery worker -A dolores.worker.core.celery_task --loglevel=DEBUG