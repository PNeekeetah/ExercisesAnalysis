import json_rules as jr
from json_rules import content

print(content["messages"][2773]["text"])

def reparator_bulangiu_di_virguli():
    global content
    for i, broken_rules in jr.dictionary.items():
        if ('comma_rule' in broken_rules):
            content["messages"][i]["text"]=content["messages"][i]["text"].replace(',','')

reparator_bulangiu_di_virguli()

print(content["messages"][2773]["text"])


