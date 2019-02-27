import os
import logging
from dotenv import load_dotenv

# from slack_log_handler import SlackLogHandler

# OR, the same with increased verbosity:


class Config:
    """Base configuration."""

    if str(os.environ.get('FLASK_ENV')) != 'prod':
        app_debug = True
        load_dotenv(verbose=True)
    else:
        app_debug = False

    SECRET_KEY = os.getenv("SECRET_KEY")
    SESSION_COOKIE_NAME = 'weisaw_app'

    SENTRY_DSN = os.getenv("SENTRY_DSN")

    UPLOAD_FOLDER = os.getcwd() + "/weisaw/static/"

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SLACK_CLIENT_ID = os.getenv('SLACK_CLIENT_ID')
    SLACK_CLIENT_SECRET = os.getenv('SLACK_CLIENT_SECRET')
    SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
    SLACK_BOT_SCOPE = os.getenv('SLACK_BOT_SCOPE')
    SLACK_OAUTH_TOKEN = os.getenv('SLACK_OAUTH_TOKEN')
    SLACK_OAUTH_BOT_TOKEN = os.getenv("SLACK_OAUTH_BOT_TOKEN")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    # BROKER_POOL_LIMIT = 1


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'

    DEBUG = False


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True

    SQLALCHEMY_ECHO = True

    SESSION_COOKIE_SECURE = False

    SENTRY_DSN = ""


class TestConfig(Config):
    """Test configuration."""

    ENV = 'test'
    TESTING = True
    DEBUG = True



