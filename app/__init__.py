from flask import Flask
from flasgger import Swagger

def create_app():
    app = Flask(__name__)

    # Enable Swagger UI
    Swagger(app)

    from app.routes import payment_bp
    app.register_blueprint(payment_bp)

    return app