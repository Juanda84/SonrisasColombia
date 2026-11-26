'use strict';
(() => {
  const text = JSON.parse(document.querySelector('#page-data').textContent);
  const config = window.SONRISAS || {};
  const menu = document.querySelector('#menu-toggle');
  const nav = document.querySelector('#navigation');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  function closeMenu(returnFocus = false) {
    nav.classList.remove('open'); menu.setAttribute('aria-expanded', 'false');
    if (returnFocus) menu.focus();
  }
  menu.addEventListener('click', () => {
    const open = nav.classList.toggle('open'); menu.setAttribute('aria-expanded', String(open));
  });
  nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => closeMenu()));
  document.addEventListener('keydown', event => { if (event.key === 'Escape' && nav.classList.contains('open')) closeMenu(true); });
  document.addEventListener('click', event => { if (!event.target.closest('.header')) closeMenu(); });
  matchMedia('(min-width: 951px)').addEventListener('change', () => closeMenu());
  document.querySelectorAll('[data-language]').forEach(link => link.addEventListener('click', () => {
    try { localStorage.setItem('sonrisas-language', link.getAttribute('href') === '/en/' ? 'en' : 'es'); } catch {}
  }));
  // Direct campaign URLs always win. The preference is saved for subsequent navigation, never forced by a redirect.
  let lastDialogTrigger;
  function showDialog(dialog, trigger) {
    lastDialogTrigger = trigger; dialog.showModal(); document.body.classList.add('dialog-open');
  }
  document.querySelectorAll('[data-contact]').forEach(button => button.addEventListener('click', () => {
    if (/^[1-9]\d{7,14}$/.test(config.whatsapp || '')) {
      const url = 'https://wa.me/' + config.whatsapp + '?text=' + encodeURIComponent(text.contactMessage);
      window.open(url, '_blank', 'noopener,noreferrer');
    } else showDialog(document.querySelector('#contact-dialog'), button);
  }));
  document.querySelectorAll('[data-privacy]').forEach(button => button.addEventListener('click', () => showDialog(document.querySelector('#privacy-dialog'), button)));
  document.querySelectorAll('dialog').forEach(dialog => {
    dialog.querySelectorAll('[data-close]').forEach(button => button.addEventListener('click', () => dialog.close()));
    dialog.addEventListener('close', () => { document.body.classList.remove('dialog-open'); lastDialogTrigger?.focus(); });
    dialog.addEventListener('click', event => {
      const r = dialog.getBoundingClientRect();
      if (event.target === dialog && (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom)) dialog.close();
    });
  });
  document.querySelectorAll('[data-consent]').forEach(button => button.addEventListener('click', () => {
    try { localStorage.setItem('sonrisas-consent-v3', JSON.stringify({analytics:false,marketing:false,choice:button.dataset.consent})); } catch {}
    document.querySelector('#privacy-dialog').close();
  }));
  const tabList = document.querySelector('#studio-tabs');
  const tabs = [...tabList.querySelectorAll('[data-treatment]')];
  const panels = tabs.map(tab => document.getElementById(tab.dataset.treatment));

  function showTreatment(index) {
    tabs.forEach((tab, position) => {
      const selected = position === index;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
      panels[position].hidden = !selected;
    });
  }

  function treatmentFromHash() {
    return panels.findIndex(panel => '#' + panel.id === location.hash);
  }

  tabList.setAttribute('role', 'tablist');
  tabs.forEach((tab, index) => {
    const panel = panels[index];
    tab.setAttribute('role', 'tab');
    tab.setAttribute('aria-controls', panel.id);
    panel.setAttribute('role', 'tabpanel');
    panel.setAttribute('aria-labelledby', tab.id);
    panel.tabIndex = 0;
    tab.addEventListener('click', () => showTreatment(index));
    tab.addEventListener('keydown', event => {
      const target = {
        ArrowLeft: (index - 1 + tabs.length) % tabs.length,
        ArrowRight: (index + 1) % tabs.length,
        Home: 0,
        End: tabs.length - 1
      }[event.key];
      if (target === undefined) return;
      event.preventDefault();
      showTreatment(target);
      tabs[target].focus();
    });
  });
  showTreatment(Math.max(0, treatmentFromHash()));
  tabList.hidden = false;
  addEventListener('hashchange', () => {
    const target = treatmentFromHash();
    if (target < 0) return;
    showTreatment(target);
    panels[target].scrollIntoView({behavior: 'instant'});
  });

  const reviewTrack = document.querySelector('[data-review-track]');
  if (reviewTrack) {
    const controls = reviewTrack.nextElementSibling;
    controls.hidden = false;

    function updateReviewControls() {
      controls.querySelector('[data-review-step="-1"]').disabled = reviewTrack.scrollLeft < 2;
      const end = reviewTrack.scrollWidth - reviewTrack.clientWidth;
      controls.querySelector('[data-review-step="1"]').disabled = reviewTrack.scrollLeft >= end - 2;
    }

    controls.addEventListener('click', event => {
      const button = event.target.closest('[data-review-step]');
      if (!button) return;
      const [first, second] = reviewTrack.children;
      const step = second.offsetLeft - first.offsetLeft;
      reviewTrack.scrollBy({
        left: step * Number(button.dataset.reviewStep),
        behavior: reduced.matches ? 'instant' : 'smooth',
      });
    });

    reviewTrack.addEventListener('scroll', updateReviewControls, {passive: true});
    addEventListener('resize', updateReviewControls);
    updateReviewControls();
  }

  if ('IntersectionObserver' in window && !reduced.matches) {
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('reveal-in'); observer.unobserve(entry.target); }
    }), {threshold:.12});
    document.querySelectorAll('.section-heading,.team-feature,.journey-phase,.destination-copy').forEach(el => observer.observe(el));
  }
  let scheduled = false;
  function updateProgress() {
    scheduled = false;
    const root = document.documentElement;
    document.querySelector('.scroll-progress').style.transform = 'scaleX(' + Math.min(1,root.scrollTop / Math.max(1,root.scrollHeight-root.clientHeight)) + ')';
  }
  addEventListener('scroll', () => { if (!scheduled && !reduced.matches) {scheduled=true;requestAnimationFrame(updateProgress);} }, {passive:true});
})();
