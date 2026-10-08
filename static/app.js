/* crypto-tracker / app.js
   Polls /api/prices every 30s, renders the table, draws inline SVG sparklines.
   No frameworks, no build step. Just fetch + DOM.
*/

const REFRESH_MS = 30000;
const fmtUSD = (v) => {
  if (v == null || isNaN(v)) return '\u2014';
  if (v >= 1e12) return `$${(v / 1e12).toFixed(2)}T`;
  if (v >= 1e9)  return `$${(v / 1e9).toFixed(2)}B`;
  if (v >= 1e6)  return `$${(v / 1e6).toFixed(2)}M`;
  return `$${v.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
};

const fmtPrice = (v) => {
  if (v == null || isNaN(v)) return '\u2014';
  if (v >= 100) return `$${v.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
  if (v >= 1)   return `$${v.toFixed(3)}`;
  return `$${v.toFixed(6)}`;
};

const fmtChange = (v) => {
  if (v == null || isNaN(v)) return '\u2014';
  const sign = v > 0 ? '+' : '';
  return `${sign}${v.toFixed(2)}%`;
};

/* Draw a sparkline as an inline SVG polyline.
   Width 100, height 30. Scales the price range to fit. */
function drawSparkline(svg, prices) {
  if (!svg) return;
  while (svg.firstChild) svg.removeChild(svg.firstChild);
  if (!prices || prices.length < 2) return;

  const W = 100, H = 30, PAD = 2;
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const range = max - min || 1;

  const stepX = (W - PAD * 2) / (prices.length - 1);
  const points = prices.map((p, i) => {
    const x = PAD + i * stepX;
    const y = H - PAD - ((p - min) / range) * (H - PAD * 2);
    return `${x.toFixed(2)},${y.toFixed(2)}`;
  });

  const last = prices[prices.length - 1];
  const up = last >= prices[0];
  const color = up ? '#16c784' : '#ea3943';

  const polyline = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
  polyline.setAttribute('points', points.join(' '));
  polyline.setAttribute('fill', 'none');
  polyline.setAttribute('stroke', color);
  polyline.setAttribute('stroke-width', '1.5');
  polyline.setAttribute('stroke-linejoin', 'round');
  polyline.setAttribute('stroke-linecap', 'round');
  svg.appendChild(polyline);
}

async function fetchPrices() {
  const status = document.getElementById('status');
  try {
    const res = await fetch('/api/prices', { cache: 'no-store' });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'api error');

    const tbody = document.getElementById('coin-rows');
    const rowsByCoin = new Map();
    tbody.querySelectorAll('tr[data-coin]').forEach(r => rowsByCoin.set(r.dataset.coin, r));

    data.coins.forEach((coin, i) => {
      const row = rowsByCoin.get(coin.id);
      if (!row) return;

      row.querySelector('.rank').textContent = i + 1;
      row.querySelector('.price').textContent = fmtPrice(coin.price);

      const changeEl = row.querySelector('.change');
      changeEl.textContent = fmtChange(coin.change_24h);
      changeEl.classList.toggle('up',   coin.change_24h > 0);
      changeEl.classList.toggle('down', coin.change_24h < 0);

      row.querySelector('.cap').textContent = fmtUSD(coin.market_cap);

      const svg = row.querySelector('.spark svg');
      drawSparkline(svg, coin.sparkline);

      // Pulse the price cell on update.
      row.classList.remove('fresh');
      // Force reflow so the animation restarts.
      void row.offsetWidth;
      row.classList.add('fresh');
    });

    const ts = new Date(data.fetched_at * 1000);
    status.textContent = `updated ${ts.toLocaleTimeString()} \u00b7 next refresh in ${REFRESH_MS / 1000}s`;
  } catch (err) {
    status.textContent = `error: ${err.message}. retrying\u2026`;
  }
}

fetchPrices()
  .finally(() => {
    // First tick + steady refresh loop.
    fetchPrices();
    setInterval(fetchPrices, REFRESH_MS);
  });