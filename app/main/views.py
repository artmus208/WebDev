
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
from app.models import (
    Records, Employees,
    Costs, Tasks, Projects,
    GIPs, ProjectCosts, CostsTasks,
    Admins)
from app.helper_functions import (
    sorting_projects_names, revise_records_for_ProjectCosts, 
    none_or_value)

from app.reports_makers import (
    make_query_to_dict_list,
    make_report_that_andrews_like,
    get_project_report_dict,
    replace_id_to_name_in_record_dict)

main = Blueprint('main', __name__, static_url_path="/static/main", static_folder="/static/main")
folder_path_that_contains_this_file = pathlib.Path(__file__).parent.resolve()

# DONE:
#  [x]: Реструктурировать все таблицы с Costs, главным образом в отчетах

# TODO:
# [x]: Добавить реальных ГИПов в реальные проекты на проде
# [ ]: Заняться динамическими выпадающими списками 

@main.cli.command("create_db")
def init_emp():
    db.create_all()

@main.cli.command("drop_db")
def init_emp():
    db.drop_all()

@main.cli.command("revise_records")
def rev_rec():
    res = revise_records_for_ProjectCosts()

# TIPS: Убрать в help funcs
def clear_strings(str_list):
    for i in range(len(str_list)):
        str_list[i] = str_list[i].replace('\n', '')
        str_list[i] = str_list[i].replace('\t', '')
        if str_list[i][0] == ' ': 
            str_list[i] = str_list[i].replace(' ', '', 1)
    return str_list

def delete_spaces_in(list_of_str:list):
    while True:
        try:
            space_idx = list_of_str.index("")
            list_of_str.pop(space_idx)
        except Exception as e:
            return " ".join(list_of_str)

### BACKUPS STARTS 
@main.cli.command("admins_backup")
def admins_backup():
    all_records = Admins.query.all()
    with open(str(folder_path_that_contains_this_file)+"/files/admins.txt", "w+", encoding="utf-8") as f:
        for record in all_records:
            splited_list = clear_strings(record.__repr__().split(","))
            joined_str = ','.join(splited_list)
            f.write(joined_str)
            f.write('\n')
    print(admins_backup.name, "done.")

@main.cli.command("costs_backup")
def costs_backup():
    all_records = Costs.query.all()
    with open(str(folder_path_that_contains_this_file)+"/files/costs.txt", "w+", encoding="utf-8") as f:
        for record in all_records:
            splited_list = clear_strings(record.__repr__().split(","))
            joined_str = ','.join(splited_list)
            f.write(joined_str)
            f.write('\n')
    print(costs_backup.name, "done.")

@main.cli.command("costs_tasks_backup")
def costs_tasks_backup():
    all_records = CostsTasks.query.all()
    with open(str(folder_path_that_contains_this_file)+"/files/costs_tasks.txt", "w+", encoding="utf-8") as f:
        for record in all_records:
            splited_list = clear_strings(record.__repr__().split(","))
            joined_str = ','.join(splited_list)
            f.write(joined_str)
            f.write('\n')
    print(costs_tasks_backup.name, "done.")

@main.cli.command("employees_backup")
def employees_backup():
    all_records = Employees.query.all()
    with open(str(folder_path_that_contains_this_file)+"/files/employees.txt", "w+", encoding="utf-8") as f:
        for record in all_records:
            splited_list = clear_strings(record.__repr__().split(","))
            joined_str = ','.join(splited_list)
            f.write(joined_str)
            f.write('\n')
    print(employees_backup.name, "done.")

@main.cli.command("gips_backup")
def gips_backup():
    all_records = GIPs.query.all()
    with open(str(folder_path_that_contains_this_file)+"/files/gips.txt", "w+", encoding="utf-8") as f:
        for record in all_records:
            splited_list = clear_strings(record.__repr__().split(","))
            joined_str = ','.join(splited_list)
            f.write(joined_str)
            f.write('\n')
    print(gips_backup.name, "done.")

