
import datetime
import json
from typing import Dict, List
from sqlalchemy import func
from transliterate import translit

from app import db, app
from app.models import (
    Employees, Projects, Records,
    Costs, Tasks, ProjectCosts, CostsTasks
)
from app import logger
from utils import timeit
# 

def replace_id_to_name_in_record_dict(list_of_ditc) -> dict:
    try:
        for item in list_of_ditc:
            item["employee_id"] = db.session.get(Employees, item["employee_id"]).login
            item["project_id"] = db.session.get(Projects, item["project_id"]).project_name
            # logger.info(f"item['cost_id']:{item['cost_id']}")
            project_cost_id = db.session.get(ProjectCosts, item["cost_id"]).id
            # logger.info(f"project_cost_id:{project_cost_id}")
            
            CostTasks_id = CostsTasks.query.filter_by(cost_id=project_cost_id).first().task_name_fk
            project_cost_name_id = db.session.get(ProjectCosts, item["cost_id"]).cost_name_fk
            # logger.info(f" CostTasks_id:{CostTasks_id}")
            item["cost_id"] = db.session.get(Costs, project_cost_name_id).cost_name
            
            
            # logger.info(f" CostTasks_id:{CostTasks_id}")
            item["task_id"] = db.session.get(Tasks, CostTasks_id).task_name
            cost_postfix = translit(item["cost_id"][:4], language_code='ru', reversed=True)
            if item["task_id"] == "blank_task":
                item["task_id"] = item["employee_id"] + "_" + item["task_id"] + "_" + cost_postfix
        return list_of_ditc
    except Exception as e:
        logger.warning(f"replace_id_to_name_in_record_dict fail has been ocured: {e}")

def make_query_to_dict_list(query_obj) -> List[Dict]:
    try:
        res = list()
        for q_o in query_obj:
            res.append(q_o.as_dict_name())
        return res
    except Exception as e:
        logger.warning(f"make_query_to_dict_list fail has been ocured: {e}")


def filter_dict_by(list_of_dicts, dict_item):
    """Only those that have a dict_item pair remain in the list of dictionaries."""
    filtered_list = list_of_dicts.copy()
    for i in range(len(list_of_dicts)):
        d_One = list_of_dicts[i]
        if not dict_item in d_One.items():
            filtered_list.remove(d_One)
    return filtered_list


list_of_dicts=[
    {'id': 1, 'time_created': datetime.datetime(2023, 3, 3, 11, 33, 11), 'employee': 'mar', 'project_name': 'Проект 1', 'category_of_costs': 'Управление проектом', 'task': '123', 'hours': 1, 'minuts': 34},
    {'id': 2, 'time_created': datetime.datetime(2023, 3, 3, 11, 34, 31), 'employee': 'mar', 'project_name': 'Проект 1', 'category_of_costs': 'Управление проектом', 'task': '321', 'hours': 121, 'minuts': 123},
    {'id': 3, 'time_created': datetime.datetime(2023, 3, 3, 11, 37, 37), 'employee': 'mpa', 'project_name': 'Проект 1', 'category_of_costs': 'Управление проектом', 'task': '123', 'hours': 123, 'minuts': 123},
    {'id': 4, 'time_created': datetime.datetime(2023, 3, 3, 11, 45, 9), 'employee': 'gmi', 'project_name': 'Проект 1', 'category_of_costs': 'Проектирование', 'task': '123', 'hours': 123, 'minuts': 123}
    ]

def get_uniq_key_values(list_of_dict:List[Dict], key:str) -> List[str]:
    """Returns uniq key values from list of dict"""
    res = set()
    for dict_ in list_of_dict:
        res.add(dict_.get(key, None))
    return list(res)


example = \
{
    "p_name":"Proj1",
    "list_of_cat_cos":[
        {"category_of_costs": "Prog", "list_of_tasks":[
            {"task":"task1", "list_of_emp":[
                {"emp":"Artur", "summ_time_h": 123, "summ_time_m": 30}
            ]},
            {"task":"task2", "list_of_emp":[
                {"emp":"Maria", "summ_time_h": 3, "summ_time_m": 34}
            ]}
        ]},
        {"category_of_costs": "Naladka", "list_of_tasks":[
            {"task":"task1"},
            {"task":"task2"}
        ]},
    ]
}

