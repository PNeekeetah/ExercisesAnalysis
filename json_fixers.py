import json_rules as jr
from json_rules import content

print(content["messages"][2773]["text"])

def reparator_bulangiu_di_virguli():
    for i, broken_rules in jr.dictionary.items():
        if ('comma_rule' in broken_rules):
            content["messages"][i]["text"]=content["messages"][i]["text"].replace(',','')

print(content["messages"][2773]["text"])


