"""Build the bilingual static site using only Python's standard library."""
import json
import os
from datetime import date
from html import escape
from pathlib import Path
from string import Template
from urllib.parse import urlparse

BASE = Path(__file__).resolve().parents[1]
SITE = BASE / 'site'
CONTENT = json.loads((BASE / 'src/content.json').read_text(encoding='utf-8'))
TEMPLATE = Template((BASE / 'src/page.html').read_text(encoding='utf-8'))
url = os.getenv('PUBLIC_SITE_URL', '').rstrip('/')
if url and (urlparse(url).scheme != 'https' or not urlparse(url).netloc or urlparse(url).query or urlparse(url).fragment):
    raise ValueError('PUBLIC_SITE_URL must be a clean absolute HTTPS URL')
indexable = os.getenv('ENABLE_INDEXING', 'false').lower() == 'true' and bool(url)

def e(value):
    return escape(str(value), quote=True)

def lines(value):
    return e(value).replace('\n', '<br>')

def cta(text, klass='button'):
    return f'<button type="button" class="{klass}" data-contact>{e(text)}</button>'

for lang, d in CONTENT.items():
    path = '/' if lang == 'en' else '/es/'
    nav = ''.join(f'<a href="#{section}">{e(label)}</a>' for section, label in zip(['treatments','investment','team','journey'], d['nav']))
    treatments = ''.join(f'''<article class="treatment" id="{t['id']}">
      <div class="treatment-heading"><p class="eyebrow">{e(t['tag'])}</p><h3>{e(t['name'])}</h3></div>
      <div class="treatment-copy"><p>{e(t['text'])}</p><details><summary>{e(d['detailsLabel'])}<span aria-hidden="true">+</span></summary><ul>{''.join(f'<li>{e(x)}</li>' for x in t['details'])}</ul></details>{cta(d['cta'], 'text-button')}</div></article>''' for t in d['treatments'])
    fields = ''.join(f'<label for="cost-{i}">{e(label)}<span class="money"><span aria-hidden="true">$</span><input id="cost-{i}" name="cost-{i}" type="number" inputmode="decimal" min="{0.01 if i == 0 else 0}" max="100000000" step="0.01" placeholder="0.00" required aria-describedby="currency"></span></label>' for i, label in enumerate(d['fields']))
    doctors = ''.join(f'<article class="doctor"><div class="doctor-monogram" aria-hidden="true">{e(p["initials"])}</div><div><p class="eyebrow">{e(p["role"])}</p><h3>{e(d["doctorPrefix"])} {e(p["name"])}</h3><p>{e(p["text"])}</p>{cta(d["shortCta"], "text-button")}</div></article>' for p in d['doctors'])
    steps = ''.join(f'<li><h3>{e(title)}</h3><p>{e(text)}</p></li>' for title,text in d['steps'])
    faqs = ''.join(f'<details><summary>{e(q)}<span aria-hidden="true">+</span></summary><p>{e(a)}</p></details>' for q,a in d['faqs'])
    seo = ''
    if url:
        seo = f'<link rel="canonical" href="{e(url+path)}"><link rel="alternate" hreflang="en-US" href="{e(url)}/"><link rel="alternate" hreflang="es-PR" href="{e(url)}/es/"><link rel="alternate" hreflang="x-default" href="{e(url)}/"><meta property="og:url" content="{e(url+path)}"><meta property="og:image" content="{e(url)}/assets/editorial-smile.webp">'
        schema = {'@context':'https://schema.org','@type':'Organization','name':'Sonrisas Colombia','url':url,'logo':url+'/assets/logo-onix.webp'}
        seo += '<script type="application/ld+json">'+json.dumps(schema, ensure_ascii=False).replace('<','\\u003c')+'</script>'
    values = {k:lines(v) for k,v in d.items() if isinstance(v,str)}
    values.update(home=path,year=str(date.today().year),navTitle=e(d['nav'][0]),nav=nav,treatments=treatments,doctors=doctors,fields=fields,steps=steps,faqs=faqs,seo=seo,robots='index,follow' if indexable else 'noindex,nofollow',ctaButton=cta(d['cta']),shortButton=cta(d['shortCta'],'button button-small'),strip=''.join(f'<span>{e(s)}</span>' for s in d['strip']),compareHead=''.join(f'<th scope="col">{e(s)}</th>' for s in d['compareHeaders']),compareBody=''.join('<tr>'+f'<th scope="row">{e(row[0])}</th>'+''.join(f'<td>{e(s)}</td>' for s in row[1:])+'</tr>' for row in d['compareRows']),client=json.dumps({k:d[k] for k in ['locale','savings','extra','neutral','invalid','total','homeLabel','percentage','contactMessage','contactUnavailable']},ensure_ascii=False).replace('<','\\u003c'))
    target = SITE / path.lstrip('/') / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(TEMPLATE.substitute(values), encoding='utf-8')

config = {'whatsapp':os.getenv('PUBLIC_WHATSAPP_NUMBER',''),'siteUrl':url,'ga4':os.getenv('PUBLIC_GA4_ID',''),'metaPixel':os.getenv('PUBLIC_META_PIXEL_ID',''),'gtm':os.getenv('PUBLIC_GTM_ID',''),'trackingEnabled':False}
(SITE/'assets/config.js').write_text('window.SONRISAS = '+json.dumps(config)+';\n',encoding='utf-8')
(SITE/'robots.txt').write_text('User-agent: *\n'+('Allow: /\nSitemap: '+url+'/sitemap.xml\n' if indexable else 'Disallow: /\n'), encoding='utf-8')
sitemap = SITE/'sitemap.xml'
if url:
    sitemap.write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+e(url+p)+'</loc></url>' for p in ['/','/es/'])+'</urlset>',encoding='utf-8')
elif sitemap.exists():
    sitemap.unlink()
print('Built English and Spanish. Indexing:', indexable)
