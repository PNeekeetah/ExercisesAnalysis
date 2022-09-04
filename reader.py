import json


with open('sanitized.json','r',encoding='cp850') as file:
    all_content = json.loads(file.read())
    exercises = list()
    failed_exercises = list()
    for message in all_content['messages']:
        try:
            exercise = json.loads(message['text'])
            exercises.append(exercise)
        except:
            failed_exercises.append(message['text'])
            print(message['text'])
            all_lines = message['text'].split('\n')
            new_all_lines = []
            for line in all_lines:
                line = line.replace(',', '')
                line = line + ',' if 'super_set' not in line else line
                new_all_lines.append(line)
            print ('\n'.join(new_all_lines))
            break

    
print(len(exercises))
print(len(failed_exercises)) # we want to dump these into a file and analyze why they fail