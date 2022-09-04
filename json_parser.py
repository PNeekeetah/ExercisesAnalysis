import json
import re

KEYWORDS_TO_SEARCH = [
    '{',
    '}',
#    'weight',  # Appears in session weight as well
    'grip_mod',
]

# [Columns], (Allowed Types)
instance_checking = [
    (['exercise'], (str)),
    (['total_weight','weight'], (float, int, str)),
    (['angle'], (float, int)),
    (['equipment'], (str)),
    (['reps'], (int)),
    (['assisted'], (int)),
    (['partial_rom'], (int)),
    (['dropped_weight'], (int)),
    (['grip_mod_1'], (str)),
    (['grip_mod_2'], (str)),
    (['grip_mod_3'], (str)),
    (['grip_mod_4'], (str)),
    (['plates'], (int, type(None), float)),
    (['half_weight'], (bool)),
    (['drop_set'], (bool)),
    (['super_set'], (bool)),
]

def fix_dictionary_keys(dictionary):
    return { key.strip():dictionary[key] for key in dictionary.keys()}
    
def dict_type_checking(sets_list):
    discarded_sets = []
    correct_sets = []
    should_keep = True
    for exercise_set in sets_list:
        for inst in instance_checking:
            
            if not any(i in exercise_set.keys() for i in inst[0]): # cannot find the key in the dictionary
                discarded_sets.append((exercise_set, 'Incorrect formatting'))
                should_keep = False
                break
            
            key = list(set(inst[0]).intersection(exercise_set.keys()))[0]
            if not isinstance(exercise_set[key], inst[1]):
                discarded_sets.append((exercise_set, inst[0]))
                should_keep = False
                break

        if should_keep:
            correct_sets.append(exercise_set)
        should_keep = True
    
    return correct_sets, discarded_sets


def attempt_parse_message(text):
    if any(list(k in text for k in KEYWORDS_TO_SEARCH)):
        try:
            set_details = json.loads(text)
            return True, set_details, None
        except Exception as e:
            #print("Cannot parse as is")
            return False, text, e
    return False, text, None


def correct_bodyweight_plus_numbers(text):
    if 'BW' not in text:
        return False, text, None
    text = re.sub(
        'total_weight":[ ]*([a-zA-Z\-\+0-9\. ]*),',
        lambda m: f'total_weight": "{m[1]}",',
        text
    )
    try:
        set_details = json.loads(text)
        return True, set_details, None
    except Exception as e:
        #print("BW was not the issue")
        return False, text, e


def correct_lines(text):
    
    if not any(list(k in text for k in KEYWORDS_TO_SEARCH)):
        return False, text, None
    
    def add_comma(text):
        return text.replace(',','') + ','
    
    def remove_comma(text):
        return text.replace(',','')
    
    def remove_dot(text):
        return text.replace('.','')

    def contains(object, sequence):
        return object in sequence
    
    def doesnt_contain(object, sequence):
        return object not in sequence
    
    
    lines = []
    try:
        lines = text.split('\n')
    except Exception as e:
        return False, text, e 
        
    to_not_add_comma = (doesnt_contain, ('super_set','{','}'), add_comma)
    to_remove_comma = (contains, ('super_set'), remove_comma)
    to_remove_dot = (contains, ('{', '}'), remove_dot)
    operations = [
        to_not_add_comma,
        to_remove_comma,
        to_remove_dot
    ]
    for i in range(0, len(lines)):
        for op in operations:
            if (
                all(
                    op[0](item, lines[i])
                    for item in op[1]
                )
            ):
                lines[i] = op[2](lines[i])


    reassembled_text = '\n'.join(lines)
    try:
        set_details = json.loads(reassembled_text)
        return True, set_details, None
    except Exception as e:
        #print("Comma not a problem")
        return False, reassembled_text, e

def readd_quotes_and_strip(text):
    no_quotes = text.replace('"','')
    readd_quotes = '"' + no_quotes.strip() + '"'
    return readd_quotes

def fix_quotes(text):
    if not any(list(k in text for k in KEYWORDS_TO_SEARCH)):
        return False, text, None
    lines = []
    try:
        lines = text.split('\n')
    except Exception as e:
        return False, text, e 
    for i in range(1, len(lines)-1): # first and last lines are { and }
        line_elems = lines[i].split(':')
        if len(line_elems) == 2:
            line_elems[0] = readd_quotes_and_strip(line_elems[0])
            if '"' in line_elems[1]:
                line_elems[1] = readd_quotes_and_strip(line_elems[1])
        lines[i] = ' : '.join(line_elems)
    reassembled_text = '\n'.join(lines)
    try:
        set_details = json.loads(reassembled_text)
        return True, set_details, None
    except Exception as e:
        #print("Quotes not a problem")
        return False, reassembled_text, e
            


functions = [
    attempt_parse_message,
    correct_bodyweight_plus_numbers,
    fix_quotes, # has to be before correct lines because code is written badly :)
    correct_lines,
]


errors_per_message = []
discarded_messages = []
set_dict_list = []
with open ('result.json','r',encoding='utf8') as file:
    text = file.read()
    json_text = json.loads(text)
    success = False
    for cnt,message_dict in enumerate(json_text['messages']):
        message_text = message_dict['text']
        errors = []
        for func in functions:
            success, message_text, exception = func(message_text)
            if success:
                set_dict_list.append(message_text)
                break # succesfully converted
            if exception is not None:
                errors.append(exception)
        if errors and not success:
            errors_per_message.append((cnt, errors))
            discarded_messages.append((cnt, message_text))

#print(len(discarded_messages))
#print(len(set_dict_list))

correct, discarded = dict_type_checking(set_dict_list)
attempt_correct = []

for d in discarded:
    attempt_correct.append(fix_dictionary_keys(d[0]))

c1, discarded = dict_type_checking(attempt_correct)

correct.extend(c1)

print(len(correct))

with open('discarded.json', 'w') as file:
    counter = 0
    file.write('{')
    for d in discarded_messages:
        file.write(f'"d_{counter}" :' + d[1])
        file.write(',')
        counter += 1
    file.write('}')


'([a-zA-Z:_\-\+><" _0-9\.]+),$'