import logging
import click
import datetime

from flask import Flask, redirect, render_template, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

from reports_makers import make_query_to_dict_list, get_project_report_dict

db = SQLAlchemy()
from config import Config

# Импорт модели данных
from models import Employees, Admins, Costs, Tasks, CostsProjectsTasks, GIPs
from models import Records, Projects, Record_Keeping
from forms import *
# Создание таблиц в БД

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


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
            login = spl_line[0]
            password = spl_line[1]
            emp = Employees(login=login, password=password)
            db.session.add(emp)
            print(emp.login)
        db.session.commit()

@app.cli.command("add_admin")
@click.argument("admin_login")
def add_admin(admin_login):
    emp_logins = [emp.login for emp in db.session.execute(db.select(Employees)).scalars()]
    if admin_login in emp_logins:
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




# Конфигурация логгера
def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    file_handler = logging.FileHandler('log/api.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = setup_logger()

@app.route("/", methods=['GET', 'POST'])
def home():
    try:
        form = UserForm()
        reportBtn = ProjectButton()
        if form.validate_on_submit():
            username = form.username.data
            return redirect(url_for('record', login=username))
        else:
            return render_template('home.html', form=form, reportBtn=reportBtn)
    except Exception as e:
        logger.warning(f"In Index page fail has been ocured: {e}")

@app.route("/record/<login>", methods=['GET', 'POST'])
def record(login):
    try:
        form = Record()        
        if form.validate_on_submit():
            rec = Records()
            rec.employee = login
            rec.project_name = form.project_name.data
            rec.category_of_costs = form.category_of_costs.data
            rec.task = form.task.data
            rec.hours = form.hours.data
            rec.minuts = form.minuts.data
            db.session.add(rec)
            db.session.commit()
            return render_template('success.html', login=login)
        else:
            return render_template('records.html', form=form, login=login)
    except Exception as e:
        logger.warning(f"In record page fail has been ocured: {e}")

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


@app.before_first_request
def create_database():
    with app.app_context():
        db.create_all()


@app.route('/rep', methods=['GET', 'POST'])
def project_report():
    try:
        form = ReportProjectForm()
        if form.validate_on_submit():
            selectedProj = form.project_name.data
            records = Record_Keeping.query.filter_by(project_name=selectedProj).all()
            rec_list_dict = make_query_to_dict_list(records)
            res_dict = get_project_report_dict(all_records=rec_list_dict, p_name=selectedProj)
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