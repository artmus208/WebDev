from typing import List
import time
import pathlib

from flask import Blueprint

from app import logger, db, app
from app.models import (
    Employees, GIPs, Projects, 
    Costs, Tasks, ProjectCosts,
    CostsTasks, Records, Admins
)
from app.helper_functions import(
    revise_records_for_ProjectCosts, clear_strings, delete_spaces_in
)

from app import select, execute

from app.main.loaders import (
    load_emps, load_gips, load_projects,
    load_costs, load_tasks, load_project_costs,
    load_costs_tasks, load_records, load_admins
)

app.jinja_env.globals.update(sum=sum)
app.jinja_env.globals.update(round=round)
main = Blueprint('main', __name__, static_url_path="/static/main", static_folder="/static/main")
folder_path_that_contains_this_file = pathlib.Path(__file__).parent.resolve()

@main.before_request
def ping_connect():
    try:
        # logger.info("Ping DB")
        res = execute(
            select(Records)
        ).first()
    except:
        logger.exception("Ping DB")


@main.cli.command("create_db")
def create_db():
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
@main.cli.command("load_all_into_db")
def load_all_into_db():
    print("Start loading data into DB")
    try:
        load_emps()
        load_gips()
        load_projects()
        load_costs()
        load_tasks()
        load_project_costs()
        load_costs_tasks()
        load_records()
        load_admins()
        print("End loading data into DB")
    except:
        print("Fail, maybe DB is not clear. Check log")
        logger.exception("Fail, maybe DB is not clear")
### LOAD ENDS ######################################################################