from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

all_textall_text = """"
 Google and Facebook are strangling the free press to death. Democracy is the loserGoogle an
Your 60-second guide to security stuff Google touted today at Next '18
A Guide to Using Android Without Selling Your Soul to Google
Review: Lenovo’s Google Smart Display is pretty and intelligent
Google Maps user spots mysterious object submerged off the coast of Greece - and no-one knows what it is
Android is better than IOS
In information retrieval, tf–idf or TFIDF, short for term frequency–inverse document frequency
is a numerical statistic that is intended to reflect
how important a word is to a document in a collection or corpus.
It is often used as a weighting factor in searches of information retrieval
text mining, and user modeling. The tf-idf value increases proportionally
to the number of times a word appears in the document
and is offset by the frequency of the word in the corpus
""".split("\n")[1:-1]

tfidf_vectorizer = TfidfVectorizer()
tfidf = tfidf_vectorizer.fit_transform(all_textall_text)

kmeans = KMeans(n_clusters=2).fit(tfidf)

lines_for_predicting = ["tf and idf is awesome!", "some androids is there"]
print(kmeans.predict(tfidf_vectorizer.transform(lines_for_predicting)))
