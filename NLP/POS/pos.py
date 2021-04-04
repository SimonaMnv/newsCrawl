import string
import spacy
import regex as re
from elasticsearchapp.query_results import gather_raw_verbs, get_specific_analyzed
import nltk
from NLP.POS.patterns import victim_patterns
from spacy.matcher import Matcher
import random
import unicodedata as ud

# nltk.download('punkt') # only run once
nlp = spacy.load('el_core_news_lg')

random.seed(30)

matcher = Matcher(nlp.vocab)
matcher.add("ΘΥΜΑ", victim_patterns)

VERBS_TO_EXCLUDE = ['φέρει', 'υποστήριξη', 'ανέφερε', 'Δείτε', 'ΔΕΙΤΕ', 'γωνία', 'φορές', 'κακούς', 'δηλώσει', 'κανείς',
                    'ειδικού', 'gr', 'σπιτι', '2018', 'ελενης', 'star', 'δικηγορος', 'βιντεο', 'πηγε', 'λογο', 'πει',
                    'παει', 'φορά', 'είπαν', 'δήλωση', 'κάνει', 'φαινόνταν']

FEMALE_VICTIMS = ['φοιτήτρια', 'γυναίκα', 'γυναίκ', 'μητέρα', 'κορίτσ', 'φοιτήτ', 'κοπέλ', 'χρονη', 'κόρη', 'οποία']
MALE_VICTIMS = ['φοιτητή', 'άντρ', 'πατέρα', 'χρονος', 'αγόρ', 'χρονου', 'Πακιστανός', 'Έλληνας', 'τον', 'Αλβανό']
NEUTRAL_VICTIMS = ['παιδί', 'παιδιά', 'μωρό', 'κόρη', 'χρονο', 'αδελφούλες', 'κοριτσάκ', 'αγοράκ']


def remove_similar(string_list):
    unique_lst = set(i for i in string_list if not any(i in s for s in string_list if i != s))
    return unique_lst


def most_common(lst):
    lst = [i for i in lst if i]
    if not lst:
        return "ΑΓΝΩΣΤΟ"
    return max(set(lst), key=lst.count)


def custom_NER_analysis(sentence):
    sentence = sentence.replace('!', '. ').replace(":", '. ').replace(", ", '. ').replace("(", "").replace(")", "") \
        .replace("-", ". ").replace("–", ". ")

    nlp = spacy.load('../../NLP/NER/custom_model')     # custom NER
    nlp.add_pipe(nlp.create_pipe('sentencizer'))  # updated
    doc = nlp(sentence)

    nlp2 = spacy.load('el_core_news_lg')  # the default NER too, for specific person
    nlp2.add_pipe(nlp2.create_pipe('sentencizer'))  # updated
    doc2 = nlp2(sentence)

    specific_person = [e.string.strip() for e in doc2.ents if e.label_ == 'PERSON']

    location = [e.string.strip() for e in doc2.ents if e.label_ == 'GPE']

    act = [e.string.strip() for e in doc.ents if e.label_ == 'ΠΡΑΞΗ']

    sentences = [sent.string.strip() for sent in doc.sents for word in sent.string.strip().split(" ") if
                 word.translate(str.maketrans('', '', string.punctuation)).replace("«", "").replace("»", "") in act]

    age = [e.string.strip() for e in doc.ents if e.label_ == 'ΗΛΙΚΙΑ']

    sentences.extend([sent.string.strip() for sent in doc.sents for word in sent.string.strip().split(" ") if
                      word.translate(str.maketrans('', '', string.punctuation)).replace("«", "").replace("»",
                                                                                                         "") in age])

    date = [e for e in doc.ents if e.label_ == 'ΗΜΕΡΟΜΗΝΙΑ']

    return remove_similar(act), remove_similar(age), date, sentences, remove_similar(specific_person), remove_similar(location)


