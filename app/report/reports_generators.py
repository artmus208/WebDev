from copy import copy
from datetime import datetime, timedelta
from app import logger
from app.models import (
    Employees, GIPs, Projects,
    Costs, Tasks, ProjectCosts,
    CostsTasks, Records, Admins
)


from .utils import get_end_week_dates

RIGHT_ORDER_CC_NAMES = [
    "Управление проектом",
    "Проектирование",
    "Программирование",
    "Сборка",
    "Тестирование",
    "ПНР и ШМР",
]

RANDOM_ORDER_CC_NAMES = [
    "Тестирование",
    "Управление проектом",
    "Сборка",
    "Проектирование",
    "ПНР и ШМР",
    "Программирование",
]

def weekly_project_report(project_id):
    """Краткий отчет по проекту за прошлую неделю, все значения в чел/д
    
    report = {
        "Программирование": {
            "week_labor": 0,  
            "fact_labor": 0,  
            "plan_labor": 0,  
            "delta": 0,  
            "progress": 0  
        },
        ...
    }
    """
    cc_report = {
        "fact_labor": 0,
        "plan_labor": 0,
        "delta": 0,
        "progress": 0,
        "week_labor": 0
    }
    prev_monday_date, prev_friday_date = get_end_week_dates()
    p = Projects.get(project_id)
    project_name = p.project_name
    gip_id = p.gip_id
    
    gip_symbols:str = Employees.get(GIPs.get(gip_id).employee_id).login
    gip_symbols = gip_symbols.upper()
    
    
    cat_costs = Records.get_cat_costs_ids_by_project_id(project_id)
    
    cat_costs_names_records = [ProjectCosts.get_cat_cost_name_by_id(cc_id) for cc_id in cat_costs] 
    
    cat_costs_names = ProjectCosts.get_costs_id_name(project_id)
    cat_costs_id = [cc_name[0] for cc_name in cat_costs_names[1:]]
    cat_costs_names = [cc_name[1] for cc_name in cat_costs_names[1:]]
    
    
    all_cat_costs_names = list(set(cat_costs_names + cat_costs_names_records))
    all_cat_costs_id = list(set(cat_costs_id + cat_costs))
    
    d = [(cc_name, copy(cc_report)) for cc_name in all_cat_costs_names]
    report = dict(d)
    caption = f"{project_name}, отчет от {prev_monday_date.date().strftime('%d.%m.%Y')} по {prev_friday_date.date().strftime('%d.%m.%Y')}, ГИП: {gip_symbols}"
    for cc_id in reversed(all_cat_costs_id):
        cc_name = ProjectCosts.get_cat_cost_name_by_id(cc_id)
        current_cc_report = report.get(cc_name, cc_report)
        
        labors_plan_days = ProjectCosts.get(cc_id).man_days
         
        iter_labors_gen_fact = Records.get_labors_by_cat_cost_id(cc_id, project_id)
        iter_labors_week = Records.get_labors_by_cat_cost_id(
            cc_id,
            project_id,
            date_from=prev_monday_date,
            date_to=prev_friday_date
        )       
        
        labors_gen_fact = next(iter_labors_gen_fact)
        labors_week = next(iter_labors_week)
        
        if not any(labors_gen_fact):
            labors_gen_fact = [0, 0]
        if not any(labors_week):
            labors_week = [0, 0]
            
        hours_fact, minuts_fact = map(int, labors_gen_fact)
        hours_week, minuts_week = map(int, labors_week)
        
        labors_hours_fact = minuts_fact/60 + hours_fact
        labors_fact_days = round(labors_hours_fact/8)
        
        labors_hours_week = minuts_week/60 + hours_week
        labors_week_days = round(labors_hours_week/8, 1)
        
        current_cc_report["fact_labor"] += labors_fact_days
        current_cc_report["plan_labor"] = labors_plan_days
        current_cc_report["delta"] = current_cc_report["plan_labor"] - current_cc_report["fact_labor"] 
        
        if current_cc_report["plan_labor"]:
            current_cc_report["progress"] = round((current_cc_report["delta"]/current_cc_report["plan_labor"])*100)
        else:
            current_cc_report["progress"] += 0
            
        current_cc_report["week_labor"] += labors_week_days
    summury = copy(cc_report)
    
    for key in report:
        summury["fact_labor"] += report[key]["fact_labor"]
        summury["plan_labor"] += report[key]["plan_labor"]
        summury["week_labor"] += report[key]["week_labor"]
        
    summury["delta"] = summury["plan_labor"] - summury["fact_labor"]
    if summury["plan_labor"]:
        summury["progress"] = round((summury["delta"]/summury["plan_labor"])*100)
    else:
        summury["progress"] = 0
    
    report = dict(
        sorted(
            report.items(), key=lambda item: RIGHT_ORDER_CC_NAMES.index(item[0]) if item[0] in RIGHT_ORDER_CC_NAMES else len(RIGHT_ORDER_CC_NAMES)
        )
    )
    
    
    return report, summury, caption
    
    
    
    
