# Mastodon Topic Analysis mit BERTopic

Dieses Python-Skript dient dazu, Toots von Mastodon basierend auf einem bestimmten Hashtag zu sammeln, die Textdaten vorzuverarbeiten und mithilfe von BERTopic eine Themenmodellierung durchzuführen. Das Ergebnis ist eine Auflistung der wichtigsten Themen im gesammelten Datensatz sowie die Angabe des Coherence Scores für diese Themen.

## Funktionen

- Laden von Toots welche einen bestimmten Hashtag enthalten
- Vorverarbeitung der Texte (Entfernung von HTML und URLs)
- Themenextraktion mit BERTopic
- Berechnung des Coherence Scores zur Bewertung der Themenqualität
- Speicherung der Ergebnisse in einer Textdatei

## Voraussetzungen

Der Code wurde mit **Python 3.13** getestet.  
Es wird eine **credentials.py** benötigt, welche die Mastodon Instanz und den Access Token enthält:

*   MASTODON_INSTANCE = "mastodon.instanz"
*   ACCESS_TOKEN = "API_TOKEN_XXXXXXXXXXXXXX"

Folgende externe Pakete werden verwendet:

*   `beautifulsoup4` (HTML-Cleaning)
*   `mastodon.py` (Mastodon API Schnittstelle)
*   `bertopic` (Themenmodellierung)
*   `umap-learn` (Dimensionalitätsreduktion für BERTopic)
*   `sentence-transformers` (Bert-Baselines für Embeddings)
*   `nltk` (Textverarbeitung/Stopwords)
*   `scikit-learn` (Vektorisierung)
*   `gensim` (Coherence Berechnung)

## Ausführung

```bash
python main.py
```

Alternativ können die Toots mit Scraper.py abgerufen und in einer Datei gespeichert werden.  
Anschließend kann die Topic Analyse mit Analyzer.py durchgeführt werden.  

## Konfigurationsparameter

| Parameter        | Beschreibung                                    | Standardwert |
|------------------|-------------------------------------------------|--------------|
| `HASHTAG`        | Der zu analysierende Hashtag                    | `"hamburg"`  |
| `TOOTS`          | Anzahl der zu ladenden Toots                    | `1000`       |
| `EMBEDDING`      | Embedding-Modell für BERTopic                   | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| `NR_TOPICS`      | Vorgabe der Anzahl der Topics                   | `None`       |
| `MIN_TOPIC_SIZE` | Mindestgröße pro Topic                          | `20`         |
| `N_NEIGHBORS`    | Anzahl der betrachteten "Nachbarn" im Embedding | `50`         |
| `MIN_DIST`       | Mindestabstand zwischen Punkten im Embedding    | `0.05`       |

## Ausgabe

Nach erfolgreicher Ausführung werden die wichtigsten fünf Topics sowie der Coherence Score im Terminal ausgegeben.  
Die gesamte Liste aller erfassten Topics wird in topic_results.txt gespeichert.