def project_report2(p_id):
    """
       Функция генерирует отчет по проекту в виде словаря:

       project_report = {
            "p_id": p_id,
            "p_name": Projects.get_project_name_by_id(p_id),
            "cat_cost_list": {},
            "total_perf_time": 0,
        }
        Значение ключа "cat_cost_list" тоже словарь с ключами-именами категорий
        затрат, значения которых тоже словари вида:
            cat_cost_report = {
                "cat_cost_id": cat_cost_id,
                "emp_list": {},
                "total_perf_time": 0,
            }         
            Значение ключа "emp_list" тоже словарь с ключами-логинами сотрудников,
            значения этихх ключей словари вида:
                    cat_cost_report["emp_list"][emp_login] = {
                        "emp_id": emp_id,
                        "total_perf_time": list()
                    }
            
    """
    project_report = {
        "p_id": p_id,
        "p_name": Projects.get_project_name_by_id(p_id),
        "cat_cost_list": {},
        "total_perf_time": 0,
        "plan_time": 0,
        "abs_diff": 0,
        "rel_diff": 0
    }

    for cat_cost_id in Records.get_cat_costs_ids_by_project_id(p_id):
        cat_cost_name = ProjectCosts.get_cat_cost_name_by_id(cat_cost_id)
        if not (cat_cost_name in project_report["cat_cost_list"]): 
            cat_cost_plan = ProjectCosts.get(cat_cost_id).man_days * 8 * 60 
            project_report["cat_cost_list"][cat_cost_name] = {
                "cat_cost_id": cat_cost_id,
                "cat_cost_plan": cat_cost_plan,
                "emp_list": {},
                "total_perf_time": 0,
                "abs_diff": 0,
                "rel_diff": 0 
            }
            project_report["plan_time"] += cat_cost_plan
        for emp_id in Records.get_emp_ids_by_project_id_cat_cost_id(
                        project_id=p_id, cat_cost_id=cat_cost_id):
            emp_login = Employees.get_login_by_id(emp_id)
            if (emp_login not in project_report["cat_cost_list"][cat_cost_name]["emp_list"]):
                project_report["cat_cost_list"][cat_cost_name]["emp_list"][emp_login] = {
                    "emp_id": emp_id,
                    "total_perf_time": list()
                }
            project_report["cat_cost_list"][cat_cost_name]["emp_list"][emp_login]["total_perf_time"].append(
                Records.get_info_by_proj_id_cat_id_emp_id(
                    project_id=p_id,
                    project_cost_id=cat_cost_id,
                    employee_id=emp_id,
                )
            )
        total_cat_cost_time = []
        for emp_login_ in project_report["cat_cost_list"][cat_cost_name]["emp_list"]:
            total_cat_cost_time.append(sum(project_report["cat_cost_list"][cat_cost_name]["emp_list"][emp_login_]["total_perf_time"]))

        cat_cost_fact = sum(total_cat_cost_time)
        project_report["cat_cost_list"][cat_cost_name]["total_perf_time"] = cat_cost_fact
        project_report["cat_cost_list"][cat_cost_name]["abs_diff"] = cat_cost_plan - cat_cost_fact
        if cat_cost_plan:
            project_report["cat_cost_list"][cat_cost_name]["rel_diff"] = round(
                100*(cat_cost_plan - cat_cost_fact)/cat_cost_plan, 2
            )
        else:
            project_report["cat_cost_list"][cat_cost_name]["rel_diff"] = 0

    for cat_cost_name in project_report["cat_cost_list"]:
        project_report["total_perf_time"] += project_report["cat_cost_list"][cat_cost_name]["total_perf_time"]
     
    project_report["abs_diff"] = project_report["plan_time"] - project_report["total_perf_time"]
    
    if project_report["plan_time"]:
        project_report["rel_diff"] = round((project_report["abs_diff"] / project_report["plan_time"])*100, 2)
    else:
        project_report["rel_diff"] = 0
        
    return project_report


