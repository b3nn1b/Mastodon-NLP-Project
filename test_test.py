from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import gensim.corpora as corpora
from gensim.models.coherencemodel import CoherenceModel

FILE = 'hamburg1.txt'

#EMBEDDING = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
EMBEDDING = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
#EMBEDDING = 'all-MiniLM-L6-v2'
NR_TOPICS = "auto"
MIN_TOPIC_SIZE = 5

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

#topic_model = BERTopic(n_gram_range=(2, 3), min_topic_size=5)

embedding_model = SentenceTransformer(EMBEDDING)
topic_model = BERTopic(
    language="german",
    embedding_model=embedding_model,
    nr_topics=NR_TOPICS,  # Try with a small number first
    min_topic_size=MIN_TOPIC_SIZE,  # Minimum documents per topic
    verbose=True
)

topics, _ = topic_model.fit_transform(docs)

cleaned_docs = topic_model._preprocess_text(docs)
vectorizer = topic_model.vectorizer_model
analyzer = vectorizer.build_analyzer()
tokens = [analyzer(doc) for doc in cleaned_docs]

dictionary = corpora.Dictionary(tokens)
corpus = [dictionary.doc2bow(token) for token in tokens]

topics = topic_model.get_topics()
topics.pop(-1, None)
topic_words = [
    [word for word, _ in topic_model.get_topic(topic) if word != ""] for topic in topics
]
topic_words = [[words for words, _ in topic_model.get_topic(topic)]
    for topic in range(len(set(topics))-1)]

topic_anzahl = str(len(set(topics)))
print(f"Topic Anzahl: {topic_anzahl}")

for topic_id in range(len(topic_model.get_topic_info())-1):  # -1 für Outliers
    woerter = get_topic_words(topic_model, topic_id, top_n=10)
    print(topic_id)
    print(woerter)

# Evaluate
coherence_model = CoherenceModel(topics=topic_words,
    texts=tokens,
    corpus=corpus,
    dictionary=dictionary,
    coherence='c_v')

coherence_score = coherence_model.get_coherence()
print(f"Coherence Score: {coherence_score}")