def delete_spaces_in(list_of_str:list):
    while True:
        try:
            space_idx = list_of_str.index("")
            list_of_str.pop(space_idx)
        except Exception as e:
            print("Deleted all spaces\n")
            return " ".join(list_of_str)
            

list_ = ['23П15', '', '', '', '', '', '', 'Ультрамар', 'Транзит']
list_ =  delete_spaces_in(list_)
print(list_)