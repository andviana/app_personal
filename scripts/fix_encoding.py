import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from app import create_app, db
from app.models import Bookmark

def fix_utf8_encoding(text):
    if not text:
        return ""
    
    # Common UTF-8 corrupted sequences in Latin-1
    replacements = {
        'Ã§': 'ç',
        'Ã§Ã£': 'ção',
        'Ã£': 'ã',
        'Ã¡': 'á',
        'Ã©': 'é',
        'Ã­': 'í',
        'Ã³': 'ó',
        'Ãº': 'ú',
        'Ã¢': 'â',
        'Ãª': 'ê',
        'Ã´': 'ô',
        'Ã ': 'à',
        'Ã': 'Á',
        'Ã‰': 'É',
        'Ã': 'Í',
        'Ã“': 'Ó',
        'Ãš': 'Ú',
        'Ã‡': 'Ç',
        'Ã‚': 'Â',
        'Ã': 'Ê',
        'Ã': 'Ô',
        'Ãƒ': 'Ã',
        'â€“': '–',
        'â€”': '—',
        'â€™': '’',
        'â€œ': '“',
        'â€': '”',
    }
    
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text

app = create_app()
with app.app_context():
    bookmarks = Bookmark.query.all()
    count = 0
    for b in bookmarks:
        old_desc = b.descricao
        new_desc = fix_utf8_encoding(old_desc)
        
        old_title = b.titulo
        new_title = fix_utf8_encoding(old_title)
        
        changed = False
        if new_desc != old_desc:
            b.descricao = new_desc
            changed = True
        if new_title != old_title:
            b.titulo = new_title
            changed = True
            
        if changed:
            count += 1
            print(f"Fixed ID {b.id}:")
            print(f"  Title: {old_title} -> {new_title}")
            print(f"  Desc:  {old_desc[:60]} -> {new_desc[:60]}")
            
    if count > 0:
        db.session.commit()
        print(f"Successfully fixed {count} bookmarks encoding!")
    else:
        print("No encoding issues found.")
