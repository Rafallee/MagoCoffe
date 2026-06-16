// ── Mago Coffee BI Dashboard — main.js ─────────────────────────────────────

// ── Chart defaults ──────────────────────────────────────────────────────────
Chart.defaults.color = '#7A6E58';
Chart.defaults.borderColor = '#3A3020';
Chart.defaults.font.family = "'Space Grotesk', sans-serif";
Chart.defaults.font.size = 11;

const GOLD    = '#C8994A';
const GOLD_LT = '#E8B96A';
const GOLD_DK = '#8B6A2E';
const BLUE    = '#4A8BC8';
const GREEN   = '#4AC88B';
const ROSE    = '#C84A82';
const PURPLE  = '#7A4AC8';
const PALETTE = [GOLD, BLUE, GREEN, ROSE, PURPLE, '#E8A04A', '#4AC8C8', '#C84A4A'];

// ── Helpers ─────────────────────────────────────────────────────────────────
const rupiah = (v) => 'Rp ' + new Intl.NumberFormat('id-ID').format(Math.round(v));
const num    = (v) => new Intl.NumberFormat('id-ID').format(v);
const api    = (path) => fetch(path).then(r => r.json());
const $      = (id) => document.getElementById(id);

// ── Moving Average ───────────────────────────────────────────────────────────
function movingAvg(data, win = 7) {
  return data.map((_, i) => {
    const slice = data.slice(Math.max(0, i - win + 1), i + 1);
    return slice.reduce((a, b) => a + b, 0) / slice.length;
  });
}

// ── Chart store (for destroy/recreate) ─────────────────────────────────────
const charts = {};
function destroyChart(id) {
  if (charts[id]) { charts[id].destroy(); delete charts[id]; }
}

// ── Navigation ───────────────────────────────────────────────────────────────
const sections = {
  overview : { el: 'section-overview',  title: 'Overview Penjualan',      init: false },
  menu     : { el: 'section-menu',      title: 'Analisis Menu',           init: false },
  trend    : { el: 'section-trend',     title: 'Tren Penjualan',          init: false },
  prediksi : { el: 'section-prediksi',  title: 'Prediksi Juni–Juli 2026', init: false },
  peak     : { el: 'section-peak',      title: 'Analisis Peak Hour',      init: false },
};

document.querySelectorAll('.nav-item').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const key = link.dataset.section;
    switchSection(key);
  });
});

function switchSection(key) {
  // Update nav
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelector(`[data-section="${key}"]`).classList.add('active');

  // Hide all sections
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  $(`section-${key}`).classList.add('active');

  // Page title
  $('page-title').textContent = sections[key].title;

  // Lazy init section
  if (!sections[key].init) {
    sections[key].init = true;
    initFns[key] && initFns[key]();
  }
}

// ── Data cache ──────────────────────────────────────────────────────────────
let DATA = {};

// ── Boot ────────────────────────────────────────────────────────────────────
async function boot() {
  try {
    const [summary, topMenu, kategori, dailyTrend, weeklyTop5, prediksi, peakHour, weatherRevenue] =
      await Promise.all([
        api('/api/summary'),
        api('/api/top-menu'),
        api('/api/kategori'),
        api('/api/daily-trend'),
        api('/api/weekly-top5'),
        api('/api/prediksi'),
        api('/api/peak-hour'),
        api('/api/weather-revenue'),
      ]);

    DATA = { summary, topMenu, kategori, dailyTrend, weeklyTop5, prediksi, peakHour, weatherRevenue };

    // Init overview immediately
    initOverview();
    sections.overview.init = true;

    // Hide loader
    setTimeout(() => {
      $('loadingOverlay').classList.add('hidden');
    }, 400);

  } catch(err) {
    console.error('Boot failed:', err);
    $('loadingOverlay').innerHTML = '<div style="color:#C84A4A;font-size:14px;text-align:center">Gagal memuat data.<br>Pastikan Flask server berjalan.</div>';
  }
}

