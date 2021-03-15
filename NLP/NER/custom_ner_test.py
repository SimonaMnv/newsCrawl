import spacy
from elasticsearchapp.query_results import get_latest_raw_data


# nlp = spacy.load('el')
nlp = spacy.load('custom_model')

raw_data, raw_type = get_latest_raw_data(article_index=0, article_type='δολοφονια')

specific_text = raw_data[0][0]

doc = nlp(specific_text)

doc.ents = [e for e in doc.ents if e.label_ == 'ΠΡΑΞΗ']
print(doc.ents)

print(spacy.displacy.serve(doc, style='ent'))
