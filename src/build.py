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
EDITORIAL = json.loads((BASE / 'src/editorial.json').read_text(encoding='utf-8'))
TEMPLATE = Template((BASE / 'src/page.html').read_text(encoding='utf-8'))
EXAMPLE_COSTS = (8500, 3300, 550, 680, 320)
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

def render_smile_comparison(key, lang, title, *, high_priority=False):
    if lang == 'es':
        before, after = 'Antes', 'Después'
        label = 'Ajustar la comparación entre antes y después'
        caption = 'Simulación generada de un caso ficticio.'
        alt_before = 'Ilustración de la sonrisa inicial de una persona ficticia'
        alt_after = 'Ilustración de la misma sonrisa con cambios simulados'
    else:
        before, after = 'Before', 'After'
        label = 'Adjust the before and after comparison'
        caption = 'Generated simulation of a fictional case.'
        alt_before = 'Illustration of a fictional person’s initial smile'
        alt_after = 'Illustration of the same smile with simulated changes'

    prefix = f'/assets/smile-example-{key}'

    def photo(state, alt, *, first=False):
        loading = 'fetchpriority="high"' if high_priority and first else 'loading="lazy"' if not high_priority else ''
        return f'''<picture class="smile-comparison__photo smile-comparison__photo--{state}">
          <source type="image/avif" srcset="{prefix}-{state}.avif">
          <img src="{prefix}-{state}.webp" width="864" height="648" alt="{e(alt)}" {loading}>
        </picture>'''

    return f'''<figure class="smile-comparison smile-comparison--{key}" data-smile-comparison
      data-comparison-before="{e(before)}" data-comparison-after="{e(after)}">
      <div class="smile-comparison__stage">
        {photo('after', alt_after, first=True)}
        {photo('before', alt_before)}
        <span class="smile-comparison__badge smile-comparison__badge--before" aria-hidden="true">{e(before)}</span>
        <span class="smile-comparison__badge smile-comparison__badge--after" aria-hidden="true">{e(after)}</span>
        <div class="smile-comparison__divider" aria-hidden="true"></div>
        <input class="smile-comparison__range" type="range" min="0" max="100" value="50"
          aria-label="{e(f'{title}. {label}')}" aria-describedby="comparison-caption-{key}">
        <span class="smile-comparison__knob" aria-hidden="true">↔</span>
      </div>
      <figcaption class="smile-comparison__caption" id="comparison-caption-{key}">{e(caption)}</figcaption>
    </figure>'''

def render_treatments(d):
    tabs = []
    panels = []
    for treatment in d['treatments']:
        name = e(treatment['name'])
        slug = treatment['id']
        image = f'/assets/studio-{slug}'
        alt = e(d['treatmentImages'][slug])
        tabs.append(
            f'<button type="button" id="tab-{slug}" data-treatment="{slug}">{name}</button>'
        )
        points = ''.join(f'<li>{e(point)}</li>' for point in treatment['details'])
        panels.append(f'''
        <article class="studio-panel" id="{slug}">
          <picture class="studio-image">
            <source type="image/avif" srcset="{image}-720.avif 720w, {image}-1200.avif 1200w"
              sizes="(max-width: 760px) 92vw, 55vw">
            <img src="{image}-720.webp" width="720" height="480" alt="{alt}" loading="lazy" decoding="async">
          </picture>
          <div class="studio-copy">
            <p class="eyebrow">{e(treatment['tag'])}</p>
            <h3>{name}</h3>
            <p>{e(treatment['text'])}</p>
            <details>
              <summary>{e(d['detailsLabel'])}<span aria-hidden="true">+</span></summary>
              <ul>{points}</ul>
            </details>
            {cta(d['cta'], 'text-button')}
          </div>
        </article>''')
    return ''.join(tabs), ''.join(panels)

def render_journey(d):
    ranges = ((0, 5), (5, 7), (7, 8))
    phases = []
    for phase, (start, end) in zip(d['journeyPhaseTitles'], ranges):
        steps = []
        for number, (title, description) in enumerate(d['steps'][start:end], start=start + 1):
            travel_class = ' class="journey-step-travel"' if number == 5 else ''
            travel_note = f'<p class="journey-travel">{e(d["travelNote"])}</p>' if number == 5 else ''
            steps.append(f'<li{travel_class}><h4>{e(title)}</h4><p>{e(description)}</p>{travel_note}</li>')
        phases.append(f'<section class="journey-phase"><h3>{e(phase)}</h3>'
                      f'<ol class="journey-phase-steps" start="{start + 1}">{"".join(steps)}</ol></section>')
    return ''.join(phases)

def render_katherine_photos(alts):
    portraits = []
    for angle, alt in zip(('feature', 'clinic', 'profile'), alts):
        image = f'/assets/katherine-{angle}'
        source = (f'{image}-420.avif 420w, {image}-720.avif 720w'
                  if angle == 'feature' else f'{image}-420.avif')
        portraits.append(f'''
          <picture class="team-photo team-photo--{angle}">
            <source type="image/avif" srcset="{source}" sizes="(max-width: 760px) 86vw, 35vw">
            <img src="{image}-420.webp" alt="{e(alt)}" width="420" height="560" loading="lazy" decoding="async">
          </picture>''')
    return ''.join(portraits)

