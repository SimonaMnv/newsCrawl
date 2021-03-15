import json

with open('ner_annotator_output.json', encoding='utf8') as f:
    TRAIN_DATA = json.load(f)


for data in TRAIN_DATA:
    content = data['content']
    entities = [ent[0:3] for ent in data['entities']]
    TRAIN_DATA = ("(\"" + content + "\", {'entities':" + str(entities) + "}),")

    print(TRAIN_DATA)