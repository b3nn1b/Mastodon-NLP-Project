import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from bertopic import BERTopic
import plotly.graph_objects as go

try:
    stopwords.words('german')
except LookupError:
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('punkt_tab')

def load_list_from_file(filename):
    data_list = []
    with open(filename, 'r', encoding='utf-8') as f:  # 'r' für Lesen, encoding für Sonderzeichen
        for line in f:
            data_list.append(line.rstrip('\n'))  # Entfernt *nur* den Zeilenumbruch am Ende
    return data_list

def remove_stopwords(text_liste, sprache='german'):
    stoppwoerter = stopwords.words(sprache)
    filtered_list = []
    for text in text_liste:
        woerter = word_tokenize(text)
        gefilterte_woerter = [w.lower() for w in woerter if w.lower() not in stoppwoerter]
        filtered_list.append(" ".join(gefilterte_woerter))
    return filtered_list

content = load_list_from_file('content.txt')
filtered_content = remove_stopwords(content)

topic_model = BERTopic(language="german", nr_topics="auto")
topics, probs = topic_model.fit_transform(filtered_content)

#fig = topic_model.visualize_topics()
#fig.write_html("topics.html")

#print(topic_model.get_topic_info())
print(topic_model.get_topic(1))
print(topic_model.get_topic(2))
print(topic_model.get_topic(3))
print(topic_model.get_topic(4))
print(topic_model.get_topic(5))