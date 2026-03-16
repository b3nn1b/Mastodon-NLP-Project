from bertopic import BERTopic
from umap import UMAP
from sentence_transformers import SentenceTransformer
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
import gensim.corpora as corpora
from gensim.models import CoherenceModel

FILE = 'hamburg.txt' # Mit Scraper extrahierte Toots
HASHTAG = "hamburg" # Ohne #

# BERTopic Parameter
EMBEDDING = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
#EMBEDDING = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
#EMBEDDING = 'all-MiniLM-L6-v2'
NR_TOPICS = None        # Topic Anzahl nicht vorgeben
MIN_TOPIC_SIZE = 20     # Topic Mindestgröße
N_NEIGHBORS = 50        # Anzahl Nachbarn
MIN_DIST = 0.05         # Entfernung zwischen Punkten

# Stopwörterliste erstellen
try:
    stop_words = stopwords.words('german')
except LookupError:
    nltk.download('stopwords')
    stop_words = stopwords.words('german')

stop_words.append(HASHTAG)   # HASHTAG wird als Stopwort eingetragen um in den Topics nicht aufzutauchen
stop_words.extend(stopwords.words('english'))

# Toots aus Datei laden
def load_list_from_file(filename):
    data_list = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            data_list.append(line.rstrip('\n'))
    return data_list

# Topic Wörter pro Topic anzeigen
def get_topic_words(topic_model, topic_id, top_n=10):
    words = topic_model.get_topic(topic_id)
    return [word for word, score in words[:top_n]]

docs = load_list_from_file(FILE)    # Datei laden

# Topics mit BERTopic extrahieren
try:
    vectorizer = CountVectorizer(
        stop_words=stop_words,
        min_df=2,              # Wörter ignorieren, die <2 mal vorkommen
        ngram_range=(1, 2),    # Bigramme
        lowercase=True         # Nur Kleinschreibung
    )

    umap_model = UMAP(n_neighbors=N_NEIGHBORS, n_components=5, min_dist=MIN_DIST, metric='cosine', random_state=12)
    embedding_model = SentenceTransformer(EMBEDDING)
    topic_model = BERTopic(
        language="german",
        embedding_model=embedding_model,
        umap_model=umap_model,
        vectorizer_model=vectorizer,
        nr_topics=NR_TOPICS,
        min_topic_size=MIN_TOPIC_SIZE,
        calculate_probabilities=True,
        #verbose=True
    )

    topics, _ = topic_model.fit_transform(docs)

except Exception as e:
    print(f"Fehler bei BERTopic Verarbeitung: {e}")
    exit()

# Coherence Score berechnen
try:
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

except Exception as e:
    print(f"Fehler bei der Coherence Score Berechnung: {e}")
    exit()

# Ausgabe
try:
    topic_info = topic_model.get_topic_info()
    topic_info = topic_info[topic_info['Topic'] != -1]

    print("\n" + "="*35)
    print("            Ergebnis")
    print("="*35)

    print(f"Gesamtanzahl gefundener Topics: {len(topic_info)}")
    print(f"Coherence Score: {coherence_score:.5f}")
    print("Top 5 Topics:")

    top5count = 0
    for _, row in topic_info.iterrows():
        top5count += 1
        topic_id = row['Topic']
        topic_words = get_topic_words(topic_model, topic_id, top_n=10)
        print(f"\nTopic {topic_id + 1} (In {row['Count']} Toots enthalten)")
        print("  ", ", ".join(topic_words))
        if top5count == 5:
            break

    with open("topic_results.txt", "w", encoding="utf-8") as f:
        f.write("BERTopic Ergebnis\n")
        f.write("="*35 + "\n")
        f.write(f"Gesamtanzahl gefundener Topics: {len(topic_info)}\n")
        f.write(f"Coherence Score: {coherence_score:.5f}\n\n")
        f.write(f"Topics:\n\n")
        for _, row in topic_info.iterrows():
            topic_id = row['Topic']
            topic_words = get_topic_words(topic_model, topic_id, top_n=10)
            f.write(f"Topic {topic_id + 1} (In {row['Count']} Toots enthalten)\n")
            f.write("  " + ", ".join(topic_words) + "\n\n")

    print("\nAlle Ergebnisse in topic_results.txt geschrieben")

except Exception as e:
    print(f"Fehler bei der Ausgabe: {e}")
    exit()