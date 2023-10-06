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
    
    
    bd_connectorname = os.environ.get("TCS_BD_CONNECTOR", "mariadb+mariadbconnector")
    bd_username = os.environ.get("TCS_BD_USER", "root")
    bd_password = os.environ.get("TCS_BD_PASSWORD", "pesk-2020")
    bd_host = os.environ.get("TCS_BD_HOST", "127.0.0.1:3306")
    bd_name = os.environ.get("TCS_BD_NAME", "time_managment_web_app")
    
    if not all([bd_connectorname, bd_username, bd_password, bd_host, bd_name]):
        raise Exception(f"DSN error: {[bd_connectorname, bd_username, bd_password, bd_host, bd_name]}")
        
    
    data_base_URI = f"{bd_connectorname}://{bd_username}:{bd_password}@{bd_host}/{bd_name}"
    
    app.config['SQLALCHEMY_DATABASE_URI'] = data_base_URI
    app.config['SQLALCHEMY_ECHO'] = False
    db.init_app(app)
    return app, db


# Конфигурация логгера
def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    file_handler = logging.FileHandler('api.log') # WebDev/log/api.log
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = setup_logger()
app, db = create_app_db()
select = db.select
execute = db.session.execute


from app.main.views import main
from app.auth.views import auth
from app.gip.views import gip
from app.admin import admin
from app.report.routes import report 

app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(gip)
app.register_blueprint(admin)
app.register_blueprint(report)

with app.app_context():
    db.create_all()