def render_doctors(d):
    vanessa, katherine = d['doctors']
    details = d['doctorDetails']
    return f'''
      <article class="team-feature">
        <div class="team-mosaic">{render_katherine_photos(d['portraitAlts'])}</div>
        <div class="team-profile">
          <p class="eyebrow">{e(katherine['role'])}</p>
          <h3>{e(d['doctorPrefix'])} {e(katherine['name'])}</h3>
          <p>{e(details['katherine']['text'])}</p>
          <ul class="team-topics">{''.join(f'<li>{e(topic)}</li>' for topic in details['katherine']['topics'])}</ul>
          {cta(d['cta'])}
        </div>
      </article>
      <article class="team-support">
        <span class="team-initials" aria-hidden="true">{e(vanessa['initials'])}</span>
        <div><p class="eyebrow">{e(vanessa['role'])}</p>
          <h3>{e(d['doctorPrefix'])} {e(vanessa['name'])}</h3></div>
        <div><p>{e(details['vanessa']['text'])}</p>
          <a href="#treatments" class="text-button">{e(d['secondary'])}</a></div>
      </article>'''

def render_editorial(d):
    recs = d['recommendations']
    stories = d['stories']
    recommendations = ''.join(
        f"<li><h3>{e(item['title'])}</h3><p>{e(item['text'])}</p></li>"
        for item in recs['items']
    )
    quotes = ''.join(
        f"<figure><figcaption>{e(item['caption'])}</figcaption>"
        f"<blockquote><p>“{e(item['quote'])}”</p></blockquote>"
        f"<p class=\"review-title\">{e(item['title'])}</p></figure>"
        for item in stories['items']
    )
    return dict(recsTitle=e(recs['title']), recsIntro=e(recs['intro']), recs=recommendations,
                storiesTitle=e(stories['title']), storiesIntro=e(stories['intro']), stories=quotes)

for lang, d in CONTENT.items():
    d = d | EDITORIAL[lang]
    path = '/' if lang == 'en' else '/es/'
    sections = ['results', 'treatments', 'investment', 'team', 'journey', 'faq']
    nav = ''.join(f'<a href="#{section}">{e(label)}</a>' for section, label in zip(sections, d['nav']))
    studio_tabs, treatments = render_treatments(d)
    fields = ''.join(
        f'<label for="cost-{i}">{e(label)}<span class="money"><span aria-hidden="true">$</span>'
        f'<input id="cost-{i}" name="cost-{i}" type="number" inputmode="decimal" '
        f'min="{0.01 if i == 0 else 0}" max="100000000" step="0.01" placeholder="0.00" '
        f'value="{amount}" required aria-describedby="currency example-note"></span></label>'
        for i, (label, amount) in enumerate(zip(d['fields'], EXAMPLE_COSTS))
    )
    doctors = render_doctors(d)
    steps = render_journey(d)
    faqs = ''.join(f'<details><summary>{e(q)}<span aria-hidden="true">+</span></summary><p>{e(a)}</p></details>' for q,a in d['faqs'])
    seo = ''
    if url:
        seo = f'<link rel="canonical" href="{e(url+path)}"><link rel="alternate" hreflang="en-US" href="{e(url)}/"><link rel="alternate" hreflang="es-PR" href="{e(url)}/es/"><link rel="alternate" hreflang="x-default" href="{e(url)}/"><meta property="og:url" content="{e(url+path)}"><meta property="og:image" content="{e(url)}/assets/editorial-smile.webp">'
        schema = {'@context':'https://schema.org','@type':'Organization','name':'Sonrisas Colombia','url':url,'logo':url+'/assets/logo-onix.webp'}
        seo += '<script type="application/ld+json">'+json.dumps(schema, ensure_ascii=False).replace('<','\\u003c')+'</script>'
    values = {k:lines(v) for k,v in d.items() if isinstance(v,str)}
    values.update(home=path,year=str(date.today().year),navTitle=e(d['nav'][0]),nav=nav,treatments=treatments,doctors=doctors,fields=fields,steps=steps,faqs=faqs,seo=seo,robots='index,follow' if indexable else 'noindex,nofollow',ctaButton=cta(d['cta']),shortButton=cta(d['shortCta'],'button button-small'),strip=''.join(f'<span>{e(s)}</span>' for s in d['strip']),compareHead=''.join(f'<th scope="col">{e(s)}</th>' for s in d['compareHeaders']),compareBody=''.join('<tr>'+f'<th scope="row">{e(row[0])}</th>'+''.join(f'<td>{e(s)}</td>' for s in row[1:])+'</tr>' for row in d['compareRows']),client=json.dumps({k:d[k] for k in ['locale','savings','extra','neutral','invalid','total','homeLabel','percentage','contactMessage','contactUnavailable','difference']},ensure_ascii=False).replace('<','\\u003c'))
    values.update(render_editorial(d))
    values.update(
        studioTabs=studio_tabs, otherLocale='es-PR' if lang == 'en' else 'en-US',
        heroComparison=render_smile_comparison('hero', lang, d['heroVisualTitle'], high_priority=True),
        galleryComparison=render_smile_comparison('gallery', lang, d['resultsExample']),
        flowLinks=''.join(f'<a href="#{target}">{e(label)}</a>'
                          for target, label in zip(('contact', 'treatments', 'journey'), d['flow'])),
        navTitle=e(d['nav'][1]),
    )
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
