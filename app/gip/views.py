from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for, g
)



from app.models import (
    GIPs, Projects,
    ProjectCosts, Tasks,
    Costs, CostsTasks 
    )
from app import logger
from app.helper_functions import is_empty_default_or_none, sorting_projects_names

gip = Blueprint('gip', __name__, 
               url_prefix="/gip", 
               template_folder="templates/gip", 
               static_folder="static/gip")



# TODO: Выбор проекта для ГИПа (если он ГИП в нескольких проектах)
# [ ]:  Написать запрос, который достает проекты, которые числятся за этим ГИПом
# [ ]:  Составить список, который будет состоять из пар: (id, имя проекта)
# [ ]:  Отобразить этот список в select на форме

@gip.route('/', methods=['GET', 'POST'])
def gips_project():
    try:
        if not session.get("emp_is_gip", False):
            return redirect(url_for('main.index'))
        emp_id = session.get("emp_id")
        gip_id = GIPs.query.filter_by(employee_id=emp_id).first().id
        projects = Projects.get_projects_id_name_list_gip(gip_id)
        sorted_projects_name_list = sorting_projects_names(projects)
        if request.method == "POST":
            session["gip_project"] = Projects.get(request.form.get('gips_project_list')).project_name
            session["gip_project_id"] = request.form.get('gips_project_list')
        return render_template('gip/base_gip.html', 
                               project_list=sorted_projects_name_list,
                               )
    except Exception as e:
        logger.warning(f"In gips_project fail: {e}")
        return redirect(url_for('main.index'))


@gip.route('/cat_cost', methods=['GET', 'POST'])
def edit_cat_cost():
    error = False
    try:
        # Если пользователь не является ГИПом
        if not session.get("emp_is_gip", False):
            return redirect(url_for('main.index'))
        # Определяется ГИП и его проект
        gip_id = GIPs.query.filter_by(employee_id=session.get("emp_id")).first().id
        project = Projects.query.filter_by(gip_id=gip_id).first()
        selected_project_id = session.get("gip_project_id", project.id)
        # Получаем список добавленных статей расходов в виде (id, cost_name, man_days)
        added_costs_list_id_name = ProjectCosts.get_costs_info(selected_project_id)
        # Только список имен для последующей проверки
        list_of_cats_name = [c[1] for c in added_costs_list_id_name]
        
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
                costs_names = Costs.get_costs_names()
                if cost_name not in costs_names:
                    new_cost = Costs(cost_name=cost_name)
                    new_cost.save()
                new_cost_id = Costs.get_id_by_name(cost_name)
                new_cost_in_project = ProjectCosts(new_cost_id, man_days, selected_project_id)
                new_cost_in_project.save()
                new_cost_task = CostsTasks(1, 100, ProjectCosts.query.order_by(ProjectCosts.id.desc()).first().id)
                new_cost_task.save()
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
                               added_cost=added_costs_list_id_name,
                               project_name=project.project_name)
    except Exception as e:
        logger.exception(f"In edit_cat_cost fail: {e}")
        flash("Что-то пошло не по плану в редакторе статей расходов...", category="error")
        return redirect(url_for("gip.edit_cat_cost"))


def print_repr(list_):
    print("upd_cost_id", "upd_task_id", "upd_man_days", "add_cost_id", "new_task_name", "new_man_days", sep=" | ")
    for l in list_:
        print(l.__repr__(), end='|\t')

def print_type_and_repr(list_):
    for x,l in enumerate(list_):
        print(x, end=" ")
        for l_ in l:
            print(type(l_), l_.__repr__())
    print()





# DONE:
# [x]: Редактирование задач
# [x]: Добавление задач
@gip.route('/task', methods=['GET', 'POST'])
def edit_task():
    try:
        # Если пользователь не является ГИПом
        if not session.get("emp_is_gip", False):
            return redirect(url_for('main.index'))
        # Определяется ГИП и его проект
        gip_id = GIPs.query.filter_by(employee_id=session.get("emp_id")).first().id
        project = Projects.query.filter_by(gip_id=gip_id).first()
        # Получаем список добавленных статей расходов в виде (id, cost_name, man_days)
        costs_id_name_list = ProjectCosts.get_costs_info(project.id)
        # print_type_and_repr(costs_id_name_list)
        # Получаем список ранее добавленных задач в этом проекте в виде (id, task_name, man_days)
        tasks_id_name_list = CostsTasks.get_tasks_info(project.id)
        # print_type_and_repr(tasks_id_name_list)
# DONE:
# [x] Проверить данные с формы
        if request.method == 'POST':
            # Данные для редактирования
            for_upd_cots_id = request.form.get("old_cost_list")
            upd_task_id = request.form.get("old_task_list")
            upd_task_name = request.form.get("upd_task_name")
            upd_man_days = request.form.get("updated_man_days")
            # Данные для добавления
            for_add_cost_id = request.form.get("for_add_cost_list")
            new_task_name = request.form.get("new_task_name")
            new_man_days = request.form.get("new_man_days")

            # DONE:
            # [x]: Делаю обработку данных редактируемой задачи 
            # [x]: Делаю обработку данных добавляемой вновь задачи
            is_edit_empty = is_empty_default_or_none([for_upd_cots_id,
                                                   upd_task_id,
                                                   upd_task_name,
                                                   upd_man_days])
            is_add_empty = is_empty_default_or_none([
                                                 for_add_cost_id,
                                                 new_task_name,
                                                 new_man_days])
            
            # Обработка данных редактируемой задачи
            if not is_edit_empty:
                print("HEY in edit check!", is_edit_empty)
                edit_CostTask = CostsTasks.query.filter_by(
                                                        task_name_fk=upd_task_id,
                                                        cost_id=for_upd_cots_id
                                                          ).first()
                edit_task = Tasks.query.filter_by(
                                id=edit_CostTask.task_name_fk
                            ).first()
                edit_task.task_name = upd_task_name
                Tasks.commit()
                edit_CostTask.man_days = float(upd_man_days)
                CostsTasks.commit()
                flash("Задача отредактирована!", category="success")

            # Обработка данных новой задачи
            if not is_add_empty:
                print("HEY in add check!", is_add_empty)
                new_task = Tasks(
                    task_name = new_task_name
                )
                new_task.save()
                # TIPS: Можно не запрашивать только что добавленную запись (наверное)
                new_id = Tasks.get_task_by_name_use_careful(new_task_name).id
                new_CostTask = CostsTasks(
                    task_name_fk=new_id,
                    man_days=new_man_days,
                    cost_id=for_add_cost_id
                )
                new_CostTask.save()       
                flash("Задача добавлена!", category="success")
        
            is_all_empty = (is_edit_empty == True) and (is_add_empty == True)
            print("is_all_empty:",is_all_empty, "is_edit_empty:", is_edit_empty, "is_add_empty:",is_add_empty)
            if is_all_empty:
                flash("Никаких данных заполнено не было", category="error")

            return redirect(url_for("gip.edit_task"))

        return render_template('gip/edit_task.html', 
                                project_name=project.project_name,
                                added_cost=costs_id_name_list,
                                added_tasks=tasks_id_name_list
                                )
    except Exception as e:
        logger.warning(f"In edit_tasks fail: {e}")
        flash("В редакторе задач что-то пошло не по плану...", category="error")
        return redirect(url_for('main.index'))


    