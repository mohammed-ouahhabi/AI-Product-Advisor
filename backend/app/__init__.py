from flask import Flask
from flask_cors import CORS

from .config import settings
from .extensions import db, jwt
from .routes import api


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = settings.JWT_SECRET_KEY

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    app.register_blueprint(api)

    with app.app_context():
        db.create_all()

    return app
