from operator import itemgetter


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




def sorting_projects_names(projects_name_list):
    list_of_2words = []
    res_words = []
    for i in projects_name_list:
        splitters = i.split()
        word1 = splitters[0]
        word2 = " ".join(splitters[1:])
        list_of_2words.append([word1,word2])
    sorted_list_of_2words = sorted(list_of_2words, key=itemgetter(0))
    for i in sorted_list_of_2words:
        if i[0] != "Разработка":
            res_word = i[0] + " \t" + i[1]
            res_words.append(res_word)
        else:
            res_word = ' '.join([i[0], i[1]])
            res_words.append(res_word)
    return res_words

if __name__ == "__main__":
    sorted_list = sorting_projects_names(projects_name_list)
    [print(i) for i in sorted_list]
