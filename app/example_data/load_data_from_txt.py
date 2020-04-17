import codecs


def load_names(path):
    names = []
    with codecs.open(path, 'r', 'utf-8') as source_file:
        for line in source_file:
            line = line.strip()
            line = line.title()
            names.append(line)
    return names


if __name__ == '__main__':
    first_name_path = 'first_names.txt'
    first_name_list = load_names(first_name_path)
    last_name_path = 'last_names.txt'
    last_name_list = load_names(last_name_path)

