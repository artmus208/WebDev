import logging

import pathlib
import os

from dotenv import load_dotenv

from flask import Flask, redirect, render_template, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from app.config import Config
folder_path_that_contains_this_file = pathlib.Path(__file__).parent.resolve()

def create_app_db():
    app = Flask(__name__)
    app.config.from_object(Config)
    db = SQLAlchemy()
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    load_dotenv(os.path.join(basedir, '.env'))
    
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
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 60,
        'pool_pre_ping': True
    }
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
from app.stub import stub_bp

app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(gip)
app.register_blueprint(admin)
app.register_blueprint(report)
app.register_blueprint(stub_bp)

with app.app_context():
    db.create_all()
