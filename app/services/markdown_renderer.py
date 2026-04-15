import markdown
import bleach
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension

def render_markdown(text):
    """
    Converte Markdown para HTML com suporte a blocos de código e sintaxe,
    aplicando sanitização para evitar XSS.
    """
    if not text:
        return ""
    
    # Extensões para Markdown
    extensions = [
        FencedCodeExtension(),
        CodeHiliteExtension(css_class='codehilite', guess_lang=False)
    ]
    
    html = markdown.markdown(text, extensions=extensions)
    
    # Sanitização para segurança (XSS)
    # Permite tags comuns de formatação e estrutura geradas pelo Markdown + CodeHilite
    allowed_tags = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr', 'pre', 'code', 
        'span', 'div', 'ul', 'ol', 'li', 'strong', 'em', 'a', 'img', 
        'table', 'thead', 'tbody', 'tr', 'th', 'td', 'blockquote', 'del'
    ]
    allowed_attrs = {
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title'],
        'span': ['class'],
        'div': ['class'],
        'code': ['class'],
        'pre': ['class']
    }
    
    return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs)

