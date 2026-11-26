"""Genera el sitio bilingüe estático usando solo la biblioteca estándar de Python.

Precios: se cambian en un solo lugar, PRICES (USD por diente). Se reflejan en la
portada, tratamientos, calculadora, tabla comparativa y preguntas frecuentes.

Contenido pendiente: cualquier texto que empiece por "Aquí pones:" se muestra en
el sitio como un recuadro punteado para que sepas qué reemplazar.
"""
import json
import math
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

DEFAULT_SITE_URL = 'https://sonrisascolombia.com'
DEFAULT_WHATSAPP = '573044650264'

url = (os.getenv('PUBLIC_SITE_URL', '') or DEFAULT_SITE_URL).rstrip('/')
parsed = urlparse(url)
if parsed.scheme != 'https' or not parsed.netloc or parsed.query or parsed.fragment:
    raise ValueError('PUBLIC_SITE_URL must be a clean absolute HTTPS URL')
indexable = os.getenv('ENABLE_INDEXING', 'false').lower() == 'true'
whatsapp = os.getenv('PUBLIC_WHATSAPP_NUMBER', '') or DEFAULT_WHATSAPP

# Valores aproximados de referencia (USD por diente), investigados en nov. 2026.
# Colombia: resina 120–400, porcelana 300–650. Puerto Rico: porcelana 600–900.
# EE. UU.: resina ~800 promedio, porcelana ~1.450 promedio.
# >>> Reemplazar por los precios reales de Sonrisas Colombia. <<<
PRICES = {
    'resin': {'colombia': 180, 'pr': 400, 'us': 800},
    'porcelain': {'colombia': 420, 'pr': 750, 'us': 1450},
}

PLACEHOLDER = 'Aquí pones:'


def save_pct(market):
    pct = min(1 - p['colombia'] / p[market] for p in PRICES.values()) * 100
    return math.floor(pct / 5) * 5


TOKENS = {
    'resin': f"{PRICES['resin']['colombia']:,}",
    'porcelain': f"{PRICES['porcelain']['colombia']:,}",
    'saveUs': str(save_pct('us')),
    'savePr': str(save_pct('pr')),
}


def fill(value):
    text = str(value)
    for key, token in TOKENS.items():
        text = text.replace('{' + key + '}', token)
    return text


def e(value):
    return escape(fill(value), quote=True)


def lines(value):
    return e(value).replace('\n', '<br>')


def is_ph(value):
    return str(value).startswith(PLACEHOLDER)


def ph(text, kind='block', tag='Contenido pendiente'):
    body = e(text)[len(PLACEHOLDER):].strip()
    return (f'<div class="ph ph--{kind}" role="note"><span class="ph__tag">{e(tag)}</span>'
            f'<p><strong>{e(PLACEHOLDER)}</strong> {body}</p></div>')


def text_or_ph(value, klass, kind='inline'):
    if is_ph(value):
        return ph(value, kind)
    return f'<p class="{klass}">{e(value)}</p>'


WA_ICON = ('<svg class="i-wa" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.1 5.1 0 0 0 1.1 2.7 11.7 11.7 0 0 0 4.5 4c1.7.7 2.3.8 3.1.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.1-1.2l-.4-.2Z"/></svg>')
CHECK = '<svg class="i-check" viewBox="0 0 20 20" aria-hidden="true"><path d="M4 10.5l4 4 8-9" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
PIN = '<svg class="i-pin" viewBox="0 0 16 20" aria-hidden="true"><path d="M8 19s6-6.2 6-11A6 6 0 0 0 2 8c0 4.8 6 11 6 11Z" fill="none" stroke="currentColor" stroke-width="1.4"/><circle cx="8" cy="8" r="2.2" fill="currentColor"/></svg>'


def wa_button(label, klass='btn btn--gold', attrs=''):
    return f'<button type="button" class="{klass}" data-wa {attrs}>{WA_ICON}<span>{e(label)}</span></button>'


