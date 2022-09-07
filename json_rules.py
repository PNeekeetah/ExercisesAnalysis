import json
from typing import List, Callable, Tuple, Set

FILE_NAME = "sanitized.json"

def find_occurrences(string: str, character_to_find: chr) -> List[int]:
    """
    Return a list of all character occurences

    In:
        string: the string where we want to find the positions
        character_to_find: the symbol we wish to find in "string"

    Out:
        A list of all positions of "character_to_find" in "string"
    """
    return [
        i 
        for i, letter in enumerate(string) 
        if letter == character_to_find
    ]

def message_is_readable(func: Callable) -> Tuple[bool, str]:
    """
    A wrapper which checks whether there are at least 2 lines
    in the message. 

    In:
        func: function to be called, one of the rules
    Out:
        True, "reason" if the rule specified in "func" is
        broken or the message is not readable
    """
    def wrap(*args, **kwargs):
        if len(args[0]) <= 2:
            return True, "readability_rule"
        result = func(*args, **kwargs)
        return result

    return wrap


def split_json_message_into_lines(message: str) -> List[str]:
    """
    All JSON entries are split into one key - value pair per line

    In:
        message: the JSON as a string
    Out:
        The lines which make up the message
    """
    return message.split('\n')

def recreate_json(json_lines_list: List[str]) -> str:
    """
    This recreates the initial JSON string
    """
    return '\n'.join(json_lines_list)

@message_is_readable
def breaks_braces_rule(json_lines: List[str]) -> Tuple[bool, str]:
    """
    The first and last lines of each message should be '{' and '}'.
    
    In:
        json_lines: The lines which make up the message
    
    Out:
        True, "braces_rule" if the rule written above is broken.
        False, "" otherwise
    """
    first_line = json_lines[0].strip()
    last_line = json_lines[-1].strip()
    if (
        first_line == '{' 
        and last_line == '}'
    ):
        return False, ""
    return True, "braces_rule"

@message_is_readable
def breaks_comma_rule(json_lines: List[str]) -> Tuple[bool, str]:
    """
    1. Only 1 comma is allowed at the end of a line
    2. No comma is allowed for the last JSON entry
    3. A comma is allowed between quotes
    4. There should always be at least one comma per line
    5. The last character on a line should be a comma ( minus whitespaces)

    In:
        json_lines: The lines which make up the message
    
    Out:
        True, "comma_rule" if the rules written above are broken.
        False, "" otherwise
    """

    # Ignore first line ( which is supposed to be '{') and
    # ignore last 2 lines ( "super_set" entry and '}').
    for line in json_lines[1:-2]:
        commas = line.count(',')
        # 4
        if commas == 0:
            return True, "comma_rule"
        # 3
        if commas > 1:
            comma_positions = find_occurrences(line, ',')
            quote_positions = find_occurrences(line, '"')
            paired_quote_positions = list(zip(*[iter(quote_positions)]*2))
            for comma_position in comma_positions[:-1]:
                if not any (
                    first_q_pos < comma_position 
                    and comma_position < second_q_pos
                    for (first_q_pos, second_q_pos) in paired_quote_positions
                ):
                    return True, "comma_rule"
        # 1, 5
        if line.strip()[-1] != ',':
            return True, "comma_rule"
    
    # 2
    if ',' in json_lines[-2]:
        return True, "comma_rule"
    
    return False, ""

@message_is_readable
def breaks_colon_rule(json_lines: List[str]) -> Tuple[bool, str]:
    """
    Only one ':' should be on each line
    There must be at least 1 colon on each line

    In:
        json_lines: The lines which make up the message
    
    Out:
        True, "colon_rule" if the rule written above is broken.
        False, "" otherwise
    """
    for line in json_lines[1:-2]:
        colons = line.count(':')
        if colons != 1:
            return True, "colon_rule"
    
    return False, ""

@message_is_readable
def breaks_quote_rule(json_lines: List[str]) -> Tuple[bool, str]:
    """
    There should be either 2 or 4 quotation marks on each line.

    In:
        json_lines: The lines which make up the message
    
    Out:
        True, "quote_rule" if the rule written above is broken.
        False, "" otherwise
    """
    for line in json_lines[1:-2]:
        quotes = line.count('"')
        if quotes not in {2, 4}:
            return True, "quote_rule"
    
    return False, ""

@message_is_readable
def breaks_weight_rule(json_lines: List[str]) -> Tuple[bool, str]:
    """
    Weight should be an int, a float or an expression.
    In the first 2 cases, this rule wouldn't be broken. However,
    we don't have expressions yet, so anything such as BW + 3 
    would break this rule.

    In:
        json_lines: The lines which make up the message
    
    Out:
        True, "weight_rule" if the rule written above is broken.
        False, "" otherwise
    """
    weight_line = ""
    for line in json_lines[1:-2]:
        if "weight" in line:
            weight_line = line
            break
    weight_value = weight_line.split(':')
    try:
        float(weight_value)
    except TypeError:
        # If we can't convert automatically 
        # to float, it's probably supposed
        # to be an expression
        return True, "weight_rule"
    
    return False, ""

@message_is_readable
def breaks_misc_extra_symbols_rule(json_lines: List[str]) -> Tuple[bool, str]:
    """
    The only allowable symbols should be : +, -, ", :, [a-zA-Z0-9], ., <, >, {
    }, , , \n, _

    In:
        json_lines: The lines which make up the message
    
    Out:
        True, "misc_rule" if the rule written above is broken.
        False, "" otherwise

    """
    #TODO : Implement
    return False, ""

RULES = [
    breaks_comma_rule,
    breaks_braces_rule,
    breaks_colon_rule,
    breaks_quote_rule,
    breaks_weight_rule,
    breaks_misc_extra_symbols_rule,
]

def check_rules(json_lines: List[str], rules_list: List[Callable]) -> Set[str]:
    """
    Takes as input the JSON lines and a set of rules to check.
    The rules are callable functions which return tuples of type 
    bool, str. 

    In:
        json_lines: The lines which make up the message
        rules_list: A list of callable functions
    
    Out:
        A set of all broken rules for this message
    """
    broken_rules = set()
    for check in rules_list:
        broken, rule = check(json_lines)
        if broken:
            broken_rules.add(rule)
    return broken_rules



with open(FILE_NAME, 'r') as file:
    content = json.loads(file.read())
    dictionary = dict()
    for message in content["messages"]:
        json_message = message["text"]
        json_lines : List[str] = split_json_message_into_lines(json_message)
        broken_rules = check_rules(json_lines, RULES)
        dictionary[message["id"]] = broken_rules

"""
s = set()
for k,v in dictionary.items():
    if 'colon_rule' in v:
        print (dictionary[k])
    s = s.union(v)

print(s)
"""