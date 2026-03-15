def load_list_from_file(filename):
    data_list = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            data_list.append(line.rstrip('\n'))
    return data_list

loaded_content_list = load_list_from_file('../content.txt')
print(loaded_content_list)