def show_project_report2(p_id=3):
    print("\n\nВерсия отчета II:")
    with app.app_context():
        project_report = project_report2(p_id)
        print(
            "Отчет по проекту:\n",
            f'({project_report["p_id"]})',
            project_report["p_name"],
            f'{project_report["total_perf_time"] // 60}ч',
            f'{project_report["total_perf_time"] % 60}мин',
        )
        for cat_cost_name in project_report["cat_cost_list"]:
            cat_cost_report = project_report["cat_cost_list"][cat_cost_name]
            print(
                "\t Отчет по категории затрат:",
                f'({cat_cost_report["cat_cost_id"]})',
                cat_cost_name,
                f'{cat_cost_report["total_perf_time"] // 60}ч',
                f'{cat_cost_report["total_perf_time"] % 60}мин',
            )
            for emp_login in cat_cost_report["emp_list"]:
                emp_report = cat_cost_report["emp_list"][emp_login]
                print(
                    "\t\t Отчет по сотруднику:",
                    f'({emp_report["emp_id"]})',
                    emp_login,
                    f'{sum(emp_report["total_perf_time"]) // 60}ч',
                    f'{sum(emp_report["total_perf_time"]) % 60}мин',
                )

# TIPS:
# TODO: 
# [ ] Можно сделать рефактор этой функции с использованием словаря
def get_project_report_dict(all_records: List[Dict], p_name:str) -> Dict:
    """Из all_records получается словарь заданной структуры. См example в этом модуле
        Структура словаря:
            Имя проекта: p_name 
                Статьи расходов
                    Задачи
                        Работники  
                            Часы и минуты работника
    """
    try:   
            emp_summ_time_h = 0
            emp_summ_time_min = 0
            list_of_category_of_costs = get_uniq_key_values(all_records, "cost_id")
            buff_dict_item_0 = {"list_of_cat_cos": [0 for i in range(len(list_of_category_of_costs))]}
            if not buff_dict_item_0['list_of_cat_cos']:
                buff_dict_item_0['list_of_cat_cos'] = "No data available"
            for i_c, category_of_costs in enumerate(list_of_category_of_costs):
                buff_dict_1 = filter_dict_by(all_records, ("cost_id", category_of_costs))
                list_uniq_tasks = get_uniq_key_values(buff_dict_1, "task_id")
                # 
                buff_dict_item_1 = {"cat_of_cost": ProjectCosts.get_cat_cost_name_by_id(category_of_costs), "list_of_tasks": [0 for i in range(len(list_uniq_tasks))]}
                # reportDict[category_of_costs] = list()
                for i_t, task in enumerate(list_uniq_tasks): 
                    buff_dict_2 = filter_dict_by(all_records, ("task_id", task))
                    list_uniq_emp = get_uniq_key_values(buff_dict_2, "employee_id")
                    buff_dict_item_2 = {"task_name": task, "list_of_emp": [0 for i in range(len(list_uniq_emp))]}
                    for i_e, employee in enumerate(list_uniq_emp):                
                        buff_dict_3 = filter_dict_by(all_records, ("employee_id", employee))
                        for d_item in buff_dict_3:
                            emp_summ_time_h = emp_summ_time_h + d_item['hours']
                            emp_summ_time_min = emp_summ_time_min + d_item['minuts']
                        emp_summ_time_gen_h = (60*emp_summ_time_h + emp_summ_time_min) // 60
                        emp_summ_time_gen_m = (60*emp_summ_time_h + emp_summ_time_min) % 60
                        emp_summ_time_h = 0
                        emp_summ_time_min = 0
                        buff_dict_item_3 = {"emp_name":Employees.get_login_by_id(employee), "summ_time_h":emp_summ_time_gen_h, "summ_time_m":emp_summ_time_gen_m}
                        buff_dict_item_2['list_of_emp'][i_e] = buff_dict_item_3
                    buff_dict_item_1['list_of_tasks'][i_t] = buff_dict_item_2 
                buff_dict_item_0['list_of_cat_cos'][i_c] = buff_dict_item_1
            buff_dict_item_0["project_name"] = p_name
            return buff_dict_item_0
    except Exception as e:
            logger.warning(f"get_project_report_dict fail has been ocured: {e}")

            

def make_report_that_andrews_like(old_report: List[Dict]):
    if old_report['list_of_cat_cos'] != "No data available":
        new_report = {}
        new_report["project_name"] = old_report["project_name"]
        new_report["list_of_cat_cos"] = [{} for i in range(len(old_report["list_of_cat_cos"]))]
        s = 0
        g_s = 0
        for cat_new, cat_old in zip(new_report["list_of_cat_cos"], old_report["list_of_cat_cos"]):
            for t in cat_old["list_of_tasks"]:
                for e in t["list_of_emp"]:
                    s += e["summ_time_h"]*60 + e["summ_time_m"]
            cat_new["time"] = s
            cat_new["cat_name"] = cat_old["cat_of_cost"]
            g_s += s
            s = 0 
        new_report["general_time"] = round(g_s/60,1)
        return new_report
    else:
        return "None"