def picture(base, alt, sizes, *, widths=None, w=720, h=480, fmt_widths=None, lazy=True, klass=''):
    srcset = ', '.join(f'{base}-{x}.avif {x}w' for x in (widths or [w]))
    loading = 'loading="lazy" decoding="async"' if lazy else 'fetchpriority="high"'
    return (f'<picture class="{klass}"><source type="image/avif" srcset="{srcset}" sizes="{sizes}">'
            f'<img src="{base}-{fmt_widths or w}.webp" width="{w}" height="{h}" alt="{e(alt)}" {loading}></picture>')


# ---------------------------------------------------------------- secciones

def render_comparison(key, lang, title, *, hero=False):
    if lang == 'es':
        before, after = 'Antes', 'Después'
        label = 'Ajustar la comparación entre antes y después'
        alt_before = 'Ilustración de la sonrisa inicial de una persona ficticia'
        alt_after = 'Ilustración de la misma sonrisa con cambios simulados'
    else:
        before, after = 'Before', 'After'
        label = 'Adjust the before and after comparison'
        alt_before = 'Illustration of a fictional person’s initial smile'
        alt_after = 'Illustration of the same smile with simulated changes'
    prefix = f'/assets/smile-example-{key}'

    def photo(state, alt, first=False):
        loading = 'fetchpriority="high"' if hero and first else 'loading="lazy" decoding="async"'
        return (f'<picture class="cmp__photo cmp__photo--{state}"><source type="image/avif" srcset="{prefix}-{state}.avif">'
                f'<img src="{prefix}-{state}.webp" width="864" height="648" alt="{e(alt)}" {loading}></picture>')

    sweep = ' data-autosweep' if hero else ''
    return f'''<figure class="cmp" data-cmp{sweep} data-before="{e(before)}" data-after="{e(after)}">
      <div class="cmp__stage">
        {photo('after', alt_after, True)}{photo('before', alt_before)}
        <span class="cmp__badge cmp__badge--before" aria-hidden="true">{e(before)}</span>
        <span class="cmp__badge cmp__badge--after" aria-hidden="true">{e(after)}</span>
        <span class="cmp__line" aria-hidden="true"></span>
        <input class="cmp__range" type="range" min="0" max="100" value="50" aria-label="{e(title + '. ' + label)}">
        <span class="cmp__knob" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M9 6l-6 6 6 6M15 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
      </div>
    </figure>'''


def render_hero(d, lang):
    title_lines = ''.join(f'<span class="ln"><span>{e(t)}</span></span>' for t in d['heroTitle'].split('\n'))
    proof = ''.join(f'<li>{CHECK}<span>{e(p)}</span></li>' for p in d['heroProof'])
    cities = ''.join(f'<li><a href="#ciudades" data-city-link="{c["id"]}">{PIN}{e(c["name"])}</a></li>' for c in d['cities'])
    return f'''
<section class="hero" aria-labelledby="hero-title">
  <div class="hero__glow" aria-hidden="true"></div>
  <div class="wrap hero__grid">
    <div class="hero__copy">
      <p class="kicker" data-intro="1">{e(d['heroKicker'])}</p>
      <h1 id="hero-title" class="hero__title">{title_lines}</h1>
      <p class="hero__lead" data-intro="3">{e(d['heroLead'])}</p>
      <div class="hero__ctas" data-intro="4">
        {wa_button(d['cta'], 'btn btn--gold btn--lg')}
        <a class="link link--light" href="#precios">{e(d['heroSecondary'])}</a>
      </div>
      <ul class="hero__proof" data-intro="5">{proof}</ul>
    </div>
    <div class="hero__visual" data-intro="2">
      <div class="frame">
        <div class="frame__head"><span>{e(d['heroVisualTitle'])}</span><span class="frame__hint">{e(d['heroVisualHint'])}</span></div>
        {render_comparison('hero', lang, d['heroVisualTitle'], hero=True)}
      </div>
    </div>
  </div>
  <div class="wrap cityband" data-intro="6">
    <span class="cityband__label">{e(d['cityStrip'])}</span>
    <ul>{cities}</ul>
    <span class="cityband__note">{e(d['priceNote'])}</span>
  </div>
</section>'''


