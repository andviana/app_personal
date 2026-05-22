import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from app import create_app, db
from app.models import Bookmark

app = create_app()
with app.app_context():
    bookmarks = Bookmark.query.all()
    print(f"Total bookmarks: {len(bookmarks)}")
    for b in bookmarks[:5]:
        print(f"ID: {b.id} | Title: {b.titulo} | Desc: {b.descricao[:60] if b.descricao else 'None'}")
