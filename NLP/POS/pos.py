import spacy
from spacy import displacy
import regex as re
from elasticsearchapp.query_results import gather_raw_verbs, get_specific_analyzed, get_latest_raw_data
import nltk

# nltk.download('punkt') # only run once
nlp = spacy.load('el_core_news_lg', disable=['ner', 'textcat'])


def important_verb_dict_spacy(type):
    # take the important verbs from all articles based on type
    important_verbs = []

    important_terms = gather_raw_verbs(type=type, threshold=30)  # TODO: play with threshold
    for term in important_terms:
        doc = nlp(term[0])
        for token in doc:
            if token.pos_ == "VERB":
                important_verbs.append(token.text)

    return important_verbs


def dependency_collector(article):
    doc = nlp(article)
    subject = []
    object = []
    verb = []
    gender_subject = []
    gender_object = []

    for token in doc:
        if len(token) > 4:  # skip and ignore small words, probably junk
            # extract verb
            if token.pos_ == 'VERB':
                verb.append(token.text)

            check = re.findall("Gender=[^|]*", token.tag_)
            if not check == []:
                if not check[0] == 'Gender=Neut':
                    # extract subject
                    if token.dep_ == 'nsubj' or token.dep_ == 'iobj' or token.dep_ == 'conj':
                        gender_subject.append(re.findall("Gender=[^|]*", token.tag_))
                        subject.append(token.text)
                    # extract object
                    elif token.dep_ == 'dobj' or token.dep_ == 'obj':
                        gender_object.append(re.findall("Gender=[^|]*", token.tag_))
                        object.append(token.text)

    # with open("dependencyLogs/dependency.html", "w") as file:
    #     file.write(displacy.render(doc, style='dep', jupyter=False))

    return verb, subject, object, gender_subject, gender_object


# get 1 article based on index given for testing
raw_data, raw_type = get_latest_raw_data(article_index=3)  # raw_data[0][0]
verb, subject, object, gender_subj, gender_obj = dependency_collector(raw_data[0][0])

# leave space after punctuation -> fix this @crawling stage
data = raw_data[0][0].replace('!', '! ')
print("article:", data)

verbs_dictionary = important_verb_dict_spacy('δολοφονια')  # TODO: change this if article isn't murder

# all the verbs in the article
article_verbs = []
for v in verb:
    article_verbs.append({
        'raw': v,
        'analyzed': get_specific_analyzed(v)[0][0]
    })

# all the verbs in dictionary from elastic
elastic_dict_verbs = []
for v in verbs_dictionary:
    elastic_dict_verbs.append({
        'raw': v,
        'analyzed': get_specific_analyzed(v)[0][0]
    })

# all the matching from the above two
matched_verbs = [[v2['raw'] for v1 in elastic_dict_verbs for v2 in article_verbs if v1['analyzed'] == v2['analyzed']]]
print("Matched verbs:", set(matched_verbs[0]))

# break article to sentences and find object and subject only where matched verb is located
tokens = nltk.sent_tokenize(data)

important_sentences = []
for verb in set(matched_verbs[0]):
    for t in tokens:
        if verb in t:
            important_sentences.append(t)
            print("Article sentence:", t, "___", "verb matched:", verb)

# now get the subject and object of each of the important sentences
for sent in important_sentences:
    verb, subject, object_, gender_subj, gender_obj = dependency_collector(sent)
    if not subject == []:
        print("ΘΥΤΗΣ:", subject, "ΦΥΛΟ:", gender_subj)
    if not object_ == []:
        print("ΘΥΜΑ:", object_, "ΦΥΛΟ:", gender_obj)
