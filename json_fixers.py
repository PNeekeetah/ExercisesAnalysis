import json
from json_rules import breaks_quote_rule, split_json_message_into_lines, message_is_readable

def fix_quote_rule_issues(json_lines):
    new_list = []
    new_list.append(json_lines[0])
    for line in json_lines[1:-1]:
        if line.count('"') not in {2,4}:
            if line.count(':') != 1:
                new_list.append(line)
                continue
            part_1, part_2 = line.split(":")
            part_1 = part_1.replace('"','').strip()
            part_2 = part_2.replace('"','').strip()[0:-2]
            part_1 = '"' + part_1 + '"'
            part_2 = '"' + part_2 + '",'
            new_list.append(part_1 + ':' + part_2)
        else:
            new_list.append(line)
    return new_list


with open("sanitized.json", "r") as file:
    all_messages = json.loads(file.read())["messages"]
    for message in all_messages:
        
        json_lines = split_json_message_into_lines(message["text"])
        if not message_is_readable(json_lines):
            continue
        if breaks_quote_rule(json_lines)[0]:
            new_json_lines = fix_quote_rule_issues(json_lines)
            print(breaks_quote_rule(new_json_lines))
            


