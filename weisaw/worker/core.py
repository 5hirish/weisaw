import logging
import sys
import os
# from celery import Celery, states
# from weisaw.worker.settings import get_logger

# from raven import Client
# from raven.contrib.celery import register_signal, register_logger_signal

from weisaw.api.core import create_app
from weisaw.api.settings import DevConfig, TestConfig, ProdConfig

# celery worker -A dolores.worker.core.celery_task --loglevel=DEBUG
# celery flower -A dolores.worker.core.celery_task

# def get_sentry_client(app_conf):
#     client = Client(app_conf.SENTRY_DSN)
#     # register a custom filter to filter out duplicate logs
#     register_logger_signal(client)
#
#     # The register_logger_signal function can also take an optional argument
#     # `loglevel` which is the level used for the handler created.
#     # Defaults to `logging.ERROR`
#     register_logger_signal(client, loglevel=logging.INFO)
#
#     # hook into the Celery error handler
#     register_signal(client)
#
#     # The register_signal function can also take an optional argument
#     # `ignore_expected` which causes exception classes specified in Task.throws
#     # to be ignored
#     register_signal(client, ignore_expected=True)
#
#     return client


flask_env = str(os.environ.get('FLASK_ENV'))
if flask_env == 'dev':
    app_config = DevConfig
elif flask_env == 'test':
    app_config = TestConfig
else:
    app_config = ProdConfig


task_app = create_app(app_config, enable_blueprints=False)
task_app.app_context().push()

# logger = get_logger()
# sentry_client = get_sentry_client(app_config)

# celery_task = Celery()
# celery_task.config_from_object(task_app.config, namespace='CELERY')
# celery_task.autodiscover_tasks(packages=['weisaw.worker'])


# class BaseTask(celery_task.Task):
#     """Abstract base class for all tasks in the app."""
#
#     abstract = True
#
#     def on_retry(self, exc, task_id, args, kwargs, einfo):
#         """Log the exceptions to something like sentry at retry."""
#         super(BaseTask, self).on_retry(exc, task_id, args, kwargs, einfo)
#
#     def on_failure(self, exc, task_id, args, kwargs, einfo):
#         """Log the exceptions to something like sentry."""
#         # sentry_client.captureException()
#         super(BaseTask, self).on_failure(exc, task_id, args, kwargs, einfo)
