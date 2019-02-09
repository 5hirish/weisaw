import os
import logging
from dotenv import load_dotenv
# from slack_log_handler import SlackLogHandler

# load_dotenv()

# OR, the same with increased verbosity:
load_dotenv(verbose=True)


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY")

    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))

    # DB_DIALECT = ''
    # DB_DRIVER = ''
    # DB_NAME = ''

    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

    SESSION_COOKIE_NAME = 'wahkhen_app'
    # SESSION_COOKIE_SECURE = False    # Browsers will only send cookies with requests over HTTPS.
    # SESSION_PERMANENT = False
    # SESSION_USE_SIGNER = True

    # MAIL_SERVER = 'localhost'
    # MAIL_PORT = 25
    # MAIL_DEFAULT_SENDER = 'no_reply@localhost.com'

    SENTRY_DSN = ""

    UPLOAD_FOLDER = os.getcwd() + "/weisaw/static/"


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'

    DEBUG = False

    # CELERY_BROKER_URL = ''
    # CELERY_RESULT_BACKEND = ''

    # DB_USERNAME = ''
    # DB_PASSWORD = ''
    # DB_HOSTNAME = ''
    # DB_PORT = ''
    #
    # SQLALCHEMY_DATABASE_URI = Config.DB_DIALECT + '+' + Config.DB_DRIVER + '://' \
    #                           + DB_USERNAME + ':' + DB_PASSWORD +'@' + DB_HOSTNAME + ':'
    #                           + DB_PORT + '/' + Config.DB_NAME

    SENTRY_DSN = "https://7e422fa26fc741e6a0612d4163a1bdbe@sentry.io/1361447"


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True

    # CELERY_BROKER_URL = ''
    # CELERY_RESULT_BACKEND = ''

    # DB_USERNAME = ''
    # DB_PASSWORD = ''
    # DB_HOSTNAME = ''
    # DB_PORT = ''

    # SQLALCHEMY_DATABASE_URI = Config.DB_DIALECT + '+' + Config.DB_DRIVER + '://' \
    #                          + DB_USERNAME + ':' + DB_PASSWORD + '@' + DB_HOSTNAME
    #                          + ':' + DB_PORT + '/' + Config.DB_NAME

    # DATABASE_URL = SQLALCHEMY_DATABASE_URI

    SQLALCHEMY_ECHO = True

    SESSION_COOKIE_SECURE = False

    SENTRY_DSN = ""


class TestConfig(Config):
    """Test configuration."""

    ENV = 'test'
    TESTING = True
    DEBUG = True


def get_logger(name):
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(name)

    gunicorn_logger = logging.getLogger('gunicorn.error')

    # log_dir = "/var/log/wahkhen_app/"
    # create file handler which logs even debug messages
    # os.makedirs(os.path.dirname(log_dir), exist_ok=True)

    slack_hook_url = os.getenv("SLACK_HOOK_URL")
    slack_log_channel = os.getenv("SLACK_CHANNEL_NAME")

    # Create slack handler
    # sh = SlackLogHandler(slack_hook_url,
    #                      channel=slack_log_channel, username="wahkhen_api")

    # fh = logging.FileHandler(log_dir+'wahkhen_app.log')

    # fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # sh.setLevel(logging.WARNING)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # fh.setFormatter(formatter)

    # add the handlers to logger
    logger.addHandler(ch)
    # logger.addHandler(fh)
    # logger.addHandler(sh)
    logger.addHandler(gunicorn_logger)

    return logger
