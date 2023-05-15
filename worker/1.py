# def add_steam_ids_to_file(steam_ids):
#     with open('users.ini', 'r', encoding='utf-8', errors='ignore') as f:
#         file_content = f.read()
#     # Find the position of the last closing curly brace in the file
#     last_bracket_index = file_content.rfind("}")
#     # Build the string to be added to the file
#     steam_id_str = "\n".join([f'\t"{sid}"\n\t{{\n\t\t"name"\t\t"Unknown"\n\t\t"expires"\t\t"0"\n\t\t"group"\t\t"GOLD"\n\t}}' for sid in steam_ids]) + '\n'
#     updated_file_content = file_content[:last_bracket_index] + steam_id_str + file_content[last_bracket_index:]
#     with open('users.ini', 'w', encoding='utf-8', errors='ignore') as f:
#         f.write(updated_file_content)
#
#
#
# add_steam_ids_to_file(['STEAM_0:0:553203625', 'STEAM_0:0:102538018'])

from datetime import datetime

now = datetime.now()
till = None
if now.hour in [22, 23]:
    till = datetime(now.year, now.month, now.day + 1, 6, 0)
elif now.hour in [i for i in range(6)]:
    till = datetime(now.year, now.month, now.day, 6, 0)
print(till)
print(int(till.timestamp()))