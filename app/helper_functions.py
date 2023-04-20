from operator import itemgetter
from app.models import ProjectCosts, Costs, Records

projects_name_list = ["22П46 	Балтика СПб Термоупаковщик 2 (банки)",
"22П47 	Балтика СПб Термоупаковщик 3 (ПЭТ)",
"22П50 	Ультрамар СПМ-02",
"23П02 	Гамбит ШУ-НС",
"23П03 	Доступные решения шкаф ГОРЭЛТЕХ",
"23П04 	АБДС ФосАгро Узлы учета",
"23П06 	ЭБС Котел №8 Красносельская",
"23П07 	Балтика СПб Контроль фитинга кег",
"23П08 	Ультрамар замена УПП на ПЧ Стакера",
"23П09 	Ультрамар АСУ магистральных конвейеров",
"23П10 	Карельский окатыш перенос заземления",
"23П11 	Элколог сборка ШУГА",
"23П12 	Антарус сборка шкафов",
"23П01       Мегион Славнефть модернизация КНС4",
"22П17       ВЕЗА ЛСУ ОВКВ Амурский ГХК",
"21П18       Сиб МИР Котел №4",
"22П01       Балтика СПб Термоупаковщик-5",
"22П26       ИСУ Дробления",
"22П29       СтройЭнергоКом Диспетчеризация котельных",
"Разработка этого сайта"]

def clear_strings(str_list):
    for i in range(len(str_list)):
        str_list[i] = str_list[i].replace('\n', '')
        str_list[i] = str_list[i].replace('\t', '')
        if str_list[i][0] == ' ': 
            str_list[i] = str_list[i].replace(' ', '', 1)
    return str_list

def delete_spaces_in(list_of_str:list):
    while True:
        try:
            space_idx = list_of_str.index("")
            list_of_str.pop(space_idx)
        except Exception as e:
            return " ".join(list_of_str)


def none_or_value(value):
    if value == "None":
        return None
    else:
        return value

def is_empty_default_or_none(list_:list) -> bool:
    """Для валидации данных с формы"""
    r = False
    for value in list_:
        if value == "default" or value is None or value == '':
            r = True
    return r

def concatenate_costs(project_id):
    """Функция возвращает объединение стандартных статей расходов и новых (добавленные ГИПом)"""
    old_costs = Costs.get_costs_id_name_in_project()
    new_costs = ProjectCosts.get_costs_id_name_in_project(project_id)
    all_costs = old_costs + new_costs
    return all_costs

def sorting_projects_names(projects_name_id_list):
    list_of_3words = []
    res_words = []
    for i in projects_name_id_list:
        splitters = i[1].split()
        word1 = splitters[0]
        word2 = " ".join(splitters[1:])
        list_of_3words.append([i[0],word1,word2])
    sorted_list_of_3words = sorted(list_of_3words, key=itemgetter(1))
    for i in sorted_list_of_3words:
        if i[1] != "Разработка":
            res_word = i[1] + " 	" + i[2]
            res_words.append((i[0],res_word))
        else:
            res_word = ' '.join([i[1], i[2]])
            res_words.append((i[0],res_word))
    return res_words

# DONE: 
# [x]: 1) Выгружаем все записи в единный список
# [x]: 2) Составить множество уникальных id проектов
# [x]: 3) В разрезе одного уникального проекта составить
#         множество уникальных id статей затрат
# [x]: 4) Для каждой уникальной статьи затрат в проекте, добавляем 
#         эту запись в ProjectCosts
# [x]: 5) Меняем cost_id на id из ProjectCosts

def revise_records_for_ProjectCosts():
    """
        Функция добавляет  в таблицу ProjectCosts те статьи расходов для проектов,
        кторые есть на данный момент в таблице Records.
    """
    all_records = Records.query.all()
    uniq_proj_id = {}
    # Для каждой записи
    for record in all_records:
        # Если id проекта есть, то проверям
        if record.project_id in uniq_proj_id:
            if record.cost_id not in uniq_proj_id[record.project_id]:
                uniq_proj_id[record.project_id].append(record.cost_id)
        # Если в ключах словаря нет id проекта, то добавляем к этому ключу 
        # список пока из одного элемента
        else:
            uniq_proj_id[record.project_id] = [record.cost_id]
    # Добавляем статьи расходов в ProjectCosts
    for proj_id in uniq_proj_id:
        for cost_id in uniq_proj_id[proj_id]:
            new_project_cost = ProjectCosts(cost_id=cost_id,
                                            man_days=100,
                                            project_id=proj_id)
            new_project_cost.save()
            on_change_records = Records.query.filter_by(project_id=proj_id,
                                                        cost_id=cost_id).all()
            # Обновляем cost_id в Records
            for record in on_change_records:
                record.cost_id = new_project_cost.id
            Records.commit()
# BUG: IDK what bug, but bug is there
    return uniq_proj_id
    


if __name__ == "__main__":
    sorted_list = sorting_projects_names(projects_name_list)
    [print(i) for i in sorted_list]
