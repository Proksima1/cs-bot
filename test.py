import json
try:
    with open('statistics.json', 'r+', encoding='utf-8') as reader:
        data = json.loads(reader.read())
except FileNotFoundError:
    open('statistics.json', 'a+').close()
    data = {'all_came_money': 0, 'buyers_count': 0}
with open('statistics.json', 'w+', encoding='utf-8') as writer:
    data['all_came_money'] += 300
    data['buyers_count'] += 1
    writer.write(json.dumps(data))