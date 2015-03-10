#!flask/bin/python
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
import psycopg2
from config import basedir
from config import config

db = SQLAlchemy()
lm = LoginManager()
lm.login_view = 'login'
login_manager = LoginManager()
login_manager.login_view = 'layout.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config.from_object(config[config_name])
    db.init_app(app)
    login_manager.init_app(app)
    # login_manager.user_loader(load_user)
    from .layout import layout as appr_blueprint
    # register our blueprints
    app.register_blueprint(appr_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    return app
