"""
Validação de URLs fornecidas pelo usuário antes de o servidor buscá-las
(scraping de listas e favoritos). Sem essa checagem, um usuário autenticado
poderia usar o campo de URL para fazer o servidor requisitar endereços
internos/privados (SSRF) — ex.: `http://127.0.0.1:5432`,
`http://169.254.169.254/...` (metadados de nuvem) — em vez de uma loja
online de verdade.

Usada por `ScraperService` (listas) e `BookmarkService` (favoritos), que
são os dois pontos da aplicação onde o servidor busca uma URL arbitrária
informada pelo usuário.
"""
import ipaddress
import socket
from urllib.parse import urlparse

ALLOWED_SCHEMES = {'http', 'https'}


def is_safe_external_url(url: str) -> bool:
    """Retorna True se a URL usa http(s) e resolve para um host público
    (não loopback, privado, link-local ou multicast)."""
    if not url:
        return False

    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    if parsed.scheme not in ALLOWED_SCHEMES or not parsed.hostname:
        return False

    try:
        resolved_ips = {info[4][0] for info in socket.getaddrinfo(parsed.hostname, None)}
    except socket.gaierror:
        # Não foi possível resolver o host — trata como inseguro.
        return False

    for ip in resolved_ips:
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            return False
        if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved or addr.is_multicast:
            return False

    return True
