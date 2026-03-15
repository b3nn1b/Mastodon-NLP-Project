import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from HanTa import HanoverTagger as ht
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from gensim.models import CoherenceModel
from gensim.corpora import Dictionary
import numpy as np

FILE = 'hamburg3.txt'

COHERENCE_SCORE='c_v'
#COHERENCE_SCORE='u_mass'
#COHERENCE_SCORE='c_npmi'
#COHERENCE_SCORE='c_uci'

EMBEDDING = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
#EMBEDDING = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
NR_TOPICS = 6
MIN_TOPIC_SIZE = 4

try:
    stopwords.words('german')
except LookupError:
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('wordnet')

def load_list_from_file(filename):
    data_list = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            data_list.append(line.rstrip('\n'))
    return data_list

def remove_stopwords(text_liste, sprache='german'):
    stoppwoerter = stopwords.words(sprache)
    filtered_list = []
    for text in text_liste:
        woerter = word_tokenize(text)
        gefilterte_woerter = [w.lower() for w in woerter if w.lower() not in stoppwoerter]
        filtered_list.append(" ".join(gefilterte_woerter))
    return filtered_list

def remove_stopwords_lemma(text_liste, sprache='german'):
    tagger = ht.HanoverTagger('morphmodel_ger.pgz')

    stoppwoerter = stopwords.words(sprache)
    filtered_list = []

    for text in text_liste:
        woerter = word_tokenize(text)
        gefilterte_woerter = []

        for w in woerter:
            if w.lower() not in stoppwoerter:
                tagged = tagger.tag_sent([w.lower()])
                if tagged:
                    lemma = tagged[0][1]
                    gefilterte_woerter.append(lemma)
                else:
                    gefilterte_woerter.append(w.lower())

        filtered_list.append(" ".join(gefilterte_woerter))

    return filtered_list

def get_topic_words(topic_model, topic_id, top_n=10):
    topic_words = topic_model.get_topic(topic_id)
    return [word for word, score in topic_words[:top_n]]

content = load_list_from_file(FILE)
#filtered_content = remove_stopwords(content)
lemma_content = remove_stopwords_lemma(content)

#print(filtered_content)
#print(lemma_content)

embedding_model = SentenceTransformer(EMBEDDING)
topic_model = BERTopic(
    language="german",
    embedding_model=embedding_model,
    nr_topics=NR_TOPICS,
    min_topic_size=MIN_TOPIC_SIZE,
    verbose=True
)
topics, probs = topic_model.fit_transform(lemma_content)

topic_anzahl = str(len(set(topics)))
print(f"Topic Anzahl: {topic_anzahl}")

#topic_words = topic_model.get_topic_info()

all_topics = []
for topic_id in range(len(topic_model.get_topic_info())-1):
    topic_words = get_topic_words(topic_model, topic_id, top_n=5)
    print(topic_id)
    print(topic_words)
    all_topics.append(topic_words)

print(all_topics)

content_list = [string.split() for string in lemma_content]
tokenized_docs = [doc.lower().split() for doc in lemma_content]
dictionary = Dictionary(content_list)

coherence_model = CoherenceModel(
    topics=all_topics,
    texts=tokenized_docs,
    dictionary=dictionary,
    coherence=COHERENCE_SCORE
)

coherence_score = coherence_model.get_coherence()

print(f"Coherence Score: {coherence_score}")

#top_words = get_topic_words(topic_model, 0, top_n=10)
#print(top_words)
#top_words = get_topic_words(topic_model, 1, top_n=10)
#print(top_words)
#top_words = get_topic_words(topic_model, 2, top_n=10)
#print(top_words)
#top_words = get_topic_words(topic_model, 3, top_n=10)
#print(top_words)
#top_words = get_topic_words(topic_model, 4, top_n=10)
#print(top_words)