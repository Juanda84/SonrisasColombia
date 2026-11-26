'use strict';
/* Sonrisas Colombia — interacciones del sitio. Sin dependencias. */
(() => {
  const root = document.documentElement;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  root.classList.add('js');
  if (!reduced) root.classList.add('js-motion');

  const text = JSON.parse(document.getElementById('page-data').textContent);
  const config = window.SONRISAS || {};
  const lang = root.lang;
  const money = new Intl.NumberFormat(lang, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
  const state = { city: null, quote: null };

  /* ---------- WhatsApp con contexto */
  function waMessage(button) {
    if (button.hasAttribute('data-wa-quote') && state.quote) return state.quote;
    if (button.hasAttribute('data-wa-photos')) return text.photosMessage + (state.city ? text.contactCity.replace('{city}', state.city) : '');
    let msg = button.dataset.waTreatment
      ? text.contactTreatment.replace('{treatment}', button.dataset.waTreatment)
      : text.contactMessage;
    if (state.city) msg += text.contactCity.replace('{city}', state.city);
    return msg;
  }
  document.addEventListener('click', event => {
    const button = event.target.closest('[data-wa]');
    if (!button) return;
    const number = /^[1-9]\d{7,14}$/.test(config.whatsapp || '') ? config.whatsapp : '';
    const href = 'https://wa.me/' + number + '?text=' + encodeURIComponent(waMessage(button));
    window.open(href, '_blank', 'noopener,noreferrer');
  });

  /* ---------- intro de la portada */
  requestAnimationFrame(() => document.querySelector('.hero')?.classList.add('is-loaded'));

  /* ---------- header */
  const header = document.querySelector('[data-header]');
  const fab = document.querySelector('.fab');
  const mbar = document.querySelector('.mbar');
  const closing = document.getElementById('contacto');
  let ticking = false;
  function onScroll() {
    ticking = false;
    const y = scrollY;
    header.classList.toggle('is-scrolled', y > 24);
    const nearEnd = closing && closing.getBoundingClientRect().top < innerHeight * .6;
    mbar?.classList.toggle('is-visible', y > innerHeight * .7 && !nearEnd);
    fab?.classList.toggle('is-hidden', y < innerHeight * .5 || nearEnd);
  }
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  const menu = document.querySelector('[data-menu]');
  const nav = document.getElementById('nav');
  function setMenu(open) {
    nav.classList.toggle('is-open', open);
    menu.setAttribute('aria-expanded', String(open));
  }
  menu.addEventListener('click', () => setMenu(menu.getAttribute('aria-expanded') !== 'true'));
  nav.addEventListener('click', event => { if (event.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', event => { if (event.key === 'Escape' && nav.classList.contains('is-open')) { setMenu(false); menu.focus(); } });

  document.querySelectorAll('[data-lang]').forEach(link => link.addEventListener('click', () => {
    try { localStorage.setItem('sonrisas-language', link.hreflang); } catch {}
  }));

  /* ---------- comparadores antes/después */
  const pct = new Intl.NumberFormat(lang, { style: 'percent' });
  document.querySelectorAll('[data-cmp]').forEach(cmp => {
    const range = cmp.querySelector('.cmp__range');
    const set = value => {
      cmp.style.setProperty('--split', value + '%');
      cmp.dataset.edge = value < 12 ? 'start' : value > 88 ? 'end' : 'middle';
      range.setAttribute('aria-valuetext', `${cmp.dataset.before} ${pct.format(value / 100)}, ${cmp.dataset.after} ${pct.format(1 - value / 100)}`);
    };
    let touched = false;
    range.addEventListener('input', () => { touched = true; set(range.valueAsNumber); });
    range.addEventListener('pointerdown', () => { touched = true; });
    set(range.valueAsNumber);

    // Barrido de demostración una sola vez: enseña que se puede arrastrar.
    if (cmp.hasAttribute('data-autosweep') && !reduced) {
      const keys = [[0, 50], [.32, 84], [.68, 18], [1, 50]];
      const duration = 2600;
      const ease = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
      setTimeout(() => {
        const start = performance.now();
        const frame = now => {
          if (touched) return;
          const t = Math.min(1, (now - start) / duration);
          let i = 0;
          while (i < keys.length - 2 && t > keys[i + 1][0]) i++;
          const [t0, v0] = keys[i], [t1, v1] = keys[i + 1];
          const local = ease((t - t0) / (t1 - t0));
          const value = v0 + (v1 - v0) * local;
          range.value = value;
          set(value);
          if (t < 1) requestAnimationFrame(frame);
        };
        requestAnimationFrame(frame);
      }, 1300);
    }
  });

  /* ---------- tratamientos (pestañas) */
  const tabList = document.querySelector('[data-tabs]');
  if (tabList) {
    const tabs = [...tabList.querySelectorAll('[data-tab]')];
    const panels = tabs.map(tab => document.getElementById(tab.dataset.tab));
    const show = index => tabs.forEach((tab, i) => {
      const on = i === index;
      tab.setAttribute('aria-selected', String(on));
      tab.tabIndex = on ? 0 : -1;
      panels[i].hidden = !on;
    });
    tabs.forEach((tab, i) => {
      tab.setAttribute('role', 'tab');
      tab.setAttribute('aria-controls', panels[i].id);
      panels[i].setAttribute('role', 'tabpanel');
      panels[i].setAttribute('aria-labelledby', tab.id);
      tab.addEventListener('click', () => show(i));
      tab.addEventListener('keydown', event => {
        const next = { ArrowLeft: (i - 1 + tabs.length) % tabs.length, ArrowRight: (i + 1) % tabs.length, Home: 0, End: tabs.length - 1 }[event.key];
        if (next === undefined) return;
        event.preventDefault(); show(next); tabs[next].focus();
      });
    });
    const fromHash = panels.findIndex(p => '#' + p.id === location.hash);
    show(Math.max(0, fromHash));
    tabList.hidden = false;
  }

  /* ---------- calculadora */
  const form = document.querySelector('[data-calc]');
  if (form) {
    const prices = JSON.parse(form.dataset.prices);
    const labels = JSON.parse(form.dataset.labels);
    const qty = form.elements.quantity;
    const slider = form.querySelector('.qty__range');
    const receipt = document.querySelector('.receipt');
    const out = name => receipt.querySelector(`[data-r-${name}]`);
    const hint = form.querySelector('[data-calc-hint]');
    const hintText = hint.textContent;
    const shown = { home: 0, col: 0, save: 0 };
    let animation;

    const tween = target => {
      cancelAnimationFrame(animation);
      const from = { ...shown };
      const start = performance.now();
      const duration = reduced ? 0 : 700;
      const step = now => {
        const t = duration ? Math.min(1, (now - start) / duration) : 1;
        const k = 1 - Math.pow(1 - t, 3);
        for (const key of Object.keys(target)) {
          shown[key] = from[key] + (target[key] - from[key]) * k;
          out(key).textContent = money.format(Math.round(shown[key]));
        }
        if (t < 1) animation = requestAnimationFrame(step);
      };
      animation = requestAnimationFrame(step);
    };

    const update = () => {
      const material = form.elements.material.value;
      const market = form.elements.market.value;
      const count = qty.valueAsNumber;
      const valid = Number.isInteger(count) && count >= 1 && count <= 28;
      qty.setAttribute('aria-invalid', String(!valid));
      hint.textContent = valid ? hintText : labels.invalid;
      if (!valid) return;
      if (slider) slider.value = Math.min(20, count);
      const p = prices[material];
      const home = p[market] * count;
      const col = p.colombia * count;
      const save = home - col;
      out('item').textContent = `${count} × ${labels[material]}`;
      out('home-label').textContent = labels.home.replace('{market}', labels[market]);
      out('pct').textContent = labels.pct.replace('{pct}', Math.round(save / home * 100));
      out('travel').hidden = save < 1200; // solo cuando el ahorro cubre un viaje típico
      tween({ home, col, save });
      receipt.classList.remove('is-bump'); void receipt.offsetWidth; receipt.classList.add('is-bump');
      state.quote = labels.message
        .replace('{qty}', count)
        .replace('{material}', labels[material].toLowerCase())
        .replace('{market}', labels[market])
        .replace('{total}', money.format(col))
        + (state.city ? text.contactCity.replace('{city}', state.city) : '');
    };
    form.addEventListener('input', event => {
      if (event.target === slider) qty.value = slider.value;
      update();
    });
    form.addEventListener('submit', event => event.preventDefault());
    form.querySelectorAll('[data-step]').forEach(btn => btn.addEventListener('click', () => {
      const next = Math.min(28, Math.max(1, (qty.valueAsNumber || 0) + Number(btn.dataset.step)));
      qty.value = next; update();
    }));
    state.refreshQuote = update;
    update();
  }

  /* ---------- ciudades */
  const cities = [...document.querySelectorAll('[data-city]')];
  const media = [...document.querySelectorAll('[data-city-media]')];
  const routeCity = document.querySelector('[data-route-city]');
  function activate(id, pick) {
    cities.forEach(c => c.classList.toggle('is-active', c.dataset.city === id));
    media.forEach(m => m.classList.toggle('is-active', m.dataset.cityMedia === id));
    if (pick) {
      const city = cities.find(c => c.dataset.city === id);
      state.city = city.dataset.cityName;
      cities.forEach(c => c.querySelector('[data-city-pick]').setAttribute('aria-pressed', String(c === city)));
      if (routeCity) routeCity.textContent = state.city;
      state.refreshQuote?.();
    }
  }
  cities.forEach(c => {
    const head = c.querySelector('[data-city-pick]');
    head.addEventListener('click', () => activate(c.dataset.city, true));
    c.addEventListener('pointerenter', event => { if (event.pointerType === 'mouse') activate(c.dataset.city, false); });
    head.addEventListener('focus', () => activate(c.dataset.city, false));
  });
  document.querySelector('.cities__list')?.addEventListener('pointerleave', () => {
    const picked = cities.find(c => c.querySelector('[aria-pressed="true"]'));
    if (picked) activate(picked.dataset.city, false);
  });
  document.querySelectorAll('[data-city-link]').forEach(link => link.addEventListener('click', () => activate(link.dataset.cityLink, true)));
  if (cities.length) activate(cities[0].dataset.city, false);

  /* ---------- ruta de vuelo */
  const route = document.querySelector('[data-route]');
  if (route) {
    const path = route.querySelector('.route__line');
    const plane = route.querySelector('.route__plane');
    const total = path.getTotalLength();
    const place = t => {
      const point = path.getPointAtLength(total * t);
      const ahead = path.getPointAtLength(Math.min(total, total * t + 1));
      const before = path.getPointAtLength(Math.max(0, total * t - 1));
      const sx = route.clientWidth / 1200, sy = route.clientHeight / 220;
      const angle = Math.atan2((ahead.y - before.y) * sy, (ahead.x - before.x) * sx) * 180 / Math.PI;
      plane.style.transform = `translate(${point.x * sx - 17}px, ${point.y * sy - 17}px) rotate(${angle}deg)`;
    };
    let progress = reduced ? 1 : 0;
    place(progress);
    addEventListener('resize', () => place(progress));
    if (!reduced) {
      const fly = () => {
        const start = performance.now();
        const frame = now => {
          const t = Math.min(1, (now - start) / 2400);
          progress = t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
          place(progress);
          if (t < 1) requestAnimationFrame(frame);
        };
        requestAnimationFrame(frame);
      };
      new IntersectionObserver((entries, obs) => entries.forEach(entry => {
        if (entry.isIntersecting) { route.classList.add('is-in'); fly(); obs.disconnect(); }
      }), { threshold: .5 }).observe(route);
    }
  }

  /* ---------- aparición al hacer scroll */
  if (!reduced && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('is-in'); io.unobserve(entry.target); }
    }), { threshold: .15, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('[data-reveal]').forEach(el => io.observe(el));
  }

  /* ---------- diálogo de privacidad */
  const dialog = document.getElementById('privacy-dialog');
  document.querySelectorAll('[data-privacy]').forEach(b => b.addEventListener('click', () => dialog.showModal()));
  dialog.querySelectorAll('[data-close]').forEach(b => b.addEventListener('click', () => dialog.close()));
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
})();
