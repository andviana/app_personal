import sys
import os
sys.path.insert(0, os.path.abspath('.'))
import requests
from app import create_app, db
from app.models import Bookmark

def clean_title(title):
    if not title:
        return ""
    for separator in [' - ', ' | ', ' – ', ' » ', ' : ']:
        if separator in title:
            parts = [p.strip() for p in title.split(separator) if p.strip()]
            if len(parts) > 1:
                # Check for TLDs
                for part in parts:
                    if any(tld in part.lower() for tld in ['.com', '.org', '.net', '.io', '.ai', '.co', '.edu', '.gov', '.app']):
                        return part
                # Check for short parts
                sorted_parts = sorted(parts, key=len)
                for part in sorted_parts:
                    if 3 <= len(part) <= 25:
                        return part
                return parts[0]
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

app = create_app()
with app.app_context():
    bookmarks = Bookmark.query.all()
    print(f"Starting migration for {len(bookmarks)} bookmarks...")
    
    updated_count = 0
    for b in bookmarks:
        old_title = b.titulo
        old_desc = b.descricao
        
        new_title = clean_title(old_title)
        new_desc = translate_to_portuguese(old_desc)
        
        changed = False
        if new_title != old_title:
            b.titulo = new_title
            changed = True
        if new_desc != old_desc:
            b.descricao = new_desc
            changed = True
            
        if changed:
            updated_count += 1
            print(f"[{updated_count}] Updated ID {b.id}:")
            print(f"  Title: '{old_title}' -> '{new_title}'")
            print(f"  Desc:  '{old_desc[:50]}...' -> '{new_desc[:50]}...'")
            
    if updated_count > 0:
        db.session.commit()
        print(f"Successfully migrated {updated_count} bookmarks!")
    else:
        print("No changes needed.")