// ── SECTION: OVERVIEW ───────────────────────────────────────────────────────
function initOverview() {
  const s = DATA.summary;

  // 1. KPI COUNTERS ANIMATION
  animateCounter('kpi-revenue', 0, s.total_revenue, v => rupiah(v));
  animateCounter('kpi-item', 0, s.total_item, v => num(v));
  animateCounter('kpi-trx', 0, s.total_transaksi, v => num(v));
  animateCounter('kpi-avg', 0, s.avg_trx_value, v => rupiah(v));

  // 2. DATA PREPARATION
  const labels      = DATA.dailyTrend.map(d => d.tanggal);
  const revenue     = DATA.dailyTrend.map(d => d.revenue);
  const ma7         = movingAvg(revenue, 7);

  // 3. DAILY TREND CHART (LINE CHART)
  destroyChart('chartDaily');
  charts['chartDaily'] = new Chart($('chartDaily'), {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Revenue Harian',
          data: revenue,
          borderColor: GOLD,
          backgroundColor: hexAlpha(GOLD, .12),
          borderWidth: 1.5,
          pointRadius: 2.5,
          pointHoverRadius: 5,
          fill: true,
          tension: 0.35,
        },
        {
          label: 'Moving Avg 7H',
          data: ma7,
          borderColor: '#FFF',
          borderWidth: 2,
          borderDash: [6, 3],
          pointRadius: 0,
          fill: false,
          tension: 0.35,
        },
      ],
    },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      plugins: { legend: { display: false } },
      scales: {
        y: {
          grid: { color: '#2A2218' },
          ticks: { callback: v => `Rp ${(v/1e6).toFixed(1)}jt` },
        },
        x: { grid: { display: false }, ticks: { maxTicksLimit: 10 } },
      },
    },
  });

  // 4. KATEGORI CHART (DOUGHNUT CHART)
  destroyChart('chartKategori');
  charts['chartKategori'] = new Chart($('chartKategori'), {
    type: 'doughnut',
    data: {
      labels: DATA.kategori.map(k => k.kategori),
      datasets: [{
        data: DATA.kategori.map(k => k.jumlah),
        backgroundColor: [GOLD, BLUE, GREEN, ROSE, PURPLE, GOLD_DK],
        borderColor: '#131009',
        borderWidth: 3,
        hoverOffset: 8,
      }],
    },
    options: {
      responsive: true,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'right',
          labels: { boxWidth: 10, padding: 12, font: { size: 11 } },
        },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.label}: ${ctx.parsed.toLocaleString('id-ID')} unit (${DATA.kategori[ctx.dataIndex].pct}%)`,
          },
        },
      },
    },
  });

  // 5. UPDATE REVISI: GROUPED BAR CHART KOMPARASI BULAN MEI PENUH (PER MINGGU)
  // Ambil semua data tren penjualan lalu filter hanya yang bertanggal di bulan Mei 2026 (Format data dari backend: "YYYY-MM-DD" atau "DD MMM")
  // Untuk memastikan akurasi filter, kita cek string yang mengandung kata kunci Mei atau angka bulan 05.
  const dataMei = DATA.dailyTrend.filter(d => {
    const tglLower = d.tanggal.toLowerCase();
    return tglLower.includes('mei') || tglLower.includes('-05-') || tglLower.startsWith('05/');
  });

  const weeklyLabels = [];
  const weeklyActualRev = [];
  const weeklyEstimatedCerah = [];

  // Bagi 31 hari di bulan Mei menjadi blok-blok per 7 hari (Minggu 1 s.d Minggu 5)
  const daysInWeek = 7;
  for (let i = 0; i < dataMei.length; i += daysInWeek) {
    const chunk = dataMei.slice(i, i + daysInWeek);
    
    if (chunk.length > 0) {
      const weekNum = Math.floor(i / daysInWeek) + 1;
      const startDay = chunk[0].tanggal;
      const endDay = chunk[chunk.length - 1].tanggal;
      
      weeklyLabels.push(`Minggu ${weekNum} (${startDay} - ${endDay})`);

      // Hitung total akumulasi aktual minggu tersebut
      const totalActual = chunk.reduce((sum, item) => sum + item.revenue, 0);
      weeklyActualRev.push(totalActual);

      // Hitung estimasi omzet seandainya cerah (+30% booster dari tren penjualan aktual akibat reduksi hujan)
      const totalEstimated = chunk.reduce((sum, item) => sum + (item.revenue * 1.30), 0);
      weeklyEstimatedCerah.push(totalEstimated);
    }
  }

  destroyChart('chartWeatherRevenue');
  charts['chartWeatherRevenue'] = new Chart($('chartWeatherRevenue'), {
    type: 'bar',
    data: {
      labels: weeklyLabels,
      datasets: [
        {
          label: '☔ Realisasi Omzet (Aktual Mei)',
          data: weeklyActualRev,
          backgroundColor: '#4A90E2', // Biru
          borderRadius: 6
        },
        {
          label: '☀️ Proyeksi Optimal (Jika Full Cerah)',
          data: weeklyEstimatedCerah,
          backgroundColor: GOLD, // Emas Mago
          borderRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: { color: '#7A6E58', font: { size: 11 } }
        },
        tooltip: {
          callbacks: {
            label: function(ctx) {
              let value = ctx.parsed.y.toLocaleString('id-ID');
              return ` ${ctx.dataset.label}: Rp ${value}`;
            }
          }
        },
        title: {
          display: true,
          text: `📊 Analisis Finansial Dampak Cuaca Bulan Mei (Penuh 1 - 31 Mei)`,
          color: GOLD,
          font: { size: 13, weight: 'bold' },
          padding: { bottom: 15 }
        }
      },
      scales: {
        x: {
          stacked: false,
          grid: { display: false },
          ticks: { color: '#7A6E58' }
        },
        y: {
          stacked: false,
          grid: { color: '#2A2218' },
          ticks: {
            color: '#7A6E58',
            callback: v => `Rp ${(v/1e6).toFixed(1)}jt`
          }
        }
      }
    }
  });
}

// ── SECTION: MENU ────────────────────────────────────────────────────────────
function initMenu() {
  const menus   = DATA.topMenu.map(m => m.menu);
  const qty     = DATA.topMenu.map(m => m.jumlah_terjual);
  const rev     = DATA.topMenu.map(m => m.total_revenue / 1e6);

  const barColors = menus.map((_, i) =>
    i < 3 ? GOLD : i < 6 ? GOLD_DK : '#4d3e22'
  );

  const barOpts = (label, yLabel) => ({
    responsive: true,
    indexAxis: 'y',
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: ctx => ` ${yLabel}: ${ctx.parsed.x.toLocaleString('id-ID')}` } },
    },
    scales: {
      x: { grid: { color: '#2A2218' }, ticks: { color: '#7A6E58' } },
      y: { grid: { display: false }, ticks: { font: { size: 11 } } },
    },
  });

  destroyChart('chartTop15Vol');
  charts['chartTop15Vol'] = new Chart($('chartTop15Vol'), {
    type: 'bar',
    data: {
      labels: menus,
      datasets: [{ label: 'Qty', data: qty, backgroundColor: barColors, borderRadius: 4 }],
    },
    options: barOpts('Qty Terjual', 'Qty'),
  });

  destroyChart('chartTop15Rev');
  charts['chartTop15Rev'] = new Chart($('chartTop15Rev'), {
    type: 'bar',
    data: {
      labels: menus,
      datasets: [{ label: 'Revenue (jt Rp)', data: rev, backgroundColor: barColors, borderRadius: 4 }],
    },
    options: barOpts('Revenue (jt Rp)', 'Rp jt'),
  });

  // Table
  const tbody = $('tableMenu').querySelector('tbody');
  tbody.innerHTML = '';
  DATA.topMenu.forEach((m, i) => {
    const r = i + 1;
    const cls = r <= 3 ? `rank-${r}` : 'rank-n';
    tbody.insertAdjacentHTML('beforeend', `
      <tr>
        <td><span class="rank-badge ${cls}">${r}</span></td>
        <td style="color:var(--text-1);font-weight:500">${m.menu}</td>
        <td style="font-family:var(--font-mono)">${num(m.jumlah_terjual)}</td>
        <td style="font-family:var(--font-mono)">${rupiah(m.total_revenue)}</td>
        <td>
          <div style="display:flex;align-items:center;gap:8px">
            <div style="flex:1;height:4px;background:var(--bg-card2);border-radius:99px">
              <div style="width:${m.revenue_pct * 5}%;height:100%;background:${GOLD};border-radius:99px;opacity:.8"></div>
            </div>
            <span style="font-family:var(--font-mono);font-size:11px;color:var(--text-2)">${m.revenue_pct}%</span>
          </div>
        </td>
      </tr>
    `);
  });
}

// ── SECTION: TREND ───────────────────────────────────────────────────────────
function initTrend() {
  // Weekly top5
  const { weeks, menus } = DATA.weeklyTop5;
  const menuColors = [GOLD, GREEN, BLUE, ROSE, PURPLE];

  destroyChart('chartWeekly');
  charts['chartWeekly'] = new Chart($('chartWeekly'), {
    type: 'line',
    data: {
      labels: weeks,
      datasets: Object.entries(menus).map(([name, vals], i) => ({
        label: name,
        data: vals,
        borderColor: menuColors[i],
        backgroundColor: hexAlpha(menuColors[i], .08),
        borderWidth: 2.5,
        pointRadius: 5,
        pointHoverRadius: 7,
        fill: false,
        tension: 0.3,
      })),
    },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          position: 'bottom',
          labels: { boxWidth: 12, padding: 16, font: { size: 11 } },
        },
      },
      scales: {
        y: { grid: { color: '#2A2218' } },
        x: { grid: { display: false } },
      },
    },
  });

  // Daily full
  const labels  = DATA.dailyTrend.map(d => d.tanggal);
  const revenue = DATA.dailyTrend.map(d => d.revenue);
  const ma7     = movingAvg(revenue, 7);

  destroyChart('chartDailyFull');
  charts['chartDailyFull'] = new Chart($('chartDailyFull'), {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Revenue',
          data: revenue,
          borderColor: GOLD,
          backgroundColor: hexAlpha(GOLD, .1),
          borderWidth: 1.5,
          pointRadius: 2,
          fill: true,
          tension: 0.3,
        },
        {
          label: 'MA-7',
          data: ma7,
          borderColor: '#FFFFFF',
          borderWidth: 2.5,
          borderDash: [5, 3],
          pointRadius: 0,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'top', labels: { boxWidth: 12, padding: 14 } },
      },
      scales: {
        y: {
          grid: { color: '#2A2218' },
          ticks: { callback: v => `Rp ${(v/1e6).toFixed(1)}jt` },
        },
        x: { grid: { display: false }, ticks: { maxTicksLimit: 12 } },
      },
    },
  });
}

// ── SECTION: PREDIKSI ────────────────────────────────────────────────────────
function initPrediksi() {
  const top10   = DATA.prediksi.slice(0, 10);
  const labels  = top10.map(d => d.menu);
  const scores  = top10.map(d => d.skor_bi);

  // Bar chart skor
  const barColors = labels.map((_, i) =>
    i === 0 ? GOLD : i < 3 ? hexAlpha(GOLD, .8) : hexAlpha(GOLD, .45)
  );

  destroyChart('chartSkor');
  charts['chartSkor'] = new Chart($('chartSkor'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Skor BI',
        data: scores,
        backgroundColor: barColors,
        borderRadius: 5,
        borderSkipped: false,
      }],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` Skor: ${ctx.parsed.x.toFixed(3)}` } },
      },
      scales: {
        x: { min: 0, max: 1, grid: { color: '#2A2218' }, ticks: { callback: v => v.toFixed(1) } },
        y: { grid: { display: false }, ticks: { font: { size: 11 } } },
      },
    },
  });

  // Proyeksi grouped bar (top 5)
  const top5 = DATA.prediksi.slice(0, 5);
  destroyChart('chartProyeksi');
  charts['chartProyeksi'] = new Chart($('chartProyeksi'), {
    type: 'bar',
    data: {
      labels: top5.map(d => d.menu.split(' ').slice(0,2).join(' ')),
      datasets: [
        {
          label: 'Juni (Proj)',
          data: top5.map(d => d.proyeksi_juni),
          backgroundColor: hexAlpha(GOLD, .8),
          borderRadius: 4,
        },
        {
          label: 'Juli (Proj)',
          data: top5.map(d => d.proyeksi_juli),
          backgroundColor: hexAlpha(GREEN, .75),
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'top', labels: { boxWidth: 10, padding: 12 } },
      },
      scales: {
        y: { grid: { color: '#2A2218' } },
        x: { grid: { display: false }, ticks: { font: { size: 9 } } },
      },
    },
  });

  // Prediction cards (top 5)
  const grid = $('predGrid');
  grid.innerHTML = '';
  DATA.prediksi.slice(0, 5).forEach(d => {
    const trendIcon = d.slope > 5 ? '↑' : d.slope > 0 ? '→' : '↓';
    const trendColor = d.slope > 5 ? GREEN : d.slope > 0 ? GOLD : '#C84A4A';
    grid.insertAdjacentHTML('beforeend', `
      <div class="pred-card">
        <div class="pred-rank">#${d.rank} · Skor BI</div>
        <div class="pred-skor">${d.skor_bi.toFixed(3)}</div>
        <div class="pred-menu">${d.menu}</div>
        <div class="pred-stat">
          <span class="pred-stat-label">Mei Terjual</span>
          <span class="pred-stat-val">${num(d.total_mei)}</span>
        </div>
        <div class="pred-stat">
          <span class="pred-stat-label">Slope (tren)</span>
          <span class="pred-stat-val" style="color:${trendColor}">${trendIcon} ${d.slope}</span>
        </div>
        <div class="pred-stat">
          <span class="pred-stat-label">Growth W1→W5</span>
          <span class="pred-stat-val">${d.growth}%</span>
        </div>
        <div class="pred-stat">
          <span class="pred-stat-label">Proj Juni</span>
          <span class="pred-stat-val" style="color:${GOLD}">${d.proyeksi_juni}</span>
        </div>
        <div class="pred-stat">
          <span class="pred-stat-label">Proj Juli</span>
          <span class="pred-stat-val" style="color:${GREEN}">${d.proyeksi_juli}</span>
        </div>
        <div class="pred-score-bar">
          <div class="pred-score-fill" style="width:${d.skor_bi * 100}%"></div>
        </div>
      </div>
    `);
  });
}

// ── SECTION: PEAK HOUR ───────────────────────────────────────────────────────
function initPeak() {
  const ph = DATA.peakHour;
  const labels = ph.map(d => `${String(d.jam).padStart(2,'0')}:00`);
  const rev    = ph.map(d => d.revenue / 1e3);
  const trx    = ph.map(d => d.transaksi);

  // Identify peak
  const peakIdx = rev.indexOf(Math.max(...rev));
  $('peakLabel').textContent = `Peak Hour: ${labels[peakIdx]}`;

  const barColorsPeak = labels.map((_, i) =>
    i === peakIdx ? GOLD : hexAlpha(GOLD, .4)
  );

  // Revenue chart
  destroyChart('chartPeakRev');
  charts['chartPeakRev'] = new Chart($('chartPeakRev'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Revenue (ribu Rp)',
        data: rev,
        backgroundColor: barColorsPeak,
        borderRadius: 4,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: {
          grid: { color: '#2A2218' },
          ticks: { callback: v => `${(v/1000).toFixed(0)}jt` },
        },
        x: { grid: { display: false } },
      },
    },
  });

  // Transaksi chart
  destroyChart('chartPeakTrx');
  charts['chartPeakTrx'] = new Chart($('chartPeakTrx'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Transaksi',
        data: trx,
        backgroundColor: barColorsPeak,
        borderRadius: 4,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: { grid: { color: '#2A2218' } },
        x: { grid: { display: false } },
      },
    },
  });

  // Heat row
  const heatRow    = $('heatRow');
  const heatLabels = $('heatLabels');
  heatRow.innerHTML = '';
  heatLabels.innerHTML = '';
  const maxTrx = Math.max(...trx);
  ph.forEach((d, i) => {
    const intensity = d.transaksi / maxTrx;
    const h = Math.max(20, Math.round(intensity * 140));
    const alpha = 0.15 + intensity * 0.85;
    heatRow.insertAdjacentHTML('beforeend', `
      <div class="heat-cell"
           style="height:${h}px;background:${hexAlpha(GOLD, alpha)}"
           data-tip="${labels[i]} · ${d.transaksi} trx · ${rupiah(d.revenue)}">
      </div>
    `);
    heatLabels.insertAdjacentHTML('beforeend', `
      <span>${String(d.jam).padStart(2,'0')}</span>
    `);
  });
}

// ── Section init map ─────────────────────────────────────────────────────────
const initFns = { menu: initMenu, trend: initTrend, prediksi: initPrediksi, peak: initPeak };

// ── Counter animation ────────────────────────────────────────────────────────
function animateCounter(id, from, to, formatter, duration = 900) {
  const el = $(id);
  if (!el) return;
  const start = performance.now();
  const step = (now) => {
    const progress = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    el.textContent = formatter(Math.round(from + (to - from) * ease));
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

// ── Hex alpha helper ─────────────────────────────────────────────────────────
function hexAlpha(hex, alpha) {
  const r = parseInt(hex.slice(1,3), 16);
  const g = parseInt(hex.slice(3,5), 16);
  const b = parseInt(hex.slice(5,7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

// ── Start ────────────────────────────────────────────────────────────────────
boot();