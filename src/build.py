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
PAGES = json.loads((BASE / 'src/pages.json').read_text(encoding='utf-8'))
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


PRICES_UPDATED = '2026-11-26'  # fecha de los precios de referencia (schema dateModified)

TOKENS = {
    'resin': f"{PRICES['resin']['colombia']:,}",
    'porcelain': f"{PRICES['porcelain']['colombia']:,}",
    'saveUs': str(save_pct('us')),
    'savePr': str(save_pct('pr')),
    'prResin': f"{PRICES['resin']['pr']:,}", 'usResin': f"{PRICES['resin']['us']:,}",
    'prPorcelain': f"{PRICES['porcelain']['pr']:,}", 'usPorcelain': f"{PRICES['porcelain']['us']:,}",
    'coPorc8': f"{PRICES['porcelain']['colombia'] * 8:,}", 'prPorc8': f"{PRICES['porcelain']['pr'] * 8:,}",
    'usPorc8': f"{PRICES['porcelain']['us'] * 8:,}",
    'savePorc8Pr': f"{(PRICES['porcelain']['pr'] - PRICES['porcelain']['colombia']) * 8:,}",
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


def render_steps(d, to='Colombia'):
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
      <span class="route__end route__end--to">{PIN}<span data-route-city>{e(to)}</span></span>
    </div>
    <ol class="steps__list">{steps}</ol>
    <div class="steps__cta">{wa_button(d['cta'], 'btn btn--gold btn--lg')}</div>
  </div>
</section>'''


def render_cities(d, P=None, prefix='/'):
    rows, media = [], []

    def city_link(c):
        if not P:
            return ''
        href = prefix + P['cities'][c['id']]['slug'] + '/'
        return f'<a class="link city__more" href="{href}">{e(d["cityPageLink"]).replace("{city}", e(c["name"]))}</a>'

    for i, c in enumerate(d['cities']):
        pick = e(d['citiesPick']).replace('{city}', e(c['name']))
        address = '' if not c['address'] else ph(c['address'], 'inline') if is_ph(c['address']) else f'<p>{e(c["address"])}</p>'
        rows.append(f'''
        <li class="city" data-city="{c['id']}" data-city-name="{e(c['name'])}">
          <button type="button" class="city__head" aria-pressed="false" data-city-pick>
            <span class="city__name">{e(c['name'])}</span><span class="city__go">{e(pick)}</span>
          </button>
          <div class="city__body"><div class="city__inner"><div class="city__pad"><p>{e(c['note'])}</p>{address}{city_link(c)}</div></div></div>
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


def render_faq(d, title=None, faqs=None):
    title = title or d['faqTitle']
    items = ''.join(f'<details class="faq__item"><summary><span>{e(q)}</span><span class="plus" aria-hidden="true"></span></summary><div class="faq__a"><p>{e(a)}</p></div></details>'
                    for q, a in (faqs or d['faqs']))
    return f'''
<section class="sec sec--ivory" id="preguntas" aria-labelledby="faq-title">
  <div class="wrap faq">
    <div data-reveal><h2 id="faq-title">{lines(title)}</h2>{wa_button(d['cta'], 'btn btn--ink')}</div>
    <div class="faq__list">{items}</div>
  </div>
</section>'''


TIP_ICONS = ["<svg viewBox=\"0 0 24 24\"><circle cx=\"12\" cy=\"12\" r=\"4\"/><path d=\"M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4\"/></svg>", "<svg viewBox=\"0 0 24 24\"><path d=\"M13 2 4 14h7l-1 8 9-12h-7z\"/><path d=\"M3 3l18 18\"/></svg>", "<svg viewBox=\"0 0 24 24\"><rect x=\"7\" y=\"2\" width=\"10\" height=\"20\" rx=\"2\"/><path d=\"M11 18h2\"/></svg>", "<svg viewBox=\"0 0 24 24\"><circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M5.6 5.6l12.8 12.8\"/></svg>"]


def render_closing(d):
    cards = ''.join(f'''
      <li class="shot" data-reveal>
        <figure>
          <div class="shot__img">
            <picture><source type="image/avif" srcset="/assets/foto-guia-{g['id']}-360.avif 360w, /assets/foto-guia-{g['id']}-640.avif 640w" sizes="(max-width: 760px) 44vw, 18vw">
            <img src="/assets/foto-guia-{g['id']}-640.webp" width="640" height="640" alt="{e(d['photoExample'])}: {e(g['title'])}" loading="lazy" decoding="async"></picture>
            <span class="shot__n" aria-hidden="true">{i}</span>
          </div>
          <figcaption><h3>{e(g['title'])}</h3><p>{e(g['text'])}</p></figcaption>
        </figure>
      </li>''' for i, g in enumerate(d['photoGuide'], 1))
    tips = ''.join(f'<li><span class="tip__icon" aria-hidden="true">{icon}</span>{e(t)}</li>'
                   for icon, t in zip(TIP_ICONS, d['photoTips']))
    return f'''
<section class="closing" id="contacto" aria-labelledby="closing-title">
  <div class="wrap">
    <div class="closing__head" data-reveal>
      <h2 id="closing-title">{lines(d['closingTitle'])}</h2>
      <p class="lead">{e(d['closingLead'])}</p>
    </div>
    <ol class="shots">{cards}</ol>
    <div class="photo-foot">
      <div class="tips" data-reveal>
        <h3>{e(d['photoTipsTitle'])}</h3>
        <ul>{tips}</ul>
      </div>
      <div class="photo-cta" data-reveal>
        <h3>{e(d['photoCtaTitle'])}</h3>
        <p>{e(d['photoCtaText'])}</p>
        {wa_button(d['photoCta'], 'btn btn--gold btn--lg btn--block', 'data-wa-photos')}
      </div>
    </div>
  </div>
</section>'''


# ---------------------------------------------------------------- página

SECTIONS = ['resultados', 'precios', 'como-funciona', 'ciudades', 'doctoras', 'preguntas']
OG_LOCALE = {'es': 'es_PR', 'en': 'en_US'}


def ld(data):
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('<', '\\u003c') + '</script>'


def faq_schema(faqs):
    return {'@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': fill(q), 'acceptedAnswer': {'@type': 'Answer', 'text': fill(a)}} for q, a in faqs]}


