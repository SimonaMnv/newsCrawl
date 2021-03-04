import spacy
import regex as re
from elasticsearchapp.query_results import gather_raw_verbs, get_specific_analyzed, get_latest_raw_data
import nltk
from spacy.matcher import Matcher

# nltk.download('punkt') # only run once
nlp = spacy.load('el_core_news_lg')

matcher = Matcher(nlp.vocab)
patterns = [
    [{"POS": "NOUN"}, {"DEP": "det"}, {"DEP": "nmod"}],
    [{"POS": "NOUN"}, {"DEP": "det"}, {"POS": "X"}],
    [{"POS": "NOUN"}, {"POS": "NUM"}, {"POS": "NOUN"}],
    [{"POS": "NOUN"}, {"POS": "NUM"}, {"POS": "ADJ"}],
    [{"POS": "NOUN"}, {"DEP": "det"}, {"POS": "ADJ"}, {"POS": "NOUN"}],
    [{"POS": "NOUN"}, {"DEP": "det"}, {"POS": "ADJ"}],
    [{"POS": "VERB"}, {"POS": "NUM"}, {"POS": "NOUN"}],
    [{"POS": "NOUN"}, {"DEP": "det"}, {"POS": "NUM"}, {"POS": "NOUN"}],
    [{"POS": "VERB"}, {"POS": "CCONJ"}, {"POS": "VERB"}, {"POS": "NUM"}, {"POS": "NOUN"}],
    [{"POS": "VERB"}, {"POS": "DET"}, {"POS": "NOUN"}, {"POS": "DET"}, {"POS": "X"}],
    [{"POS": "VERB"}, {"POS": "DET"}, {"POS": "NOUN"}, {"POS": "DET"}, {"POS": "NOUN"}],
    [{"POS": "DET"}, {"POS": "NOUN"}, {"POS": "DET"}, {"POS": "VERB"}],
    [{"POS": "DET"}, {"POS": "NOUN"}, {"POS": "PRON"}, {"POS": "VERB"}],
    [{"POS": "VERB"}, {"POS": "DET"}, {"POS": "ADJ"}, {"POS": "NOUN"}],
    [{"POS": "VERB"}, {"POS": "DET"}, {"POS": "NOUN"}, {"POS": "PRON"}],
    [{"POS": "VERB"}, {"POS": "DET"}, {"POS": "PROPN"}],

]
matcher.add("ΘΥΜΑ", patterns)

VERBS_TO_EXCLUDE = ['φέρει', 'υποστήριξη', 'ανέφερε']  # 'φέρεται', 'ανέφερε', 'είπαν'


def most_common(lst):
    return max(set(lst), key=lst.count)


def important_verb_dict_spacy(type, thres):
    # take the important verbs from all articles from elastic based on type
    important_verbs = []

    important_terms = gather_raw_verbs(type=type, threshold=thres)
    for term in important_terms:
        doc = nlp(term[0])
        for token in doc:
            if token.pos_ == "VERB":
                important_verbs.append(token.text)

    return important_verbs


def dependency_collector(article, type=None):
    # https://explosion.ai/demos/displacy
    doc = nlp(article)
    subject = []
    object = []
    verb = []
    gender_subject = []
    gender_object = []
    gender = "ΑΓΝΩΣΤΟ"

    if type is "victim":
        for token in doc:
            # print(token.text, '->', token.pos_, token.dep_)
            check = re.findall("Gender=[^|]*", token.tag_)
            if not check == []:
                if not check[0] == 'Gender=Neut':
                    if token.dep_ == 'dobj' or token.dep_ == 'obj' or token.dep_ == "det" or token.dep_ == "nsubj":
                        gender = check[0].split("=")[1]
            if 'κορίτ' in token.text: gender = "Κορίτσι"
            if 'αγόρ' in token.text: gender = "Αγόρι"
            if 'παιδί' in token.text: gender = "Παιδί"
            if gender == 'Masc': gender = "ΑΝΤΡΑΣ"
            if gender == 'Fem': gender = "ΓΥΝΑΙΚΑ"
        return gender
    else:
        for token in doc:
            if len(token) > 4:  # skip and ignore small words, probably junk
                # extract verb
                if token.pos_ == 'VERB':
                    verb.append(token.text)

                check = re.findall("Gender=[^|]*", token.tag_)
                if not check == []:
                    if not check[0] == 'Gender=Neut':
                        # extract subject
                        if token.dep_ == 'nsubj' or token.dep_ == 'iobj':  # or token.dep_ == 'conj':
                            gender_subject.append(re.findall("Gender=[^|]*", token.tag_))
                            subject.append(token.text)
                        # extract object
                        if token.dep_ == 'dobj' or token.dep_ == 'obj':
                            gender_object.append(re.findall("Gender=[^|]*", token.tag_))
                            object.append(token.text)

                    verb.append(token.text)

    return verb, subject, object, gender_subject, gender_object


# get 1 article based on index given for testing
raw_data, raw_type = get_latest_raw_data(article_index=9, article_type='δολοφονια')
verb, subject, object, gender_subj, gender_obj = dependency_collector(raw_data[0][0])

# leave space after punctuation
data = raw_data[0][0].replace('!', '. ').replace(":", '. ')
print("article:", data)

verbs_dictionary = important_verb_dict_spacy('δολοφονια', 100)  # TODO: change this if article isn't murder

# all the verbs in the article
article_verbs = []
status = "ΑΓΝΩΣΤΟ"
for v in verb:
    if len(get_specific_analyzed(v)) > 0:
        article_verbs.append({
            'raw': v,
            'analyzed': get_specific_analyzed(v)[0][0]
        })
        if 'ομολόγησε' in v or 'συνελήφθη' in v or 'φυλακίστηκε' in v:
            status = "ΣΥΝΕΛΗΦΘΗ"

# all the verbs in dictionary from elastic
elastic_dict_verbs = []
for v in verbs_dictionary:
    elastic_dict_verbs.append({
        'raw': v,
        'analyzed': get_specific_analyzed(v)[0][0]
    })

# all the matching from the above two
matched_verbs = [[v2['raw'] for v1 in elastic_dict_verbs for v2 in article_verbs if v1['analyzed'] == v2['analyzed']
                  and v2['raw'] not in VERBS_TO_EXCLUDE]]
print("Elastic keywords and article matching verbs:", set(matched_verbs[0]))

# break article to sentences and find object and subject only where matched verb is located
tokens = nltk.sent_tokenize(data)

important_sentences = []
for verb in set(matched_verbs[0]):
    for t in tokens:
        if verb in t:
            important_sentences.append(t)
            print("Article (Important) sentence:", t, "___", "verb matched:", verb)

# POS Pattern matching based on important sentences and based on matching verbs
genders = []
for sent in important_sentences:
    doc = nlp(sent)
    # dependency_collector(sent, type="victim")
    matches = matcher(doc)
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]
        span = doc[start:end]
        matching_verbs = set(matched_verbs[0])
        for verb in matching_verbs:
            # print("VERB--", verb.lower(), "SPANTEXT--", span.text.lower())
            if verb.lower() in span.text.lower():
                gender = dependency_collector(span.text, type="victim")
                genders.append(gender)
                print(string_id, span.text, "ΦΥΛΟ:", gender)

print("[1] ΦΥΛΟ ΘΥΜΑΤΟΣ:", most_common(genders))
print("[3] ΚΑΤΑΣΤΑΣΗ:", status)
