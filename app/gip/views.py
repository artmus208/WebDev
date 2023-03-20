from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for, g
)
from app.models import GIPs, Projects, CustomCosts, Tasks
from app import logger
from app.support_functions import concatenate_costs
gip = Blueprint('gip', __name__, 
               url_prefix="/gip", 
               template_folder="templates/gip", 
               static_folder="static/gip")


@gip.route('/', methods=['GET', 'POST'])
def gips_project():
    try:
        if session.get("emp_role", "Нет роли") != 'gip':
            return redirect(url_for('main.index'))
        gip_id = GIPs.query.filter_by(employee_id=session.get("emp_id")).first().id
        project = Projects.query.filter_by(gip_id=gip_id).first()
        return render_template('gip/base_gip.html', project_name=project.project_name)
    except Exception as e:
        logger.warning(f"In gips_project fail: {e}")
        return redirect(url_for('main.index'))


@gip.route('/cat_cost', methods=['GET', 'POST'])
def edit_cat_cost():
    prev_cost = None
    try:
        if session.get("emp_role", "Нет роли") != 'gip':
            return redirect(url_for('main.index'))
        gip_id = GIPs.query.filter_by(employee_id=session.get("emp_id")).first().id
        project = Projects.query.filter_by(gip_id=gip_id).first()
        prev_cost = CustomCosts.query.filter_by(project_id=project.id).all()
        if request.method == 'POST':
            cost_name = request.form.get('cost_name')
            man_days = request.form.get('man_days')
            new_one = CustomCosts(cost_name, man_days, project.id)
            new_one.save()
            flash("Статья добавлена!", category="success")  
        return render_template('gip/edit_cat_cost.html', prev_cost=prev_cost,
                               project_name=project.project_name)
    except Exception as e:
        logger.warning(f"In edit_cat_cost fail: {e}")
        flash("Что-то пошло не по плану...", category="error")
        return redirect(url_for('main.index'))
    
@gip.route('/task', methods=['GET', 'POST'])
def edit_task():
    prev_tasks = None
    try:
        if session.get("emp_role", "Нет роли") != 'gip':
            return redirect(url_for('main.index'))
        gip_id = GIPs.query.filter_by(employee_id=session.get("emp_id")).first().id
        project = Projects.query.filter_by(gip_id=gip_id).first()
        costs_id_name_list = CustomCosts.get_costs_id_name_in_project(project.id)
        # concatenated_costs = concatenate_costs(project.id)
        if request.method == 'POST':
            task_name = request.form.get('task_name')
            man_days = float(request.form.get('man_days'))
            cost_id = request.form.get('cost_list')
            prev_tasks = Tasks.query.filter_by(cost_id=cost_id).all()
            new_one = Tasks(task_name, man_days, cost_id)
            new_one.save()
            flash("Задача добавлена!", category="success")
        return render_template('gip/edit_task.html', 
                                prev_tasks=prev_tasks,
                                cat_list=costs_id_name_list,
                                project_name=project.project_name)
    except Exception as e:
        logger.warning(f"In edit_tasks fail: {e}")
        flash("Что-то пошло не по плану...", category="error")
        return redirect(url_for('main.index'))


    