def render_results(d, lang):
    slots = ''.join(ph(s, 'media') for s in d['caseSlots'])
    return f'''
<section class="sec sec--ivory" id="resultados" aria-labelledby="results-title">
  <div class="wrap results">
    <div class="results__copy" data-reveal>
      <h2 id="results-title">{lines(d['resultsTitle'])}</h2>
      <p class="lead">{e(d['resultsLead'])}</p>
      {wa_button(d['cta'], 'btn btn--ink')}
    </div>
    <div class="results__visual" data-reveal>
      <p class="frame__label">{e(d['resultsExample'])}</p>
      {render_comparison('gallery', lang, d['resultsExample'])}
    </div>
  </div>
  <div class="wrap results__cases">
    <div class="results__pair">{slots}</div>
    {ph(d['caseVideo'], 'video')}
  </div>
</section>'''


def render_treatments(d):
    tabs, panels = [], []
    for i, t in enumerate(d['treatments']):
        slug = t['id']
        name = e(t['name'])
        tabs.append(f'<button type="button" class="tabs__tab" id="tab-{slug}" data-tab="{slug}">{name}</button>')
        points = ''.join(f'<li>{CHECK}<span>{e(p)}</span></li>' for p in t['points'])
        price = ('' if not t['price'] else ph(t['price'], 'inline') if is_ph(t['price'])
                 else f'<p class="treat__price">{e(t["price"])}</p>')
        image = picture(f'/assets/studio-{slug}', d['treatmentImages'][slug], '(max-width: 760px) 92vw, 50vw',
                        widths=[720, 1200], w=720, h=480, klass='treat__img')
        panels.append(f'''
      <article class="treat" id="{slug}" data-panel="{slug}">
        {image}
        <div class="treat__copy">
          <h3>{name}</h3>
          {price}
          <p class="treat__time">{e(t['time'])}</p>
          <p>{e(t['text'])}</p>
          <ul class="checks">{points}</ul>
          {wa_button(d['cta'], 'btn btn--gold', f'data-wa-treatment="{name}"')}
        </div>
      </article>''')
    head = ''.join(f'<th scope="col">{e(h)}</th>' for h in d['compareHeaders'])
    body = ''.join('<tr><th scope="row">' + e(r[0]) + '</th>' + ''.join(f'<td>{e(c)}</td>' for c in r[1:]) + '</tr>'
                   for r in d['compareRows'])
    return f'''
<section class="sec sec--onyx" id="tratamientos" aria-labelledby="treat-title">
  <div class="wrap">
    <div class="sec__head" data-reveal>
      <h2 id="treat-title">{lines(d['treatmentsTitle'])}</h2>
      <p class="lead">{e(d['treatmentsLead'])}</p>
    </div>
    <div class="tabs" role="tablist" aria-labelledby="treat-title" data-tabs hidden>{''.join(tabs)}</div>
    <div class="treats">{''.join(panels)}</div>
    <details class="compare">
      <summary><span>{e(d['compareTitle'])}</span><span class="plus" aria-hidden="true"></span></summary>
      <div class="compare__scroll" role="region" aria-label="{e(d['compareTitle'])}" tabindex="0">
        <table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>
      </div>
    </details>
  </div>
</section>'''


