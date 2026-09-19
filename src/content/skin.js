/**
 * qBittorrent Islands — enable / disable switcher.
 *
 * The islands skin lives in src/skin/islands.css, injected statically via the
 * manifest. Every rule in it is scoped under `body.qbis-islands`, so the skin
 * is applied purely by toggling classes on <body>. This script only decides
 * whether the page is a qBittorrent WebUI and whether the skin is enabled.
 *
 * The WebUI opens its dialogs (upload.html, confirmdeletion.html, about,
 * statistics, ...) as same-origin iframes. With `all_frames` this script also
 * runs inside them; a frame adopts the host page's decision so dialog content
 * is styled together with the window around it.
 */
(function () {
  'use strict';

  // DOM markers of the classic 4.6.x WebUI.
  const PAGE_MARKERS = [
    'desktopNavbar',
    'torrentsTable',
    'transferInfo',
    'DlInfos',
    'UpInfos',
    'propertiesPanel',
    'filtersColumn',
  ];

  function isQbittorrentDocument(doc) {
    return PAGE_MARKERS.some((id) => doc.getElementById(id) !== null);
  }

  // A same-origin iframe of a qBittorrent page (dialogs open this way).
  function isQbittorrentFrame() {
    try {
      return window.self !== window.top && isQbittorrentDocument(window.top.document);
    } catch (e) {
      return false; // cross-origin frame: leave it alone
    }
  }

  // DOMContentLoaded: body may not exist yet (run_at: document_start).
  function apply(mode) {
    const body = document.body;
    if (!body) return;
    body.classList.toggle('qbis-islands', mode !== 'off');
    // dialog iframes get a content-scoped variant of the skin
    body.classList.toggle('qbis-frame', isQbittorrentFrame());
  }

  function start() {
    chrome.storage.local.get(['qbisMode']).then((data) => {
      // Only the literal `off` disables the skin; anything else — including
      // no stored value on a first run — enables it.
      apply(data.qbisMode || 'on');
    });
    chrome.storage.onChanged.addListener((changes, area) => {
      if (area === 'local' && changes.qbisMode) {
        apply(changes.qbisMode.newValue || 'on');
      }
    });
  }

  function boot() {
    if (isQbittorrentDocument(document) || isQbittorrentFrame()) {
      if (document.body) {
        start();
      } else {
        document.addEventListener('DOMContentLoaded', start, { once: true });
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot, { once: true });
  } else {
    boot();
  }
})();
