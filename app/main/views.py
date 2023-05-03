from typing import List
import time

from flask import (
    render_template, redirect, 
    url_for, flash, session, g, request,
    jsonify)

from app import logger
from app.forms import (
    RecordsForm, ReturnButton, 
    ReportProjectForm, ProjectAddForm,
    ReportFormEmp
)

from app.models import (
    Records, Employees,
    Costs, Tasks, Projects,
    GIPs, ProjectCosts, CostsTasks,
)
from app.helper_functions import (
        sorting_projects_names
)

from app.reports_makers import (
    make_query_to_dict_list,
    make_report_that_andrews_like,
    get_project_report_dict,
    replace_id_to_name_in_record_dict)

from . import main

# TODO:
# [x]: Добавить реальных ГИПов в реальные проекты на проде
# [ ]: Заняться динамическими выпадающими списками 

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
        last_5_records = []
        res:List[Records] = Records.get_last_5_records(emp_id=g.emp.id)
        for r in res:
            record_with_names = r.replace_ids_to_names(
                EmployeesObj=Employees, ProjectsObj=Projects,
                ProjectCostObj=ProjectCosts, CostsObj=Costs
            )
            last_5_records.append(record_with_names)
        form = RecordsForm()
        costs_name_list = Costs.get_costs_names()
        projects_name_id_list = Projects.get_projects_id_name_list()
        sorted_projects_name_list = sorting_projects_names(projects_name_id_list)
        form.project_name.choices = sorted_projects_name_list
        form.category_of_costs.choices = costs_name_list
        if form.is_submitted():
            project_id = int(form.project_name.data)
            employee_id = Employees.query.filter_by(login=login).first().id
            # print("employee_id:",employee_id)
            # DONE:Правильно заносить записи с учётом новой таблицы ProjectsCosts 
            # [x]: 
            # print(form.category_of_costs.data.__repr__())
            # print(Costs.query.filter_by(cost_name=form.category_of_costs.data).first().id)
            cost_id = Costs.query.filter_by(cost_name=form.category_of_costs.data).first().id
            # print("cost_id:",cost_id)
            cost_id_ = ProjectCosts.query.filter_by(cost_name_fk=cost_id, project_id=project_id).first().id
            # print("cost_id_:",cost_id_)
            task_id = Tasks.query.filter_by(task_name=form.task.data).first().id     
            # print("task_id:", task_id)
            task_id_ = CostsTasks.query.filter_by(task_name_fk=task_id, cost_id=cost_id_).first().id
            # print("task_id_:",task_id_)
            # print(project_id, cost_id, cost_id_, task_id, task_id_)
            hours = form.hours.data
            minuts = form.minuts.data
            # print("Hours:", hours, "Minuts:", minuts)
            rec = Records(employee_id, project_id, cost_id_, task_id_, hours, minuts)
            rec.save()
            flash('Запись добавлена. Несите следующую!', category="success")
            return redirect(url_for('main.record', login=login))
        else:
            return render_template('main/records.html', form=form,
                                    login=login, last_5_records=last_5_records)
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
    

@main.route('/add-project', methods = ['GET', 'POST'])
def add_project():
    emp = g.emp
    if emp is None:
        return redirect(url_for('auth.login'))
    try:
        form = ProjectAddForm()
        form.gip.choices = Employees.get_id_logins()
        form.cat_costs.choices = Costs.get_costs_id_names()
        if request.method == "POST":
            if form.validate_on_submit():
                logger.info(
                    ','.join((form.code.data,
                    form.name.data,
                    '|'.join(list(map(str, form.cat_costs.data))),
                    form.gip.data)
                    ))
                if int(form.gip.data) not in GIPs.get_emp_id_in_gips():
                    new_gip = GIPs(int(form.gip.data))
                    new_gip.save()
                    gip_id = new_gip.id
                else:
                    gip_id = GIPs.get_by_employee_id(int(form.gip.data)).id
                new_project = Projects(
                    p_name=form.name.data,
                    code=form.code.data,
                    gip_id=gip_id
                    )
                new_project.save()
                for cost_id_fk in form.cat_costs.data:
                    new_project_costs = ProjectCosts(
                                        cost_id=cost_id_fk,
                                        man_days=100,
                                        project_id=new_project.id)
                    new_project_costs.save()
                    new_costs_tasks = CostsTasks(
                        task_name_fk=1,
                        man_days=100,
                        cost_id=new_project_costs.id)
                    new_costs_tasks.save()
                flash("Проект добавлен", category='success')
            else: 
                flash("Возникли ошибки при заполнении формы", category='error')
            return redirect(url_for("main.add_project"))
        return render_template("main/add_project.html", form=form)
    except Exception as e:
        flash("Произошла ошибка. Проект не добавлен", category='error')
        logger.warning(f"add_project: {e}")
        time.sleep(1)
        return redirect(url_for('main.add_project'))



@main.route("/emp-report", methods=["POST", "GET"])
def emp_report():
    emp = g.emp
    if emp is None:
        return redirect(url_for('auth.login'))
    form = ReportFormEmp()
    # Перезапись ключевых слов при отображении полей
    # form.lower_date.render_kw = {"min": "2023-04-03"}
    # form.lower_date.render_kw = {"max": "2023-05-03"}
    # form.upper_date.render_kw = {"min": "2023-04-03"}
    # form.upper_date.render_kw = {"max": "2023-05-03"}

    form.employee.choices = Employees.get_id_logins()
    try:
        if request.method == "GET":
            return render_template('main/emp_report.html', form=form)
        if form.validate_on_submit():
            flash("Отчет ниже:", category='success')    
            logger.info(f"Date from: {form.lower_date.data}, {type(form.lower_date.data)}")
            logger.info(f"Date to: {form.upper_date.data}, {type(form.upper_date.data)}")
            return render_template('main/emp_report.html', form=form)
        else:
            flash("Произошла ошибка заполнения формы", category='error')
            return render_template('main/emp_report.html', form=form)
    except Exception as e:
        flash("Произошла ошибка генерации отчета сотрудника.", category='error')
        logger.warning(f"emp_report: {e}")
        time.sleep(1)
        return redirect(url_for('main.record'))

@main.route("/test_j2", methods=["POST", "GET"])
def test_j2():
    data = {
        "name": "Artur"
    }
    return render_template("main/test_j2.html", data = data )

@main.errorhandler(500)
def handle_error(err):
    headers = err.data.get('headers', None)
    messages = err.data.get('messages', ['Invalid Request.'])
    logger.warning(f'Error 500: {messages}')
    time.sleep(1)
    return redirect(url_for("main.index"))