def find_verbs(sentences):
    important_verbs = []

    for sentence in sentences:
        doc = nlp(sentence)
        for token in doc:
            if token.pos_ == "VERB":
                important_verbs.append(token.text)

    return important_verbs


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
        # 1. text mining scenario
        matched_female_victims = [female for female in FEMALE_VICTIMS if female in doc.text]
        matched_male_victims = [male for male in MALE_VICTIMS if male in doc.text]
        matched_neutral_victims = [child for child in NEUTRAL_VICTIMS if child in doc.text]
        if matched_female_victims: return "ΓΥΝΑΙΚΑ"
        if matched_male_victims: return "ΑΝΤΡΑΣ"
        if matched_neutral_victims: return "ΠΑΙΔΙ"

        # 2. fallback strategy
        for token in doc:
            check = re.findall("Gender=[^|]*", token.tag_)
            # print(token.text, '->', token.pos_, token.dep_, check)
            if not check == []:
                if token.dep == 'nmod' or token.pos_ == 'DET' or token.dep_ == 'iobj':
                    # print(token.text, '---->', token.pos_, token.dep_, check[0].split("=")[1])
                    gender = check[0].split("=")[1]
                if gender == 'Masc':
                    return "ΑΝΤΡΑΣ"
                elif gender == 'Fem':
                    return "ΓΥΝΑΙΚΑ"
                elif gender == "Neut" and (
                        'παιδί' in token.text or 'κορίτσι' in token.text or 'αγόρι' in token.text or 'μωρό' in token.text):
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

        return verb, subject, object, gender_subject, gender_object


def analyse_victim(raw_data, crime_type):
    """ get victim's gender """
    verb, subject, object, gender_subj, gender_obj = dependency_collector(raw_data)

    act, age, date, extra_important_sentence, specific_person, location = custom_NER_analysis(raw_data)
    extra_important_sentence_verbs = find_verbs(extra_important_sentence)

    # shorten sentences
    data = raw_data.replace('!', '. ').replace(":", '. ').replace(", ", '. ').replace("(", "").replace(")", "") \
        .replace("-", ". ").replace("–", ". ").replace(";", ". ").replace("...", ". ")
    print("Article:", data)

    verbs_dictionary = important_verb_dict_spacy(crime_type, 20)

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
            if 'συνελήφθη' in v or 'φυλακίστηκε' in v or 'συλληφθεί' in v or 'συνέλαβαν' in v:
                status = "ΣΥΝΕΛΗΦΘΗ"

    # all the verbs in dictionary from elastic
    elastic_dict_verbs = []
    for v in verbs_dictionary:
        doc_v = nlp(v)
        for token in doc_v:
            if token.pos_ == "VERB":
                elastic_dict_verbs.append({
                    'raw': token.text,
                    'analyzed': get_specific_analyzed(token.text)[0][0]
                })

    # all the matching from the above two
    matched_verbs = [v2['raw'] for v1 in elastic_dict_verbs for v2 in article_verbs if
                     (v1['analyzed'] == v2['analyzed'])
                     and v2['raw'] not in VERBS_TO_EXCLUDE]
    print("Elastic and article matching verbs:", set(matched_verbs))

    # break article to sentences and find object and subject only where matched verb is located
    tokens = nltk.sent_tokenize(data)

    important_sentences = []
    for verb in set(matched_verbs):
        for t in tokens:
            if verb in t:
                important_sentences.append(t)

    victim_genders = []
    if important_sentences == []:
        important_sentences.extend(extra_important_sentence)
        matched_verbs.extend(extra_important_sentence_verbs)
    for sent in important_sentences:
        doc = nlp(sent)
        print("Important Sentences:", doc)
        # POS Pattern matching based on important sentences and based on matching verbs
        matches = matcher(doc)
        for match_id, start, end in matches:
            string_id = nlp.vocab.strings[match_id]
            span = doc[start:end]
            # for verb in set(matched_verbs):
            # print("VERB--", verb.lower(), "SPANTEXT--", span.text.lower())
            # if verb.lower() in span.text.lower():
            victim_gender = dependency_collector(span.text, type="person")
            victim_genders.append(victim_gender)
            print(string_id, span.text, "ΘΥΜΑ:", victim_gender)

    print("[1] ΘΥΜΑ:", most_common(victim_genders))
    print("[2] ΚΑΤΑΣΤΑΣΗ:", status)
    print("[3] ΠΡΑΞΕΙΣ:", act)
    print("[4] ΗΛΙΚΙΕΣ:", age)
    print("[5] ΗΜΕΡΟΜΗΝΙΑ:", date)
    print("[6] ΠΡΟΣΩΠΑ:", specific_person)
    print("[5] ΤΟΠΟΘΕΣΙΑ:", location)

    return important_sentences, most_common(victim_genders), status, act, age, date, specific_person, location


# analyse_victim("ο άντρας χτύπησε την γυναίκα", 'δολοφονια')

# doc = nlp("Μυστήριο με τη δολοφονία Ινδού Τραγική κατάληξη είχε η απαγωγή ενός 44χρονου Ινδού στο Ρέθυμνο")
# for token in doc:
#     print(token.text, token.dep_, token.pos_)
