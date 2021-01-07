import spacy

nlp = spacy.load('el_core_news_lg')


def greek_lemmatizer(text):
    doc = nlp(text)
    print([token.lemma_ for token in doc])

    # return lemmatized_words

text='αστυνομικοί αστυνομικούσ αστυνομικών'
print(greek_lemmatizer(text))