(() => {
  const suits = [
    { code: 'S', symbol: '\u2660', color: 'black' },
    { code: 'H', symbol: '\u2665', color: 'red' },
    { code: 'D', symbol: '\u2666', color: 'red' },
    { code: 'C', symbol: '\u2663', color: 'black' }
  ];
  const ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];

  function getDayOfYear(now) {
    const start = new Date(now.getFullYear(), 0, 1);
    const diff = now - start;
    return Math.floor(diff / 86400000) + 1;
  }

  function getCardMeta(now) {
    const dayOfYear = getDayOfYear(now);
    const weekNumber = Math.floor((dayOfYear - 1) / 7) + 1;

    if (weekNumber >= 53) {
      return {
        weekNumber,
        code: 'JOKER',
        label: 'Joker',
        symbol: '\u2605',
        color: 'joker'
      };
    }

    const cardIndex = weekNumber - 1;
    const suit = suits[Math.floor(cardIndex / ranks.length)];
    const rank = ranks[cardIndex % ranks.length];

    return {
      weekNumber,
      code: `${rank}${suit.code}`,
      label: `${rank}${suit.symbol}`,
      symbol: suit.symbol,
      rank,
      color: suit.color
    };
  }

  function buildCard(meta) {
    const card = document.createElement('div');
    card.className = `site-author-playing-card is-${meta.color}`;
    card.setAttribute('role', 'img');
    card.setAttribute('aria-label', `Week ${meta.weekNumber} - ${meta.code}`);
    card.title = `Week ${meta.weekNumber} - ${meta.code}`;

    if (meta.code === 'JOKER') {
      card.innerHTML = `
        <span class="playing-card-corner top"><span class="rank">JOKER</span><span class="suit">${meta.symbol}</span></span>
        <span class="playing-card-center playing-card-joker-word">JOKER</span>
        <span class="playing-card-center playing-card-joker-mark">${meta.symbol}</span>
        <span class="playing-card-corner bottom"><span class="rank">JOKER</span><span class="suit">${meta.symbol}</span></span>
      `;
      return card;
    }

    card.innerHTML = `
      <span class="playing-card-corner top"><span class="rank">${meta.rank}</span><span class="suit">${meta.symbol}</span></span>
      <span class="playing-card-center"><span class="rank">${meta.rank}</span><span class="suit">${meta.symbol}</span></span>
      <span class="playing-card-corner bottom"><span class="rank">${meta.rank}</span><span class="suit">${meta.symbol}</span></span>
    `;
    return card;
  }

  function ensureTarget() {
    const existing = document.querySelector('[data-card-avatar]');
    if (existing) return existing;

    const fallback = document.querySelector('.site-author-image');
    if (!fallback) return null;
    const originalParent = fallback.parentNode;

    const shell = document.createElement('div');
    shell.className = 'site-author-card-shell';

    const target = document.createElement('div');
    target.className = 'site-author-card-face';
    target.dataset.cardAvatar = 'true';

    fallback.classList.add('site-author-image-fallback');
    target.appendChild(fallback);
    shell.appendChild(target);
    originalParent.insertBefore(shell, originalParent.firstChild);

    return target;
  }

  function renderCardAvatar() {
    const target = ensureTarget();
    if (!target) return;
    if (target.querySelector('.site-author-playing-card')) return;

    const fallback = target.querySelector('.site-author-image-fallback');
    const meta = getCardMeta(new Date());
    const card = buildCard(meta);

    target.dataset.cardCode = meta.code;
    target.dataset.cardWeek = String(meta.weekNumber);
    target.appendChild(card);

    requestAnimationFrame(() => {
      if (fallback) fallback.remove();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderCardAvatar, { once: true });
  } else {
    renderCardAvatar();
  }
})();
