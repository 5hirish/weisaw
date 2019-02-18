import sys
import os
import logging
from weisaw.api.core import create_app
# from weisaw.worker.core import celery_task
from weisaw.api.settings import DevConfig, TestConfig, ProdConfig


def configure_app():
    flask_env = str(os.environ.get('FLASK_ENV'))
    if flask_env == 'dev':
        return DevConfig
    elif flask_env == 'test':
        return TestConfig
    else:
        return ProdConfig


app_config = configure_app()
weisaw_app = create_app(app_config)

# weisaw_app.debug = True

if __name__ == '__main__':

    if str(os.environ.get('FLASK_ENV')) != 'prod':
        app_debug = True
    else:
        app_debug = False

    app_config = configure_app()
    weisaw_app = create_app(app_config)

    weisaw_app.debug = app_debug
    # set a 'SECRET_KEY' to enable the Flask session cookies in debug toolbar
    # The toolbar will automatically be injected into HTML responses when debug mode is on.
    # In production, setting `app.debug = False` will disable the toolbar.

    # Werkzeug, WSGI utility library for Python, enable module reloader
    weisaw_app.run(use_reloader=True, reloader_interval=0, use_debugger=app_debug, reloader_type='watchdog')