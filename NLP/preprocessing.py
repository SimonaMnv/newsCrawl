import spacy
import re

nlp = spacy.load('el_core_news_lg')


def greek_lemmatizer(text):
    add_space_after_dot = r"\.(?=\S)"
    text = re.sub(add_space_after_dot, ". ", text)

    doc = nlp(text)
    sentences = list(doc.sents)
    print(sentences)
