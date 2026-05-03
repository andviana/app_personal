import requests
from bs4 import BeautifulSoup
from app import db
from app.models import Bookmark, BookmarkCategory
from sqlalchemy.exc import SQLAlchemyError

class BookmarkService:
    @staticmethod
    def scrape_url(url):
        """Extrai título e descrição de uma URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.title.string if soup.title else ""
            
            # Tenta encontrar a imagem (Thumbnail)
            image_url = ""
            img_tag = (
                soup.find('meta', attrs={'property': 'og:image'}) or 
                soup.find('meta', attrs={'name': 'twitter:image'}) or
                soup.find('link', attrs={'rel': 'image_src'})
            )
            if img_tag:
                image_url = img_tag.get('content', img_tag.get('href', ''))

            # Lógica especial para YouTube (caso o scraping falhe ou queira ser mais preciso)
            if "youtube.com" in url or "youtu.be" in url:
                import re
                video_id = None
                if "youtu.be" in url:
                    video_id = url.split("/")[-1].split("?")[0]
                else:
                    match = re.search(r"[?&]v=([^&#]+)", url)
                    if match:
                        video_id = match.group(1)
                
                if video_id:
                    # Prefere a imagem do YouTube se for um vídeo
                    image_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

            # Tenta encontrar a descrição em várias meta tags
            description = ""
            desc_tag = (
                soup.find('meta', attrs={'name': 'description'}) or 
                soup.find('meta', attrs={'property': 'og:description'}) or
                soup.find('meta', attrs={'name': 'twitter:description'})
            )
            if desc_tag:
                description = desc_tag.get('content', '')

            return {
                'success': True,
                'title': title.strip() if title else "",
                'description': description.strip() if description else "",
                'image_url': image_url
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_all_bookmarks():
        return Bookmark.query.order_by(Bookmark.data_criacao.desc()).all()

    @staticmethod
    def get_all_categories():
        return BookmarkCategory.query.order_by(BookmarkCategory.nome).all()

    @staticmethod
    def create_bookmark(titulo, url, descricao, category_ids=None, image_url=None):
        try:
            bookmark = Bookmark(titulo=titulo, url=url, descricao=descricao, image_url=image_url)
            if category_ids:
                categories = BookmarkCategory.query.filter(BookmarkCategory.id.in_(category_ids)).all()
                bookmark.categories = categories
            
            db.session.add(bookmark)
            db.session.commit()
            return True, "Bookmark salvo com sucesso!"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def update_bookmark(bookmark_id, titulo, url, descricao, category_ids=None, image_url=None):
        try:
            bookmark = Bookmark.query.get(bookmark_id)
            if not bookmark:
                return False, "Bookmark não encontrado."
            
            bookmark.titulo = titulo
            bookmark.url = url
            bookmark.descricao = descricao
            bookmark.image_url = image_url
            
            if category_ids is not None:
                categories = BookmarkCategory.query.filter(BookmarkCategory.id.in_(category_ids)).all()
                bookmark.categories = categories
            
            db.session.commit()
            return True, "Bookmark atualizado com sucesso!"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def delete_bookmark(bookmark_id):
        try:
            bookmark = Bookmark.query.get(bookmark_id)
            if not bookmark:
                return False, "Bookmark não encontrado."
            
            db.session.delete(bookmark)
            db.session.commit()
            return True, "Bookmark removido com sucesso!"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def create_category(nome):
        try:
            category = BookmarkCategory(nome=nome.upper())
            db.session.add(category)
            db.session.commit()
            return True, "Categoria criada!"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    @staticmethod
    def update_category(category_id, novo_nome):
        try:
            category = BookmarkCategory.query.get(category_id)
            if not category:
                return False, "Categoria não encontrada."
            category.nome = novo_nome.upper()
            db.session.commit()
            return True, "Categoria atualizada!"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def delete_category(category_id):
        try:
            category = BookmarkCategory.query.get(category_id)
            if not category:
                return False, "Categoria não encontrada."
            db.session.delete(category)
            db.session.commit()
            return True, "Categoria removida!"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def create_batch_bookmarks(batch_text, category_ids=None):
        """Cria bookmarks em lote a partir de um texto com múltiplas URLs."""
        try:
            import re
            # Extrai URLs usando regex simples
            urls = re.findall(r'https?://[^\s,;]+', batch_text)
            
            if not urls:
                return False, "Nenhuma URL válida encontrada."

            count = 0
            for url in urls:
                # Tenta fazer o scraping básico
                data = BookmarkService.scrape_url(url)
                
                if data['success']:
                    titulo = data['title'] or url
                    descricao = data['description']
                    image_url = data['image_url']
                else:
                    titulo = url
                    descricao = ""
                    image_url = ""

                bookmark = Bookmark(
                    titulo=titulo,
                    url=url,
                    descricao=descricao,
                    image_url=image_url
                )
                
                if category_ids:
                    categories = BookmarkCategory.query.filter(BookmarkCategory.id.in_(category_ids)).all()
                    bookmark.categories = categories
                
                db.session.add(bookmark)
                count += 1
            
            db.session.commit()
            return True, f"{count} favoritos adicionados com sucesso!"
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao processar lote: {str(e)}"
