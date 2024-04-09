from pathlib import Path
from typing import List
from datetime import time as time_dt
from datetime import datetime
import time
from flask import (
    Response, abort, render_template, redirect, 
    url_for, flash, session, g, request,
    jsonify, current_app)
from sqlalchemy import func

import schedule
import requests
import threading
import json

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
    project_report2,
    get_projects_with_unfilled_costs
)

from . import main

# TODO:
# [x]: Добавить реальных ГИПов в реальные проекты на проде
# [ ]: Заняться динамическими выпадающими списками  

@main.route("/", methods=['GET', 'POST'])
def index():
    emp = g.emp
    if emp is None:
        return redirect(url_for('auth.login'))
    else:
        return redirect(url_for('.record', login=emp.login))
    

@main.route("/inspect")   
def inspect():
    report = get_projects_with_unfilled_costs()
    return render_template("report/inspect.html", report=report)

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
        logger.exception(f"detailed_project_report")
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

######################### TG BOT NOTIFIER ###################################################

url = 'https://api.telegram.org/bot6985903476:AAHb_dmARjQXg7lBBqGCJnpBgR07VWEoJmQ/sendMessage'


def background_process():
    while True:
        schedule.run_pending()

        sleep_time = schedule.idle_seconds()

        if sleep_time is not None and sleep_time > 0:
            sleep_time_formatted = time.strftime('%H:%M:%S', time.gmtime(sleep_time))
            print(f"будет спать еще {sleep_time_formatted}")
            logger.info(f"будет спать еще {sleep_time_formatted}")

            # Ожидание до следующей задачи
            time.sleep(sleep_time)
        else:
            logger.info("Задач нет, спать 1 секунду")
            time.sleep(1)


def notification1645():
    day_without_notice = datetime.now().weekday()
    if day_without_notice != 5 and day_without_notice != 6:
        with open('users.json', 'r') as file:
            data = json.load(file)

            for tg_id in data:
                message_text = (f'🔔❗️{tg_id["first_name"]}не забудьте внести трудозатраты за сегодняшний день. Сделайте это прямо сейчас в приложении\n'
                                f'<a href="https://tcs.pesk.spb.ru/auth/login">TaskPesk</a>🔔❗️')
                params = {'chat_id': tg_id['tg_id'], 'text': message_text, 'parse_mode': 'HTML'}  #
                response = requests.post(url, data=params)


schedule.every().day.at("16:45").do(notification1645)


bg_process = threading.Thread(target=background_process)
bg_process.daemon = True
bg_process.start()

lock = threading.Lock()

def add_user(data):
    with lock:
        # file_path = Path(url_for('static', filename='users.json'))
        file_path = Path("./app/static/users.json")

        if file_path.is_file():
            with open(file_path, 'r', encoding='utf-8') as file:
                users = json.load(file)
        else:
            users = []

        existing_user = next((user for user in users if user['tg_id'] == data['tg_id']), None)
        if existing_user:
            existing_user.update(data)
        else:
            users.append(data)

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(users, file, ensure_ascii=False, indent=4)

