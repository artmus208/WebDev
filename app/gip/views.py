from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for, g
)
from app.models import GIPs, Projects, ProjectCosts, Tasks, Costs
from app import logger
from app.helper_functions import concatenate_costs
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
    error = False
    try:
        # Если пользователь не является ГИПом
        if session.get("emp_role", "Нет роли") != 'gip':
            return redirect(url_for('main.index'))
        # Определяется ГИП и его проект
        gip_id = GIPs.query.filter_by(employee_id=session.get("emp_id")).first().id
        project = Projects.query.filter_by(gip_id=gip_id).first()
        # Получаем список добавленных статей расходов в виде (id, cost_name_fk)
        added_costs_list_id_namefk = ProjectCosts.get_costs_info(project.id)
        if added_costs_list_id_namefk:
            # Заменяем foreign key cost name на name
            for old_cat in added_costs_list_id_namefk:
                old_cat[1] = Costs.get_name_by_id(old_cat[1])
        else:
            added_costs_list_id_namefk = [[0,"Нет данных"]]
        # Только список имен для последующей проверки
        list_of_cats_name = [c[1] for c in added_costs_list_id_namefk]

        if request.method == 'POST':
            cost_name = request.form.get('cost_name')
            man_days = request.form.get('man_days')
            
            old_cost_name_id = request.form.get('old_cost_list')
            new_man_days = request.form.get("updated_man_days")

            print(cost_name, man_days, old_cost_name_id, new_man_days)
            print(type(cost_name), type(man_days), type(old_cost_name_id), type(new_man_days))
            
            if cost_name in list_of_cats_name:
                error = True
                flash("Такая статья расходов уже добавлена", category="error")
                return redirect(url_for("gip.edit_cat_cost"))
            # Для новой статьи расходов:
            if cost_name:
                new_cost = Costs(cost_name)
                new_cost.save()
                new_cost_id = Costs.get_id_by_name(cost_name)
                new_cost_in_project = ProjectCosts(new_cost_id, man_days, project.id)
                new_cost_in_project.save()
            # Если пытаются отредактировать старую статью
            print("Элемент из списка:", old_cost_name_id)
            if old_cost_name_id != "default":
                old_project_cost = ProjectCosts.query.filter_by(id=int(old_cost_name_id)).first()
                if new_man_days:
                    old_project_cost.man_days = int(new_man_days)
                    Costs.commit()
                    flash("Статья расходов была изменена!", category="success")
                else:
                    error = True
                    flash("Похоже, что вы пытались редактировать добавленную статью расходов, \
                        но не указали новое время", category="error")
                    
            if not error:
                flash("Статья добавлена!", category="success")  
            return redirect(url_for("gip.edit_cat_cost"))
        return render_template('gip/edit_cat_cost.html',
                               added_cost=added_costs_list_id_namefk,
                               project_name=project.project_name)
    except Exception as e:
        logger.warning(f"In edit_cat_cost fail: {e}")
        flash("Что-то пошло не по плану...", category="error")
        return redirect(url_for('main.index'))
    
@gip.route('/task', methods=['GET', 'POST'])
def edit_task():
    prev_tasks = None
    try:
        # Если пользователь не является ГИПом
        if session.get("emp_role", "Нет роли") != 'gip':
            return redirect(url_for('main.index'))
        
        gip_id = GIPs.query.filter_by(employee_id=session.get("emp_id")).first().id
        project = Projects.query.filter_by(gip_id=gip_id).first()
        costs_id_name_list = ProjectCosts.get_costs_id_name_in_project(project.id)
        
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


    