def org_schema(d, home):
    offers = []
    for key, label in (('resin', d['treatments'][0]['name']), ('porcelain', d['treatments'][1]['name'])):
        offers.append({'@type': 'Offer', 'name': label, 'priceCurrency': 'USD', 'price': PRICES[key]['colombia'],
                       'priceSpecification': {'@type': 'UnitPriceSpecification', 'price': PRICES[key]['colombia'],
                                              'priceCurrency': 'USD', 'unitText': 'tooth', 'minPrice': PRICES[key]['colombia']},
                       'availability': 'https://schema.org/InStock', 'url': url + home + '#precios'})
    return {
        '@type': 'Dentist', '@id': url + '/#org', 'name': 'Sonrisas Colombia', 'url': url + '/',
        'logo': url + '/assets/logo-onix.webp', 'image': url + '/assets/og-image.jpg',
        'description': fill(d['description']), 'telephone': '+' + whatsapp, 'priceRange': '$$',
        'currenciesAccepted': 'USD', 'paymentAccepted': 'USD', 'availableLanguage': ['es', 'en'],
        'areaServed': [{'@type': 'Country', 'name': 'Puerto Rico'}, {'@type': 'Country', 'name': 'United States'}],
        'address': [{'@type': 'PostalAddress', 'addressLocality': c['name'], 'addressCountry': 'CO'} for c in d['cities']],
        'contactPoint': {'@type': 'ContactPoint', 'telephone': '+' + whatsapp, 'contactType': 'customer service',
                         'availableLanguage': ['Spanish', 'English']},
        'makesOffer': offers,
        'employee': [{'@type': 'Person', 'name': doc['name'], 'jobTitle': doc['role'], 'worksFor': {'@id': url + '/#org'}}
                     for doc in d['doctors']],
    }


