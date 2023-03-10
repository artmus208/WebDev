from operator import itemgetter


projects_name_list = ["22П46 	Балтика СПб Термоупаковщик 2 (банки)",
                      "22П47 	Балтика СПб Термоупаковщик 3 (ПЭТ)",
                      "22П50 	Ультрамар СПМ-02",
                      "23П02 	Гамбит ШУ-НС",
                      "23П03 	Доступные решения шкаф ГОРЭЛТЕХ",
                    "23П04 	АБДС ФосАгро Узлы учета",
                     "Разработка этого сайта",
                      "cnhfyas" ]




def sorting_projects_names(projects_name_list):
    list_of_2words = []
    unusual_words = [] 
    for i in projects_name_list:
        split_i = i.split("\t")
        if len(split_i) != 1:
            list_of_2words.append(split_i)
        else:
            unusual_words.append(split_i[0])
    for item in list_of_2words:
        item[0] = item[0].strip()
    sorted(list_of_2words, key=itemgetter(1))
    pre_words = [" ".join(i) for i in list_of_2words]
    res_words = pre_words + unusual_words
    return res_words


    


if __name__ == "__main__":
    sorted_list = sorting_projects_names(projects_name_list)
    [print(i) for i in sorted_list]
