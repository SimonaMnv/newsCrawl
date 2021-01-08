import json
import numpy as np
from elasticsearchapp.query_results import analyzed_results_body, analyzed_results_title, analyzed_results_tags

np.random.seed(500)

with open("custom_crime_dictionaries.json", "r", encoding='utf-8') as json_file:
    custom_dict = json.load(json_file)

body_to_classify, title_to_classify, tags_to_classify = analyzed_results_body(), \
                                                        analyzed_results_title(), \
                                                        analyzed_results_tags()

lala = []
for i in range(0, 50):
    lala.append(body_to_classify[i])

print(lala)

