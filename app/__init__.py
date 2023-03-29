import logging

import pathlib
import os

from flask import Flask, redirect, render_template, url_for, jsonify, flash

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from app.config import Config
folder_path_that_contains_this_file = pathlib.Path(__file__).parent.resolve()

def create_app_db():
    app = Flask(__name__)
    app.config.from_object(Config)
    db = SQLAlchemy()
    data_base_URI = None
    if os.name == 'posix':
        data_base_URI = "{connectorname}://{username}:{password}@{hostname}/{databasename}".format(
            connectorname="mysql+mysqlconnector",
            username="artmus208",
            password="pesk-2020",
            hostname="artmus208.mysql.pythonanywhere-services.com",
            databasename="artmus208$time_managment_web_app",
            )
    else:
        data_base_URI = "{connectorname}://{username}:{password}@{hostname}/{databasename}".format(
            connectorname="mariadb+mariadbconnector",
            username="root",
            password="pesk-2020",
            hostname="127.0.0.1:3306",
            databasename="time_managment_web_app",
            )
    app.config['SQLALCHEMY_DATABASE_URI'] = data_base_URI
    # @app.teardown_appcontext
    # def shutdown_session(exception=None):
    #     db.session.remove()

    @app.before_first_request
    def create_database():
        with app.app_context():
            db.create_all()

    db.init_app(app)
    return app, db


# Конфигурация логгера
def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    file_handler = logging.FileHandler( 
        str(folder_path_that_contains_this_file)+'/log/api.log') # WebDev/log/api.log
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = setup_logger()
app, db = create_app_db()
from app.main.views import main
from app.auth.views import auth
from app.gip.views import gip
app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(gip)
