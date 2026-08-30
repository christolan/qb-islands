/**
 * Toolbar popup: enable the light Islands skin or restore the stock UI.
 * The choice is stored under `qbisMode`; src/content/skin.js applies it live.
 */
(function () {
  'use strict';

  const radios = Array.from(document.querySelectorAll('input[name="mode"]'));

  function mark(mode) {
    document.querySelectorAll('.mode').forEach((label) => {
      label.classList.toggle('on', label.dataset.mode === mode);
    });
    const radio = radios.find((r) => r.value === mode);
    if (radio) radio.checked = true;
  }

  chrome.storage.local.get(['qbisMode']).then((data) => {
    mark(data.qbisMode === 'off' ? 'off' : 'on');
  });

  radios.forEach((radio) => {
    radio.addEventListener('change', () => {
      if (!radio.checked) return;
      chrome.storage.local.set({ qbisMode: radio.value });
      mark(radio.value);
    });
  });
})();
