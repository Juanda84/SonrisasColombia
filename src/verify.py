"""Comprobaciones de integridad del sitio generado."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.refs, self.h1, self.sliders, self.lang = set(), [], 0, 0, ''
        self.imgs_without_alt = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, 'Duplicate id: ' + a['id']
            self.ids.add(a['id'])
        if tag == 'html':
            self.lang = a.get('lang', '')
        if tag == 'h1':
            self.h1 += 1
        if tag == 'img' and 'alt' not in a:
            self.imgs_without_alt += 1
        if tag == 'input' and a.get('type') == 'range' and 'cmp__range' in a.get('class', ''):
            self.sliders += 1
        for key in ('href', 'src'):
            if a.get(key):
                self.refs.append(a[key])
        for key in ('srcset',):
            if a.get(key):
                self.refs += [part.strip().split(' ')[0] for part in a[key].split(',')]


data = json.loads((ROOT / 'src/content.json').read_text(encoding='utf-8'))
assert set(data['es']) == set(data['en']), 'Missing translation keys: ' + str(set(data['es']) ^ set(data['en']))

for route, language, caption in [
    ('index.html', 'es-PR', 'Simulación generada de un caso ficticio.'),
    ('en/index.html', 'en-US', 'Generated simulation of a fictional case.'),
    ('es/index.html', 'es-PR', 'Simulación generada de un caso ficticio.'),
]:
    html = (SITE / route).read_text(encoding='utf-8')
    page = Page()
    page.feed(html)
    assert page.lang == language, route
    assert page.h1 == 1, route
    assert page.imgs_without_alt == 0, route
    assert page.sliders == 2, 'Los dos comparadores antes/después deben estar siempre'
    assert 'data-calc' in html, 'La calculadora debe estar siempre'
    assert not re.search(r'\{(resin|porcelain|saveUs|savePr)\}', html), 'Token de precio sin reemplazar'
    for ref in page.refs:
        if ref.startswith('#') and len(ref) > 1:
            assert ref[1:] in page.ids, route + ': missing anchor ' + ref
        elif ref.startswith('/'):
            assert (SITE / ref.lstrip('/').split('#')[0]).exists() or ref in ('/', '/en/'), route + ': missing ' + ref
    print(route + ': enlaces, imágenes, títulos y comparadores OK — pendientes:', html.count('class="ph '))

for font in (SITE / 'assets/fonts').glob('*.woff2'):
    assert font.read_bytes()[:4] == b'wOF2', 'Invalid WOFF2: ' + str(font)
compose = (ROOT / 'docker-compose.yml').read_text()
assert 'ports:' not in compose
assert 'expose:' in compose and 'healthcheck:' in compose
print('Traducciones, fuentes y Compose OK')
