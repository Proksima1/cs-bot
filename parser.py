import re
from typing import List, Union
file_path = 'users.ini'


def clear_items(row: List[Union[str, str, str, str]]):
    output = {}
    output["steam_id"] = row[0][1:-1]
    for item in row[1:]:
        spis = item.replace('""', '" "').split()
        output[spis[0][1:-1]] = spis[1][1:-1]
    return output


def get_data(path_to_file):
    with open(path_to_file, 'r', encoding='utf-8') as reader:
        data = list(map(lambda x: x.replace('\t', '').replace('\n', ''), reader.readlines()))[2:-1]
        count = 0
        output = []
        for i in range(len(data)):
            if i % 6 == 0:
                output.append(list())
            output[i // 6].append(data[i])
        for row in range(len(output)):
            for item in range(len(output[row])):
                try:
                    if output[row][item] in ['{', '}']:
                        output[row].pop(item)
                except IndexError:
                    pass
        output = list(map(lambda x: clear_items(x), output))
    return output


def set_time(path_to_file, user: str):
    data = get_data(file_path)
    for i in data:
        if i['steam_id'] == user:
            i['expires'] = '421412'
    with open(path_to_file, 'a+', encoding='utf-8') as reader:
        a = reader.readlines()
        print(a)


def get_data(path_to_file):
    with open(path_to_file, encoding='utf-8') as f:
        text = f.read()
        items = []
        current_level = 0
        for line in text.splitlines():
            l = line.strip()
            if l == '{':
                current_level += 1
                continue
            elif l == '}':
                current_level -= 1
                continue
            if current_level == 1:
                steam_id = l[1:-1]
                items.append({'steam_id': steam_id})
            elif current_level == 2:
                m = re.search(r'"(.+?)"\s+"(.+?)"', l)
                key, value = m.group(1), m.group(2)
                print(l)
                items[-1][key] = value
    return items


def write_data(path_to_file):
    s = ''
    with open(path_to_file, encoding='utf-8') as f:
        text = f.read()
        current_level = 0
        found = False
        for line in text.splitlines():
            l = line.strip()
            if l == '{':
                current_level += 1
                s += line + '\n'
                continue
            elif l == '}':
                current_level -= 1
                s += line + '\n'
                continue
            if current_level == 1:
                steam_id = l[1:-1]
                s += line + '\n'
                if steam_id == 'STEAM_0:0:548438205':
                    found = True
            elif current_level == 2:
                m = re.search(r'"(.+?)"\s+"(.+?)"', l)
                key, value = m.group(1), m.group(2)
                if found and key == 'expires':
                    s += line.replace(value, '12412') + '\n'
                    found = False
                else:
                    s += line + '\n'
        s = s.rstrip()
    with open(path_to_file, mode='w', encoding='utf-8') as w:
        w.write(s)



# data = write_data(file_path)
# print(data)
#set_time(file_path, 'STEAM_0:1:577154573')
