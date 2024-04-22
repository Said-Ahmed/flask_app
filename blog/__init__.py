from flask import Flask
from flask_login import LoginManager
from flask_restful import Api
from flask_wtf import CSRFProtect

from blog.models import Base

app = Flask(__name__)

csrf = CSRFProtect()
manager = LoginManager()
api = Api(app)


def create_app():
    app.secret_key = 'some secret key'
    manager.init_app(app)

    with app.app_context():
        from . import routes

    return app
