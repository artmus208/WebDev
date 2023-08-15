from typing import List
from datetime import time as time_dt
from datetime import datetime
import time
from flask import (
    render_template, redirect, 
    url_for, flash, session, g, request,
    jsonify)
from sqlalchemy import func

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
    replace_id_to_name_in_record_dict,
    report_about_employee,
    project_report2)

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


@main.route("/_update_dropdown")
def update_cat_costs_list():
    """
    Функция генерирует новый SelectedField для категорий затрат в зависимости от 
    выбранного id проекта.
    """
    try:
        selected_project_id = request.args.get("selected_project_id", type=int)
        updated_costs = ProjectCosts.get_costs_id_name(project_id=selected_project_id)
        html_string_selected = ''
        for cost in updated_costs:
            html_string_selected += f'<option value="{cost[0]}">{cost[1]}</option>'
        return jsonify(html_string_selected=html_string_selected)
    except Exception as e:
        logger.warning(f"update_cat_costs_list: {e}")
        return jsonify(html_string_selected="<option value='-1'>Произошла ошибка!</option>")


@main.route("/record", methods=['GET', 'POST'])
def record():
    try:
        login = g.emp.login
    except:
        return redirect(url_for("auth.login"))
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
        costs_name_list = Costs.get_costs_id_names()
        form.project_name.choices = sorting_projects_names(Projects.get_projects_id_name_list())
        form.category_of_costs.choices = costs_name_list
        if request.method == "GET":
            return render_template('main/records.html', form=form,
                                    login=login, last_5_records=last_5_records)
        if form.validate_on_submit():
            project_id = int(form.project_name.data)
            employee_id = Employees.query.filter_by(login=login).first().id
            cost_id = int(form.category_of_costs.data)
            # cost_id_ = ProjectCosts.query.filter_by(cost_name_fk=cost_id, project_id=project_id).first().id
            task_id = Tasks.query.filter_by(task_name=form.task.data).first().id     
            task_id_ = CostsTasks.query.filter_by(task_name_fk=task_id, cost_id=cost_id).first().id
            hours = form.hours.data
            minuts = form.minuts.data
            rec = Records(
                employee_id=employee_id,
                project_id=project_id,
                cost_id=cost_id,
                task_id=task_id_,
                hours=hours,
                minuts=minuts)
            rec.save()
            flash('Запись добавлена. Несите следующую!', category="success")
            return redirect(url_for('main.record', login=login))
        else:
            flash('Кажется, кто-то ошибся при заполнении формы...', category="error")
            logger.info(f"cost_id:{form.category_of_costs.data}, type: {type(form.category_of_costs.data)}")
            return render_template('main/records.html', form=form,
                                    login=login, last_5_records=last_5_records)
    except Exception as e:
        logger.exception(f"In record page fail has been ocured: {e}")
        flash('Что-то пошло не так...', category="error")
        time.sleep(1)
        return redirect(url_for('main.record', login=login))


@main.route('/rep', methods=['GET', 'POST'])
def project_report():
    try:
        form = ReportProjectForm()
        returnBtn = ReturnButton()
        # TIPS: Убрать лишнее ниже (sorting_projects_names(projects_name_id_list))
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
    

@main.route('/detailed-project-report', methods=['GET', 'POST'])
def detailed_project_report():
    if g.emp is None:
        return redirect(url_for('auth.login'))
    form = ReportProjectForm()
    form.project_name.choices = Projects.get_projects_id_name_list()
    try:
        if form.validate_on_submit():
            proj_id = int(form.project_name.data)
            detail_project_report = project_report2(p_id=proj_id)
            return render_template('main/detailed_project_report.html',
                                    form=form, project_report=detail_project_report)    
        else:
            return render_template('main/detailed_project_report.html', form=form)    
    except Exception as e:
        flash("Произошла ошибка при генерации подробного отчета (возможно нет записей)", category="error")
        logger.warning(f"detailed_project_report: {e}")
        time.sleep(1)
        return redirect(url_for('main.detailed_project_report'))

@main.route('/add-project', methods = ['GET', 'POST'])
def add_project():
    emp = g.emp
    if emp is None:
        return redirect(url_for('auth.login'))
    try:
        form = ProjectAddForm()
        form.gip.choices = Employees.get_id_logins()
        form.cat_costs.choices = Costs.get_costs_id_names()[1:]        
        if form.validate_on_submit():
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
                                    man_days=0,
                                    project_id=new_project.id)
                new_project_costs.save()
                new_costs_tasks = CostsTasks(
                    task_name_fk=1,
                    man_days=0,
                    cost_id=new_project_costs.id)
                new_costs_tasks.save()
            flash("Проект добавлен", category='success')
            return redirect(url_for('main.add_project'))
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
            date_low = None
            date_upp = None
            if not form.is_all_period.data:
                t_low = time_dt(hour=0, minute=0) 
                t_upp = time_dt(hour=23, minute=59)
                date_low = datetime.combine(form.lower_date.data, t_low)
                date_upp = datetime.combine(form.upper_date.data, t_upp)
                data = report_about_employee(
                    employee_id=form.employee.data,
                    lower_date=date_low,
                    upper_date=date_upp
                )
            else:
                data = report_about_employee(employee_id=form.employee.data)
            emp_login = Employees.get_login_by_id(int(form.employee.data))
            return render_template('main/emp_report.html', 
                                    form=form, emp_data=data,
                                    date_low=date_low, date_upp=date_upp, emp_login=emp_login)
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
