'use strict';

(() => {
  const calculator = document.querySelector('[data-veneer-calculator]');
  if (!calculator) return;

  const prices = JSON.parse(calculator.dataset.pricing);
  const material = calculator.elements.material;
  const quantity = calculator.elements.quantity;
  const location = calculator.elements.market;
  const totalAmount = calculator.querySelector('[data-veneers-total]');
  const savingsAmount = calculator.querySelector('[data-veneers-savings]');
  const savingsLabel = calculator.querySelector('[data-veneers-savings-label]');
  const quantityError = calculator.querySelector('[data-veneers-error]');
  const currency = new Intl.NumberFormat(document.documentElement.lang, {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  });

  function updateEstimate() {
    const selectedPrices = prices[material.value];
    const count = quantity.valueAsNumber;
    const market = location.value;
    const marketLabel = location.selectedOptions[0].textContent;
    const savings = calculator.dataset.savings.replace('{market}', marketLabel);
    const valid = quantity.validity.valid && Number.isInteger(count);
    quantityError.hidden = valid;

    if (!valid) {
      quantity.setAttribute('aria-invalid', 'true');
      totalAmount.textContent = '—';
      savingsAmount.textContent = '—';
      savingsLabel.textContent = savings;
      return;
    }

    quantity.removeAttribute('aria-invalid');
    const colombiaTotal = selectedPrices.colombia * count;
    const difference = selectedPrices[market] * count - colombiaTotal;
    let label = savings;
    if (difference < 0) label = calculator.dataset.extra.replace('{market}', marketLabel);
    if (difference === 0) label = calculator.dataset.equal.replace('{market}', marketLabel);

    totalAmount.textContent = currency.format(colombiaTotal);
    savingsAmount.textContent = currency.format(Math.abs(difference));
    savingsLabel.textContent = label;
  }

  quantity.addEventListener('input', updateEstimate);
  material.addEventListener('change', updateEstimate);
  location.addEventListener('change', updateEstimate);
  calculator.addEventListener('submit', event => event.preventDefault());
  updateEstimate();
})();
