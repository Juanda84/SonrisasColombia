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
url = os.getenv('PUBLIC_SITE_URL', '').rstrip('/')
if url and (urlparse(url).scheme != 'https' or not urlparse(url).netloc or urlparse(url).query or urlparse(url).fragment):
    raise ValueError('PUBLIC_SITE_URL must be a clean absolute HTTPS URL')
indexable = os.getenv('ENABLE_INDEXING', 'false').lower() == 'true' and bool(url)
show_examples = not url

def e(value):
    return escape(str(value), quote=True)

def lines(value):
    return e(value).replace('\n', '<br>')

def cta(text, klass='button'):
    return f'<button type="button" class="{klass}" data-contact>{e(text)}</button>'

# Importes inventados por carilla, en USD, para el sitio local.
VENEER_EXAMPLE_RATES = {
    'resin': {'colombia': 160, 'pr': 375, 'us': 500},
    'porcelain': {'colombia': 360, 'pr': 850, 'us': 1200},
}

VENEER_LABELS = {
    'es': {
        'title': '¿Cuánto costarían\ntus carillas?',
        'intro': 'Elige el material y cuántas carillas quieres comparar con el precio en tu lugar de residencia.',
        'controls': 'Calcula tu tratamiento',
        'demo': 'Importes orientativos en USD. El precio final se confirma en la valoración.',
        'material': 'Material', 'resin': 'Resina', 'porcelain': 'Porcelana',
        'quantity': 'Número de carillas', 'market': 'Comparar con',
        'pr': 'Puerto Rico', 'us': 'Estados Unidos',
        'total': 'Tratamiento en Colombia',
        'savings': 'Ahorro frente a {market}',
        'extra': 'Costo adicional frente a {market}',
        'equal': 'Sin diferencia frente a {market}',
        'invalid': 'Ingresa una cantidad del 1 al 32.',
        'productionIntro': 'En tu valoración puedes consultar qué material y cuántas carillas serían adecuados para ti, y solicitar un presupuesto del tratamiento.',
    },
    'en': {
        'title': 'What would\nyour veneers cost?',
        'intro': 'Choose a material and the number of veneers to compare treatment costs with where you live.',
        'controls': 'Estimate your treatment',
        'demo': 'Illustrative amounts in USD. Your consultation confirms your final price.',
        'material': 'Material', 'resin': 'Composite resin', 'porcelain': 'Porcelain',
        'quantity': 'Number of veneers', 'market': 'Compare with',
        'pr': 'Puerto Rico', 'us': 'United States',
        'total': 'Treatment in Colombia',
        'savings': 'Savings vs. {market}',
        'extra': 'Additional cost vs. {market}',
        'equal': 'No difference vs. {market}',
        'invalid': 'Enter a number from 1 to 32.',
        'productionIntro': 'Ask which material and how many veneers could suit you during your consultation, and request an estimate for the treatment.',
    },
}


def render_veneer_estimator(lang, d, *, show_examples):
    copy = VENEER_LABELS[lang]
    title = lines(copy['title'])
    intro = e(copy['intro'] if show_examples else copy['productionIntro'])
    action = cta(d['cta'])
    if show_examples:
        prices = e(json.dumps(VENEER_EXAMPLE_RATES, separators=(',', ':')))
        default_total = VENEER_EXAMPLE_RATES['resin']['colombia'] * 8
        default_savings = VENEER_EXAMPLE_RATES['resin']['pr'] * 8 - default_total
        initial_savings = e(copy['savings'].format(market=copy['pr']))
        demo = f'''
          <div class="calculator">
            <div class="calculator-top"><h3>{e(copy['controls'])}</h3><span>USD</span></div>
            <form class="veneer-calculator" data-veneer-calculator data-pricing="{prices}"
              data-savings="{e(copy['savings'])}" data-extra="{e(copy['extra'])}" data-equal="{e(copy['equal'])}">
              <div class="veneer-inputs">
                <label>{e(copy['material'])}<select name="material">
                  <option value="resin">{e(copy['resin'])}</option>
                  <option value="porcelain">{e(copy['porcelain'])}</option>
                </select></label>
                <label>{e(copy['quantity'])}<input name="quantity" type="number" inputmode="numeric"
                  min="1" max="32" step="1" value="8" required aria-describedby="veneers-quantity-error"></label>
                <label>{e(copy['market'])}<select name="market">
                  <option value="pr">{e(copy['pr'])}</option>
                  <option value="us">{e(copy['us'])}</option>
                </select></label>
              </div>
              <p class="veneer-note" id="veneers-quantity-error" data-veneers-error hidden>{e(copy['invalid'])}</p>
              <dl class="veneer-results" aria-live="polite" aria-atomic="true">
                <div><dt>{e(copy['total'])}</dt><dd data-veneers-total>${default_total:,}</dd></div>
                <div><dt data-veneers-savings-label>{initial_savings}</dt><dd data-veneers-savings>${default_savings:,}</dd></div>
              </dl>
              <p class="veneer-note">{e(copy['demo'])}</p>
            </form>
          </div>'''
    else:
        demo = ''
    return f'''
      <section class="section investment" id="investment">
        <div class="wrap investment-grid">
          <div class="investment-copy">
            <p class="eyebrow">{e(d['savingsLabel'])}</p>
            <h2>{title}</h2><p>{intro}</p>
            <div class="calc-cta veneer-consultation">{action}</div>
          </div>
          {demo}
        </div>
      </section>'''