def render_calculator(d):
    prices = e(json.dumps(PRICES, separators=(',', ':')))
    labels = {
        'resin': d['calcResin'], 'porcelain': d['calcPorcelain'], 'pr': d['calcPR'], 'us': d['calcUS'],
        'home': d['calcHome'], 'pct': d['calcSavingsPct'], 'message': d['calcMessage'], 'invalid': d['calcInvalid'],
    }
    return f'''
<section class="sec sec--stone" id="precios" aria-labelledby="calc-title">
  <div class="wrap calc">
    <div class="calc__copy" data-reveal>
      <h2 id="calc-title">{e(d['calcTitle'])}</h2>
      <p class="lead">{e(d['calcLead'])}</p>
      <form class="calc__form" data-calc data-prices="{prices}" data-labels="{e(json.dumps(labels, ensure_ascii=False))}">
        <fieldset class="seg">
          <legend>{e(d['calcMaterial'])}</legend>
          <label><input type="radio" name="material" value="resin" checked><span>{e(d['calcResin'])}</span></label>
          <label><input type="radio" name="material" value="porcelain"><span>{e(d['calcPorcelain'])}</span></label>
        </fieldset>
        <div class="qty">
          <label for="calc-qty">{e(d['calcQuantity'])}</label>
          <div class="qty__row">
            <button type="button" class="qty__btn" data-step="-1" aria-label="−1">−</button>
            <input id="calc-qty" name="quantity" type="number" inputmode="numeric" min="1" max="28" step="1" value="8" aria-describedby="calc-qty-hint">
            <button type="button" class="qty__btn" data-step="1" aria-label="+1">+</button>
          </div>
          <input class="qty__range" type="range" min="1" max="20" value="8" aria-hidden="true" tabindex="-1">
          <p class="hint" id="calc-qty-hint" data-calc-hint>{e(d['calcQuantityHint'])}</p>
        </div>
        <fieldset class="seg">
          <legend>{e(d['calcMarket'])}</legend>
          <label><input type="radio" name="market" value="pr" checked><span>{e(d['calcPR'])}</span></label>
          <label><input type="radio" name="market" value="us"><span>{e(d['calcUS'])}</span></label>
        </fieldset>
      </form>
    </div>
    <div class="receipt" data-reveal aria-live="polite">
      <div class="receipt__paper">
        <p class="receipt__title">{e(d['calcReceiptTitle'])}<span>USD</span></p>
        <p class="receipt__item" data-r-item>8 × {e(d['calcResin'])}</p>
        <dl>
          <div class="receipt__row receipt__row--home"><dt data-r-home-label></dt><dd data-r-home>—</dd></div>
          <div class="receipt__row"><dt>{e(d['calcColombia'])}</dt><dd data-r-col>—</dd></div>
        </dl>
        <div class="receipt__save">
          <p>{e(d['calcSavings'])}</p>
          <p class="receipt__big" data-r-save>—</p>
          <p class="chip" data-r-pct></p>
        </div>
        <p class="receipt__travel" data-r-travel>{e(d['calcTravel'])}</p>
        <button type="button" class="btn btn--gold btn--block" data-wa data-wa-quote>{WA_ICON}<span>{e(d['calcSend'])}</span></button>
        <p class="fine">{e(d['calcNote'])}</p>
      </div>
    </div>
  </div>
</section>'''


def render_includes(d):
    items = ''.join(f'<li>{CHECK}<div><h3>{e(t)}</h3><p>{e(x)}</p></div></li>' for t, x in d['includes'])
    pending = ''.join(ph(p, 'inline') for p in d['includesPlaceholders'])
    return f'''
<section class="sec sec--ivory" id="incluye" aria-labelledby="inc-title">
  <div class="wrap includes">
    <div class="sec__head sec__head--stack" data-reveal>
      <h2 id="inc-title">{lines(d['includesTitle'])}</h2>
      <p class="lead">{e(d['includesLead'])}</p>
      {wa_button(d['cta'], 'btn btn--ink')}
    </div>
    <div>
      <ul class="includes__list" data-reveal>{items}</ul>
      {f'<div class="includes__pending">{pending}</div>' if pending else ''}
    </div>
  </div>
</section>'''


