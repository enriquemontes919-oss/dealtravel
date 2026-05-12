function renderHotDeals(ofertas) {
  const hot = ofertas.filter(o => o.tipo !== 'viajes').slice(0, 4);
  const grid = document.getElementById('hot-grid');
  if(!hot.length) { grid.innerHTML = ''; return; }
  grid.innerHTML = hot.map(o => {
    const sinPrecio = o.precio_fmt === 'Ver precio';
    return `
    <a href="${o.url}" target="_blank" rel="noopener noreferrer" style="text-decoration:none;">
      <div class="hot-card">
        <div class="hot-card-store">${o.fuente}</div>
        <div class="hot-card-title">${o.destino}</div>
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:4px;">
          ${!sinPrecio && o.precio_original ? `<span style="text-decoration:line-through;color:#aeaeb2;font-size:0.8rem;">$${o.precio_original.toLocaleString('es-MX')} MXN</span>` : ''}
          ${sinPrecio
            ? `<span style="font-size:0.95rem;font-weight:700;color:#0071e3;">Ver precio →</span>`
            : `<span class="hot-card-price">${o.precio_fmt}</span>`}
          ${!sinPrecio && o.descuento_pct ? `<span style="background:#ff3b30;color:#fff;font-size:0.65rem;font-weight:700;padding:2px 7px;border-radius:6px;">-${o.descuento_pct}%</span>` : ''}
        </div>
        <div class="hot-card-promo">${o.tipo_promo}</div>
      </div>
    </a>`}).join('');
}

function renderOfertas(ofertas) {
  const grid = document.getElementById('deals-grid');
  if(!ofertas || ofertas.length === 0) {
    grid.innerHTML = '<div class="no-results">No hay ofertas en esta categoría.</div>';
    return;
  }
  grid.innerHTML = ofertas.map(o => {
    const sinPrecio = o.precio_fmt === 'Ver precio';
    return `
    <div class="deal-card" data-tipo="${o.tipo||'general'}">
      <div class="deal-img-wrap">
        <div class="deal-img-placeholder">${ICONS[o.tipo]||'🛍️'}</div>
        <span class="deal-discount">${!sinPrecio && o.descuento_pct ? `-${o.descuento_pct}%` : 'Oferta'}</span>
        <span class="deal-store">${o.fuente}</span>
      </div>
      <div class="deal-body">
        <div class="deal-category">${o.tipo||'General'}</div>
        <div class="deal-title">${o.destino||'Producto en oferta'}</div>
        <div class="deal-promo">${o.tipo_promo||''}</div>
        <div class="deal-footer">
          <div class="deal-prices">
            ${!sinPrecio && o.precio_original ? `<div class="deal-old">$${o.precio_original.toLocaleString('es-MX')} MXN</div>` : ''}
            ${sinPrecio
              ? `<div style="font-size:1rem;font-weight:700;color:#0071e3;">Ver precio →</div>`
              : `<div class="deal-price">${o.precio_fmt}</div>`}
          </div>
          <a href="${o.url}" target="_blank" rel="noopener noreferrer" class="deal-btn">Ver →</a>
        </div>
      </div>
    </div>`}).join('');
}