def page_graph(d, lang, path, title, description, *, faqs=None, crumbs=None, extra=()):
    graph = [
        org_schema(d, '/' if lang == 'es' else '/en/'),
        {'@type': 'WebSite', '@id': url + '/#website', 'url': url + '/', 'name': 'Sonrisas Colombia',
         'inLanguage': ['es-PR', 'en-US'], 'publisher': {'@id': url + '/#org'}},
        {'@type': 'WebPage', '@id': url + path + '#page', 'url': url + path, 'name': fill(title),
         'description': fill(description), 'inLanguage': d['locale'], 'isPartOf': {'@id': url + '/#website'},
         'about': {'@id': url + '/#org'}, 'dateModified': PRICES_UPDATED,
         'primaryImageOfPage': url + '/assets/og-image.jpg'},
    ]
    if faqs:
        graph.append(faq_schema(faqs))
    if crumbs:
        graph.append({'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'name': name, 'item': url + href} for i, (name, href) in enumerate(crumbs, 1)]})
    graph.extend(extra)
    return {'@context': 'https://schema.org', '@graph': graph}


def howto_schema(d):
    return {'@type': 'HowTo', 'name': fill(d['closingTitle']).replace('\n', ' '), 'description': fill(d['closingLead']),
            'totalTime': 'PT2M', 'tool': [{'@type': 'HowToTool', 'name': 'Smartphone'}],
            'step': [{'@type': 'HowToStep', 'position': i, 'name': g['title'], 'text': g['text'],
                      'image': f"{url}/assets/foto-guia-{g['id']}-640.webp"} for i, g in enumerate(d['photoGuide'], 1)]}


def breadcrumbs_html(P, crumbs):
    items = []
    for i, (name, href) in enumerate(crumbs):
        last = i == len(crumbs) - 1
        items.append(f'<li><span aria-current="page">{e(name)}</span></li>' if last else f'<li><a href="{href}">{e(name)}</a></li>')
    return f'<nav class="crumbs" aria-label="{e(P["breadcrumbLabel"])}"><ol>{"".join(items)}</ol></nav>'


def price_chips(d, P):
    return ('<ul class="chips">'
            f'<li><span>{e(d["calcResin"])}</span><strong>USD {TOKENS["resin"]}</strong><small>{e(P["perTooth"])}</small></li>'
            f'<li><span>{e(d["calcPorcelain"])}</span><strong>USD {TOKENS["porcelain"]}</strong><small>{e(P["perTooth"])}</small></li>'
            '</ul>')


def page_hero(d, P, crumbs, h1, lead, media='', extra=''):
    title_lines = ''.join(f'<span class="ln"><span>{e(t)}</span></span>' for t in fill(h1).split('\n'))
    return f'''
<section class="hero hero--page" aria-labelledby="hero-title">
  <div class="hero__glow" aria-hidden="true"></div>
  <div class="wrap hero__grid">
    <div class="hero__copy">
      {breadcrumbs_html(P, crumbs)}
      <h1 id="hero-title" class="hero__title hero__title--page">{title_lines}</h1>
      <p class="hero__lead" data-intro="3">{e(lead)}</p>
      <div class="hero__ctas" data-intro="4">{wa_button(d['cta'], 'btn btn--gold btn--lg')}</div>
      <div data-intro="5">{price_chips(d, P)}{extra}</div>
    </div>
    <div class="hero__visual" data-intro="2">{media}</div>
  </div>
</section>'''


def city_media(d, cid):
    src = {'pereira': 'cocora'}.get(cid, cid)
    return picture(f'/assets/destination-{src}', d['cityAlts'][cid], '(max-width: 1080px) 92vw, 46vw',
                   widths=[480, 840], w=840, h=560, lazy=False, klass='page-photo')


def render_why(title, items):
    lis = ''.join(f'<li>{CHECK}<div><h3>{e(t)}</h3><p>{e(x)}</p></div></li>' for t, x in items)
    return f'''
<section class="sec sec--ivory" aria-labelledby="why-title">
  <div class="wrap includes">
    <div class="sec__head sec__head--stack" data-reveal><h2 id="why-title">{e(title)}</h2></div>
    <ul class="includes__list" data-reveal>{lis}</ul>
  </div>
</section>'''


def render_travel(d, P, lang, city_id):
    prefix = '/' if lang == 'es' else '/en/'
    others = ''.join(
        f'<li><a class="link" href="{prefix}{P["cities"][c["id"]]["slug"]}/">{e(P["seeCity"]).replace("{city}", e(c["name"]))}</a></li>'
        for c in d['cities'] if c['id'] != city_id)
    city = P['cities'][city_id]
    return f'''
<section class="sec sec--stone" aria-labelledby="travel-title">
  <div class="wrap travel">
    <div data-reveal><h2 id="travel-title">{e(P['travelTitle'])}</h2><p class="lead">{e(city['travel'])}</p></div>
    <div class="travel__more" data-reveal>
      <h3>{e(P['otherCitiesTitle'])}</h3><ul>{others}</ul>
      <a class="link" href="{prefix}{P['pricePage']['slug']}/">{e(P['seePrices'])}</a>
    </div>
  </div>
</section>'''


def render_price_table(d, P):
    pp = P['pricePage']
    head = ''.join(f'<th scope="col">{e(h)}</th>' for h in pp['tableHeaders'])
    rows = []
    for label, key, n in ((pp['tableRowResin'], 'resin', 1), (pp['tableRowPorcelain'], 'porcelain', 1),
                          (pp['tableRowResin8'], 'resin', 8), (pp['tableRowPorcelain8'], 'porcelain', 8)):
        cells = ''.join(f'<td>USD {PRICES[key][m] * n:,}</td>' for m in ('colombia', 'pr', 'us'))
        rows.append(f'<tr><th scope="row">{e(label)}</th>{cells}</tr>')
    factors = ''.join(f'<li><h3>{e(t)}</h3><p>{e(x)}</p></li>' for t, x in pp['factors'])
    tips = ''.join(f'<li>{CHECK}<span>{e(t)}</span></li>' for t in pp['tips'])
    return f'''
<section class="sec sec--ivory" id="tabla" aria-labelledby="table-title">
  <div class="wrap">
    <h2 id="table-title" class="table-title" data-reveal>{e(pp['tableTitle'])}</h2>
    <div class="price-table" role="region" aria-labelledby="table-title" tabindex="0">
      <table><thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>
    </div>
    <p class="fine table-note">{e(pp['tableNote'])}</p>
    <div class="guide-cols">
      <div data-reveal><h2>{e(pp['factorsTitle'])}</h2><ul class="factors">{factors}</ul></div>
      <div data-reveal><h2>{e(pp['tipsTitle'])}</h2><ul class="checks checks--lg">{tips}</ul></div>
    </div>
  </div>
</section>'''


def footer_extra(d, P, lang):
    prefix = '/' if lang == 'es' else '/en/'
    cities = ''.join(f'<a href="{prefix}{P["cities"][c["id"]]["slug"]}/">{e(P["seeCity"]).replace("{city}", e(c["name"]))}</a>'
                     for c in d['cities'])
    phone = f'+{whatsapp[:2]} {whatsapp[2:5]} {whatsapp[5:8]} {whatsapp[8:]}'
    return f'''
  <div class="wrap ftr__cols">
    <div><h2 class="ftr__h">{e(d['phoneLabel'])}</h2><a class="ftr__phone" href="tel:+{whatsapp}">{phone}</a></div>
    <div><h2 class="ftr__h">{e(P['footerCities'])}</h2><nav class="ftr__list">{cities}</nav></div>
    <div><h2 class="ftr__h">{e(P['footerGuides'])}</h2><nav class="ftr__list"><a href="{prefix}{P['pricePage']['slug']}/">{e(fill(P['pricePage']['h1']).replace(chr(10), ' '))}</a></nav></div>
  </div>'''


def alt_links(alts):
    return ''.join(f'<link rel="alternate" hreflang="{hl}" href="{e(url + p)}">' for hl, p in alts.items()) + \
        f'<link rel="alternate" hreflang="x-default" href="{e(url + alts["es-PR"])}">'


def write_page(lang, d, P, path, title, description, sections, graph, alts, *, preset_city=''):
    home = '/' if lang == 'es' else '/en/'
    other = alts['en-US'] if lang == 'es' else alts['es-PR']
    anchor = home if path != home else ''
    nav = ''.join(f'<a href="{anchor}#{s}">{e(label)}</a>' for s, label in zip(SECTIONS, d['nav']))
    subs = {
        'ciudades': [(f'{anchor}#ciudades', P['menuAllCities'])] + [
            (f"{home}{P['cities'][c['id']]['slug']}/", P['seeCity'].replace('{city}', c['name'])) for c in d['cities']],
        'preguntas': [(f'{anchor}#preguntas', P['menuFaq']), (f"{home}{P['pricePage']['slug']}/", P['menuPriceGuide'])],
    }
    header_nav = ''
    for s_id, label in zip(SECTIONS, d['nav']):
        if s_id not in subs:
            header_nav += f'<a href="{anchor}#{s_id}">{e(label)}</a>'
            continue
        current = ' aria-current="page"'
        links = ''.join(f'<a href="{href}"{current if href == path else ""}>{e(text)}</a>' for href, text in subs[s_id])
        header_nav += (f'<div class="nav__item" data-sub>'
                       f'<a href="{anchor}#{s_id}">{e(label)}</a>'
                       f'<button type="button" class="nav__toggle" aria-expanded="false" aria-controls="sub-{s_id}" '
                       f'aria-label="{e(P["menuMore"])} {e(label)}"><svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></button>'
                       f'<div class="nav__sub" id="sub-{s_id}">{links}</div></div>')
    seo = (f'<link rel="canonical" href="{e(url + path)}">' + alt_links(alts) +
           f'<meta property="og:url" content="{e(url + path)}"><meta property="og:locale" content="{OG_LOCALE[lang]}">'
           f'<meta property="og:locale:alternate" content="{OG_LOCALE["en" if lang == "es" else "es"]}">'
           f'<meta property="og:image" content="{e(url)}/assets/og-image.jpg"><meta property="og:image:width" content="1200">'
           f'<meta property="og:image:height" content="630"><meta property="og:image:alt" content="Sonrisas Colombia">'
           f'<meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(description)}">'
           f'<meta name="twitter:image" content="{e(url)}/assets/og-image.jpg">' + ld(graph))
    client = {k: fill(d[k]) for k in ('contactMessage', 'contactCity', 'contactTreatment', 'photosMessage')}
    values = dict(
        locale=e(d['locale']), title=e(title), description=e(description),
        robots='index,follow,max-image-preview:large' if indexable else 'noindex,nofollow', seo=seo, home=home,
        skip=e(d['skip']), menu=e(d['menu']), close=e(d['close']), nav=nav, navHeader=header_nav,
        otherUrl=other, otherLocale=d['otherLocale'], otherLabel=e(d['otherLabel']),
        headerCta=wa_button(d['headerCta'], 'btn btn--gold btn--sm hdr__cta'),
        sections=sections, footerLine=e(d['footerLine']), footerExtra=footer_extra(d, P, lang),
        privacy=e(d['privacy']), copyright=e(d['copyright']), year=str(date.today().year),
        privacyTitle=e(d['privacyTitle']), privacyText=e(d['privacyText']), privacyMore=ph(d['privacyMore'], 'inline'),
        floating=wa_button(d['ctaShort'], 'fab', f'aria-label="{e(d["headerCta"])}"'),
        mobileBar=wa_button(d['headerCta'], 'btn btn--gold btn--block'),
        client=json.dumps(client, ensure_ascii=False).replace('<', '\\u003c'),
        bodyAttrs=f' data-preset-city="{e(preset_city)}"' if preset_city else '',
    )
    html = bust_cache(TEMPLATE.substitute(values))
    target = SITE / path.lstrip('/') / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding='utf-8')
    return html


import hashlib
import re

_HASHES = {}


def asset_version(rel):
    """Huella corta del contenido de un archivo de /assets/ (cambia solo si el archivo cambia)."""
    if rel not in _HASHES:
        f = SITE / rel.lstrip('/')
        _HASHES[rel] = hashlib.md5(f.read_bytes()).hexdigest()[:10] if f.is_file() else ''
    return _HASHES[rel]


def bust_cache(html):
    """Agrega ?v=<huella> a cada /assets/... para que los navegadores (incluido Safari en iPhone)
    descarguen la versión nueva apenas cambia un archivo, sin borrar caché a mano."""
    def repl(m):
        rel = m.group(1)
        v = asset_version(rel)
        return f'{rel}?v={v}' if v else rel
    return re.sub(r'(/assets/[A-Za-z0-9_./-]+\.(?:css|js|webp|avif|jpg|png|svg|woff2))(?![?\w])', repl, html)


config = {'whatsapp': whatsapp, 'siteUrl': url, 'ga4': os.getenv('PUBLIC_GA4_ID', ''),
          'metaPixel': os.getenv('PUBLIC_META_PIXEL_ID', ''), 'gtm': os.getenv('PUBLIC_GTM_ID', ''),
          'trackingEnabled': False}
(SITE / 'assets/config.js').write_text('window.SONRISAS = ' + json.dumps(config) + ';\n', encoding='utf-8')

SITEMAP = []  # (path, alts)

for lang, d in CONTENT.items():
    P = PAGES[lang]
    home = '/' if lang == 'es' else '/en/'
    O = PAGES['en' if lang == 'es' else 'es']

    # ---- portada
    alts = {'es-PR': '/', 'en-US': '/en/'}
    sections = ''.join([
        render_hero(d, lang), render_results(d, lang), render_treatments(d), render_calculator(d),
        render_includes(d), render_steps(d), render_cities(d, P, home), render_team(d), render_reviews(d),
        render_faq(d), render_closing(d),
    ])
    graph = page_graph(d, lang, home, d['title'], d['description'], faqs=d['faqs'], extra=[howto_schema(d)])
    html = write_page(lang, d, P, home, fill(d['title']), fill(d['description']), sections, graph, alts)
    SITEMAP.append((home, alts))
    if lang == 'es':
        (SITE / 'es').mkdir(exist_ok=True)
        (SITE / 'es' / 'index.html').write_text(html, encoding='utf-8')

    # ---- páginas por ciudad
    for c in d['cities']:
        cp = P['cities'][c['id']]
        path = f"{home}{cp['slug']}/"
        alts = {'es-PR': f"/{PAGES['es']['cities'][c['id']]['slug']}/", 'en-US': f"/en/{PAGES['en']['cities'][c['id']]['slug']}/"}
        crumbs = [(P['home'], home), (c['name'], path)]
        sections = ''.join([
            page_hero(d, P, crumbs, cp['h1'], fill(cp['lead']), city_media(d, c['id'])),
            render_why(P['whyTitle'].replace('{city}', c['name']), cp['why']),
            render_treatments(d), render_steps(d, c['name']), render_travel(d, P, lang, c['id']),
            render_faq(d, P['cityFaqTitle'].replace('{city}', c['name']), cp['faqs']), render_closing(d),
        ])
        graph = page_graph(d, lang, path, cp['title'], cp['description'], faqs=cp['faqs'], crumbs=crumbs)
        write_page(lang, d, P, path, fill(cp['title']), fill(cp['description']), sections, graph, alts, preset_city=c['name'])
        SITEMAP.append((path, alts))

    # ---- guía de precios
    pp = P['pricePage']
    path = f"{home}{pp['slug']}/"
    alts = {'es-PR': f"/{PAGES['es']['pricePage']['slug']}/", 'en-US': f"/en/{PAGES['en']['pricePage']['slug']}/"}
    crumbs = [(P['home'], home), (fill(pp['h1']).replace('\n', ' '), path)]
    updated = f'<p class="updated">{e(P["updatedLabel"])} <time datetime="{PRICES_UPDATED}">{e(P["updatedText"])}</time></p>'
    sections = ''.join([
        page_hero(d, P, crumbs, pp['h1'], fill(pp['lead']), media=render_comparison('hero', lang, d['heroVisualTitle'], hero=True), extra=updated),
        render_price_table(d, P), render_calculator(d),
        render_faq(d, d['faqTitle'], pp['faqs'] + d['faqs'][1:3]), render_closing(d),
    ])
    graph = page_graph(d, lang, path, pp['title'], pp['description'], faqs=pp['faqs'] + d['faqs'][1:3], crumbs=crumbs)
    write_page(lang, d, P, path, fill(pp['title']), fill(pp['description']), sections, graph, alts)
    SITEMAP.append((path, alts))

# ---------------------------------------------------------------- archivos de apoyo


AI_BOTS = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'PerplexityBot', 'Perplexity-User', 'ClaudeBot', 'Claude-SearchBot',
           'Claude-User', 'Google-Extended', 'Applebot-Extended', 'Bingbot']
