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
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, 'Duplicate ID: '+attrs['id']
            self.ids.add(attrs['id'])
        self.h1 += tag == 'h1'
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
for route in ['index.html','es/index.html']:
    page = Page()
    html = (SITE/route).read_text(encoding='utf-8')
    page.feed(html)
    assert page.h1 == 1
    assert page.inputs == 5
    assert page.sliders == 2
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
