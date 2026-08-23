import requests
from bs4 import BeautifulSoup
from app.models import Bookmark, BookmarkCategory
from app.repositories.bookmark_repository import BookmarkRepository, BookmarkCategoryRepository
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
                if image_url and not image_url.startswith('http') and not image_url.startswith('//'):
                    from urllib.parse import urljoin
                    image_url = urljoin(url, image_url)

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

            final_title = BookmarkService.clean_title(title)
            final_description = BookmarkService.translate_to_portuguese(description)

            return {
                'success': True,
                'title': final_title,
                'description': final_description,
                'image_url': image_url
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
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

    @staticmethod
    def translate_to_portuguese(text):
        if not text:
            return ""
        try:
            import requests
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
            pass
        return text

    @staticmethod
    def get_all_bookmarks():
        repo = BookmarkRepository()
        return repo.list_ordered_by_creation()

    @staticmethod
    def get_all_categories():
        repo_cat = BookmarkCategoryRepository()
        return repo_cat.list_ordered_by_nome()

    @staticmethod
    def create_bookmark(titulo, url, descricao, category_ids=None, image_url=None):
        repo = BookmarkRepository()
        repo_cat = BookmarkCategoryRepository()
        try:
            bookmark = Bookmark(titulo=titulo, url=url, descricao=descricao, image_url=image_url)
            if category_ids:
                categories = repo_cat.find_by_ids(category_ids)
                bookmark.categories = categories
            
            repo.add(bookmark)
            repo.commit()
            return True, "Bookmark salvo com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, str(e)

    @staticmethod
    def update_bookmark(bookmark_id, titulo, url, descricao, category_ids=None, image_url=None):
        repo = BookmarkRepository()
        repo_cat = BookmarkCategoryRepository()
        try:
            bookmark = repo.get_by_id(bookmark_id)
            if not bookmark:
                return False, "Bookmark não encontrado."
            
            bookmark.titulo = titulo
            bookmark.url = url
            bookmark.descricao = descricao
            bookmark.image_url = image_url
            
            if category_ids is not None:
                categories = repo_cat.find_by_ids(category_ids)
                bookmark.categories = categories
            
            repo.commit()
            return True, "Bookmark atualizado com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, str(e)

    @staticmethod
    def delete_bookmark(bookmark_id):
        repo = BookmarkRepository()
        try:
            bookmark = repo.get_by_id(bookmark_id)
            if not bookmark:
                return False, "Bookmark não encontrado."
            
            repo.delete(bookmark)
            repo.commit()
            return True, "Bookmark removido com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, str(e)

    @staticmethod
    def create_category(nome):
        repo_cat = BookmarkCategoryRepository()
        try:
            category = BookmarkCategory(nome=nome.upper())
            repo_cat.add(category)
            repo_cat.commit()
            return True, "Categoria criada!"
        except Exception as e:
            repo_cat.rollback()
            return False, str(e)

    @staticmethod
    def update_category(category_id, novo_nome):
        repo_cat = BookmarkCategoryRepository()
        try:
            category = repo_cat.get_by_id(category_id)
            if not category:
                return False, "Categoria não encontrada."
            category.nome = novo_nome.upper()
            repo_cat.commit()
            return True, "Categoria atualizada!"
        except Exception as e:
            repo_cat.rollback()
            return False, str(e)

    @staticmethod
    def delete_category(category_id):
        repo_cat = BookmarkCategoryRepository()
        try:
            category = repo_cat.get_by_id(category_id)
            if not category:
                return False, "Categoria não encontrada."
            repo_cat.delete(category)
            repo_cat.commit()
            return True, "Categoria removida!"
        except Exception as e:
            repo_cat.rollback()
            return False, str(e)

    @staticmethod
    def create_batch_bookmarks(batch_text, category_ids=None):
        """Cria bookmarks em lote a partir de um texto com múltiplas URLs."""
        repo = BookmarkRepository()
        repo_cat = BookmarkCategoryRepository()
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
                    categories = repo_cat.find_by_ids(category_ids)
                    bookmark.categories = categories
                
                repo.add(bookmark)
                count += 1
            
            repo.commit()
            return True, f"{count} favoritos adicionados com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, f"Erro ao processar lote: {str(e)}"
