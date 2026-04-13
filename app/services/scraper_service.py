import requests
from bs4 import BeautifulSoup
import re
import json

class ScraperService:
    @staticmethod
    def scrape_url(url):
        """
        Main entry point for scraping.
        Returns a dict: {'item': str, 'valor': float, 'success': bool, 'is_restricted': bool}
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Extrair Título
            title = ScraperService._extract_title(soup, url)
            
            # Verificar se caímos em uma página de login/home genérica
            if ScraperService._is_login_wall(title, url):
                # Fallback: Tentar pegar nome pela URL
                url_name = ScraperService._extract_name_from_url(url)
                return {
                    'item': url_name.upper() if url_name else "ITEM (SITE RESTRITO)",
                    'valor': None,
                    'success': True if url_name else False,
                    'is_restricted': True
                }
            
            # 2. Extrair Preço
            price = ScraperService._extract_price(soup, response.text)
            
            return {
                'item': title.upper() if title else "ITEM IMPORTADO",
                'valor': price,
                'success': True if title else False,
                'is_restricted': False
            }
            
        except Exception as e:
            print(f"Scraping error: {str(e)}")
            return {'item': None, 'valor': None, 'success': False, 'is_restricted': False}

    @staticmethod
    def _is_login_wall(title, url):
        if not title: return False
        
        restricted_indicators = [
            'PRIVALIA - Seu desejo a um click',
            'login',
            'entrar',
            'fazer login',
            'inicie sessão',
            'create account',
            'shein.com/login',
        ]
        
        title_low = title.lower()
        for indicator in restricted_indicators:
            if indicator.lower() in title_low:
                return True
        return False

    @staticmethod
    def _extract_name_from_url(url):
        # Ex: https://br.privalia.com/lojas/pdp/productId/359485?campaignName=Di%25C3%25A2metro
        # Tenta pegar de parâmetros conhecidos
        params_to_check = ['campaignName', 'productName', 'item', 'q', 'name']
        for p in params_to_check:
            match = re.search(f'[?&]{p}=([^&]+)', url)
            if match:
                name = requests.utils.unquote(match.group(1)).replace('+', ' ').replace('%20', ' ')
                return name.strip()

        # Se não encontrar em params, tenta no path
        path = url.split('?')[0] # remove query string
        segments = [s for s in path.split('/') if s and not s.isdigit() and len(s) > 3]
        
        # Ignorar segmentos genéricos de sistemas
        ignore = ['lojas', 'pdp', 'productId', 'items', 'products', 'item', 'product', 'br', 'pt', 'com']
        relevant = [s for s in segments if s.lower() not in ignore]
        
        if relevant:
            # Pegar o último segmento significativo
            name = relevant[-1].replace('-', ' ').replace('_', ' ')
            # Limpar lixo
            name = re.sub(r'\.\w+$', '', name) # remove extensão .html etc
            return name.strip()
            
        return None

    @staticmethod
    def _extract_title(soup, url):
        title = None
        # Prioridade 1: Meta Tags (OG / Twitter)
        og_title = soup.find('meta', property='og:title') or soup.find('meta', name='twitter:title')
        if og_title and og_title.get('content'):
            title = og_title.get('content').strip()
        
        # Prioridade 2: Amazon Específico
        if not title and 'amazon' in url:
            amazon_title = soup.select_one('#productTitle')
            if amazon_title:
                title = amazon_title.get_text().strip()
                
        # Prioridade 3: Mercado Livre
        if not title and 'mercadolivre' in url:
            ml_title = soup.select_one('.ui-pdp-title')
            if ml_title:
                title = ml_title.get_text().strip()
        
        # Prioridade 4: Zattini/Netshoes Específico
        if not title and ('zattini' in url or 'netshoes' in url):
            z_title = soup.select_one('h1[data-productname]') or soup.select_one('.product-name')
            if z_title:
                title = z_title.get_text().strip()

        # Prioridade 5: Tag <title> generica
        if not title and soup.title:
            title = soup.title.string.strip()
            
        if title:
            # Limpeza de sufixos comuns
            title = re.sub(r'\s*\|\s*Zattini.*', '', title, flags=re.I)
            title = re.sub(r'\s*\|\s*Netshoes.*', '', title, flags=re.I)
            title = re.sub(r'\s*\|\s*Mercado\s*Livre.*', '', title, flags=re.I)
            title = re.sub(r'\s*\|\s*Privalia.*', '', title, flags=re.I)
            return title
            
        return None

    @staticmethod
    def _extract_price(soup, raw_html):
        # Estratégia 1: JSON-LD (Schema.org)
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        price = ScraperService._find_price_in_json(item)
                        if price: return price
                else:
                    price = ScraperService._find_price_in_json(data)
                    if price: return price
            except:
                continue

        # Estratégia 2: Meta Tags
        # product:price:amount, og:price:amount, price
        meta_selectors = [
            ('meta', {'property': 'product:price:amount'}),
            ('meta', {'property': 'og:price:amount'}),
            ('meta', {'name': 'twitter:data1'}),
            ('meta', {'itemprop': 'price'}),
        ]
        for tag, attrs in meta_selectors:
            meta = soup.find(tag, attrs)
            if meta:
                content = meta.get('content') or meta.get('value')
                price = ScraperService._parse_price_string(content)
                if price: return price

        # Estratégia 3: Seletores CSS Comuns
        selectors = [
            '.price-tag-amount', # ML
            '.a-price-whole',    # Amazon
            '[itemprop="price"]', # Genérico
            '.product-price',    # Zattini
            '.actual-price',     # Shein
            '.sale-price',
            '.current-price',
        ]
        for sel in selectors:
            elem = soup.select_one(sel)
            if elem:
                price = ScraperService._parse_price_string(elem.get_text())
                if price: return price

        # Estratégia 4: Regex para "R$ 1.234,56" ou "1.234,56"
        # Tenta primeiro com R$ para ser mais preciso
        price_match = re.search(r'R\$\s*(\d{1,3}(\.\d{3})*,\d{2})', raw_html)
        if price_match:
            return ScraperService._parse_price_string(price_match.group(1))
            
        # Estratégia 5: Lidar com "X de R$ Y" (Comum em Zattini/Netshoes se o preço principal sumir)
        # Ex: "2x de R$ 95,00" -> 190.00
        installment_match = re.search(r'(\d+)x\s*de\s*R\$\s*(\d{1,3}(\.\d{3})*,\d{2})', raw_html, re.I)
        if installment_match:
            cuantity = int(installment_match.group(1))
            unit_price = ScraperService._parse_price_string(installment_match.group(2))
            if unit_price:
                return cuantity * unit_price

        return None

    @staticmethod
    def _find_price_in_json(data):
        if not isinstance(data, dict): return None
        
        # Caso clássico de Offers
        if 'offers' in data:
            offers = data['offers']
            if isinstance(offers, dict):
                p = offers.get('price') or offers.get('lowPrice') or offers.get('highPrice')
                if p: return ScraperService._parse_price_string(str(p))
            elif isinstance(offers, list) and len(offers) > 0:
                p = offers[0].get('price') or offers[0].get('lowPrice')
                if p: return ScraperService._parse_price_string(str(p))
        
        # Caso direto (alguns sites colocam no root do JSON)
        if 'price' in data:
            return ScraperService._parse_price_string(str(data['price']))
            
        return None

    @staticmethod
    def _parse_price_string(price_str):
        if not price_str: return None
        # Remover lixo comum
        price_str = price_str.replace('\xa0', ' ').strip()
        
        # Se for apenas números e ponto/vírgula
        clean = re.sub(r'[^\d,.]', '', price_str)
        if not clean: return None
        
        # Lógica de decodificação de separadores
        if ',' in clean and '.' in clean:
            # Formato 1.234,56 (BR) ou 1,234.56 (US)
            if clean.rfind(',') > clean.rfind('.'): # BR
                clean = clean.replace('.', '').replace(',', '.')
            else: # US
                clean = clean.replace(',', '')
        elif ',' in clean:
            # Formato 1234,56
            clean = clean.replace(',', '.')
            
        try:
            return float(clean)
        except:
            return None