def render_steps(d):
    steps = ''.join(f'<li data-reveal><span class="step__n">{i}</span><h3>{e(t)}</h3><p>{e(x)}</p></li>'
                    for i, (t, x) in enumerate(d['steps'], 1))
    plane = '<path fill="currentColor" d="M21 12c0-.6-.5-1-1-1h-5.5L9.6 3.2a.5.5 0 0 0-.4-.2H7.8l2.4 8H5.1L3.4 9H2l1 3-1 3h1.4l1.7-2h5.1l-2.4 8h1.4c.2 0 .3-.1.4-.2l4.9-7.8H20c.5 0 1-.4 1-1Z"/>'
    return f'''
<section class="sec sec--onyx steps" id="como-funciona" aria-labelledby="steps-title">
  <div class="wrap">
    <div class="sec__head" data-reveal>
      <h2 id="steps-title">{lines(d['stepsTitle'])}</h2>
      <p class="lead">{e(d['travelNote'])}</p>
    </div>
    <div class="route" data-route aria-hidden="true">
      <svg viewBox="0 0 1200 220" preserveAspectRatio="none">
        <path class="route__track" d="M40 190 C 300 -30, 900 -30, 1160 190"/>
        <path class="route__line" pathLength="1" d="M40 190 C 300 -30, 900 -30, 1160 190"/>
      </svg>
      <span class="route__dot route__dot--from"></span><span class="route__dot route__dot--to"></span><span class="route__plane"><svg viewBox="0 0 24 24">{plane}</svg></span>
      <span class="route__end route__end--from">{PIN}{e(d['stepsRouteFrom'])}</span>
      <span class="route__end route__end--to">{PIN}<span data-route-city>Colombia</span></span>
    </div>
    <ol class="steps__list">{steps}</ol>
    <div class="steps__cta">{wa_button(d['cta'], 'btn btn--gold btn--lg')}</div>
  </div>
</section>'''


def render_cities(d):
    rows, media = [], []
    for i, c in enumerate(d['cities']):
        pick = e(d['citiesPick']).replace('{city}', e(c['name']))
        address = '' if not c['address'] else ph(c['address'], 'inline') if is_ph(c['address']) else f'<p>{e(c["address"])}</p>'
        rows.append(f'''
        <li class="city" data-city="{c['id']}" data-city-name="{e(c['name'])}">
          <button type="button" class="city__head" aria-pressed="false" data-city-pick>
            <span class="city__name">{e(c['name'])}</span><span class="city__go">{e(pick)}</span>
          </button>
          <div class="city__body"><div class="city__inner"><div class="city__pad"><p>{e(c['note'])}</p>{address}</div></div></div>
        </li>''')
        if c['photo']:
            inner = ph(c['photo'], 'media')
        else:
            src = {'pereira': 'cocora'}.get(c['id'], c['id'])
            inner = picture(f'/assets/destination-{src}', d['cityAlts'][c['id']], '(max-width: 760px) 92vw, 44vw',
                            widths=[480, 840], w=840, h=560, klass='city__img')
        media.append(f'<div class="cities__media-item" data-city-media="{c["id"]}">{inner}</div>')
    return f'''
<section class="sec sec--ivory" id="ciudades" aria-labelledby="cities-title">
  <div class="wrap">
    <div class="sec__head" data-reveal>
      <h2 id="cities-title">{lines(d['citiesTitle'])}</h2>
      <p class="lead">{e(d['citiesLead'])}</p>
    </div>
    <div class="cities">
      <ul class="cities__list">{''.join(rows)}</ul>
      <div class="cities__media">{''.join(media)}</div>
    </div>
  </div>
</section>'''