if indexable:
    robots = 'User-agent: *\nAllow: /\n\n' + ''.join(f'User-agent: {b}\nAllow: /\n\n' for b in AI_BOTS) + f'Sitemap: {url}/sitemap.xml\n'
else:
    robots = 'User-agent: *\nDisallow: /\n'
(SITE / 'robots.txt').write_text(robots, encoding='utf-8')

sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
for path, alts in SITEMAP:
    links = ''.join(f'<xhtml:link rel="alternate" hreflang="{hl}" href="{e(url + p)}"/>' for hl, p in alts.items())
    sm.append(f'<url><loc>{e(url + path)}</loc><lastmod>{PRICES_UPDATED}</lastmod>{links}</url>')
sm.append('</urlset>')
(SITE / 'sitemap.xml').write_text('\n'.join(sm), encoding='utf-8')

es, en, Pes, Pen = CONTENT['es'], CONTENT['en'], PAGES['es'], PAGES['en']
llms = f"""# Sonrisas Colombia

> Diseño de sonrisa (carillas en resina y porcelana, y ortodoncia) en Bogotá, Medellín, Cali y Pereira, Colombia, para pacientes que viajan desde Puerto Rico y Estados Unidos. Valoración virtual gratis por WhatsApp. / Smile design (composite and porcelain veneers, orthodontics) in Bogotá, Medellín, Cali and Pereira, Colombia, for patients traveling from Puerto Rico and the U.S. Free virtual consultation on WhatsApp.

## Datos clave / Key facts

- Carillas en resina / Composite veneers: desde / from USD {TOKENS['resin']} por diente / per tooth (Puerto Rico ≈ USD {TOKENS['prResin']}, EE. UU./U.S. ≈ USD {TOKENS['usResin']}).
- Carillas en porcelana / Porcelain veneers: desde / from USD {TOKENS['porcelain']} por diente / per tooth (Puerto Rico ≈ USD {TOKENS['prPorcelain']}, EE. UU./U.S. ≈ USD {TOKENS['usPorcelain']}).
- Precios de referencia actualizados / Reference prices updated: {PRICES_UPDATED}. El precio final se confirma en la valoración / Final price confirmed at consultation.
- Días en Colombia (referencia) / Days in Colombia (reference): resina 3–5, porcelana 7–10.
- Ciudades / Cities: Bogotá, Medellín, Cali, Pereira.
- Equipo / Team: {', '.join(f"Dra. {doc['name']} ({doc['role']})" for doc in es['doctors'])}.
- Contacto / Contact: WhatsApp +{whatsapp} — https://wa.me/{whatsapp}
- Vuelos y hospedaje no incluidos / Flights and lodging not included.

## Páginas / Pages

- [Inicio (español)]({url}/): tratamientos, calculadora de ahorro, ciudades, doctoras y preguntas frecuentes.
- [Home (English)]({url}/en/)
- [{fill(Pes['pricePage']['h1']).replace(chr(10), ' ')}]({url}/{Pes['pricePage']['slug']}/)
- [{fill(Pen['pricePage']['h1']).replace(chr(10), ' ')}]({url}/en/{Pen['pricePage']['slug']}/)
""" + ''.join(f"- [Carillas en {c['name']}]({url}/{Pes['cities'][c['id']]['slug']}/) · [Veneers in {c['name']}]({url}/en/{Pen['cities'][c['id']]['slug']}/)\n" for c in es['cities']) + """
## Preguntas frecuentes / FAQ

""" + ''.join(f"### {fill(q)}\n{fill(a)}\n\n" for q, a in es['faqs'])
(SITE / 'llms.txt').write_text(llms, encoding='utf-8')

print(f'Built {len(SITEMAP)} pages (ES/EN) for {url}. Indexing: {indexable}. WhatsApp: +{whatsapp}')