@main.cli.command("projects_backup")
def projects_backup():
    all_records = Projects.query.all()
    with open(str(folder_path_that_contains_this_file)+"/files/projects.txt", "w+", encoding="utf-8") as f:
        for record in all_records:
            splited_list = clear_strings(record.__repr__().split(","))
            splited_list[1] = delete_spaces_in(splited_list[1].split(' '))
            joined_str = ','.join(splited_list)
            f.write(joined_str)
            f.write('\n')
    print(projects_backup.name, "done.")



@main.cli.command("project_costs_backup")
def project_costs_backup():
    all_records = ProjectCosts.query.all()
    with open(str(folder_path_that_contains_this_file)+"/files/project_costs.txt", "w+", encoding="utf-8") as f:
        for record in all_records:
            splited_list = clear_strings(record.__repr__().split(","))
            joined_str = ','.join(splited_list)
            f.write(joined_str)
            f.write('\n')
    print(project_costs_backup.name, "done.")


@main.cli.command("records_backup")
def records_backup():
    all_records = Records.query.all()
    with open(str(folder_path_that_contains_this_file)+"/files/records.txt", "w+", encoding="utf-8") as f:
        for record in all_records:
            splited_list = clear_strings(record.__repr__().split(","))
            joined_str = ','.join(splited_list)
            f.write(joined_str)
            f.write('\n')
    print(records_backup.name, "done.")

@main.cli.command("tasks_backup")
def tasks_backup():
    all_records = Tasks.query.all()
    with open(str(folder_path_that_contains_this_file)+"/files/tasks.txt", "w+", encoding="utf-8") as f:
        for record in all_records:
            splited_list = clear_strings(record.__repr__().split(","))
            joined_str = ','.join(splited_list)
            f.write(joined_str)
            f.write('\n')
    print(tasks_backup.name, "done.")
### BACKUPS ENDS ###################################################################



### LOAD STARTS ####################################################################
@main.cli.command("load_projects")
def load_projects():
    with open(str(folder_path_that_contains_this_file)+"/files/projects.txt", "r", encoding="utf-8") as f:
        for line in f:
            splited_list = clear_strings(line.split(","))
            new_rec = Projects(id=splited_list[0],
                               p_name=splited_list[1],
                               gip_id=int(splited_list[2])
                              )
            new_rec.save()
    print(load_projects.name, "done.")

@main.cli.command("load_gips")
def load_gips():
    with open(str(folder_path_that_contains_this_file)+"/files/gips.txt", "r", encoding="utf-8") as f:
        for line in f:
            splited_list = clear_strings(line.split(","))
            new_rec = GIPs(
                id=splited_list[0],
                emp_id=splited_list[1]
              )
            new_rec.save()
    print(load_gips.name, "done.")

@main.cli.command("load_employees")
def load_employees():
    with open(str(folder_path_that_contains_this_file)+"/files/employees.txt", "r", encoding="utf-8") as f:
        for line in f:
            splited_list = clear_strings(line.split(","))
            new_rec = Employees(
                id=splited_list[0],
                login=splited_list[1],
                password=splited_list[2]
              )
            new_rec.save()
    print(load_employees.name, "done.")


@main.cli.command("load_admins")
def load_admins():
    with open(str(folder_path_that_contains_this_file)+"/files/admins.txt", "r", encoding="utf-8") as f:
        for line in f:
            splited_list = clear_strings(line.split(","))
            new_rec = Admins(
                id=splited_list[0],
                employee_id=splited_list[1]
              )
            new_rec.save()
    print(load_admins.name, "done.")

@main.cli.command("load_project_costs")
def load_project_costs():
    with open(str(folder_path_that_contains_this_file)+"/files/project_costs.txt", "r", encoding="utf-8") as f:
        for line in f:
            splited_list = clear_strings(line.split(","))
            new_rec = ProjectCosts(
                id=splited_list[0],
                cost_id=splited_list[1],
                man_days=splited_list[2],
                project_id=splited_list[3]
              )
            new_rec.save()
    print(load_project_costs.name, "done.")

