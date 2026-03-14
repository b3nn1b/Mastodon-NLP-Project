import re


def clean_text(text):
    # Entferne URLs
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    text = url_pattern.sub('', text)

    # Entferne Hashtags und andere Sonderzeichen, die zusammenhängen
    text = re.sub(r'#([a-zA-Z0-9]+)', r' \1 ', text)

    # Entferne mehrfache Leerzeichen
    text = re.sub(r'\s+', ' ', text)

    # Entferne führende und nachfolgende Leerzeichen
    text = text.strip()

    # Entferne zusammenhängende Wörter ohne Leerzeichen
    text = re.sub(r'([a-zA-ZäöüÄÖÜß])([A-Z])', r'\1 \2', text)

    return text


# Verarbeite hamburg5.txt
with open('hamburg5.txt', 'r', encoding='utf-8') as file:
    content = file.read()

# Teile den Inhalt in Abschnitte auf
sections = content.split('\n\n')

# Bereinige jeden Abschnitt
cleaned_sections = [clean_text(section) for section in sections]

# Schreibe die bereinigten Abschnitte in eine neue Datei
with open('hamburg5_cleaned.txt', 'w', encoding='utf-8') as file:
    file.write('\n\n'.join(cleaned_sections))