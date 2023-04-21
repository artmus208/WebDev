from . import *


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


@main.context_processor
def utility_processor():
    return dict(
        get_login_by_id = Employees.get_login_by_id,
        get_all_employee_projects_id = Records.get_all_employee_projects_id,
        get_project_name_by_id = Projects.get_project_name_by_id,
        get_all_employee_cat_costs_id = Records.get_all_employee_cat_costs_id,
        get_cat_cost_name_by_id = ProjectCosts.get_cat_cost_name_by_id,
        get_records_by_emp_proj_cat = Records.get_records_by_emp_proj_cat
    )

@main.route("/emp-report/<int:emp_id>", methods=["POST", "GET"])
def emp_report(emp_id):
    emp = g.emp
    if emp is None:
        return redirect(url_for('auth.login'))
    try:
        return render_template('main/emp_report.html', employee_id=emp_id)
    except Exception as e:
        flash("Произошла ошибка генерации отчета сотрудника.", category='error')
        logger.warning(f"emp_report: {e}")
        time.sleep(1)
        return redirect(url_for('main.record'))





@main.errorhandler(500)
def handle_error(err):
    headers = err.data.get('headers', None)
    messages = err.data.get('messages', ['Invalid Request.'])
    logger.warning(f'Error 500: {messages}')
    time.sleep(1)
    return redirect(url_for("main.index"))
