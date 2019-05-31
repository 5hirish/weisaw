web: gunicorn run_server:weisaw_app
worker: celery worker -A weisaw.worker.core.celery_task -Q weisaw --loglevel=DEBUG