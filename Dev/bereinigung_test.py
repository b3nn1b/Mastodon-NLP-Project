import re


def clean_text(text):
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    text = url_pattern.sub('', text)

    text = re.sub(r'#([a-zA-Z0-9]+)', r' \1 ', text)

    text = re.sub(r'\s+', ' ', text)

    text = text.strip()

    text = re.sub(r'([a-zA-ZäöüÄÖÜß])([A-Z])', r'\1 \2', text)

    return text


with open('hamburg5.txt', 'r', encoding='utf-8') as file:
    content = file.read()

sections = content.split('\n\n')

cleaned_sections = [clean_text(section) for section in sections]

with open('hamburg5_cleaned.txt', 'w', encoding='utf-8') as file:
    file.write('\n\n'.join(cleaned_sections))