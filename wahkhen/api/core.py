import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from flask import Flask, jsonify
from datetime import datetime

from wahkhen.api.settings import ProdConfig, get_logger

app_name = 'wahkhen'


def create_app(config_object=ProdConfig, enable_blueprints=True):

    sentry_sdk.init(
        dsn=ProdConfig.SENTRY_DSN,
        integrations=[FlaskIntegration()]
    )

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
    # sentry.init_app(app)
    return None


def register_blueprints(app):

    # defer the import until it is really needed

    from wahkhen.api.ypro.views import ypro_blueprint
    from wahkhen.api.job.views import job_blueprint
    from wahkhen.api.slash.views import slacker_blueprint

    """Register Flask blueprints."""
    app.register_blueprint(ypro_blueprint)
    app.register_blueprint(job_blueprint)
    app.register_blueprint(slacker_blueprint)

    return None


def register_error_handlers(app):
    """Register error handlers."""
    def return_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        if error_code == 404:
            return jsonify({"success": False, "msg": "API not found :("}), error_code
        elif error_code == 405:
            return jsonify({"success": False, "msg": "API method not allowed :/"}), error_code
        elif error_code == 500:
            return jsonify({"success": False, "msg": "Internal api error X("}), error_code
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
        return jsonify({"name": "Wahkhen Waterfalls", "lat": 0, "lng": 0, "time": datetime.utcnow()})


def register_logger(app):
    app.logger = get_logger(__name__)