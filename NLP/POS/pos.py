import spacy
import regex as re
from elasticsearchapp.query_results import gather_raw_verbs, get_specific_analyzed, get_latest_raw_data
import nltk
from NLP.POS.patterns import victim_patterns
from spacy.matcher import Matcher
import random
from Levenshtein import distance

# nltk.download('punkt') # only run once
nlp = spacy.load('el_core_news_lg')

random.seed(30)

matcher = Matcher(nlp.vocab)
matcher.add("ΘΥΜΑ", victim_patterns)

VERBS_TO_EXCLUDE = ['φέρει', 'υποστήριξη', 'ανέφερε', 'Δείτε', 'ΔΕΙΤΕ']  # 'φέρεται', 'ανέφερε', 'είπαν'


def almost_match(s1, s2):
    """ catch lemmas like: δολοφονι/δολοφον as a match"""
    return distance(s1, s2) <= 1


def most_common(lst):
    lst = [i for i in lst if i]
    if not lst:
        return "ΑΓΝΩΣΤΟ"
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

    if type is "person":
        for token in doc:
            check = re.findall("Gender=[^|]*", token.tag_)
            # print(token.text, '->', token.pos_, token.dep_, check)
            if not check == []:
                if (token.pos_ == 'NOUN' and token.dep_ == 'nmod') or (token.pos_ == 'DET' and token.dep_ == 'det') or token.dep_ == 'dobj' or token.dep_ == 'obj' or token.dep_ == 'iobj' or token.dep_ == "nsubj" or token.dep_ == 'nsubj:pass':
                    # print(token.text, '---->', token.pos_, token.dep_, check[0].split("=")[1])
                    gender = check[0].split("=")[1]
                if gender == 'Masc': return "ΑΝΤΡΑΣ"
                elif gender == 'Fem': return "ΓΥΝΑΙΚΑ"
                elif gender == "Neut" and ('παιδί' in token.text or 'κορίτσι' in token.text or 'αγόρι' in token.text or 'μωρό' in token.text):
                    return "ΠΑΙΔΙ"
                elif gender == "Neut" and ('χρον' in token.text or 'άτομα' in token.text):
                    return token.text
    else:
        for token in doc:
            if len(token) > 4:  # skip and ignore small words, probably junk
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


def analyse_victim(raw_data, crime_type):
    """ get victim's gender """
    # get 1 article based on index given for testing
    # raw_data, raw_type = get_latest_raw_data(article_index=1, article_type='δολοφονια')  # todo: [1]
    verb, subject, object, gender_subj, gender_obj = dependency_collector(raw_data)

    # shorten sentences
    data = raw_data.replace('!', '. ').replace(":", '. ').replace(", ", '. ').replace("(", "").replace(")", "")
    print("Article:", data)

    verbs_dictionary = important_verb_dict_spacy(crime_type, 130)  # TODO: [2] queries only murder now, change

    # all the verbs in the article
    article_verbs = []
    status = "ΑΓΝΩΣΤΟ"
    for v in verb:
        if len(get_specific_analyzed(v)) > 0:
            article_verbs.append({
                'raw': v,
                'analyzed': get_specific_analyzed(v)[0][0]
            })
            if 'ομολόγ' in v or 'ομολογ' in v:
                status = "ΟΜΟΛΟΓΗΣΕ"
            if 'συνελήφθη' in v or 'φυλακίστηκε' in v or 'συλληφθεί' in v:
                status = "ΣΥΝΕΛΗΦΘΗ"

    # all the verbs in dictionary from elastic
    elastic_dict_verbs = []
    for v in verbs_dictionary:
        elastic_dict_verbs.append({
            'raw': v,
            'analyzed': get_specific_analyzed(v)[0][0]
        })

    # all the matching from the above two
    matched_verbs = [[v2['raw'] for v1 in elastic_dict_verbs for v2 in article_verbs if (v1['analyzed'] == v2['analyzed'] or almost_match(v1['analyzed'], v2['analyzed']))
                      and v2['raw'] not in VERBS_TO_EXCLUDE]]
    print("Elastic and article matching verbs:", set(matched_verbs[0]))

    # break article to sentences and find object and subject only where matched verb is located
    tokens = nltk.sent_tokenize(data)

    important_sentences = []
    for verb in set(matched_verbs[0]):
        for t in tokens:
            if verb in t:
                important_sentences.append(t)
                print("Article (Important) sentence:", t, "___", "verb matched:", verb)

    # POS Pattern matching based on important sentences and based on matching verbs
    victim_genders = []
    for sent in important_sentences:
        doc = nlp(sent)
        matches = matcher(doc)
        for match_id, start, end in matches:
            string_id = nlp.vocab.strings[match_id]
            span = doc[start:end]
            for verb in set(matched_verbs[0]):
                # print("VERB--", verb.lower(), "SPANTEXT--", span.text.lower())
                if verb.lower() in span.text.lower():
                    victim_gender = dependency_collector(span.text, type="person")
                    victim_genders.append(victim_gender)
                    print(string_id, span.text, "ΘΥΜΑ:", victim_gender)

    print("[1] ΘΥΜΑ:", most_common(victim_genders))
    print("[2] ΚΑΤΑΣΤΑΣΗ:", status)

    return important_sentences, most_common(victim_genders), status


# analyse_victim()

# doc = nlp("Υπόθεση δολοφονίας Λίνας Κοεμτζή.")
# for token in doc:
#     print(token.text, token.dep_, token.pos_)

# todo: train a NER for "PERSON" recognition and then apply the above POS on the sentence matching a "PERSON"  (?)
