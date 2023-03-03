import datetime
import json
from typing import Dict, List


def make_query_to_dict_list(query_obj) -> List[Dict]:
    res = list()
    for q_o in query_obj:
        res.append(q_o.as_dict())
    return res


def filter_dict_by(list_of_dicts, dict_item):
    """Only those that have a dict_item pair remain in the list of dictionaries."""
    filtered_list = list_of_dicts.copy()
    for i in range(len(list_of_dicts)):
        dOne = list_of_dicts[i]
        if not dict_item in dOne.items():
            filtered_list.remove(dOne)
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

def get_project_report_dict(all_records: List[Dict], p_name:str) -> Dict:
    """Из all_records получается словарь заданной структуры. См example в этом модуле
    
        Структура словаря:
            Имя проекта: p_name 
                Статьи расходов
                    Задачи
                        Работники  
                            Часы и минуты работника
    """
    emp_summ_time_h = 0
    emp_summ_time_min = 0
    list_of_category_of_costs = get_uniq_key_values(all_records, "category_of_costs")
    print(p_name)
    buff_dict_item_0 = {"list_of_cat_cos": [0 for i in range(len(list_of_category_of_costs))]}
    for i_c, category_of_costs in enumerate(list_of_category_of_costs):
        buff_dict_1 = filter_dict_by(all_records, ("category_of_costs", category_of_costs))
        list_uniq_tasks = get_uniq_key_values(buff_dict_1, "task")
        buff_dict_item_1 = {"cat_of_cost": category_of_costs, "list_of_tasks": [0 for i in range(len(list_uniq_tasks))]}
        print('\t', category_of_costs)
        # reportDict[category_of_costs] = list()
        for i_t, task in enumerate(list_uniq_tasks): 
            buff_dict_2 = filter_dict_by(all_records, ("task", task))
            list_uniq_emp = get_uniq_key_values(buff_dict_2, "employee")
            print('\t\t', task)
            buff_dict_item_2 = {"task_name": task, "list_of_emp": [0 for i in range(len(list_uniq_emp))]}
            for i_e, employee in enumerate(list_uniq_emp):                
                buff_dict_3 = filter_dict_by(all_records, ("employee", employee))
                for d_item in buff_dict_3:
                    emp_summ_time_h = emp_summ_time_h + d_item['hours']
                    emp_summ_time_min = emp_summ_time_min + d_item['minuts']
                emp_summ_time_gen_h = (60*emp_summ_time_h + emp_summ_time_min) // 60
                emp_summ_time_gen_m = (60*emp_summ_time_h + emp_summ_time_min) % 60
                buff_dict_item_3 = {"emp_name":employee, "summ_time_h":emp_summ_time_gen_h, "summ_time_m":emp_summ_time_gen_m}
                buff_dict_item_2['list_of_emp'][i_e] = buff_dict_item_3
                print('\t\t\t', employee, emp_summ_time_gen_h,emp_summ_time_gen_m)
            buff_dict_item_1['list_of_tasks'][i_t] = buff_dict_item_2 
        buff_dict_item_0['list_of_cat_cos'][i_c] = buff_dict_item_1
        buff_dict_item_0["project_name"] = p_name
    return buff_dict_item_0


if __name__ == "__main__":
    res = get_project_report_dict(all_records=list_of_dicts,p_name="Project 1")
    print(res)
    json_str=json.dumps(res)
    print(json_str)

        




            


