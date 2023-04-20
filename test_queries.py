from typing import List

from app import app, db, text
from app.models import (
    Projects, GIPs,
    Costs, Records,
    Employees, ProjectCosts, CostsTasks, Tasks)
from app import helper_functions
from app import select, execute

# with app.app_context():
#     res = execute(
#         select(Records)
#     ).first()
#     print(res)

with app.app_context():
    # res = Records.get_all_employee_projects_id(34)
    res = Records.get_all_employee_cat_costs_id(34, 22)
    for r in res:
        print(r)


with app.app_context():
    print(f"Отчет по сотруднику с id: {34}|{Employees.get_login_by_id(34)}")
    projects_id = set(Records.get_all_employee_projects_id(34))
    sum_proj_time = 0
    sum_cat_cost_time = 0
    sum_general_time = 0
    for ip, p_id in enumerate(projects_id):
        print(f"{ip+1}. {Projects.get_project_name_by_id(p_id)}")
        costs_id = set(Records.get_all_employee_cat_costs_id(34, p_id))

        for ic, c_id in enumerate(costs_id):
            print(f"\t {ic+1}. {ProjectCosts.get_cat_cost_name_by_id(c_id)}")
            times = Records.get_records_by_emp_proj_cat(34, p_id, c_id)
            for it, time in enumerate(times):
                print(f"\t\t {it+1}. {time[0]}: {time[1]} ч. {time[2]} мин.")
                sum_proj_time += time[1]*60 + time[2]
                sum_cat_cost_time += time[1]*60 + time[2]
                sum_general_time += time[1]*60 + time[2]
            print(f"\tОбщее время труда в статье расходов: {sum_cat_cost_time//60} ч. {sum_cat_cost_time%60} мин.")    
            sum_cat_cost_time = 0
        print(f"Общее время труда в проекте: {sum_proj_time//60} ч. {sum_proj_time%60} мин.")
        sum_proj_time = 0
    print(f"Общие трудозатраты сотрудника за весь период: {sum_general_time//60} ч. {sum_general_time%60} мин.")


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


