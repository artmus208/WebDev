
import time

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import data_required, length

from app import logger
from app.forms import (
    ProjectButton, RecordsForm, 
    available_login, ReturnButton,
    ReportProjectForm)
from app.models import Records, Employees, Costs, Tasks, Projects

from app.support_functions import sorting_projects_names
from app.reports_makers import (
    make_query_to_dict_list, 
    make_report_that_andrews_like,
    get_project_report_dict,
    replace_id_to_name_in_record_dict)

main = Blueprint('main', __name__, template_folder='templates', static_folder='static')

@main.route("/", methods=['GET', 'POST'])
def home():
    emp_logins = Employees.get_all_logins()
    class UserForm(FlaskForm):
        username = StringField(label='Логин сотрудника',
                               validators=[
                                            data_required(), length(min=3),
                                            available_login(emp_logins)
                                          ]
                                )
        submit = SubmitField('Продолжить')

    try:
        form = UserForm()
        # form = UserForm()
        reportBtn = ProjectButton()
        if form.validate_on_submit():
            username = form.username.data
            return redirect(url_for('record', login=username))
        else:
            flash("Если не пускают дальше, возможно, логин не зарегистрирован")
            return render_template('home.html', form=form, reportBtn=reportBtn)
    except Exception as e:
        logger.warning(f"In Index page fail has been ocured: {e}")
        return e

@main.route("/record/<login>", methods=['GET', 'POST'])
def record(login):
    try:
        form = RecordsForm()
        reportBtn = ProjectButton()
        returnBtn = ReturnButton()
        costs_name_list = Costs.get_costs_names()
        projects_name_id_list = Projects.get_projects_id_name_list()
        sorted_projects_name_list = sorting_projects_names(projects_name_id_list)
        form.project_name.choices = sorted_projects_name_list
        form.category_of_costs.choices = costs_name_list
        if form.validate_on_submit():
            rec = Records()
            rec.employee_id = Employees.query.filter_by(login=login).first().id
            rec.project_id = int(form.project_name.data)
            rec.cost_id = Costs.query.filter_by(cost_name=form.category_of_costs.data).first().id
            rec.task_id = Tasks.query.filter_by(task_name=form.task.data).first().id
            rec.hours = form.hours.data
            rec.minuts = form.minuts.data
            rec.save()
            flash('Запись добавлена. Несите следующую!')
            return redirect(url_for('record', login=login))
        else:
            return render_template('records.html', form=form,
                                    login=login, reportBtn=reportBtn,
                                    returnBtn=returnBtn)
    except Exception as e:
        logger.warning(f"In record page fail has been ocured: {e}")
        time.sleep(1)
        return redirect(url_for('record', login=login))


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
            new_dict = make_report_that_andrews_like(old_dict)
            return render_template('project_report.html', data=new_dict, returnBtn=returnBtn)
        else:
            return render_template('project_report_form.html', form=form)
    except Exception as e:
        logger.warning(f"In project_report fail has been ocured: {e}")
        time.sleep(1)
        return redirect(url_for('project_report'))