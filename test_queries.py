from datetime import datetime, date, time
from typing import List

from app import app, db, text
from app.models import (
    Projects, GIPs,
    Costs, Records,
    Employees, ProjectCosts, CostsTasks, Tasks)
from app import helper_functions
from app import select, execute

from app.reports_makers import report_about_employee, get_project_report_dict

from utils import timeit
@timeit
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
    }
    for cat_cost_id in Records.get_cat_costs_ids_by_project_id(p_id):
        cat_cost_name = ProjectCosts.get_cat_cost_name_by_id(cat_cost_id)
        if not (cat_cost_name in project_report["cat_cost_list"]):
            project_report["cat_cost_list"][cat_cost_name] = {
                "cat_cost_id": cat_cost_id,
                "emp_list": {},
                "total_perf_time": 0,
            }
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
        project_report["cat_cost_list"][cat_cost_name]["total_perf_time"] = sum(total_cat_cost_time)
    for cat_cost_name in project_report["cat_cost_list"]:
        project_report["total_perf_time"] += project_report["cat_cost_list"][cat_cost_name]["total_perf_time"]
    return project_report
@timeit
def report_project(p_id):
    # TODO:
    # [x]: Проверить на адекватность выдачу отчета
    total_perf_min_project = 0
    total_perf_min_cat_cost = 0
    project_report = {
        "p_id": p_id,
        "p_name": Projects.get_project_name_by_id(p_id),
        "cat_cost_list": Records.get_cat_costs_ids_by_project_id(p_id),
        "total_perf_time": 0,
    }
    for i_cat, cat_cost_id in enumerate(project_report["cat_cost_list"]):
        cat_cost_report = {
            "cat_cost_id": cat_cost_id,
            "cat_cost_name": ProjectCosts.get_cat_cost_name_by_id(cat_cost_id),
            "emp_list": Records.get_emp_ids_by_project_id_cat_cost_id(
                project_id=p_id, cat_cost_id=cat_cost_id
            ),
            "total_perf_time": 0,
        }
        for i_emp, emp_id in enumerate(cat_cost_report["emp_list"]):
            emp_report = {
                "emp_id": emp_id,
                "emp_login": Employees.get_login_by_id(emp_id),
                "total_perf_min": Records.get_info_by_proj_id_cat_id_emp_id(
                    project_id=p_id,
                    project_cost_id=cat_cost_id,
                    employee_id=emp_id,
                )
            }
            total_perf_min_cat_cost += emp_report["total_perf_min"]
            cat_cost_report["emp_list"][i_emp] = emp_report
        cat_cost_report["total_perf_time"] = total_perf_min_cat_cost
        project_report["cat_cost_list"][i_cat] = cat_cost_report
        total_perf_min_project += total_perf_min_cat_cost
        total_perf_min_cat_cost = 0
    project_report["total_perf_time"] = total_perf_min_project
    # TODO:
    # [ ]: Убрать дублирующиеся названия категорий затрат
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


def show_project_report(p_id=3):
    with app.app_context():
        project_report = report_project(p_id)
        print(
            "Отчет по проекту:\n",
            f'({project_report["p_id"]})',
            project_report["p_name"],
            f'{project_report["total_perf_time"] // 60}ч',
            f'{project_report["total_perf_time"] % 60}мин',
        )
        for cat_cost_report in project_report["cat_cost_list"]:
            print(
                "\t Отчет по категории затрат:",
                f'({cat_cost_report["cat_cost_id"]})',
                cat_cost_report["cat_cost_name"],
                f'{cat_cost_report["total_perf_time"] // 60}ч',
                f'{cat_cost_report["total_perf_time"] % 60}мин',
            )
            for emp_report in cat_cost_report["emp_list"]:
                print(
                    "\t\t Отчет по сотруднику:",
                    f'({emp_report["emp_id"]})',
                    emp_report["emp_login"],
                    f'{emp_report["total_perf_min"] // 60}ч',
                    f'{emp_report["total_perf_min"] % 60}мин',
                )

show_project_report()
show_project_report2(p_id=3)

# # Делаю отчет по проекту
# with app.app_context():
    