def render_team(d):
    kath, van = d['doctors']
    photos = []
    for angle, alt in zip(('feature', 'clinic', 'profile'), d['portraitAlts']):
        widths = [420, 720] if angle == 'feature' else [420]
        photos.append(picture(f'/assets/katherine-{angle}', alt, '(max-width: 760px) 86vw, 30vw',
                              widths=widths, w=420, h=560, klass=f'team__ph team__ph--{angle}'))

    def profile(doc):
        return f'''<div class="doc">
          <p class="doc__role">{e(doc['role'])}</p>
          <h3>{e(d['doctorPrefix'])} {e(doc['name'])}</h3>
          <p>{e(doc['text'])}</p>
          {ph(doc['credentials'], 'inline') if is_ph(doc['credentials']) else '<p class="doc__cred">' + e(doc['credentials']) + '</p>'}
        </div>'''
    return f'''
<section class="sec sec--stone" id="doctoras" aria-labelledby="team-title">
  <div class="wrap">
    <div class="sec__head" data-reveal>
      <h2 id="team-title">{lines(d['teamTitle'])}</h2>
      <p class="lead">{e(d['teamLead'])}</p>
    </div>
    <div class="team">
      <article class="team__card team__card--k" data-reveal>
        <div class="team__mosaic">{''.join(photos)}</div>
        {profile(kath)}
      </article>
      <article class="team__card team__card--v" data-reveal>
        {ph(d['vanessaPhoto'], 'portrait')}
        {profile(van)}
      </article>
    </div>
    <div class="team__cta">{wa_button(d['cta'], 'btn btn--ink')}</div>
  </div>
</section>'''


def render_reviews(d):
    cards = ''.join(f'<li>{ph(r, "quote", "Reseña pendiente")}</li>' for r in d['reviews'])
    return f'''
<section class="sec sec--onyx" id="opiniones" aria-labelledby="rev-title">
  <div class="wrap">
    <div class="sec__head" data-reveal>
      <h2 id="rev-title">{lines(d['reviewsTitle'])}</h2>
      <p class="lead">{e(d['reviewsLead'])}</p>
    </div>
    <ul class="reviews">{cards}</ul>
  </div>
</section>'''


def render_faq(d):
    items = ''.join(f'<details class="faq__item"><summary><span>{e(q)}</span><span class="plus" aria-hidden="true"></span></summary><div class="faq__a"><p>{e(a)}</p></div></details>'
                    for q, a in d['faqs'])
    return f'''
<section class="sec sec--ivory" id="preguntas" aria-labelledby="faq-title">
  <div class="wrap faq">
    <div data-reveal><h2 id="faq-title">{lines(d['faqTitle'])}</h2>{wa_button(d['cta'], 'btn btn--ink')}</div>
    <div class="faq__list">{items}</div>
  </div>
</section>'''


GUIDE_ICONS = [
    '<svg viewBox="0 0 64 64"><circle cx="32" cy="27" r="15"/><path d="M24 31c2.5 4 13.5 4 16 0M26 23h.01M38 23h.01M18 58c2-9 8-13 14-13s12 4 14 13"/></svg>',
    '<svg viewBox="0 0 64 64"><path d="M38 12c-9 0-15 7-15 15 0 3-3 6-4 8l4 1v6c0 3 2 4 5 4h3v8M38 12c7 0 12 6 12 14 0 6-3 10-6 13v15"/><path d="M27 36c2 1 5 1 7-1"/></svg>',
    '<svg viewBox="0 0 64 64"><path d="M8 30c8-8 40-8 48 0-8 12-40 12-48 0Z"/><path d="M18 27v6M26 26v8M34 26v8M42 27v6M14 30h36"/></svg>',
]


def render_closing(d):
    guide = ''.join(f'<li><span class="guide__icon" aria-hidden="true">{icon}</span><span>{e(t)}</span></li>'
                    for icon, t in zip(GUIDE_ICONS, d['photoGuide']))
    return f'''
<section class="closing" id="contacto" aria-labelledby="closing-title">
  <div class="wrap closing__in">
    <h2 id="closing-title" data-reveal>{lines(d['closingTitle'])}</h2>
    <p class="lead" data-reveal>{e(d['closingLead'])}</p>
    <ul class="guide" data-reveal>{guide}</ul>
    <div class="closing__ctas">{wa_button(d['cta'], 'btn btn--gold btn--lg')}</div>
  </div>
</section>'''


# ---------------------------------------------------------------- página

SECTIONS = ['resultados', 'precios', 'como-funciona', 'ciudades', 'doctoras', 'preguntas']

