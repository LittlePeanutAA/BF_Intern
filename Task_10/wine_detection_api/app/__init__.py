from flask import Flask
from wine_detection_api.app.routes.api import api


def create_app(config_object):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')

    return app