#     # TODO: 
#     # [x]: Получить уникальные номера сотрудников в этом проекте
#     # [x]: получить уникальные номера категорий затрат для этого сотрудника
#     # [x]: после этого итерировать под этими категориями затрат с Id этого сотрудника с этим проектом
#     emp_list_ids_list = Records.get_emp_ids_by_project_id(p_id)
#     project_costs_ids_list = Records.get_cat_costs_ids_by_project_id(p_id)
#     for emp_id in list(Records.get_emp_ids_by_project_id(p_id)):
#         print(emp_id)
#         for cat_cost_id in Records.get_all_employee_cat_costs_id(
#                                 employee_id=emp_id,
#                                 project_id=p_id
#                             ):
#             cat_cost_name = ProjectCosts.get_cat_cost_name_by_id(cat_cost_id)
#             print(f"({cat_cost_id}){cat_cost_name}", end=" ")
#             res = Records.get_info_by_proj_id_cat_id_emp_id(project_id=p_id, project_cost_id=cat_cost_id, employee_id=emp_id)
#             print(f"\t {res}")

# with app.app_context():
#     res = execute(
#         select(Records)
#     ).first()
#     print(res)

# with app.app_context():
#     # res = Records.get_all_employee_projects_id(34)
#     res = Records.get_all_employee_cat_costs_id(34, 22)
#     for r in res:
#         print(r)

# # Проверка работы отчета по сотруднику по всему периоду
# with app.app_context():
#     data = report_about_employee(34)
#     print(data)
#     print(data["total_emp_time"]//60, data["total_emp_time"]%60)

# all_records_list = []
# 
# with app.app_context():
#     for record in Records.get_records_by_proj_id(p_id):
#         all_records_list.append(record.as_dict_name())
#     res = get_project_report_dict(all_records_list, p_id)
#     for p in res["list_of_cat_cos"]:
#         print(p["cat_of_cost"])
#         for t in p["list_of_tasks"]:
#             print("\t"+str(t["task_name"]))
#             for e in t["list_of_emp"]:
#                 print("\t\t" + e["emp_name"] + " " + str(e["summ_time_h"]) + " " + str(e["summ_time_m"]))

# ## Проверка работы отчета по сотруднику по выбранному периоду:
# with app.app_context():
#     d_low = date(year=2023, month=4, day=1)
#     t_low = time(hour=0, minute=0)
#     # date_low = datetime.combine(d_low, t_low)
#     date_low = None
    
#     d_upper = date(year=2023, month=4, day=30)
#     t_upper = time(hour=23, minute=59)
#     # date_upper = datetime.combine(d_upper, t_upper)
#     date_upper = None

#     print(f"Lower time:{date_low}")
#     print(f"Upper time:{date_upper}")

#     data = report_about_employee(
#         employee_id=2,
#         lower_date=date_low,
#         upper_date=date_upper
#     )
#     print(data)
#     print(data["total_emp_time"]//60, data["total_emp_time"]%60)

# with app.app_context():
#     res = Records.get_last_5_records()
#     [print(i, item, type(item)) for i, item in enumerate(res)]

# with app.app_context():
#     res:List[Records] = Records.get_last_5_records()
#     for r in res:
#         # print("Before replacement:\n", r, sep="")
#         record_with_names = r.replace_ids_to_names(
#             EmployeesObj=Employees, ProjectsObj=Projects,
#             ProjectCostObj=ProjectCosts,  CostsObj=Costs
#         )
#         print("After replacement:\n", record_with_names,sep='')
        

# with app.app_context():
#     res:List[Records] = Records.get_last_5_records(emp_id=34)
#     for r in res:
#         # print("Before replacement:\n", r, sep="")
#         record_with_names = r.replace_ids_to_names(
#             EmployeesObj=Employees, ProjectsObj=Projects,
#             ProjectCostObj=ProjectCosts,  CostsObj=Costs
#         )
#         print("After replacement:\n", record_with_names,sep='')

# with app.app_context():
#     print(f"ProjectCosts.query.first().id: {ProjectCosts.query.order_by(ProjectCosts.id.desc()).first().id}")

# with app.app_context():
#     cost_name = Costs.query.filter_by(id=1).first().cost_name
#     print(Costs.query.filter_by(cost_name=cost_name).first().cost_name.__repr__())
    

# # Проверка текстового запроса
# with app.app_context():
#     session = db.session
#     res = session.execute(text("SELECT * FROM gips")).fetchall()
#     # print("Text query result:\n")
#     # print(res)

# # Провекра select запроса
# with app.app_context():
#     select = db.select
#     stmt = select(GIPs).where(GIPs.id == 1)
#     res = db.session.execute(stmt).scalar()
#     print(stmt)    
#     print(res)

# # Проерка order_by запроса
# with app.app_context():
#     select = db.select
#     execute = db.session.execute
#     res = execute(
#         select(Projects).where(Projects.gip_id == 1)
#     ).scalars()
#     print(res.all())


