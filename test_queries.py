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


