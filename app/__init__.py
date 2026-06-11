from flask import Flask

def create_app():
    app = Flask(__name__)

    from app.routes import payment_bp
    app.register_blueprint(payment_bp)

    return app