for lang, d in CONTENT.items():
    path = '/' if lang == 'es' else '/en/'
    nav = ''.join(f'<a href="#{s}">{e(label)}</a>' for s, label in zip(SECTIONS, d['nav']))
    schema = {
        '@context': 'https://schema.org', '@type': 'Dentist', 'name': 'Sonrisas Colombia', 'url': url + path,
        'logo': url + '/assets/logo-onix.webp', 'image': url + '/assets/editorial-smile.webp',
        'areaServed': ['Puerto Rico', 'United States'], 'telephone': '+' + whatsapp,
        'address': [{'@type': 'PostalAddress', 'addressLocality': c['name'], 'addressCountry': 'CO'} for c in d['cities']],
    }
    seo = (f'<link rel="canonical" href="{e(url + path)}">'
           f'<link rel="alternate" hreflang="es-PR" href="{e(url)}/"><link rel="alternate" hreflang="en-US" href="{e(url)}/en/">'
           f'<link rel="alternate" hreflang="x-default" href="{e(url)}/">'
           f'<meta property="og:url" content="{e(url + path)}"><meta property="og:image" content="{e(url)}/assets/editorial-smile.webp">'
           '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c') + '</script>')
    client = {k: fill(d[k]) for k in ('contactMessage', 'contactCity', 'contactTreatment')}
    sections = ''.join([
        render_hero(d, lang), render_results(d, lang), render_treatments(d), render_calculator(d),
        render_includes(d), render_steps(d), render_cities(d), render_team(d), render_reviews(d),
        render_faq(d), render_closing(d),
    ])
    values = dict(
        locale=e(d['locale']), title=e(d['title']), description=e(d['description']),
        robots='index,follow' if indexable else 'noindex,nofollow', seo=seo, home=path,
        skip=e(d['skip']), menu=e(d['menu']), close=e(d['close']), nav=nav,
        otherUrl=d['otherUrl'], otherLocale=d['otherLocale'], otherLabel=e(d['otherLabel']),
        headerCta=wa_button(d['headerCta'], 'btn btn--gold btn--sm hdr__cta'),
        sections=sections, footerLine=e(d['footerLine']), footerLegal=(ph(d['footerLegal'], 'inline') if is_ph(d['footerLegal']) else e(d['footerLegal'])),
        privacy=e(d['privacy']), copyright=e(d['copyright']), year=str(date.today().year),
        privacyTitle=e(d['privacyTitle']), privacyText=e(d['privacyText']), privacyMore=ph(d['privacyMore'], 'inline'),
        floating=wa_button(d['ctaShort'], 'fab', f'aria-label="{e(d["headerCta"])}"'),
        mobileBar=wa_button(d['headerCta'], 'btn btn--gold btn--block'),
        client=json.dumps(client, ensure_ascii=False).replace('<', '\\u003c'),
    )
    html = TEMPLATE.substitute(values)
    target = SITE / path.lstrip('/') / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding='utf-8')
    if lang == 'es':
        (SITE / 'es').mkdir(exist_ok=True)
        (SITE / 'es' / 'index.html').write_text(html, encoding='utf-8')

config = {'whatsapp': whatsapp, 'siteUrl': url, 'ga4': os.getenv('PUBLIC_GA4_ID', ''),
          'metaPixel': os.getenv('PUBLIC_META_PIXEL_ID', ''), 'gtm': os.getenv('PUBLIC_GTM_ID', ''),
          'trackingEnabled': False}
(SITE / 'assets/config.js').write_text('window.SONRISAS = ' + json.dumps(config) + ';\n', encoding='utf-8')
(SITE / 'robots.txt').write_text('User-agent: *\n' + ('Allow: /\nSitemap: ' + url + '/sitemap.xml\n' if indexable else 'Disallow: /\n'), encoding='utf-8')
(SITE / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                  + ''.join('<url><loc>' + e(url + p) + '</loc></url>' for p in ['/', '/en/']) + '</urlset>', encoding='utf-8')
print(f'Built English and Spanish for {url}. Indexing: {indexable}. WhatsApp: +{whatsapp}')