@timeit
def report_about_employee(employee_id, lower_date=None, upper_date=None):
    # print(f"Отчет по сотруднику с id: {employee_id}|{Employees.get_login_by_id(employee_id)}")
    projects_id = Records.get_all_employee_projects_id(employee_id, lower_date=lower_date, upper_date=upper_date)
    sum_proj_time = 0
    sum_cat_cost_time = 0
    sum_general_time = 0
    data = {
        "projects": [0 for i in range(len(projects_id))],
        "total_emp_time": 0
    }
    for ip, p_id in enumerate(projects_id):
        p_name = Projects.get_project_name_by_id(p_id)
        # print(f"{ip+1}. {p_name}")
        costs_id = Records.get_all_employee_cat_costs_id(employee_id, p_id, lower_date=lower_date, upper_date=upper_date)
        data["projects"][ip] = {
            "project_id": p_id, 
            "project_name": p_name,
            "projects_costs": {},
            "total_proj_time": 0
        }
        for ic, c_id in enumerate(costs_id):
            c_name = ProjectCosts.get_cat_cost_name_by_id(c_id)
            # print(f"\t {ic+1}. {c_name}")
            times = Records.get_records_by_emp_proj_cat(employee_id, p_id, c_id, lower_date=lower_date, upper_date=upper_date)
            if not (c_name in data["projects"][ip]["projects_costs"]):
                data["projects"][ip]["projects_costs"][c_name] = {
                    "cost_id": c_id, 
                    "records": [],
                    "total_cost_time": 0
                }
            for it, time in enumerate(times):
                # print(f"\t\t {it+1}. {time[0]}: {time[1]} ч. {time[2]} мин.")
                data["projects"][ip]["projects_costs"][c_name]["records"].append({"date_time": time[0], "hours": time[1], "minutes": time[2]})
                sum_cat_cost_time += time[1]*60 + time[2]
                sum_proj_time += time[1]*60 + time[2]
                sum_general_time += time[1]*60 + time[2]
            # print(f"\tОбщее время труда в статье расходов: {sum_cat_cost_time//60} ч. {sum_cat_cost_time%60} мин.")    
            data["projects"][ip]["projects_costs"][c_name]["total_cost_time"] += sum_cat_cost_time
            sum_cat_cost_time = 0
        # print(f"Общее время труда в проекте: {sum_proj_time//60} ч. {sum_proj_time%60} мин.")
        data["projects"][ip]["total_proj_time"] = sum_proj_time
        sum_proj_time = 0
    # print(f"Общие трудозатраты сотрудника за весь период: {sum_general_time//60} ч. {sum_general_time%60} мин.")
    data["total_emp_time"] = sum_general_time
    return data


def get_projects_with_unfilled_costs():
    """Для Даши отображение Статей расходов, у которых не заполнены плановые показатели
    
    res_scheme = [{
        "p_name": "p_name",
        "gip": "gip",
        "c_list": [
            "cost1", "cost2"
        ],
    },]
    """

    res = []
    all_p = Projects.query.all()
    p: Projects
    c: ProjectCosts
    for p in all_p: # type: Projects
        proj_dict = {"p_name": 0, "gip": 0, "c_list": []}
        for c in p.project_costs.all(): # type: Costs    
            if c.man_days == 0:
                if proj_dict["p_name"] == 0:
                    proj_dict["p_name"] = p.project_name
                    proj_dict["gip"] = p.gips.Employees.login
                    proj_dict["c_list"].append(c.Costs.cost_name)
                else:
                    proj_dict["c_list"].append(c.Costs.cost_name) if c.Costs.cost_name not in proj_dict["c_list"] else None
        if proj_dict["p_name"]:
            res.append(proj_dict)
            
    return res

if __name__ == "__main__":
    res = get_project_report_dict(all_records=list_of_dicts,p_name="Project 1")
    print(res)
    json_str=json.dumps(res)
    print(json_str)

        




            


