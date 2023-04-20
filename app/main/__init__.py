from typing import List
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
    none_or_value, clear_strings, delete_spaces_in)

from app.reports_makers import (
    make_query_to_dict_list,
    make_report_that_andrews_like,
    get_project_report_dict,
    replace_id_to_name_in_record_dict)

from app import select, execute

main = Blueprint('main', __name__, static_url_path="/static/main", static_folder="/static/main")
folder_path_that_contains_this_file = pathlib.Path(__file__).parent.resolve()

@main.before_app_first_request
def ping_connect():
    try:
        logger.info("Ping DB")
        res = execute(
            select(Records)
        ).first()
    except:
        logger.warning("Ping DB")


@main.cli.command("create_db")
def init_emp():
    db.create_all()

@main.cli.command("drop_db")
def init_emp():
    db.drop_all()

@main.cli.command("revise_records")
def rev_rec():
    res = revise_records_for_ProjectCosts()

@main.cli.command("init_costs_tasks")
def init_cost_task():
    all_p_costs = ProjectCosts.query.all()
    all_costs_tasks = CostsTasks.query.all()
    ex_cost_id = [i.id for i in all_costs_tasks]
    print(ex_cost_id)
    for ix, p_costs in enumerate(all_p_costs):
        if p_costs.id not in ex_cost_id:
            new_task = CostsTasks(cost_id=p_costs.id, task_name_fk=1, man_days=1)
            new_task.save()

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
            new_rec = Projects( id=splited_list[0],
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
            new_rec = Records(  need_info[0],
                                need_info[1],
                                need_info[2],
                                need_info[3],
                                need_info[4],
                                need_info[5])
            new_rec.save()
    print(load_records.name, "done.")
### LOAD ENDS ######################################################################