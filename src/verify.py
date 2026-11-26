"""Offline integrity checks for the generated bilingual site."""
from html.parser import HTMLParser
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.refs = []
        self.h1 = 0
        self.inputs = 0
        self.sliders = 0
        self.language = None
        self.review_count = 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, 'Duplicate ID: '+attrs['id']
            self.ids.add(attrs['id'])
        self.h1 += tag == 'h1'
        if tag == 'html':
            self.language = attrs.get('lang')
        self.review_count += tag == 'blockquote'
        self.inputs += tag == 'input' and attrs.get('type') == 'number'
        self.sliders += tag == 'input' and attrs.get('type') == 'range'
        if tag == 'img':
            assert 'alt' in attrs and 'width' in attrs and 'height' in attrs
        for key in ['src','href']:
            if key in attrs:
                self.refs.append(attrs[key])
        for item in attrs.get('srcset','').split(','):
            if item.strip(): self.refs.append(item.strip().split()[0])

for source in ['content.json', 'editorial.json']:
    data = json.loads((ROOT/'src'/source).read_text(encoding='utf-8'))
    assert set(data['en']) == set(data['es']), 'Missing translation keys: '+source
for route, language in [
    ('index.html', 'es-PR'),
    ('en/index.html', 'en-US'),
    ('es/index.html', 'es-PR'),
]:
    page = Page()
    html = (SITE/route).read_text(encoding='utf-8')
    page.feed(html)
    assert page.h1 == 1
    assert page.language == language
    local_page = 'data-veneer-calculator' in html
    assert page.inputs == (1 if local_page else 0)
    assert page.sliders == 2, 'Los comparadores antes/después deben estar siempre'
    assert page.review_count == (12 if local_page else 0)
    caption = 'Simulación generada de un caso ficticio.' if language == 'es-PR' else 'Generated simulation of a fictional case.'
    assert html.count(caption) == 2, 'Cada comparador debe indicar que es una simulación'
    for ref in page.refs:
        if ref.startswith('#'): assert ref[1:] in page.ids, ref
        elif ref.startswith('/'): assert (SITE/ref.lstrip('/')).exists(), ref
    assert 'DEVELOPMENT PREVIEW' not in html and 'VERSIÓN DE DESARROLLO' not in html
    print(route+': links, images, headings, fields OK')
for font in (SITE/'assets/fonts').glob('*.woff2'):
    assert font.read_bytes()[:4] == b'wOF2', 'Invalid WOFF2: '+str(font)
compose = (ROOT/'docker-compose.yml').read_text()
assert 'ports:' not in compose
assert 'expose:' in compose and 'healthcheck:' in compose
print('Translations, WOFF2 fonts, Compose exposure OK')
