import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

try:
    stopwords.words('german')
except LookupError:
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('punkt_tab')

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

content = load_list_from_file('../content.txt')
filtered_content = remove_stopwords(content)
print(filtered_content)

def save_list_to_file(data_list, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data_list:
            f.write(item + '\n')

save_list_to_file(filtered_content, 'contentstop.txt')

