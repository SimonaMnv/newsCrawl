import spacy
import random
from spacy.util import minibatch, compounding

nlp = spacy.load('el_core_news_lg')
ner = nlp.get_pipe("ner")

# training data
from doccano_to_spacy import TRAIN_DATA

# Adding labels to the `ner`
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# Disable pipeline components you dont need to change
pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
unaffected_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]


def model_train():
    # TRAINING THE MODEL
    with nlp.disable_pipes(*unaffected_pipes):

        # Training for 30 iterations
        for iteration in range(30):

            # shuffling examples  before every iteration
            random.shuffle(TRAIN_DATA)
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(
                    texts,  # batch of texts
                    annotations,  # batch of annotations
                    drop=0.5,  # dropout - make it harder to memorise data
                    losses=losses,
                )
                print("Losses", losses)


def model_test():
    # Testing the model
    doc = nlp("ο 16χρονος δράστης")
    print("Entities", [(ent.text, ent.label_) for ent in doc.ents])


model_train()
model_test()
