from bs4 import BeautifulSoup
import re
import json
import mastodon
from credentials import MASTODON_INSTANCE
from credentials import ACCESS_TOKEN
from credentials import HASHTAG

# HTML und URLs entfernen
def remove_html(html_content):
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

# Toot Content als JSON speichern
def save_list_to_json(data_list, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, ensure_ascii=False)

def save_list_to_file(data_list, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data_list:
            f.write(item + '\n')

# Initialisieren
masto = mastodon.Mastodon(
    access_token = ACCESS_TOKEN,
    api_base_url = MASTODON_INSTANCE
)
# Variablen für Pagination
all_toots = []
max_id = None
limit = 40  # Max allowed per request
total_to_fetch = 300  # Total number of toots you want to fetch

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
    data = []
    for toot in all_toots:
        data.append({
            'id': toot['id'],
            'content': remove_html(toot['content']),
            'created_at': toot['created_at'],
            'author': toot['account']['acct'],
            'url': toot['url']
        })

    content_list = []
    for item in data:
        content_list.append(item['content'])
    save_list_to_file(content_list, 'hamburg1.txt')

except Exception as e:
    print(f"Fehler beim Verarbeiten: {e}")
    exit()



