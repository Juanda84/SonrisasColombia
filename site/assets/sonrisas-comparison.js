'use strict';

(() => {
  const percent = new Intl.NumberFormat(document.documentElement.lang, { style: 'percent' });

  for (const comparison of document.querySelectorAll('[data-smile-comparison]')) {
    const range = comparison.querySelector('.smile-comparison__range');
    if (!range) continue;

    const before = comparison.dataset.comparisonBefore;
    const after = comparison.dataset.comparisonAfter;

    const update = () => {
      const revealed = range.valueAsNumber;
      comparison.style.setProperty('--comparison-split', `${revealed}%`);
      comparison.dataset.comparisonEdge = revealed < 13 ? 'start' : revealed > 87 ? 'end' : 'middle';
      range.setAttribute('aria-valuetext', `${before} ${percent.format(revealed / 100)}, ${after} ${percent.format((100 - revealed) / 100)}`);
    };

    range.addEventListener('input', update);
    update();
    comparison.setAttribute('data-comparison-ready', '');
  }
})();
