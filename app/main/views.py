
import time

from flask import Blueprint, render_template, redirect, url_for, flash, session, g
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import data_required, length

from app import logger
from app.forms import (
    ProjectButton, RecordsForm, 
    ReturnButton, ReportProjectForm, available_login)
from app.models import Records, Employees, Costs, Tasks, Projects
from app.support_functions import sorting_projects_names
from app.reports_makers import (
    make_query_to_dict_list, 
    make_report_that_andrews_like,
    get_project_report_dict,
    replace_id_to_name_in_record_dict)

main = Blueprint('main', __name__, static_url_path="/static/main", static_folder="/static/main")

@main.cli.command("init_emp")
def init_emp():
    with open("static/files/employees.txt",'r') as f:
        for line in f:
            spl_line = line.split()
            login = spl_line[0].split("@")[0]
            password = spl_line[1]
            emp = Employees(login=login, password=password)
            db.session.add(emp)
            print(emp.login)
        db.session.commit()

@main.route("/", methods=['GET', 'POST'])
def index():
    emp = g.emp
    redirect_ = None
    if emp is None:
        print("Redirect to login")
        return redirect(url_for('auth.login'))
    else:
        print("Redirect to make record")
        print(emp.login, type(emp.login))
        return redirect(url_for('.record', login=emp.login))
    

"""Что-то непонятное творится в логике предстваления ниже"""

@main.route("/record", methods=['GET', 'POST'])
def record():
    login = "mar"
    try:
        form = RecordsForm()
        reportBtn = ProjectButton()
        returnBtn = ReturnButton()
        rec = Records()
        costs_name_list = Costs.get_costs_names()
        projects_name_id_list = Projects.get_projects_id_name_list()
        sorted_projects_name_list = sorting_projects_names(projects_name_id_list)
        form.project_name.choices = sorted_projects_name_list
        form.category_of_costs.choices = costs_name_list
        if form.validate_on_submit():
            rec.employee_id = Employees.query.filter_by(login=login).first().id
            rec.cost_id = Costs.query.filter_by(cost_name=form.category_of_costs.data).first().id
            rec.task_id = Tasks.query.filter_by(task_name=form.task.data).first().id

            rec.project_id = int(form.project_name.data)
            rec.hours = form.hours.data
            rec.minuts = form.minuts.data
            rec.save()
            flash('Запись добавлена. Несите следующую!')
            return redirect(url_for('main.record', login=login))
        else:
            return render_template('main/records.html', form=form,
                                    login=login, reportBtn=reportBtn,
                                    returnBtn=returnBtn)
    except Exception as e:
        logger.warning(f"In record page fail has been ocured: {e}")
        time.sleep(1)
        return redirect(url_for('main.record', login=login))


@main.route('/rep', methods=['GET', 'POST'])
def project_report():
    try:
        form = ReportProjectForm()
        returnBtn = ReturnButton()
        projects_name_id_list = Projects.get_projects_id_name_list()
        sorted_projects_name_list = sorting_projects_names(projects_name_id_list)
        form.project_name.choices = sorted_projects_name_list
        if form.validate_on_submit():
            proj_id = int(form.project_name.data)
            records = Records.query.filter_by(project_id=proj_id).all()
            rec_list_dict = make_query_to_dict_list(records)
            rec_list_dict = replace_id_to_name_in_record_dict(rec_list_dict)
            old_dict = get_project_report_dict(all_records=rec_list_dict,
                                               p_name=Projects.query.get(proj_id).project_name)
            print(old_dict)
            new_dict = make_report_that_andrews_like(old_dict)
            return render_template('main/project_report.html', data=new_dict, returnBtn=returnBtn)
        else:
            return render_template('main/project_report_form.html', form=form)
    except Exception as e:
        logger.warning(f"In project_report fail has been ocured: {e} with new dict {new_dict}")
        time.sleep(1)
        return redirect(url_for('main.project_report'))