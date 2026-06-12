from flask import Flask
from flasgger import Swagger


def create_app():

    app = Flask(__name__)

    app.config.from_object("config.DevelopmentConfig")

    Swagger(app)

    from app.routes import payment_bp
    app.register_blueprint(payment_bp)

    return app