@main.route('/notification', methods=['POST'])
def notification():
    if request.headers.get('content-type') == 'application/json':
        data = request.json

        data = request.json
        message = data['message']

        if 'text' in message:
            content = f"Текст: {message['text']}" + f" id: {message['from']['id']} Name: {message['from']['first_name']}"
            message_text = data['message']['text']
            if message_text.endswith("@pesk.spb.ru"):
                user_id = data['message']['from']['id']
                user_name = data['message']['from']['first_name']
                user_json = {
                    'first_name': user_name,
                    'post_name': 'admin',
                    'email': message_text,
                    'tg_id': user_id
                }

                add_user(user_json)

                mess = f"Спасибо 😊"
                params1 = {'chat_id': data['message']['from']['id'], 'text': mess, 'parse_mode': 'HTML'}
                requests.post(url, data=params1)
            else:
                mess = f"Мне нужна только ваша корпоративная почта.\n\n<i>Я бот для уведомлений, старайся не засорять этот чат.</i>😊"
                params1 = {'chat_id': data['message']['from']['id'], 'text': mess, 'parse_mode': 'HTML'}
                requests.post(url, data=params1)


        elif 'sticker' in message:
            mess = f"Мне нужна только ваша корпоративная почта.\n\n<i>Я бот для уведомлений, старайся не засорять этот чат.</i>😊"
            params1 = {'chat_id': data['message']['from']['id'], 'text': mess, 'parse_mode': 'HTML'}
            requests.post(url, data=params1)


            content = f"Стикер: {message['sticker'].get('emoji', 'Нет эмодзи')}" + f" id: {message['from']['id']} Name: {message['from']['first_name']}"
        elif 'photo' in message:
            mess = f"Мне нужна только ваша корпоративная почта.\n\n<i>Я бот для уведомлений, старайся не засорять этот чат.</i>😊"
            params1 = {'chat_id': data['message']['from']['id'], 'text': mess, 'parse_mode': 'HTML'}
            requests.post(url, data=params1)


            content = "Фото получено" + f" id: {message['from']['id']} Name: {message['from']['first_name']}"
        elif 'video' in message:
            mess = f"Мне нужна только ваша корпоративная почта.\n\n<i>Я бот для уведомлений, старайся не засорять этот чат.</i>😊"
            params1 = {'chat_id': data['message']['from']['id'], 'text': mess, 'parse_mode': 'HTML'}
            requests.post(url, data=params1)

            content = "Видео получено" + f" id: {message['from']['id']} Name: {message['from']['first_name']}"
        elif 'audio' in message:
            mess = f"Мне нужна только ваша корпоративная почта.\n\n<i>Я бот для уведомлений, старайся не засорять этот чат.</i>😊"
            params1 = {'chat_id': data['message']['from']['id'], 'text': mess, 'parse_mode': 'HTML'}
            requests.post(url, data=params1)

            content = "Аудио получено" + f" id: {message['from']['id']} Name: {message['from']['first_name']}"
        elif 'voice' in message:
            mess = f"Мне нужна только ваша корпоративная почта.\n\n<i>Я бот для уведомлений, старайся не засорять этот чат.</i>😊"
            params1 = {'chat_id': data['message']['from']['id'], 'text': mess, 'parse_mode': 'HTML'}
            requests.post(url, data=params1)

            content = "Голосовое сообщение получено" + f" id: {message['from']['id']} Name: {message['from']['first_name']}"
        elif 'document' in message:
            mess = f"Мне нужна только ваша корпоративная почта.\n\n<i>Я бот для уведомлений, старайся не засорять этот чат.</i>😊"
            params1 = {'chat_id': data['message']['from']['id'], 'text': mess, 'parse_mode': 'HTML'}
            requests.post(url, data=params1)

            content = "Документ получен" + f" id: {message['from']['id']} Name: {message['from']['first_name']}"
        elif 'location' in message:
            mess = f"Мне нужна только ваша корпоративная почта.\n\n<i>Я бот для уведомлений, старайся не засорять этот чат.</i>😊"
            params1 = {'chat_id': data['message']['from']['id'], 'text': mess, 'parse_mode': 'HTML'}
            requests.post(url, data=params1)

            content = "Локация получена" + f" id: {message['from']['id']} Name: {message['from']['first_name']}"
        elif 'contact' in message:
            mess = f"Мне нужна только ваша корпоративная почта.\n\n<i>Я бот для уведомлений, старайся не засорять этот чат.</i>😊"
            params1 = {'chat_id': data['message']['from']['id'], 'text': mess, 'parse_mode': 'HTML'}
            requests.post(url, data=params1)

            content = "Контакт получен" + f" id: {message['from']['id']} Name: {message['from']['first_name']}"
        else:
            mess = f"Мне нужна только ваша корпоративная почта.\n\n<i>Я бот для уведомлений, старайся не засорять этот чат.</i>😊"
            params1 = {'chat_id': data['message']['from']['id'], 'text': mess, 'parse_mode': 'HTML'}
            requests.post(url, data=params1)

            content = "Неподдерживаемый тип сообщения" + f" id: {message['from']['id']} Name: {message['from']['first_name']}"

        return Response('ok', status=200)

    else:
        abort(403)
