import spacy
from elasticsearchapp.query_results import get_latest_raw_data


# nlp = spacy.load('el')
nlp = spacy.load('custom_model')

raw_data, raw_type = get_latest_raw_data(article_index=0, article_type='δολοφονια')

specific_text = raw_data[0][0]

# test the custom model
nlp2 = spacy.load('custom_model/')
doc = nlp(specific_text)

print(spacy.displacy.serve(doc, style='ent'))