/*
 * Catalogue layer: lets the trackers run on any store's categories instead of the built-in R for Rabbit map.
 * Plain script (no modules) so the same file is inlined into the published page and loaded by Node.
 *
 * Generic catalogue, stored in the page database as catalog/meta plus catalog/p0..pN:
 *   name        store name shown in the masthead
 *   cats        category names, in display order
 *   segments    up to 3 optional focus groups that cut across categories (a SKU can be in several)
 *   skus        { SKU: [title, category, subcategory, focusIdx] }   focusIdx: indices into segments, e.g. "02"
 *   handles     { productHandle: [category, focusIdx] }            for web landing pages
 *   collections { collectionHandle: category }                     "" = a multi-category collection
 *   excludePages        landing paths left out of every sessions figure (tools, blogs)
 *   noStockCats         categories that hold no stock of their own (bundles, gift cards, services)
 *   noStockSkuPattern   regex source for SKUs that hold no stock of their own, or ""
 */
var TKCatalog = (function () {
  'use strict';
  var CODES = ['R', 'T', 'D'];   // the All Categories tracker colours its three focus groups by these codes
  var MAX_SEGMENTS = 3;
  var SKUS_PER_PART = 1500;

  function codesOf(idx) { return String(idx || '').split('').map(function (i) { return CODES[+i]; }).filter(Boolean).join(''); }

  function validate(c) {
    var errs = [];
    if (!c || typeof c !== 'object') return ['The catalogue is empty.'];
    if (!Array.isArray(c.cats) || !c.cats.length) errs.push('Add at least one category.');
    if (c.segments && c.segments.length > MAX_SEGMENTS) errs.push('Use at most ' + MAX_SEGMENTS + ' focus groups.');
    if (!c.skus || !Object.keys(c.skus).length) errs.push('No SKUs were found.');
    var known = { Unmapped: 1 }; (c.cats || []).forEach(function (x) { known[x] = 1; });
    var stray = 0; Object.keys(c.skus || {}).forEach(function (k) { if (!known[c.skus[k][1]]) stray++; });
    if (stray) errs.push(stray + ' SKUs name a category that is not in the category list.');
    if (c.noStockSkuPattern) { try { new RegExp(c.noStockSkuPattern, 'i'); } catch (e) { errs.push('The no-stock SKU pattern is not a valid regular expression.'); } }
    return errs;
  }

  /* Tracker constants built from a catalogue. Keys match the const names each tracker reads. */
  function apply(kind, c) {
    var cats = c.cats.filter(function (x) { return x !== 'Unmapped'; });
    // An empty list would make the trackers' ShopifyQL `NOT IN ()` invalid, so it becomes one path no store has.
    var out = { NAME: c.name || '', TOOL_PAGES: (c.excludePages || []).length ? c.excludePages.slice() : ['/__no-excluded-page__'] };
    if (kind === 'bfd') {
      var CATS = cats.concat('Unmapped'), ix = {};
      CATS.forEach(function (x, i) { ix[x] = i; });
      var at = function (cat) { return cat in ix ? ix[cat] : ix.Unmapped; };
      out.CATS = CATS; out.SKUMAP = {}; out.HMAP = { p: {}, c: {} };
      Object.keys(c.skus).forEach(function (k) { out.SKUMAP[k] = at(c.skus[k][1]); });
      Object.keys(c.handles || {}).forEach(function (h) { out.HMAP.p[h] = at(c.handles[h][0]); });
      Object.keys(c.collections || {}).forEach(function (h) { var v = c.collections[h]; out.HMAP.c[h] = v ? at(v) : -1; });
      return out;
    }
    if (kind === 'r4r') {
      out.CATS = cats.concat('Unmapped');
      out.FOCUS = (c.segments || []).slice(0, MAX_SEGMENTS);
      out.SCOPE = {}; out.HMAP = { p: {}, c: {} };
      Object.keys(c.skus).forEach(function (k) { var s = c.skus[k]; out.SCOPE[k] = [s[0] || '', codesOf(s[3]), 0, s[2] || 'Other', s[1] || 'Unmapped']; });
      Object.keys(c.handles || {}).forEach(function (h) { var v = c.handles[h]; out.HMAP.p[h] = (v[0] || 'Unmapped') + '|' + codesOf(v[1]); });
      Object.keys(c.collections || {}).forEach(function (h) { var v = c.collections[h]; if (v) out.HMAP.c[h] = v + '|'; });
      out.NO_STOCK_CATS = (c.noStockCats || []).slice();
      out.NO_STOCK_RE = c.noStockSkuPattern ? new RegExp(c.noStockSkuPattern, 'i') : null;
      return out;
    }
    throw new Error('Unknown tracker kind: ' + kind);
  }

  /* The built-in R for Rabbit map as a generic catalogue (for the CSV template and for tests). */
  function fromBuiltIn(r4r) {
    var seg = r4r.FOCUS.slice(), idxOf = function (codes, dol) {
      var s = ''; for (var i = 0; i < CODES.length; i++) if ((codes || '').indexOf(CODES[i]) >= 0 || (CODES[i] === 'D' && dol)) s += i;
      return s;
    };
    var c = { v: 1, name: 'R for Rabbit', source: 'built-in', cats: r4r.CATS.filter(function (x) { return x !== 'Unmapped'; }), segments: seg, skus: {}, handles: {}, collections: {},
      excludePages: r4r.TOOL_PAGES.slice(), noStockCats: ['Combos and Bundles', 'Gift Cards', 'Services'], noStockSkuPattern: '^(combo|codfd|cobw|copb|comf|kits|tgpr)' };
    Object.keys(r4r.SCOPE).forEach(function (k) { var x = r4r.SCOPE[k]; c.skus[k] = [x[0], x[4], x[3], idxOf(x[1], x[2])]; });
    Object.keys(r4r.HMAP.p).forEach(function (h) { var p = r4r.HMAP.p[h].split('|'); c.handles[h] = [p[0], idxOf(p[1], 0)]; });
    Object.keys(r4r.HMAP.c).forEach(function (h) { c.collections[h] = String(r4r.HMAP.c[h]).split('|')[0]; });
    return c;
  }

  /* ---------- CSV: sku,title,category,subcategory,product_handle,focus_groups,collection_handle ---------- */
  var HEAD = ['sku', 'title', 'category', 'subcategory', 'product_handle', 'focus_groups', 'collection_handle'];
  function csvCell(v) { v = v == null ? '' : String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }
  function parseLine(line) {
    var out = [], cur = '', q = false;
    for (var i = 0; i < line.length; i++) {
      var ch = line[i];
      if (q) { if (ch === '"') { if (line[i + 1] === '"') { cur += '"'; i++; } else q = false; } else cur += ch; }
      else if (ch === '"') q = true; else if (ch === ',') { out.push(cur); cur = ''; } else cur += ch;
    }
    out.push(cur); return out.map(function (s) { return s.trim(); });
  }
  function toCsv(c) {
    var rows = [HEAD.join(',')], seg = c.segments || [];
    Object.keys(c.skus).forEach(function (k) {
      var s = c.skus[k];
      rows.push([k, s[0], s[1], s[2], '', String(s[3] || '').split('').map(function (i) { return seg[+i]; }).filter(Boolean).join(';'), ''].map(csvCell).join(','));
    });
    Object.keys(c.handles || {}).forEach(function (h) { var v = c.handles[h]; rows.push(['', '', v[0], '', h, String(v[1] || '').split('').map(function (i) { return seg[+i]; }).filter(Boolean).join(';'), ''].map(csvCell).join(',')); });
    Object.keys(c.collections || {}).forEach(function (h) { rows.push(['', '', c.collections[h], '', '', '', h].map(csvCell).join(',')); });
    return rows.join('\n') + '\n';
  }
  function fromCsv(text, opts) {
    opts = opts || {};
    var lines = String(text).replace(/^﻿/, '').split(/\r?\n/).filter(function (l) { return l.trim(); });
    if (!lines.length) throw new Error('The file is empty.');
    var head = parseLine(lines[0]).map(function (h) { return h.toLowerCase().replace(/\s+/g, '_'); });
    var col = {}; HEAD.forEach(function (h) { col[h] = head.indexOf(h); });
    if (col.category < 0) throw new Error('The CSV needs a "category" column. Expected columns: ' + HEAD.join(', ') + '.');
    var cats = [], seen = {}, segs = [], segIx = {}, c = { v: 1, name: opts.name || '', source: 'csv', cats: cats, segments: segs, skus: {}, handles: {}, collections: {},
      excludePages: opts.excludePages || [], noStockCats: opts.noStockCats || [], noStockSkuPattern: opts.noStockSkuPattern || '' };
    var get = function (r, k) { return col[k] >= 0 ? (r[col[k]] || '') : ''; };
    var segIdx = function (list) {
      return list.split(/[;|]/).map(function (s) { return s.trim(); }).filter(Boolean).map(function (s) {
        if (!(s in segIx)) { if (segs.length >= MAX_SEGMENTS) throw new Error('More than ' + MAX_SEGMENTS + ' focus groups in the file ("' + s + '"). Keep at most ' + MAX_SEGMENTS + '.'); segIx[s] = segs.length; segs.push(s); }
        return segIx[s];
      }).sort().join('');
    };
    for (var i = 1; i < lines.length; i++) {
      var r = parseLine(lines[i]), cat = get(r, 'category');
      if (cat && !seen[cat] && cat !== 'Unmapped') { seen[cat] = 1; cats.push(cat); }
      var sku = get(r, 'sku'), handle = get(r, 'product_handle'), coll = get(r, 'collection_handle'), fx = segIdx(get(r, 'focus_groups'));
      if (sku) c.skus[sku] = [get(r, 'title'), cat || 'Unmapped', get(r, 'subcategory'), fx];
      if (handle) {
        var prev = c.handles[handle];
        c.handles[handle] = [cat || (prev && prev[0]) || 'Unmapped', mergeIdx(prev && prev[1], fx)];
      }
      if (coll && !sku && !handle) c.collections[coll] = cat;
    }
    return c;
  }
  function mergeIdx(a, b) { var s = {}; (String(a || '') + String(b || '')).split('').forEach(function (x) { s[x] = 1; }); return Object.keys(s).sort().join(''); }

  /* ---------- Shopify: products and collections from Admin GraphQL ---------- */
  var PRODUCTS_Q = 'query($after: String) { products(first: 100, after: $after) { pageInfo { hasNextPage endCursor } nodes { handle title productType tags variants(first: 100) { nodes { sku } } } } }';
  var COLLECTIONS_Q = 'query($after: String) { collections(first: 250, after: $after) { pageInfo { hasNextPage endCursor } nodes { handle title } } }';

  /* opts: { groupBy: 'product_type' | 'tag_prefix', tagPrefix, subTagPrefix, focusTags: [], name } */
  function fromShopify(products, collections, opts) {
    opts = opts || {};
    var by = opts.groupBy || 'product_type', pre = (opts.tagPrefix || '').toLowerCase(), subPre = (opts.subTagPrefix || '').toLowerCase();
    var focus = (opts.focusTags || []).map(function (t) { return t.trim(); }).filter(Boolean).slice(0, MAX_SEGMENTS);
    var focusLc = focus.map(function (t) { return t.toLowerCase(); });
    var count = {}, c = { v: 1, name: opts.name || '', source: 'shopify:' + by + (by === 'tag_prefix' ? ':' + opts.tagPrefix : ''), cats: [], segments: focus, skus: {}, handles: {}, collections: {},
      excludePages: opts.excludePages || [], noStockCats: opts.noStockCats || [], noStockSkuPattern: opts.noStockSkuPattern || '' };
    var tagged = function (tags, prefix) {
      if (!prefix) return '';
      for (var i = 0; i < tags.length; i++) if (tags[i].toLowerCase().indexOf(prefix) === 0) return tags[i].slice(prefix.length).trim();
      return '';
    };
    (products || []).forEach(function (p) {
      var tags = p.tags || [];
      var cat = (by === 'tag_prefix' ? tagged(tags, pre) : (p.productType || '').trim()) || 'Unmapped';
      var sub = subPre ? tagged(tags, subPre) : (by === 'tag_prefix' ? (p.productType || '').trim() : '');
      var fx = focusLc.map(function (t, i) { return tags.some(function (x) { return x.toLowerCase() === t; }) ? String(i) : ''; }).join('');
      if (cat !== 'Unmapped') count[cat] = (count[cat] || 0) + 1;
      ((p.variants && p.variants.nodes) || []).forEach(function (v) { var s = (v.sku || '').trim(); if (s) c.skus[s] = [String(p.title || '').slice(0, 90), cat, sub, fx]; });
      if (p.handle) c.handles[p.handle] = [cat, fx];
    });
    c.cats = Object.keys(count).sort(function (a, b) { return count[b] - count[a] || (a < b ? -1 : 1); });
    var lc = {}; c.cats.forEach(function (x) { lc[x.toLowerCase()] = x; });
    (collections || []).forEach(function (k) { c.collections[k.handle] = lc[String(k.title || '').trim().toLowerCase()] || ''; });
    return c;
  }

  /* ---------- storage: split so a large catalogue stays under the per-document size limit ---------- */
  function toDocs(c) {
    var keys = Object.keys(c.skus), parts = [], hk = Object.keys(c.handles || {});
    for (var i = 0; i < Math.max(keys.length, 1); i += SKUS_PER_PART) {
      var p = { skus: {}, handles: {} };
      keys.slice(i, i + SKUS_PER_PART).forEach(function (k) { p.skus[k] = c.skus[k]; });
      parts.push(p);
    }
    hk.forEach(function (h, j) { parts[j % parts.length].handles[h] = c.handles[h]; });
    var meta = { v: 1, name: c.name || '', source: c.source || '', builtAt: c.builtAt || Date.now(), cats: c.cats, segments: c.segments || [], collections: c.collections || {},
      excludePages: c.excludePages || [], noStockCats: c.noStockCats || [], noStockSkuPattern: c.noStockSkuPattern || '', parts: parts.length, skuCount: keys.length };
    return { meta: meta, parts: parts };
  }
  function fromDocs(meta, parts) {
    var c = {}; Object.keys(meta).forEach(function (k) { if (k !== 'parts') c[k] = meta[k]; });
    c.skus = {}; c.handles = {};
    parts.forEach(function (p) { Object.assign(c.skus, p.skus || {}); Object.assign(c.handles, p.handles || {}); });
    return c;
  }

  return { CODES: CODES, MAX_SEGMENTS: MAX_SEGMENTS, validate: validate, apply: apply, fromBuiltIn: fromBuiltIn, toCsv: toCsv, fromCsv: fromCsv,
    PRODUCTS_Q: PRODUCTS_Q, COLLECTIONS_Q: COLLECTIONS_Q, fromShopify: fromShopify, toDocs: toDocs, fromDocs: fromDocs };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = TKCatalog;
