
import time
import pathlib

from flask import Blueprint, render_template, redirect, url_for, flash, session, g
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import data_required, length
from werkzeug.security import check_password_hash, generate_password_hash

from app import logger, db
from app.forms import (
    ProjectButton, RecordsForm,
    ReturnButton, ReportProjectForm, available_login)
from app.models import Records, Employees, Costs, Tasks, Projects, GIPs
from app.helper_functions import sorting_projects_names
from app.reports_makers import (
    make_query_to_dict_list,
    make_report_that_andrews_like,
    get_project_report_dict,
    replace_id_to_name_in_record_dict)

main = Blueprint('main', __name__, static_url_path="/static/main", static_folder="/static/main")
folder_path_that_contains_this_file = pathlib.Path(__file__).parent.resolve()

# TODO:
#  [ ]: Реструктурировать все таблицы с Costs, главным образом в отчетах

@main.cli.command("init_emp")
def init_emp():
    db.create_all()
    with open(str(folder_path_that_contains_this_file)+"/files/employees.txt",'r') as f:
        for line in f:
            spl_line = line.split()
            login = spl_line[0].split("@")[0]
            password = spl_line[1]
            hashed_password = generate_password_hash(password=password)
            new_one = Employees(login, hashed_password)
            new_one.register()

@main.cli.command("create_db")
def init_emp():
    db.create_all()

@main.cli.command("records_backup")
def do_records_backup():
    all_records = Records.query.all()
    with open(str(folder_path_that_contains_this_file)+"/files/records.txt", "w") as f:
        for record in all_records:
            f.write(record.__repr__())
            f.write('\n')

@main.cli.command("reload_records_from_records_txt")
def load_records():
    db.create_all()
    Records.__table__.drop(db.engine)
    db.create_all()
    with open(str(folder_path_that_contains_this_file)+"/files/records.txt", "r") as f:
        for line in f:
            splited_list = line.split(",")
            need_info = list(map(int, splited_list[2:]))
            new_rec = Records(need_info[0],
                              need_info[1],
                              need_info[2],
                              need_info[3],
                              need_info[4],
                              need_info[5])
            new_rec.save()



@main.route("/", methods=['GET', 'POST'])
def index():
    emp = g.emp
    if emp is None:
        print("Redirect to login")
        return redirect(url_for('auth.login'))
    else:
        print("Redirect to make record")
        return redirect(url_for('.record', login=emp.login))


@main.route("/record", methods=['GET', 'POST'])
def record():
    login = g.emp.login
    try:
        form = RecordsForm()
        rec = Records()
        # TODO: 
        # [ ]: В costs_name_list д. б. список только тех статей затрат, 
        #      которые относятся к этому проекту
        #      TIPS: Это задача создания динамичских выпадающих списков
        costs_name_list = Costs.get_costs_names()
        projects_name_id_list = Projects.get_projects_id_name_list()
        sorted_projects_name_list = sorting_projects_names(projects_name_id_list)
        form.project_name.choices = sorted_projects_name_list
        form.category_of_costs.choices = costs_name_list
        if form.is_submitted():
            # TODO: 
            # [ ]: Правильно заносить записи с учётом новой таблицы ProjectsCosts
            rec.employee_id = Employees.query.filter_by(login=login).first().id
            rec.cost_id = Costs.query.filter_by(cost_name=form.category_of_costs.data).first().id
            rec.task_id = Tasks.query.filter_by(task_name=form.task.data).first().id

            rec.project_id = int(form.project_name.data)
            rec.hours = form.hours.data
            rec.minuts = form.minuts.data
            rec.save()
            flash('Запись добавлена. Несите следующую!', category="success")
            return redirect(url_for('main.record', login=login))
        else:
            return render_template('main/records.html', form=form, login=login)
    except Exception as e:
        logger.warning(f"In record page fail has been ocured: {e}")
        flash('Что-то пошло не так...', category="error")
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
            new_dict = make_report_that_andrews_like(old_dict)
            return render_template('main/project_report.html', data=new_dict, returnBtn=returnBtn)
        else:
            return render_template('main/project_report_form.html', form=form)
    except Exception as e:
        logger.warning(f"In project_report fail has been ocured: {e} with new dict {new_dict}")
        time.sleep(1)
        return redirect(url_for('main.project_report'))
    



@main.errorhandler(500)
def handle_error(err):
    headers = err.data.get('headers', None)
    messages = err.data.get('messages', ['Invalid Request.'])
    logger.warning(f'Error 500: {messages}')
    time.sleep(1)
    return redirect(url_for("main.index"))
