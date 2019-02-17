# import sentry_sdk
# from sentry_sdk.integrations.flask import FlaskIntegration
import logging
import os

from flask import Flask, jsonify
from datetime import datetime
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from weisaw.api.settings import ProdConfig
from weisaw.api.extensions import migrate, db

app_name = 'weisaw'


def create_app(config_object=ProdConfig, enable_blueprints=True):

    # sentry_sdk.init(
    #     dsn=ProdConfig.SENTRY_DSN,
    #     integrations=[FlaskIntegration()]
    # )

    app = Flask(__name__)

    app.config.from_object(config_object)
    register_extensions(app)
    if enable_blueprints:
        register_blueprints(app)
    register_error_handlers(app)
    register_route(app)
    if enable_blueprints:
        register_logger(app)
    # register_shell_context(app)
    # register_commands(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""

    sentry_sdk.init(
        dsn=app.config.get("SENTRY_DSN"),
        integrations=[FlaskIntegration()]
    )

    db.init_app(app)
    migrate.init_app(app, db)

    return None


def register_blueprints(app):

    # defer the import until it is really needed

    from weisaw.api.auth.views import auth_blueprint
    from weisaw.api.slash.views import slash_blueprint

    """Register Flask blueprints."""
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(slash_blueprint)

    return None


def register_error_handlers(app):
    """Register error handlers."""
    def return_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        if error_code == 404:
            return jsonify({"response_type": "ephemeral", "text": "This slash command isn't supported :("}), 200
        elif error_code == 405:
            return jsonify({"response_type": "ephemeral", "text": "This slash command couldn't be served :/"}), 200
        elif error_code == 500:
            return jsonify({"response_type": "ephemeral", "text": "Something went wrong with this command X("}), 200
    for errcode in [404, 405, 500]:
        app.errorhandler(errcode)(return_error)
    return None


def register_route(app):

    # done by using alembic migrations
    # @app.before_first_request
    # def create_tables():
    #     # will not attempt to recreate tables already present in the target database.
    #     db.create_all()

    @app.before_first_request
    def first_request_tasks():
        pass

    @app.route('/', methods=['GET'])
    def init_api():
        return jsonify(
            {
                "name": "Wei Sawdong",
                "lat": 25.291632, "lng": 91.6782126,
                "time": datetime.utcnow(),
                "developer": "Alleviate"
            }
        )


def register_logger(app):

    gunicorn_logger = logging.getLogger('gunicorn.error')

    log_dir = "log/weisaw_app/"
    # create file handler which logs even debug messages
    os.makedirs(os.path.dirname(log_dir), exist_ok=True)

    slack_hook_url = os.getenv("SLACK_HOOK_URL")
    slack_log_channel = os.getenv("SLACK_CHANNEL_NAME")

    # Create slack handler
    # sh = SlackLogHandler(slack_hook_url,
    #                      channel=slack_log_channel, username="wahkhen_api")

    fh = logging.FileHandler(log_dir+'weisaw_app.log')

    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # sh.setLevel(logging.WARNING)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # add the handlers to logger
    app.logger.addHandler(ch)
    app.logger.addHandler(fh)
    # logger.addHandler(sh)
    app.logger.addHandler(gunicorn_logger)