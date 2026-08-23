import sys
import os
sys.path.insert(0, os.path.abspath('.'))
import requests

def clean_title(title):
    if not title:
        return ""
    # Look for common separators and split
    # Check for " | ", " - ", " – ", " » "
    for separator in [' - ', ' | ', ' – ', ' » ']:
        if separator in title:
            parts = title.split(separator)
            # Find the most relevant part. Usually it's the first part.
            # But let's check: if first part is very short or the brand is at the end,
            # we choose the longer part or clean it.
            # Actually, standard practice for bookmarks title:
            # We want the main name of the site/product. E.g. "Jenni | AI Academic Writer" -> "Jenni"
            # "Close Mortgage Loans 90% Faster | Addy AI" -> "Close Mortgage Loans 90% Faster" or "Addy AI"
            # Often, if the brand is at the end, the first part is the title.
            # Let's clean it by choosing the first part if it's longer than 3 characters, else the second.
            p1 = parts[0].strip()
            p2 = parts[1].strip()
            if len(p1) >= 3:
                return p1
            return p2
    return title.strip()

def translate_to_portuguese(text):
    if not text:
        return ""
    try:
        url = 'https://translate.googleapis.com/translate_a/single'
        params = {
            'client': 'gtx',
            'sl': 'auto',
            'tl': 'pt',
            'dt': 't',
            'q': text
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            result = response.json()
            translated_chunks = [chunk[0] for chunk in result[0] if chunk[0]]
            return "".join(translated_chunks)
    except Exception as e:
        print("Translation error:", e)
    return text

# Test cases
test_titles = [
    "Put AI agents to work for marketing | Jasper",
    "Jenni | AI Academic Writer & Research Tool for Students & Academics",
    "Close Mortgage Loans 90% Faster | Addy AI",
    "Rationale - a revolutionary decision-making AI powered by the latest GPT"
]

test_descs = [
    "Orchestrate intelligent agents to run end-to-end marketing campaigns.",
    "Jenni is an AI research and academic writing assistant that helps you write."
]

print("Titles:")
for t in test_titles:
    print(f"Original: {t}")
    print(f"Cleaned:  {clean_title(t)}")
    print("-" * 20)

print("\nTranslations:")
for d in test_descs:
    print(f"Original: {d}")
    print(f"Translated: {translate_to_portuguese(d)}")
    print("-" * 20)
