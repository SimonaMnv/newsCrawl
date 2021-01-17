import spacy
from spacy import displacy
import regex as re
from trankit import Pipeline
from elasticsearchapp.query_results import gather_raw_verbs

nlp = spacy.load('el_core_news_lg', disable=['ner', 'textcat'])


def important_verb_dict_trankit(type):
    # take the important verbs from all articles based on type
    p = Pipeline('greek')
    important_verbs = []

    important_terms = gather_raw_verbs(type=type, threshold=300)
    tagged_doc = p.posdep(important_terms)  # trankit!
    sentences = tagged_doc['sentences']
    important_verbs.append([sent['tokens'][0]['text'] for sent in sentences if sent['tokens'][0]['upos'] == "VERB"])

    return important_verbs


def important_verb_dict_spacy(type):
    # take the important verbs from all articles based on type
    important_verbs = []

    important_terms = gather_raw_verbs(type=type, threshold=300)
    for term in important_terms:
        doc = nlp(term[0])
        for token in doc:
            if token.pos_ == "VERB":
                important_verbs.append(token.text)
        # important_verbs.append([token.text for token in doc if token.pos_ == "VERB"])

    return important_verbs


def dependency_collector(article, type='δολοφονια'):
    doc = nlp(article)
    subject = []
    object = []
    verb = []

    for token in doc:
        gender = re.search("Gender=[^|]*", token.tag_)
        print(token.text, '->', token.pos_, '(', gender, ')')
    with open("dependency.html", "w") as file:
        file.write(displacy.render(doc, style='dep', jupyter=False))
    for token in doc:
        # extract verb
        if token.pos_ == 'VERB':
            verb.append(token.text)
        # extract subject
        if token.dep_ == 'nsubj' or token.dep_ == 'iobj':
            subject.append(token.text)
        # extract object
        elif token.dep_ == 'dobj' or token.dep_ == 'obj':
            object.append(token.text)

    return verb, subject, object


# raw_data, raw_type = get_latest_raw_data()  # raw_data[0][0]
verb, subject, object = dependency_collector("Φαίνεται οτι κάποιος ή κάποια δολοφόνησε την άτυχη γυναίκα")
print(subject)
print(verb)
print(object)

# test both
important_verb_dict_trankit('δολοφονια')
print(important_verb_dict_spacy('δολοφονια'))

# TODO: decide between trankit or spacy
# TODO: lemmatize results
# TODO: connect "dependency_collector()" with "important_verb_dict_()"
