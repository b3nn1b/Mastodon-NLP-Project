import os
import pandas as pd
from typing import List, Dict, Tuple

from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN
from sentence_transformers import SentenceTransformer
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
import gensim.corpora as corpora
from gensim.models import CoherenceModel

FILE = 'hamburg5.txt'

EMBEDDING = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
#EMBEDDING = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
#EMBEDDING = 'all-MiniLM-L6-v2'
NR_TOPICS = None
MIN_TOPIC_SIZE = 8

try:
    stop_words = stopwords.words('german')
except LookupError:
    nltk.download('stopwords')
    stop_words = stopwords.words('german')

stop_words.append("hamburg")
stop_words.extend(stopwords.words('english'))

def load_list_from_file(filename):
    data_list = []
    with open(filename, 'r', encoding='utf-8') as f:  # 'r' für Lesen, encoding für Sonderzeichen
        for line in f:
            data_list.append(line.rstrip('\n'))  # Entfernt *nur* den Zeilenumbruch am Ende
    return data_list

def get_topic_words(topic_model, topic_id, top_n=10):
    """Topic Wörter pro Topic anzeigen"""
    words = topic_model.get_topic(topic_id)
    return [word for word, score in words[:top_n]]

docs = load_list_from_file(FILE)

vectorizer = CountVectorizer(
    stop_words=stop_words, # Stopwörter entfernen
    #max_df=0.9,            # Wörter ignorieren, die in >90% der Docs vorkommen (zu allgemein)
    min_df=2,              # Wörter ignorieren, die <2 mal vorkommen (zu selten)
    ngram_range=(1, 2),
    lowercase=True         # Alles klein schreiben
)

umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine', random_state=12)
#hdbscan_model = HDBSCAN(min_cluster_size=120, metric='euclidean', cluster_selection_method='eom', prediction_data=True)

embedding_model = SentenceTransformer(EMBEDDING)
topic_model = BERTopic(
    language="german",
    embedding_model=embedding_model,
    umap_model=umap_model,
    #hdbscan_model=hdbscan_model,
    vectorizer_model=vectorizer,
    nr_topics=NR_TOPICS,  # Try with a small number first
    min_topic_size=MIN_TOPIC_SIZE,  # Minimum documents per topic
    calculate_probabilities=True,
    verbose=True
)

topics, _ = topic_model.fit_transform(docs)

cleaned_docs = topic_model._preprocess_text(docs)
analyzer = vectorizer.build_analyzer()
tokens = [analyzer(doc) for doc in cleaned_docs]

dictionary = corpora.Dictionary(tokens)
corpus = [dictionary.doc2bow(token) for token in tokens]

topics = topic_model.get_topics()
topics.pop(-1, None)
topic_words = [
    [word for word, _ in topic_model.get_topic(topic) if word != ""]
    for topic in range(len(set(topics)))]

coherence_model = CoherenceModel(topics=topic_words,
    texts=tokens,
    corpus=corpus,
    dictionary=dictionary,
    coherence='c_v')

coherence_score = coherence_model.get_coherence()

topic_anzahl = str(len(set(topics)))
print(f"Topic Anzahl: {topic_anzahl}")

for topic_id in range(len(topic_model.get_topic_info())-1):  # -1 für Outliers
    woerter = get_topic_words(topic_model, topic_id, top_n=10)
    print(topic_id)
    print(woerter)

print(f"Coherence Score: {coherence_score}")