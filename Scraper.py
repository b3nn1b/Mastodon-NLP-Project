from bs4 import BeautifulSoup
import re
import mastodon
import time
from credentials import MASTODON_INSTANCE
from credentials import ACCESS_TOKEN

HASHTAG = "hamburg" # Ohne #
TOOTS = 1000        # Anzahl der zu ladenden Toots
FILENAME = 'hamburg.txt' # Datei für extrahierte Toots

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

# Toots in Datei schreiben
def save_list_to_file(data_list, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data_list:
            f.write(item + '\n')

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

# Daten verarbeiten und in Datei schreiben
try:
    data = []
    for toot in all_toots:
        data.append({
            #'id': toot['id'],
            'content': remove_html(toot['content']),
            #'created_at': toot['created_at'],
            #'author': toot['account']['acct'],
            #'url': toot['url']
        })

    content_list = []
    for item in data:
        content_list.append(item['content'])
    save_list_to_file(content_list, FILENAME)
    print(f"Toots in {FILENAME} geschrieben")

except Exception as e:
    print(f"Fehler beim Speichern: {e}")
    exit()



