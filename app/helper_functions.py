from operator import itemgetter
from app.models import ProjectCosts, Costs

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

if __name__ == "__main__":
    sorted_list = sorting_projects_names(projects_name_list)
    [print(i) for i in sorted_list]
