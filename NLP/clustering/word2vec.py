from gensim.models import Word2Vec
from nltk.cluster import KMeansClusterer
import nltk
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn import cluster
from sklearn import metrics
from custom_label_clustering import lala

# training data
sentences = lala

model = Word2Vec(sentences, min_count=1)


def sent_vectorizer(sent, model):
    sent_vec = []
    numw = 0
    for w in sent:
        try:
            if numw == 0:
                sent_vec = model[w]
            else:
                sent_vec = np.add(sent_vec, model[w])
            numw += 1
        except:
            pass

    return np.asarray(sent_vec) / numw


X = []
for sentence in sentences:
    X.append(sent_vectorizer(sentence, model))

print(model[model.wv.vocab])

# print(model.similarity('γραμμαρ', 'αυτοκτον'))
# print(model.most_similar(positive=['γραμμαρ'], negative=[], topn=2))

NUM_CLUSTERS = 5
kclusterer = KMeansClusterer(NUM_CLUSTERS, distance=nltk.cluster.util.cosine_distance, repeats=25)
assigned_clusters = kclusterer.cluster(X, assign_clusters=True)
print(assigned_clusters)

for index, sentence in enumerate(sentences):
    print(str(assigned_clusters[index]) + ":" + str(sentence))

kmeans = cluster.KMeans(n_clusters=NUM_CLUSTERS)
kmeans.fit(X)

labels = kmeans.labels_
centroids = kmeans.cluster_centers_

print("Cluster id labels for inputted data")
print(labels)
print("Centroids data")
print(centroids)

print(
    "Score (Opposite of the value of X on the K-means objective which is Sum of distances of samples to their closest "
    "cluster center):")
print(kmeans.score(X))

silhouette_score = metrics.silhouette_score(X, labels, metric='euclidean')

print("Silhouette_score: ")
print(silhouette_score)

model = TSNE(n_components=2, random_state=0)
np.set_printoptions(suppress=True)

Y = model.fit_transform(X)

plt.scatter(Y[:, 0], Y[:, 1], c=assigned_clusters, s=290, alpha=.5)

for j in range(len(sentences)):
    plt.annotate(assigned_clusters[j], xy=(Y[j][0], Y[j][1]), xytext=(0, 0), textcoords='offset points')
    print("%s %s" % (assigned_clusters[j], sentences[j]))

plt.show()