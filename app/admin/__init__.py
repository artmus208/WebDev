from flask import Blueprint

from app.models import (
    Records, Employees,
    Costs, Tasks, Projects,
    GIPs, ProjectCosts, CostsTasks,
    Admins)

from app import select, execute
from app import logger

admin = Blueprint('admin', 
                  __name__,
                  url_prefix="/admin",
                  static_url_path="/static/admin", 
                  static_folder="/static/admin")

@admin.before_app_first_request
def ping_connect():
    try:
        # logger.info("Ping DB")
        res = execute(
            select(Records)
        ).first()
    except:
        logger.warning("Ping DB")

from .views import *