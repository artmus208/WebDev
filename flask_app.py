import logging
import click
import datetime
import time
import pathlib
from transliterate import translit

from flask import Flask, redirect, render_template, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy

from reports_makers import make_query_to_dict_list, get_project_report_dict


from config import Config
db = SQLAlchemy()
# Импорт модели данных
from models import * # Employees, Admins, Costs, Tasks, CostsProjectsTasks, GIPs
# from models import Records, Projects, Record_Keeping
from forms import *


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

EMP_LOGINS = []
# Создание таблиц в БД
@app.cli.command("check")
@click.argument("name")
def create_user(name):
    print("Check", name)

@app.cli.command("drop_db")
def drop_db():
    print("Start droping")
    db.drop_all()
    db.session.commit()
    print("End droping")

@app.cli.command("create_db")
def create_db():
    print("Start creating")
    db.drop_all()
    db.create_all()
    db.session.commit()
    print("End creating")

@app.cli.command("init_emp")
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

@app.cli.command("add_admin")
@click.argument("admin_login")
def add_admin(admin_login):
    global EMP_LOGINS
    if admin_login in EMP_LOGINS:
        admin_id = Employees.query.filter_by(login=admin_login).first().id
        admin = Admins(admin_id)
        db.session.add(admin)
        db.session.commit()
        print(admin_login, 'is added')
    else:
        print("No such employeer with login: " + admin_login)

@app.cli.command("init_costs")
def init_costs():
    with open("static/files/costs.txt",'r', encoding='utf-8') as f:
        all_costs = f.read().splitlines()
        for line in all_costs:
            cost = Costs(cost_name=line)
            db.session.add(cost)
            print(cost.cost_name)
        db.session.commit()


@app.cli.command("init_gips")
def init_gips():
    with open("static/files/gips.txt",'r') as f:
        gips_logins = f.read().splitlines()
        for gip_login in gips_logins:
            print(gip_login)
            try:
                gip_id = Employees.query.filter_by(login=gip_login).first().id
                db.session.add(GIPs(gip_id=gip_id))
            except AttributeError:
                print(gip_login, "has no in employees list")
        db.session.commit()

@app.cli.command("init_tasks")
def init_tasks():
    with open("static/files/tasks.txt",'r', encoding='utf-8') as f:
        tasks = f.read().splitlines()
        for line in tasks:
            db.session.add(Tasks(line))
            print(line)
        db.session.commit()

@app.cli.command("init_projects")
def init_projects():
    with open("static/files/projects.txt",'r', encoding='utf-8') as f:
        projects_list = f.read().splitlines()
        for p in projects_list:
            try:
                one_proj = p.split('|')
                project_name = one_proj[0]
                day, month, year = map(int, one_proj[1].split())
                start_time = datetime.datetime(year, month, day)
                day, month, year = map(int, one_proj[2].split())
                end_time = datetime.datetime(year, month, day)
                gip_login = one_proj[3]
                emp_id = Employees.query.filter_by(login=gip_login).first().id
                gip_id = GIPs.query.filter_by(employee_id=emp_id).first().id
                project = Projects(project_name, gip_id, start_time, end_time)
                db.session.add(project)
                db.session.commit()
                print(project.id, project.project_name)
            except Exception as e:
                print(f"In init projects Exception occured: {e} ")




folder_path_that_contains_this_file = pathlib.Path(__file__).parent.resolve()
# Конфигурация логгера
def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    file_handler = logging.FileHandler(
        str(folder_path_that_contains_this_file)+'/log/log.log') # WebDev/log/api.log
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
logger = setup_logger()

logger = setup_logger()

@app.route("/", methods=['GET', 'POST'])
def home():
    class UserForm(FlaskForm):
        username = StringField(label='Логин сотрудника',
                               validators=[
                                            data_required(),length(min=3),
                                            available_login(EMP_LOGINS)
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


@app.route("/record/<login>", methods=['GET', 'POST'])
def record(login):
    try:
        form = RecordsForm()
        reportBtn = ProjectButton()
        returnBtn = ReturnButton()
        costs_name_list = [
            c.cost_name for c in db.session.execute(db.select(Costs)).scalars()
            ]
        projects_name_list = [
            p.project_name for p in db.session.execute(db.select(Projects)).scalars()
            ]
        form.category_of_costs.choices = costs_name_list
        form.project_name.choices = projects_name_list
        if form.validate_on_submit():
            rec = Records()
            rec.employee_id = Employees.query.filter_by(login=login).first().id
            rec.project_id = Projects.query.filter_by(project_name=form.project_name.data).first().id
            rec.cost_id = Costs.query.filter_by(cost_name=form.category_of_costs.data).first().id
            rec.task_id = Tasks.query.filter_by(task_name=form.task.data).first().id
            rec.hours = form.hours.data
            rec.minuts = form.minuts.data
            db.session.add(rec)
            db.session.commit()
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

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


@app.before_first_request
def create_database():
    with app.app_context():
        db.create_all()
        global EMP_LOGINS
        EMP_LOGINS = [emp.login for emp in db.session.execute(db.select(Employees)).scalars()]



def replace_id_to_name_in_record_dict(list_of_ditc) -> dict:
    for item in list_of_ditc:
        item["employee_id"] = db.session.get(Employees, item["employee_id"]).login
        item["project_id"] = db.session.get(Projects, item["project_id"]).project_name
        item["cost_id"] = db.session.get(Costs, item["cost_id"]).cost_name
        item["task_id"] = db.session.get(Tasks, item["task_id"]).task_name
        cost_postfix = translit(item["cost_id"][:4], language_code='ru', reversed=True)
        if item["task_id"] == "blank_task":
            item["task_id"] = item["employee_id"] + "_" + item["task_id"] + "_" + cost_postfix
    return list_of_ditc


@app.route('/rep', methods=['GET', 'POST'])
def project_report():
    flash('Отчет будет показан в формате JSON. \n\
          Для корректного отображения таких данных, возможно, понадобится дополнение\
           к браузеру (например, JSONVue)')
    try:
        form = ReportProjectForm()
        projects_name_list = [
            p.project_name for p in db.session.execute(db.select(Projects)).scalars()
            ]
        form.project_name.choices = projects_name_list
        if form.validate_on_submit():
            selected_proj_name = form.project_name.data
            proj_id = Projects.query.filter_by(project_name=selected_proj_name).first().id
            records = Records.query.filter_by(project_id=proj_id).all()
            rec_list_dict = make_query_to_dict_list(records)
            print(rec_list_dict)
            rec_list_dict = replace_id_to_name_in_record_dict(rec_list_dict)
            print(rec_list_dict)
            res_dict = get_project_report_dict(all_records=rec_list_dict, p_name=selected_proj_name)
            return jsonify(res_dict)
        else:
            return render_template('project_report.html', form=form)
    except Exception as e:
        logger.warning(f"In project_report fail has been ocured: {e}")

@app.route('/rep/<selectedProj>', methods=['GET'])
def show_report(selectedProj):
    pass


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=1234)