(() => {
  const DEMO = /*DEMO*/false;
  const KEYS = ['bfd', 'r4r'];
  const $ = id => document.getElementById(id);
  const use = n => (window.claude && typeof window.claude.use === 'function' ? window.claude.use(n).catch(() => null) : Promise.resolve(null));
  const within = (p, ms) => Promise.race([p, new Promise(r => setTimeout(() => r(null), ms))]);
  const fmt = n => Number(n).toLocaleString('en-IN');
  const skusTxt = n => `${fmt(n)} SKU${n === 1 ? '' : 's'}`;

  /* ---------- which tracker ---------- */
  let stored = null;
  try { stored = localStorage.getItem('tk.which'); } catch (e) {}
  const fromHash = location.hash.slice(1);
  const which = KEYS.includes(fromHash) ? fromHash : KEYS.includes(stored) ? stored : 'bfd';
  try { localStorage.setItem('tk.which', which); } catch (e) {}
  if (DEMO) try { ['bfd.tab2', 'rtd.tab'].forEach(k => { if (!localStorage.getItem(k)) localStorage.setItem(k, 'sum'); }); } catch (e) {}   // D0 needs live data
  if (KEYS.includes(fromHash)) history.replaceState(null, '', location.pathname + location.search);
  document.querySelectorAll('.tk-switch [data-k]').forEach(b => {
    b.setAttribute('aria-pressed', String(b.dataset.k === which));
    b.addEventListener('click', () => {
      if (b.dataset.k === which) return;
      try { localStorage.setItem('tk.which', b.dataset.k); } catch (e) {}
      location.hash = b.dataset.k;
      location.reload();
    });
  });

  /* ---------- the built-in R for Rabbit set, read from the All Categories tracker's own constants ---------- */
  function builtIn() {
    if (!window.__TK_BUILTIN) {
      const want = ['SCOPE', 'CATS', 'HMAP', 'FOCUS', 'TOOL_PAGES'];
      const lines = $('tk-r4r-js').textContent.split('\n').filter(l => want.some(n => l.startsWith(`const ${n} = `)));
      const s = document.createElement('script');
      s.textContent = `(() => { const __OV = {};\n${lines.join('\n')}\nwindow.__TK_BUILTIN = { ${want.join(', ')} }; })();`;
      document.head.appendChild(s); s.remove();
    }
    return TKCatalog.fromBuiltIn(window.__TK_BUILTIN);
  }

  /* ---------- saved catalogue ---------- */
  async function loadCatalog(db) {
    try {
      const m = await db.doc('catalog/meta').get();
      const meta = m.exists && m.data();
      if (!meta || meta.v !== 1) return null;
      const parts = await Promise.all(Array.from({ length: meta.parts }, (_, i) => db.doc('catalog/p' + i).get().then(s => (s.exists ? s.data() : {}))));
      const c = TKCatalog.fromDocs(meta, parts);
      return TKCatalog.validate(c).length ? null : c;
    } catch (e) { return null; }
  }

  /* On phones the sale-day strip scrolls sideways; bring today's cell into view whenever the strip is redrawn. */
  function centreStrip() {
    const strip = document.querySelector('#tk-mount .strip');
    if (!strip || strip.scrollWidth <= strip.clientWidth) return;
    const cell = strip.querySelector('.today') || strip.querySelector('.sel');
    if (!cell || strip.dataset.tkCentred) return;
    const x = cell.getBoundingClientRect().left - strip.getBoundingClientRect().left + strip.scrollLeft;
    strip.scrollLeft = x - strip.clientWidth / 2 + cell.offsetWidth / 2;
    strip.dataset.tkCentred = '1';
  }
  function mount(cat) {
    $('tk-mount').appendChild($('tk-' + which + '-ui').content.cloneNode(true));
    new MutationObserver(centreStrip).observe($('tk-mount'), { childList: true, subtree: true });
    const run = document.createElement('script');
    run.textContent = $('tk-' + which + '-js').textContent;
    document.body.appendChild(run);
    if (!cat) return;
    const eb = document.querySelector('#tk-mount .eyebrow');
    if (eb && cat.name) eb.textContent = eb.textContent.replace('R for Rabbit', cat.name);
    if (which === 'r4r') {
      const offers = document.querySelector('#tk-mount .offers');
      if (offers) {
        const cols = ['var(--ride)', 'var(--toy)', 'var(--dol)'];
        offers.textContent = '';
        (cat.segments || []).forEach((g, i) => {
          const chip = document.createElement('span'); chip.className = 'chip';
          const dot = document.createElement('span'); dot.className = 'dot'; dot.style.background = cols[i];
          chip.append(dot, g); offers.appendChild(chip);
        });
        offers.hidden = !(cat.segments || []).length;
      }
    }
  }

  function summaryOf(cat) {
    if (!cat) return 'Built-in R for Rabbit set';
    const src = String(cat.source || '');
    const tpl = src.match(/:template:(.+)$/), tplName = tpl && (TKPresets.choices().templates.concat(TKPresets.choices().brands).find(x => x.id === tpl[1]) || {}).name;
    const from = tpl ? `${tplName || 'template'} template, ${src.startsWith('csv') ? 'CSV' : 'Shopify'}` : src.startsWith('shopify:tag_prefix') ? 'Shopify tags' : src.startsWith('shopify') ? 'Shopify product types' : src === 'csv' ? 'CSV' : src;
    return `${cat.name || 'Custom set'} · ${fmt(cat.cats.length)} categories · ${fmt(cat.skuCount || Object.keys(cat.skus).length)} SKUs` +
      ((cat.segments || []).length ? ` · focus: ${cat.segments.join(', ')}` : '') + (from ? ` · from ${from}` : '');
  }

  /* ---------- categories panel ---------- */
  function panel(db, current) {
    const status = (msg, kind) => { const s = $('tkStatus'); s.textContent = msg || ''; s.className = 'tk-status' + (kind ? ' ' + kind : ''); };
    const src = () => document.querySelector('input[name="tkSrc"]:checked').value;
    let candidate = null, filled = false;

    $('tkCatSummary').textContent = summaryOf(current);
    $('tkReset').hidden = !current;

    const fill = () => {
      if (filled) return; filled = true;
      const base = current || builtIn();
      $('tkName').value = base.name || '';
      $('tkExclude').value = (base.excludePages || []).join('\n');
      $('tkNoStock').value = (base.noStockCats || []).join(', ');
      $('tkNoStockRe').value = base.noStockSkuPattern || '';
      if (current && String(current.source).startsWith('shopify:tag_prefix:')) { $('tkSrcTag').checked = true; $('tkTagPrefix').value = current.source.split(':').slice(2).join(':'); }
      if (current && (current.segments || []).length) $('tkFocus').value = current.segments.join(', ');
      const tplSrc = current && String(current.source).match(/:template:(.+)$/);
      if (tplSrc && TKPresets.template(tplSrc[1])) sel.value = tplSrc[1];
      if (!current) { sel.value = 'streetwear'; applyTpl(); $('tkName').value = base.name || ''; }
      else if (current) $(String(current.source).startsWith('shopify:tag_prefix') ? 'tkSrcTag' : String(current.source) === 'csv' ? 'tkSrcCsv' : 'tkSrcType').checked = true;
      sync();
    };
    const sync = () => {
      const s = src();
      $('tkTplWrap').hidden = s !== 'template';
      $('tkTagWrap').hidden = s !== 'tag_prefix';
      $('tkCsvWrap').hidden = s !== 'csv' && s !== 'template';
      $('tkFocusWrap').hidden = s === 'csv';
      $('tkCsvHelp').textContent = s === 'template'
        ? 'Optional. Leave empty to sort your Shopify products, or upload a CSV with sku and title (product_type and tags help) to sort those instead.'
        : 'Columns: sku, title, category, subcategory, product_handle, focus_groups, collection_handle. Download the current set below as a template.';
      $('tkBuild').textContent = s === 'csv' || (s === 'template' && $('tkCsv').files[0]) ? 'Read CSV' : 'Build from Shopify';
    };
    /* template picker: verticals, then brand starters */
    const ch = TKPresets.choices(), sel = $('tkTpl');
    const group = (label, items) => { const g = document.createElement('optgroup'); g.label = label; items.forEach(i => { const o = document.createElement('option'); o.value = i.id; o.textContent = i.templateName ? `${i.name} (${i.templateName})` : i.name; g.appendChild(o); }); sel.appendChild(g); };
    group('Category templates', ch.templates);
    group('Brand starters', ch.brands);
    const applyTpl = () => {
      const d = TKPresets.defaults(sel.value); if (!d) return;
      if (d.name) $('tkName').value = d.name;
      $('tkFocus').value = d.focusTags.join(', ');
      $('tkNoStock').value = d.noStockCats.join(', ');
      $('tkExclude').value = '';      // the previous store's excluded pages and SKU pattern do not carry over
      $('tkNoStockRe').value = '';
    };
    sel.addEventListener('change', applyTpl);
    $('tkCsv').addEventListener('change', sync);
    $('tkCat').addEventListener('toggle', () => { if ($('tkCat').open) fill(); });
    document.querySelectorAll('input[name="tkSrc"]').forEach(r => r.addEventListener('change', sync));
    if (!db) { $('tkBuild').disabled = true; status('Categories can only be changed where this page can save data.', 'bad'); }

    const opts = () => ({
      name: $('tkName').value.trim(),
      excludePages: $('tkExclude').value.split('\n').map(s => s.trim()).filter(Boolean),
      noStockCats: $('tkNoStock').value.split(',').map(s => s.trim()).filter(Boolean),
      noStockSkuPattern: $('tkNoStockRe').value.trim(),
    });

    function preview(c) {
      const errs = TKCatalog.validate(c);
      const box = $('tkPreview'); box.hidden = false; box.textContent = '';
      const counts = {}; Object.values(c.skus).forEach(s => { counts[s[1]] = (counts[s[1]] || 0) + 1; });
      const head = document.createElement('div');
      head.textContent = `${fmt(Object.keys(c.skus).length)} SKUs in ${fmt(c.cats.length)} categories, ${fmt(Object.keys(c.handles).length)} product pages` +
        ((c.segments || []).length ? `, focus groups: ${c.segments.join(', ')}` : '') + (counts.Unmapped ? `. ${skusTxt(counts.Unmapped)} matched no category and ${counts.Unmapped === 1 ? 'shows' : 'show'} as Unmapped.` : '.');
      box.appendChild(head);
      const ul = document.createElement('ul');
      c.cats.slice(0, 40).forEach(k => { const li = document.createElement('li'); li.textContent = `${k}: ${skusTxt(counts[k] || 0)}`; ul.appendChild(li); });
      if (c.cats.length > 40) { const li = document.createElement('li'); li.textContent = `and ${c.cats.length - 40} more`; ul.appendChild(li); }
      box.appendChild(ul);
      if (errs.length) { status(errs.join(' '), 'bad'); $('tkSaveRow').hidden = true; candidate = null; return; }
      candidate = c; $('tkSaveRow').hidden = false; status('Check the list, then save.');
    }

    async function fromShopify() {
      const mcp = await use('mcp');
      if (!mcp) { status('Shopify is not available here. Connect the Shopify connector in claude.ai Settings, Connectors, or use a CSV.', 'bad'); return null; }
      const gql = async (query, after) => {
        const r = await mcp.callTool('Shopify', 'graphql_query', { query, variables: after ? { after } : {} });
        let p = r && r.payload; if (typeof p === 'string') p = JSON.parse(p);
        return (p && p.data) || p;
      };
      const pageAll = async (query, key, label) => {
        const out = []; let after = null;
        for (let i = 0; i < 120; i++) {
          const d = await gql(query, after); const conn = d && d[key];
          if (!conn || !Array.isArray(conn.nodes)) throw new Error(`Shopify returned an unexpected ${key} response.`);
          out.push(...conn.nodes); status(`Reading ${label}… ${fmt(out.length)}`);
          if (!conn.pageInfo || !conn.pageInfo.hasNextPage) break;
          after = conn.pageInfo.endCursor;
        }
        return out;
      };
      const products = await pageAll(TKCatalog.PRODUCTS_Q, 'products', 'products');
      const collections = await pageAll(TKCatalog.COLLECTIONS_Q, 'collections', 'collections');
      const groupBy = src();
      if (groupBy === 'tag_prefix' && !$('tkTagPrefix').value.trim()) throw new Error('Enter the tag prefix that names the category, for example "Category: ".');
      return TKCatalog.fromShopify(products, collections, { ...opts(), groupBy, template: $('tkTpl').value, tagPrefix: $('tkTagPrefix').value, focusTags: $('tkFocus').value.split(',') });
    }

    $('tkBuild').addEventListener('click', async () => {
      $('tkBuild').disabled = true; $('tkSaveRow').hidden = true; candidate = null; status('Working…');
      try {
        let c;
        const f = $('tkCsv').files[0];
        if (src() === 'csv') {
          if (!f) throw new Error('Choose a CSV file first.');
          c = TKCatalog.fromCsv(await f.text(), opts());
        } else if (src() === 'template' && f) {
          c = TKCatalog.fromCsv(await f.text(), { ...opts(), template: $('tkTpl').value });
        } else c = await fromShopify();
        if (c) { c.builtAt = Date.now(); preview(c); }
      } catch (e) {
        status((e && e.message) || 'That did not work. Check the connector and try again.', 'bad');
      } finally { $('tkBuild').disabled = !db; }
    });

    $('tkDiscard').addEventListener('click', () => { candidate = null; $('tkPreview').hidden = true; $('tkSaveRow').hidden = true; status(''); });

    $('tkSave').addEventListener('click', async () => {
      if (!candidate || !db) return;
      $('tkSave').disabled = true; status('Saving…');
      try {
        const { meta, parts } = TKCatalog.toDocs(candidate);
        for (let i = 0; i < parts.length; i++) await db.doc('catalog/p' + i).set(parts[i]);
        await db.doc('catalog/meta').set(meta);   // last, so readers never see a meta without its parts
        status('Saved. Reloading…', 'good');
        setTimeout(() => location.reload(), 600);
      } catch (e) {
        $('tkSave').disabled = false;
        status(e && /permission|not_granted|denied|forbidden/i.test(String(e.code || e.message)) ? 'You can view this page but not change its categories. Ask the owner for edit access.' : 'Saving failed. Try again in a moment.', 'bad');
      }
    });

    let armed = false;
    $('tkReset').addEventListener('click', async () => {
      if (!armed) { armed = true; $('tkReset').textContent = 'Click again to switch back'; setTimeout(() => { armed = false; $('tkReset').textContent = 'Back to built-in categories'; }, 4000); return; }
      try { await db.doc('catalog/meta').delete(); status('Switched back. Reloading…', 'good'); setTimeout(() => location.reload(), 600); }
      catch (e) { status('Could not switch back. You may not have edit access.', 'bad'); }
    });

    use('downloads').then(dl => {
      if (!dl) { $('tkExport').hidden = true; return; }
      $('tkExport').addEventListener('click', async () => {
        try { await dl.save({ filename: 'categories.csv', data: TKCatalog.toCsv(current || builtIn()) }); status('Saved categories.csv', 'good'); }
        catch (e) { status(e && e.code === 'declined' ? 'Download cancelled.' : 'Download is not available here.', e && e.code === 'declined' ? '' : 'bad'); }
      });
    });
  }

  (async () => {
    const db = await within(use('db'), 6000);
    const cat = db ? await loadCatalog(db) : null;
    if (cat) window.__TK_OV = TKCatalog.apply(which, cat);
    mount(cat);
    panel(db, cat);
  })();
})();
