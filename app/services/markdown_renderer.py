import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension

def render_markdown(text):
    """
    Converte Markdown para HTML com suporte a blocos de código e sintaxe.
    """
    if not text:
        return ""
    
    # Extensões para Markdown
    extensions = [
        FencedCodeExtension(),
        CodeHiliteExtension(css_class='codehilite', guess_lang=False)
    ]
    
    return markdown.markdown(text, extensions=extensions)