@main.cli.command("load_tasks")
def load_tasks():
    with open(str(folder_path_that_contains_this_file)+"/files/tasks.txt", "r", encoding="utf-8") as f:
        for line in f:
            splited_list = clear_strings(line.split(","))
            new_rec = Tasks(
                id=splited_list[0],
                task_name=splited_list[1]
              )
            new_rec.save()
    print(load_tasks.name, "done.")

@main.cli.command("load_costs_tasks")
def load_costs_tasks():
    with open(str(folder_path_that_contains_this_file)+"/files/costs_tasks.txt", "r",encoding="utf-8") as f:
        for line in f:
            splited_list = clear_strings(line.split(","))
            new_rec = CostsTasks(
                id=splited_list[0],
                task_name_fk=splited_list[1],
                man_days=splited_list[2],
                cost_id=splited_list[3]
              )
            new_rec.save()
    print(load_costs_tasks.name, "done.")

@main.cli.command("load_costs")
def load_costs():
    with open(str(folder_path_that_contains_this_file)+"/files/costs.txt", "r", encoding="utf-8") as f:
        for line in f:
            splited_list = clear_strings(line.split(","))
            new_rec = Costs(
                id=splited_list[0],
                cost_name=splited_list[1]
              )
            new_rec.save()
    print(load_costs.name, "done.")

@main.cli.command("load_records")
def load_records():
    with open(str(folder_path_that_contains_this_file)+"/files/records.txt", "r", encoding="utf-8") as f:
        for line in f:
            splited_list = clear_strings(line.split(","))
            need_info = list(map(int, splited_list[2:]))
            new_rec = Records(need_info[0],
                              need_info[1],
                              need_info[2],
                              need_info[3],
                              need_info[4],
                              need_info[5])
            new_rec.save()
    print(load_records.name, "done.")
### LOAD ENDS ######################################################################


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
        costs_name_list = Costs.get_costs_names()
        projects_name_id_list = Projects.get_projects_id_name_list()
        sorted_projects_name_list = sorting_projects_names(projects_name_id_list)
        form.project_name.choices = sorted_projects_name_list
        form.category_of_costs.choices = costs_name_list
        if form.is_submitted():
            project_id = int(form.project_name.data)
            employee_id = Employees.query.filter_by(login=login).first().id
            print("employee_id:",employee_id)
            # DONE:Правильно заносить записи с учётом новой таблицы ProjectsCosts 
            # [x]: 
# BUG:      Все данные в БД записаны так '\nУправление проектом\n', то есть присутствуют лишние символы
            print(form.category_of_costs.data.__repr__())
            print(Costs.query.filter_by(cost_name=form.category_of_costs.data).first().id)
            cost_id = Costs.query.filter_by(cost_name=form.category_of_costs.data).first().id
            print("cost_id:",cost_id)
            cost_id_ = ProjectCosts.query.filter_by(cost_name_fk=cost_id, project_id=project_id).first().id
            print("cost_id_:",cost_id_)
            task_id = Tasks.query.filter_by(task_name=form.task.data).first().id     
            print("task_id:", task_id)
            task_id_ = CostsTasks.query.filter_by(task_name_fk=task_id, cost_id=cost_id).first().id
            print("task_id:",task_id_)
            # print(project_id, cost_id, cost_id_, task_id, task_id_)
            hours = form.hours.data
            minuts = form.minuts.data
            rec = Records(employee_id, project_id, cost_id_, task_id_, hours, minuts)
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
        logger.warning(f"In project_report fail has been ocured: {e}")
        time.sleep(1)
        return redirect(url_for('main.project_report'))
    



@main.errorhandler(500)
def handle_error(err):
    headers = err.data.get('headers', None)
    messages = err.data.get('messages', ['Invalid Request.'])
    logger.warning(f'Error 500: {messages}')
    time.sleep(1)
    return redirect(url_for("main.index"))
