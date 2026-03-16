from bs4 import BeautifulSoup
import re
import mastodon
import time
from credentials import MASTODON_INSTANCE
from credentials import ACCESS_TOKEN
from bertopic import BERTopic
from umap import UMAP
from sentence_transformers import SentenceTransformer
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
import gensim.corpora as corpora
from gensim.models import CoherenceModel

HASHTAG = "hamburg" # Ohne #
TOOTS = 1000        # Anzahl der zu ladenden Toots

# BERTopic Parameter
EMBEDDING = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
#EMBEDDING = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
#EMBEDDING = 'all-MiniLM-L6-v2'
NR_TOPICS = None        # Topic Anzahl nicht vorgeben
MIN_TOPIC_SIZE = 20     # Topic Mindestgröße
N_NEIGHBORS = 50        # Anzahl Nachbarn
MIN_DIST = 0.05         # Entfernung zwischen Punkten

# HTML Code und URLs entfernen
def remove_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # HTML
    text = soup.get_text()
    # URLs
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    text = url_pattern.sub('', text)
    # Leerzeichen und Zeilenumbrüche
    text = re.sub(r'\s+', ' ', text).strip()
    # Leerzeichen zwischen Klein- und Großbuchstaben einfügen
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    # Leerzeichen nach Satzzeichen einfügen
    text = re.sub(r'\.(?=\w)', '. ', text)
    text = re.sub(r',(?=\w)', ', ', text)
    return text

# Topic Wörter pro Topic anzeigen
def get_topic_words(topic_model, topic_id, top_n=10):
    words = topic_model.get_topic(topic_id)
    return [word for word, score in words[:top_n]]

# Stopwörterliste erstellen
try:
    stop_words = stopwords.words('german')
except LookupError:
    nltk.download('stopwords')
    stop_words = stopwords.words('german')

stop_words.append(HASHTAG)   # HASHTAG wird als Stopwort eingetragen um in den Topics nicht aufzutauchen
stop_words.extend(stopwords.words('english'))

# Mastodon initialisieren
try:
    masto = mastodon.Mastodon(
        access_token = ACCESS_TOKEN,
        api_base_url = MASTODON_INSTANCE
    )

except Exception as e:
    print(f"Fehler bei der Mastodon Verbindung: {e}")
    exit()

# Toots laden
all_toots = []
max_id = None
limit = 40  # Limit pro Abfrage
total_to_fetch = TOOTS  # Anzahl der Toots
toots_fetched = 0

try:
    print("Mastodon Toots laden...")
    toots = masto.timeline_hashtag(
        hashtag=HASHTAG,
        limit=limit
    )

    if not toots:
        print("Keine Toots gefunden.")
        exit()

    all_toots.extend(toots)
    toots_fetched += len(toots)
    max_id = toots[-1]['id']
    rounds = 1
    print("Durchgang 1 fertig")

    # Weitere Durchgänge
    while len(all_toots) < total_to_fetch:
        if toots_fetched >= 280:    # Rate Limit beträgt 300 pro 5 Minuten
            print("Rate Limit erreicht. Warte 5 Minuten...")
            time.sleep(300)
            toots_fetched = 0

        more_toots = masto.timeline_hashtag(
            hashtag=HASHTAG,
            limit=limit,
            max_id=max_id
        )

        if not more_toots:
            break

        all_toots.extend(more_toots)
        toots_fetched += len(more_toots)
        max_id = more_toots[-1]['id']
        rounds += 1
        print(f"Durchgang {rounds} fertig")

        if len(all_toots) >= total_to_fetch:
            all_toots = all_toots[:total_to_fetch]
            print(f"{len(all_toots)} Toots in {rounds} Durchgängen geladen")
            break
except Exception as e:
    print(f"Fehler in Mastodon Abfrage: {e}")
    exit()

# Daten verarbeiten
try:
    data = []
    for toot in all_toots:
        data.append({
            'content': remove_html(toot['content']),
        })

    docs = []
    for item in data:
        docs.append(item['content'])

except Exception as e:
    print(f"Fehler bei Vorverarbeitung: {e}")
    exit()

# Topics mit BERTopic extrahieren
try:
    print("BERTopic Analyse...")
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