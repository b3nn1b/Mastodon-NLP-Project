from bs4 import BeautifulSoup
import re
import mastodon
from bertopic import BERTopic
from sklearn.datasets import fetch_20newsgroups
from credentials import MASTODON_INSTANCE
from credentials import ACCESS_TOKEN
from credentials import HASHTAG

# Nur HTML entfernen
def remove_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    text_content = []
    for p in soup.find_all('p'):
        text = p.get_text()
        text = re.sub(r'\s+', ' ', text).strip()
        if text:
            text_content.append(text)

    return ' '.join(text_content)

def remove_html_urls(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    text_content = []
    for p in soup.find_all('p'):
        text = p.get_text()
        text = re.sub(r'\s+', ' ', text).strip()
        text = url_pattern.sub('', text)  # URLs entfernen
        if text:
            text_content.append(text)
    return ' '.join(text_content)

# Initialisieren
masto = mastodon.Mastodon(
    access_token = ACCESS_TOKEN,
    api_base_url = MASTODON_INSTANCE
)
# Variablen für Pagination
all_toots = []
max_id = None
limit = 40  # Max allowed per request
total_to_fetch = 200  # Total number of toots you want to fetch

try:
    # Fetch first batch
    toots = masto.timeline_hashtag(
        hashtag=HASHTAG,
        limit=limit
    )

    if not toots:
        print("Keine Toots gefunden.")
        exit()

    all_toots.extend(toots)
    max_id = toots[-1]['id']
    print("Erster Durchgang fertig")

    # Fetch additional batches
    while len(all_toots) < total_to_fetch:
        more_toots = masto.timeline_hashtag(
            hashtag=HASHTAG,
            limit=limit,
            max_id=max_id
        )

        if not more_toots:
            break

        all_toots.extend(more_toots)
        max_id = more_toots[-1]['id']
        print("Weiterer Durchgang")

        # Stop if we have enough toots
        if len(all_toots) >= total_to_fetch:
            all_toots = all_toots[:total_to_fetch]
            print("Alle Durchgänge erledigt")
            break
except Exception as e:
    print(f"Fehler beim Abrufen: {e}")
    exit()

# Daten verarbeiten
try:
    data_roh = []
    for toot in all_toots:
        data_roh.append({
            'id': toot['id'],
            'content': toot['content'],
        })

    data_1 = []
    for toot in all_toots:
        data_1.append({
            'id': toot['id'],
            'content': remove_html(toot['content']),
        })

    data_2 = []
    for toot in all_toots:
        data_2.append({
            'id': toot['id'],
            'content': remove_html_urls(toot['content']),
        })

except Exception as e:
    print(f"Fehler beim Verarbeiten: {e}")
    exit()

# Daten Speichern
try:
    with open("Toots_roh.txt", 'w', encoding='utf-8') as f:
        for i, toot in enumerate(data_roh, 1):
            f.write(f"Toot #{i}\n")
            #f.write(f"Author: {toot['author']}\n")
            #f.write(f"Date: {toot['created_at']}\n")
            f.write(f"Content: {toot['content']}\n")
            #f.write(f"URL: {toot['url']}\n")
            f.write("-" * 50 + "\n\n")

    with open("Toots_1.txt", 'w', encoding='utf-8') as f:
        for i, toot in enumerate(data_1, 1):
            f.write(f"Toot #{i}\n")
            #f.write(f"Author: {toot['author']}\n")
            #f.write(f"Date: {toot['created_at']}\n")
            f.write(f"Content: {toot['content']}\n")
            #f.write(f"URL: {toot['url']}\n")
            f.write("-" * 50 + "\n\n")

    with open("Toots_3.txt", 'w', encoding='utf-8') as f:
        for i, toot in enumerate(data_2, 1):
            f.write(f"Toot #{i}\n")
            #f.write(f"Author: {toot['author']}\n")
            #f.write(f"Date: {toot['created_at']}\n")
            f.write(f"Content: {toot['content']}\n")
            #f.write(f"URL: {toot['url']}\n")
            f.write("-" * 50 + "\n\n")
except Exception as e:
    print(f"Fehler beim Speichern: {e}")
    exit()

print("Daten erfolgreich extrahiert und gespeichert.")