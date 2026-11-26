"""Comprobaciones de integridad del sitio generado (todas las páginas)."""
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
        self.imgs_without_alt, self.title, self._t, self.meta, self.ld, self._ld = 0, '', False, {}, [], None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, 'Duplicate id: ' + a['id']
            self.ids.add(a['id'])
        if tag == 'html':
            self.lang = a.get('lang', '')
        if tag == 'h1':
            self.h1 += 1
        if tag == 'title':
            self._t = True
        if tag == 'meta':
            self.meta[a.get('name') or a.get('property')] = a.get('content', '')
        if tag == 'link' and a.get('rel') == 'canonical':
            self.meta['canonical'] = a.get('href')
        if tag == 'script' and a.get('type') == 'application/ld+json':
            self._ld = ''
        if tag == 'img' and 'alt' not in a:
            self.imgs_without_alt += 1
        if tag == 'input' and 'cmp__range' in a.get('class', ''):
            self.sliders += 1
        for key in ('href', 'src'):
            if a.get(key):
                self.refs.append(a[key])
        if a.get('srcset'):
            self.refs += [part.strip().split(' ')[0] for part in a['srcset'].split(',')]

    def handle_endtag(self, tag):
        if tag == 'title':
            self._t = False
        if tag == 'script' and self._ld is not None:
            self.ld.append(json.loads(self._ld))
            self._ld = None

    def handle_data(self, data):
        if self._t:
            self.title += data
        if self._ld is not None:
            self._ld += data


for name in ('content.json', 'pages.json'):
    data = json.loads((ROOT / 'src' / name).read_text(encoding='utf-8'))
    assert set(data['es']) == set(data['en']), name + ': faltan traducciones ' + str(set(data['es']) ^ set(data['en']))

pages = sorted(SITE.rglob('index.html'))
assert len(pages) >= 13, 'Faltan páginas'
titles = {}
for file in pages:
    route = str(file.relative_to(SITE))
    html = file.read_text(encoding='utf-8')
    page = Page()
    page.feed(html)
    assert page.lang in ('es-PR', 'en-US'), route
    assert page.h1 == 1, route + ': debe tener un solo h1'
    assert page.imgs_without_alt == 0, route
    assert 20 <= len(page.title) <= 66, f'{route}: título de {len(page.title)} caracteres'
    assert len(page.meta.get('description', '')) <= 160, f'{route}: descripción muy larga'
    assert page.meta.get('og:image', '').split('?')[0].endswith('og-image.jpg'), route
    assert page.ld and '@graph' in page.ld[0], route + ': faltan datos estructurados'
    assert re.search(r'/assets/site\.css\?v=[0-9a-f]{10}', html) and re.search(r'/assets/site\.js\?v=[0-9a-f]{10}', html), route + ': CSS/JS sin versión (caché)'
    types = {n['@type'] for n in page.ld[0]['@graph']}
    assert {'Dentist', 'WebSite', 'WebPage', 'FAQPage'} <= types, f'{route}: {types}'
    assert 'data-calc' in html or 'carillas-' in route or 'veneers-' in route, route
    assert not re.search(r'\{(resin|porcelain|saveUs|savePr|coPorc8|prPorc8|usPorc8|savePorc8Pr|prResin|usResin|prPorcelain|usPorcelain)\}', html), route + ': token sin reemplazar'
    for ref in page.refs:
        if ref.startswith('#') and len(ref) > 1:
            assert ref[1:] in page.ids, route + ': falta el ancla ' + ref
        elif ref.startswith('/'):
            target = ref.split('#')[0].split('?')[0]
            ok = (SITE / target.lstrip('/')).exists() if not target.endswith('/') else (SITE / target.lstrip('/') / 'index.html').exists()
            assert ok, route + ': enlace roto ' + ref
    if not route.startswith('es/'):
        assert page.title not in titles, f'{route}: título repetido con {titles.get(page.title)}'
        titles[page.title] = route
    print(f'{route}: OK — {len(page.title)} car. título, {len(page.meta["description"])} car. descripción, pendientes: {html.count(chr(39)+"ph ") + html.count(chr(34)+"ph ")}')

assert (SITE / 'llms.txt').exists() and (SITE / 'sitemap.xml').exists()
assert (SITE / 'sitemap.xml').read_text(encoding='utf-8').count('<url>') == len(pages) - 1
for font in (SITE / 'assets/fonts').glob('*.woff2'):
    assert font.read_bytes()[:4] == b'wOF2', 'Invalid WOFF2: ' + str(font)
compose = (ROOT / 'docker-compose.yml').read_text()
assert 'ports:' not in compose
assert 'expose:' in compose and 'healthcheck:' in compose
print(f'{len(pages)} páginas, sitemap, llms.txt, traducciones, fuentes y Compose OK')