def render_smile_comparison(key, lang, title, *, high_priority=False):
    if lang == 'es':
        before, after = 'Antes', 'Después'
        label = 'Ajustar la comparación entre antes y después'
        alt_before = 'Sonrisa en el punto de partida'
        alt_after = 'Sonrisa con el diseño aplicado'
    else:
        before, after = 'Before', 'After'
        label = 'Adjust the before and after comparison'
        alt_before = 'Smile before the design'
        alt_after = 'Smile with the design applied'

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
          aria-label="{e(f'{title}. {label}')}">
        <span class="smile-comparison__knob" aria-hidden="true">↔</span>
      </div>
    </figure>'''

def render_smile_sections(d, lang):
    if not show_examples:
        portrait = f'''
          <picture class="signature-portrait">
            <source type="image/avif" srcset="/assets/editorial-smile-800.avif 800w, /assets/editorial-smile.avif 1536w"
              sizes="(max-width: 760px) 90vw, 48vw">
            <img src="/assets/editorial-smile.webp" width="1536" height="1024" alt="{e(d['imageAlt'])}" fetchpriority="high">
          </picture>'''
        return portrait, ''
    hero = f'''
      <div class="signature-visual">
        <div class="signature-visual-head"><span>{e(d['heroVisualTitle'])}</span><span>{e(d['heroVisualHint'])}</span></div>
        {render_smile_comparison('hero', lang, d['heroVisualTitle'], high_priority=True)}
      </div>'''
    gallery = f'''
      <section class="section paper smile-results" id="results" aria-labelledby="results-title">
        <div class="wrap results-layout">
          <div class="results-copy">
            <p class="eyebrow">{e(d['resultsLabel'])}</p><h2 id="results-title">{lines(d['resultsTitle'])}</h2>
            <p>{e(d['resultsCopy'])}</p><a class="text-button" href="#treatments">{e(d['secondary'])}</a>
          </div>
          <div class="results-visual"><p>{e(d['resultsExample'])}</p>{render_smile_comparison('gallery', lang, d['resultsExample'])}</div>
        </div>
      </section>'''
    return hero, gallery

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
    recommendations = ''.join(
        f"<li><h3>{e(item['title'])}</h3><p>{e(item['text'])}</p></li>"
        for item in recs['items']
    )
    return dict(recsTitle=e(recs['title']), recsIntro=e(recs['intro']), recs=recommendations)

def render_reviews(d):
    if not show_examples:
        return ''
    stories = d['stories']
    cards = ''.join(
        f"<figure><figcaption>{e(item['caption'])}</figcaption>"
        f"<blockquote><p>“{e(item['quote'])}”</p></blockquote>"
        f"<p class=\"review-title\">{e(item['title'])}</p></figure>"
        for item in stories['items']
    )
    return f'''
      <section class="section story-section" aria-labelledby="stories-title">
        <div class="wrap">
          <div class="section-heading"><h2 id="stories-title">{e(stories['title'])}</h2><p>{e(stories['intro'])}</p></div>
          <div class="story-grid review-track" id="review-track" data-review-track role="region" aria-labelledby="stories-title" tabindex="0">
            {cards}
          </div>
          <div class="review-controls" hidden>
            <button class="review-control" type="button" data-review-step="-1" aria-controls="review-track" aria-label="{e(d['reviewPrev'])}">‹</button>
            <button class="review-control" type="button" data-review-step="1" aria-controls="review-track" aria-label="{e(d['reviewNext'])}">›</button>
          </div>
        </div>
      </section>'''

def render_destination_cards(places):
    cards = []
    for slug, title, description, alt in places:
        asset = f'/assets/destination-{slug}'
        cards.append(f'''
          <figure class="destination-card">
            <picture>
              <source type="image/avif" srcset="{asset}-480.avif 480w, {asset}-840.avif 840w"
                sizes="(max-width: 760px) 90vw, 30vw">
              <img src="{asset}-840.webp" width="840" height="560" alt="{e(alt)}" loading="lazy" decoding="async">
            </picture>
            <figcaption><strong>{e(title)}</strong><span>{e(description)}</span></figcaption>
          </figure>''')
    return ''.join(cards)

for lang, d in CONTENT.items():
    d = d | EDITORIAL[lang]
    path = '/' if lang == 'es' else '/en/'
    sections = ['results', 'treatments', 'investment', 'team', 'journey', 'faq']
    nav = ''.join(
        f'<a href="#{section}">{e(label)}</a>'
        for section, label in zip(sections, d['nav'])
        if show_examples or section != 'results'
    )
    studio_tabs, treatments = render_treatments(d)
    doctors = render_doctors(d)
    steps = render_journey(d)
    faqs = ''.join(f'<details><summary>{e(q)}<span aria-hidden="true">+</span></summary><p>{e(a)}</p></details>' for q,a in d['faqs'])
    seo = ''
    if url:
        seo = f'<link rel="canonical" href="{e(url+path)}"><link rel="alternate" hreflang="en-US" href="{e(url)}/en/"><link rel="alternate" hreflang="es-PR" href="{e(url)}/"><link rel="alternate" hreflang="x-default" href="{e(url)}/"><meta property="og:url" content="{e(url+path)}"><meta property="og:image" content="{e(url)}/assets/editorial-smile.webp">'
        schema = {'@context':'https://schema.org','@type':'Organization','name':'Sonrisas Colombia','url':url,'logo':url+'/assets/logo-onix.webp'}
        seo += '<script type="application/ld+json">'+json.dumps(schema, ensure_ascii=False).replace('<','\\u003c')+'</script>'
    values = {k:lines(v) for k,v in d.items() if isinstance(v,str)}
    values.update(home=path,year=str(date.today().year),navTitle=e(d['nav'][0]),nav=nav,treatments=treatments,doctors=doctors,steps=steps,faqs=faqs,seo=seo,robots='index,follow' if indexable else 'noindex,nofollow',ctaButton=cta(d['cta']),shortButton=cta(d['shortCta'],'button button-small'),strip=''.join(f'<span>{e(s)}</span>' for s in d['strip']),compareHead=''.join(f'<th scope="col">{e(s)}</th>' for s in d['compareHeaders']),compareBody=''.join('<tr>'+f'<th scope="row">{e(row[0])}</th>'+''.join(f'<td>{e(s)}</td>' for s in row[1:])+'</tr>' for row in d['compareRows']),client=json.dumps({k:d[k] for k in ['locale','savings','extra','neutral','invalid','total','homeLabel','percentage','contactMessage','contactUnavailable','difference']},ensure_ascii=False).replace('<','\\u003c'))
    values.update(render_editorial(d))
    hero_visual, results_section = render_smile_sections(d, lang)
    values.update(
        studioTabs=studio_tabs, otherLocale='es-PR' if lang == 'en' else 'en-US',
        heroVisual=hero_visual, resultsSection=results_section, storiesSection=render_reviews(d),
        veneerEstimator=render_veneer_estimator(lang, d, show_examples=show_examples),
        placesCards=render_destination_cards(d['places']),
        flowLinks=''.join(f'<a href="#{target}">{e(label)}</a>'
                          for target, label in zip(('contact', 'treatments', 'journey'), d['flow'])),
        navTitle=e(d['nav'][1]),
    )
    target = SITE / path.lstrip('/') / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    html = TEMPLATE.substitute(values)
    target.write_text(html, encoding='utf-8')
    if lang == 'es':
        alias = SITE / 'es'
        alias.mkdir(exist_ok=True)
        (alias/'index.html').write_text(html, encoding='utf-8')

config = {'whatsapp':os.getenv('PUBLIC_WHATSAPP_NUMBER','') or '573044650264','siteUrl':url,'ga4':os.getenv('PUBLIC_GA4_ID',''),'metaPixel':os.getenv('PUBLIC_META_PIXEL_ID',''),'gtm':os.getenv('PUBLIC_GTM_ID',''),'trackingEnabled':False}
(SITE/'assets/config.js').write_text('window.SONRISAS = '+json.dumps(config)+';\n',encoding='utf-8')
(SITE/'robots.txt').write_text('User-agent: *\n'+('Allow: /\nSitemap: '+url+'/sitemap.xml\n' if indexable else 'Disallow: /\n'), encoding='utf-8')
sitemap = SITE/'sitemap.xml'
if url:
    sitemap.write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+e(url+p)+'</loc></url>' for p in ['/','/en/'])+'</urlset>',encoding='utf-8')
elif sitemap.exists():
    sitemap.unlink()
print('Built English and Spanish. Indexing:', indexable)
