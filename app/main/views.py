from flask import Blueprint, render_template, redirect, url_for, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import session

from .forms import *

from app import logger
from app.models import Record_Keeping

records = Blueprint('records', __name__)

@records.route("/", methods=['GET', 'POST'])
def home():
    try:
        form = UserForm()
        if form.validate_on_submit():
            username = form.username.data
            return redirect(url_for('records.record', uname=username))
        else:
            return render_template('home.html', form=form)
    except Exception as e:
        logger.warning(f"In Index page fail has been ocured: {e}")

@records.route("/record/<uname>", methods=['GET', 'POST'])
def record(uname):
    try:
        form = Record()
        if form.validate_on_submit():
            rec = Record_Keeping()
            rec.employee = uname
            rec.project_name = form.project_name.data
            rec.category_of_costs = form.category_of_costs.data
            rec.task = form.task.data 
            rec.hours = form.hours.data
            rec.minuts = form.minuts.data
            session.add(rec)
            session.commit()
            return render_template('success.html', uname=uname)
        else:
            return render_template('records.html', form=form, uname=uname)
    except Exception as e:
        logger.warning(f"In record page fail has been ocured: {e}")