/* patch_bank.js — the PATCH BANK: public instruments and patches, cached for offline use.
 *
 * Needs (in this order): patch_sources.js (the catalog), sampler.js (SampleInstrument +
 * SampleFormats), dx7_synth.js (DX7Synth + DX7). audio_kit.js is optional.
 *
 * Nothing is vendored: an item's files are fetched from raw.githubusercontent.com
 * (pinned commit, CORS *) the first time it's loaded and kept in IndexedDB 'mm_patches',
 * so after that it works offline. Your own files (SF2, SFZ folders, .syx, note-named
 * samples, midi-js) import into the same store as source 'local'.
 *
 *   PatchBank.sources()                     → catalog sources (+ licence info, + 'local')
 *   PatchBank.items(srcId) → Promise<[item]>  static items, or (SF2 / DX7) the presets /
 *                                            voices once the bank is downloaded
 *   PatchBank.prepare(srcId, onProgress)    download + index a bank (SF2 / DX7 / zip)
 *   PatchBank.all()        → Promise<[item]> every item known right now (for search)
 *   PatchBank.item(id)     → item | null      (ids: '<source>:<item>')
 *   PatchBank.load(id, ctx, onProgress) → { kind:'sampler'|'dx7', inst?, voice?, item }
 *   PatchBank.createDevice(ctx, id, {output, onProgress}) → a loaded SampleInstrument / DX7Synth
 *   PatchBank.credit(id)   → { line, licence, game:'free'|'credit'|'share-alike', url }
 *   PatchBank.credits(ids) → { lines:[…], worst:'free'|'credit'|'share-alike', text }
 *   PatchBank.isCached(id) / usage() / forget(srcId) / persist()
 *   PatchBank.fav(id, on) / favs()
 *   PatchBank.importFiles(files | dirHandle) → [item]   (local source)
 *   PatchBank.fetchBytes(url) → ArrayBuffer (cache-first)
 *   PatchBank.on('change', fn)
 */
(function (root) {
  "use strict";
  const REG = (typeof PATCH_SOURCES !== 'undefined' ? PATCH_SOURCES : root.PATCH_SOURCES) || { sources: [], licences: {} };
  const G = {
    get SampleInstrument() { return typeof SampleInstrument !== 'undefined' ? SampleInstrument : root.SampleInstrument; },
    get SampleFormats() { return typeof SampleFormats !== 'undefined' ? SampleFormats : root.SampleFormats; },
    get DX7Synth() { return typeof DX7Synth !== 'undefined' ? DX7Synth : root.DX7Synth; },
    get DX7() { return typeof DX7 !== 'undefined' ? DX7 : root.DX7; },
  };
  const listeners = {};
  const emit = (t, d) => (listeners[t] || []).forEach(f => { try { f(d); } catch (e) { console.error(e); } });

  // ── IndexedDB ─────────────────────────────────────────────────────
  let dbp = null;
  function db() {
    if (dbp) return dbp;
    dbp = new Promise((res, rej) => {
      const r = indexedDB.open('mm_patches', 1);
      r.onupgradeneeded = () => {
        const d = r.result;
        d.createObjectStore('files', { keyPath: 'url' });     // { url, bytes, size, t, src }
        d.createObjectStore('meta', { keyPath: 'k' });        // { k, v }
        d.createObjectStore('favs', { keyPath: 'id' });       // { id, t }
      };
      r.onsuccess = () => res(r.result);
      r.onerror = () => rej(r.error);
    });
    return dbp;
  }
  function tx(store, mode, fn) {
    return db().then(d => new Promise((res, rej) => {
      const t = d.transaction(store, mode), s = t.objectStore(store);
      let out; const r = fn(s);
      if (r) r.onsuccess = () => { out = r.result; };
      t.oncomplete = () => res(out); t.onerror = () => rej(t.error); t.onabort = () => rej(t.error);
    }));
  }
  const metaGet = k => tx('meta', 'readonly', s => s.get(k)).then(r => r ? r.v : undefined).catch(() => undefined);
  const metaSet = (k, v) => tx('meta', 'readwrite', s => s.put({ k, v }));

  // ── fetch, cache-first ────────────────────────────────────────────
  const inflight = new Map();
  const memHit = new Set();          // urls known cached (cheap isCached)
  function srcOfUrl(url) { const s = REG.sources.find(x => url.startsWith(x.base)); return s ? s.id : url.startsWith('local:') ? 'local' : ''; }
  async function fetchBytes(url, opts = {}) {
    if (inflight.has(url)) return inflight.get(url);
    const p = (async () => {
      const hit = await tx('files', 'readonly', s => s.get(url)).catch(() => null);
      if (hit && hit.bytes) { memHit.add(url); return hit.bytes; }
      if (url.startsWith('local:')) throw new Error('missing local file ' + url);
      if (url.startsWith('data:')) return (await fetch(url)).arrayBuffer();
      // retry with back-off: Wi-Fi drops and GitHub's rate limiting are both transient
      let r = null, err = null;
      for (let a = 0; a < 4; a++) {
        try { r = await fetch(url, { cache: 'force-cache' }); if (r.ok || r.status === 404) break; err = new Error('HTTP ' + r.status); }
        catch (e) { err = e; r = null; }
        await new Promise(res => setTimeout(res, 400 * Math.pow(2, a) + Math.random() * 300));
      }
      if (!r || !r.ok) throw new Error((r ? 'HTTP ' + r.status : (err && err.message) || 'fetch failed') + ' for ' + decodeURIComponent(url.split('/').slice(-2).join('/')));
      const bytes = await r.arrayBuffer();
      if (opts.store !== false) {
        await tx('files', 'readwrite', s => s.put({ url, bytes, size: bytes.byteLength, t: Date.now(), src: srcOfUrl(url) })).catch(e => console.warn('cache full?', e));
        memHit.add(url);
      }
      return bytes;
    })();
    inflight.set(url, p);
    try { return await p; } finally { inflight.delete(url); }
  }
  const fetchText = async url => new TextDecoder().decode(await fetchBytes(url));
  const enc = path => path.split('/').map(encodeURIComponent).join('/');
  const urlOf = (src, path) => src.base + enc(path);

  async function usage() {
    let bytes = 0, files = 0; const bySrc = {};
    await tx('files', 'readonly', s => {
      const c = s.openCursor();
      c.onsuccess = () => { const cur = c.result; if (!cur) return; const v = cur.value; bytes += v.size || 0; files++; bySrc[v.src || '?'] = (bySrc[v.src || '?'] || 0) + (v.size || 0); cur.continue(); };
      return null;
    });
    let quota = null; try { quota = await navigator.storage.estimate(); } catch (e) {}
    return { bytes, files, bySrc, quota };
  }
  async function forget(srcId) {
    const src = source(srcId);
    await tx('files', 'readwrite', s => {
      const c = s.openCursor();
      c.onsuccess = () => { const cur = c.result; if (!cur) return; if (cur.value.src === srcId) { memHit.delete(cur.value.url); cur.delete(); } cur.continue(); };
      return null;
    });
    if (src && src.kind !== 'local') { await metaSet('index:' + srcId, null); dynIndex.delete(srcId); }
    sf2Cache.delete(srcId);
    emit('change', { forget: srcId });
  }
  async function persist() { try { return await navigator.storage.persist(); } catch (e) { return false; } }

  // ── catalog ───────────────────────────────────────────────────────
  const LOCAL = { id: 'local', name: 'Your imports', author: 'you', kind: 'local', licence: 'own', credit: '', summary: 'Instruments and patches you imported from files on this machine.', items: [] };
  const LIC = Object.assign({ own: { name: 'Your files', game: 'free', note: 'Your own imports — check their licence yourself.' } }, REG.licences);
  function source(id) { return id === 'local' ? LOCAL : REG.sources.find(s => s.id === id) || null; }
  function sources() { return [...REG.sources, LOCAL].map(s => Object.assign({}, s, { licenceInfo: LIC[s.licence] || null, dynamic: ['sf2', 'dx7', 'dx7zip'].includes(s.kind) })); }

  const dynIndex = new Map();     // srcId → items (SF2 presets, DX7 voices)
  const decorate = (src, it) => Object.assign({ source: src.id, uid: src.id + ':' + it.id, licence: src.licence }, it);
  async function items(srcId) {
    const src = source(srcId); if (!src) return [];
    if (srcId === 'local') { const loc = (await metaGet('local:items')) || []; LOCAL.items = loc; return loc.map(it => decorate(LOCAL, it)); }
    if (src.kind === 'waveforms') return src.items.flatMap(b => b.waves.map(w => decorate(src, { id: b.id + '/' + w, name: (b.prefix + w).replace(/^AKWF_/, '').replace(/_/g, ' '), category: 'waveform', bank: b.name, dir: b.dir, file: b.prefix + w + '.wav' })));
    if (!['sf2', 'dx7', 'dx7zip'].includes(src.kind)) return src.items.map(it => decorate(src, it));
    if (!dynIndex.has(srcId)) { const v = await metaGet('index:' + srcId); if (v) dynIndex.set(srcId, v); }
    return (dynIndex.get(srcId) || []).map(it => decorate(src, it));
  }
  async function all() {
    const out = [];
    for (const s of sources()) out.push(...await items(s.id));
    return out;
  }
  let allCache = null;
  async function item(uid) {
    const [srcId, ...rest] = String(uid).split(':'); const id = rest.join(':');
    let list = await items(srcId);
    let it = list.find(i => i.id === id);
    // SF2 / DX7 banks list their presets once downloaded: fetch the bank on first use
    const src = source(srcId);
    if (!it && src && ['sf2', 'dx7', 'dx7zip'].includes(src.kind) && !dynIndex.has(srcId)) { list = await prepareOnce(srcId); it = list.find(i => i.id === id); }
    return it || null;
  }
  const preparing = new Map();
  function prepareOnce(srcId) { if (!preparing.has(srcId)) preparing.set(srcId, prepare(srcId).finally(() => preparing.delete(srcId))); return preparing.get(srcId); }

  // SF2 / DX7 banks: download + index (presets / voice names) so they appear in the lists
  const sf2Cache = new Map();     // srcId|localKey → parsed SF2
  async function sf2For(key, url, onProgress) {
    if (sf2Cache.has(key)) return sf2Cache.get(key);
    onProgress && onProgress({ phase: 'download', done: 0, total: 1 });
    const bytes = await fetchBytes(url);
    onProgress && onProgress({ phase: 'parse', done: 1, total: 1 });
    const sf = G.SampleFormats.parseSF2(bytes);
    sf2Cache.set(key, sf);
    return sf;
  }
  async function unzip(bytes) {           // stored / deflate entries (Dexed's builtin_pgm.zip)
    const v = new DataView(bytes), u8 = new Uint8Array(bytes), out = [];
    let eocd = -1; for (let i = u8.length - 22; i >= 0; i--) if (v.getUint32(i, true) === 0x06054b50) { eocd = i; break; }
    if (eocd < 0) throw new Error('not a zip');
    let p = v.getUint32(eocd + 16, true); const n = v.getUint16(eocd + 10, true);
    for (let k = 0; k < n; k++) {
      const method = v.getUint16(p + 10, true), csize = v.getUint32(p + 20, true), nlen = v.getUint16(p + 28, true), xlen = v.getUint16(p + 30, true), clen = v.getUint16(p + 32, true), off = v.getUint32(p + 42, true);
      const name = new TextDecoder().decode(u8.subarray(p + 46, p + 46 + nlen));
      p += 46 + nlen + xlen + clen;
      const lnl = v.getUint16(off + 26, true), lxl = v.getUint16(off + 28, true), data = u8.slice(off + 30 + lnl + lxl, off + 30 + lnl + lxl + csize);
      let raw = data;
      if (method === 8) raw = new Uint8Array(await new Response(new Blob([data]).stream().pipeThrough(new DecompressionStream('deflate-raw'))).arrayBuffer());
      else if (method !== 0) continue;
      out.push({ name, bytes: raw });
    }
    return out;
  }
  function dx7Items(bankName, bytes, prefix) {
    const r = G.DX7.parseSysex(new Uint8Array(bytes));
    return r.voices.map((v, i) => ({ id: (prefix ? prefix + '/' : '') + i, name: (G.DX7.voiceName ? G.DX7.voiceName(v) : v.name || '').replace(/\s+/g, ' ').trim() || 'voice ' + (i + 1), category: 'fm', bank: bankName, index: i,
      summary: G.DX7.describe ? G.DX7.describe(v) : '' }));
  }
  async function prepare(srcId, onProgress) {
    const src = source(srcId); if (!src) throw new Error('no source ' + srcId);
    if (!['sf2', 'dx7', 'dx7zip'].includes(src.kind)) return items(srcId);
    let list = [];
    if (src.kind === 'sf2') {
      const sf = await sf2For(srcId, urlOf(src, src.file), onProgress);
      list = sf.presets.map(p => ({ id: p.bank + '.' + p.program, name: p.name, category: p.bank >= 120 ? 'drums' : GM_CAT(p.program), bank: p.bank, program: p.program, index: p.index }));
    } else if (src.kind === 'dx7') {
      list = dx7Items(src.name, await fetchBytes(urlOf(src, src.file)), '');
    } else if (src.kind === 'dx7zip') {
      const files = await unzip(await fetchBytes(urlOf(src, src.file)));
      for (const f of files) if (/\.syx$/i.test(f.name)) { try { list.push(...dx7Items(f.name.replace(/\.syx$/i, '').replace(/_/g, ' '), f.bytes.buffer, f.name.replace(/\.syx$/i, ''))); } catch (e) { console.warn(f.name, e); } }
      dx7Zip.set(srcId, files);
    }
    dynIndex.set(srcId, list); await metaSet('index:' + srcId, list);
    emit('change', { prepared: srcId });
    return list.map(it => decorate(src, it));
  }
  const dx7Zip = new Map();
  const GM_CATS = ['piano', 'mallets', 'organ', 'guitar', 'bass', 'strings', 'ensemble', 'brass', 'woodwind', 'woodwind', 'lead', 'pad', 'synth fx', 'world', 'percussion', 'fx'];
  function GM_CAT(prog) { return GM_CATS[Math.floor((prog | 0) / 8)] || 'other'; }

  // ── load an item into something playable ──────────────────────────
  const TOK_VEL = /(?:^|_)(?:v|vl|dyn)(\d+)(?=_|$)/i, TOK_RR = /(?:^|_)rr(\d+)(?=_|$)/i, TOK_DYN = /(?:^|_)(soft|med|medium|loud|pp|p|mp|mf|f|ff)(?=_|$)/i;
  const DYN_ORDER = { pp: 1, soft: 2, p: 2, mp: 3, med: 4, medium: 4, mf: 4, f: 5, loud: 6, ff: 6 };
  // unpitched one-shots (VCSL percussion, etc.): one key per articulation from C3 up; velocity layers + round robin
  function kitFromFiles(files) {
    const groups = new Map();
    for (const f of files) {
      const base = f.name.replace(/\.[a-z0-9]+$/i, '');
      const art = base.replace(TOK_VEL, '').replace(TOK_RR, '').replace(TOK_DYN, '').replace(/_(Sum|Mid|Main|Close|Room|Far|OH)$/i, '').replace(/__+/g, '_');
      if (!groups.has(art)) groups.set(art, []);
      const vm = base.match(TOK_VEL), dm = base.match(TOK_DYN), rm = base.match(TOK_RR);
      groups.get(art).push({ url: f.url, vel: vm ? +vm[1] : dm ? DYN_ORDER[dm[1].toLowerCase()] || 3 : 1, rr: rm ? +rm[1] : 1, name: f.name });
    }
    const zones = [], keymap = [];
    let key = 48;
    for (const [art, fs] of [...groups.entries()].sort()) {
      const vels = [...new Set(fs.map(f => f.vel))].sort((a, b) => a - b), rrs = Math.max(...fs.map(f => f.rr));
      for (const f of fs) {
        const vi = vels.indexOf(f.vel), lo = Math.round(vi * 127 / vels.length) + 1, hi = Math.round((vi + 1) * 127 / vels.length);
        zones.push(G.SampleFormats.makeZone({ sample: f.url, name: f.name, root: key, lokey: key, hikey: key, lovel: vi === 0 ? 0 : lo, hivel: hi, loopMode: 'one_shot',
          seqLength: rrs > 1 ? rrs : 1, seqPosition: rrs > 1 ? Math.min(f.rr, rrs) : 1, env: { release: 0.3 } }));
      }
      keymap.push({ key, name: art.replace(/_/g, ' ') });
      if (++key > 108) break;
    }
    return { zones, keymap };
  }
  async function loadSampler(it, ctx, onProgress) {
    const SF = G.SampleFormats; if (!SF) throw new Error('sampler.js is not loaded');
    const src = source(it.source);
    let inst;
    if (src.kind === 'sf2' || it.kind === 'sf2') {
      const key = it.source === 'local' ? 'local:' + it.file : it.source;
      const url = it.source === 'local' ? it.url : urlOf(src, src.file);
      const sf = await sf2For(key, url, onProgress);
      inst = sf.instrument(it.index, ctx);
      return inst;
    }
    if (src.kind === 'midijs' || it.kind === 'midijs') {
      onProgress && onProgress({ phase: 'download', done: 0, total: 1 });
      inst = SF.parseMidiJsSoundfont(await fetchText(it.url || urlOf(src, it.path)));
    } else if (src.kind === 'sfz' || it.kind === 'sfz') {
      const url = it.url || urlOf(src, it.path);
      const base = url.slice(0, url.lastIndexOf('/') + 1);
      inst = await SF.parseSFZ(await fetchText(url), base, { readText: fetchText });
    } else if (src.kind === 'waveforms') {
      const url = urlOf(src, it.dir + it.file);
      // a 600-sample single cycle at 44.1 kHz sounds at 73.5 Hz (MIDI 38.35): loop the whole cycle
      const r = 69 + 12 * Math.log2(44100 / 600 / 440), rootKey = Math.round(r);
      inst = { format: 'files', name: it.name, unsupported: [], warnings: [], ccInit: {}, curves: {}, keyswitch: null, bend: null,
        zones: [G.SampleFormats.makeZone({ sample: url, name: it.file, root: rootKey, tune: -Math.round((r - rootKey) * 100), loopMode: 'loop_continuous', loopStart: 0, loopEnd: 600,
          env: { attack: 0.004, decay: 0.4, sustain: 0.75, release: 0.25 } })] };
    } else if (src.kind === 'files' || it.kind === 'files') {
      const files = it.urls ? it.urls : it.files.map(f => ({ name: f.split('/').pop(), url: urlOf(src, it.dir + f) }));
      const kit = () => Object.assign({ format: 'files', name: it.name, unsupported: [], warnings: [], ccInit: {}, curves: {}, keyswitch: null, bend: null }, kitFromFiles(files));
      if (it.pitched !== false) { inst = SF.instrumentFromFiles(files, { name: it.name }); if (!inst.zones.length) inst = kit(); else inst.pitchedFiles = true; }
      else inst = kit();
    } else throw new Error('cannot load ' + it.uid);
    inst.name = inst.name || it.name;
    // big multi-layer SFZ pianos (Salamander: 16 layers ≈ 1 GB) → 4 layers: same keys, a fraction of the download
    if (inst.format === 'sfz' && inst.zones.length > 240 && SF.thinLayers) SF.thinLayers(inst, 4);
    await SF.decodeAll(inst, ctx, fetchBytes, (done, total, bytes) => onProgress && onProgress({ phase: 'samples', done, total, bytes }));
    // note-named folders: fill holes left by files that failed, and some libraries call middle C "C3"
    if (inst.pitchedFiles && SF.respread) SF.respread(inst);
    if (inst.pitchedFiles && SF.autoOctave) { try { SF.autoOctave(inst); } catch (e) {} }
    inst.normGainDb = normGain(inst);
    return inst;
  }
  // sources are mastered anywhere from −30 to 0 dBFS: aim a typical note's peak at about −9 dBFS.
  // SF2 banks (GeneralUser) are voiced as a whole, so they're left alone.
  function normGain(inst) {
    if (inst.format === 'sf2') return 0;
    const peaks = [];
    const zs = inst.zones.filter(z => z.buffer && z.trigger !== 'release');
    const step = Math.max(1, Math.floor(zs.length / 24));
    for (let i = 0; i < zs.length; i += step) {
      const b = zs[i].buffer, n = Math.min(b.length, Math.round(b.sampleRate * 1.5)); let pk = 0;
      for (let c = 0; c < b.numberOfChannels; c++) { const d = b.getChannelData(c); for (let k = 0; k < n; k += 2) { const a = d[k] < 0 ? -d[k] : d[k]; if (a > pk) pk = a; } }
      if (pk > 1e-4) peaks.push(pk * Math.pow(10, (zs[i].gain || 0) / 20));
    }
    if (!peaks.length) return 0;
    peaks.sort((a, b) => a - b);
    const med = peaks[peaks.length >> 1];
    return Math.max(-9, Math.min(18, Math.round(20 * Math.log10(0.35 / med))));
  }
  async function loadDx7(it) {
    const src = source(it.source);
    let bytes;
    if (src.kind === 'dx7') bytes = await fetchBytes(urlOf(src, src.file));
    else if (src.kind === 'dx7zip') {
      if (!dx7Zip.has(src.id)) dx7Zip.set(src.id, await unzip(await fetchBytes(urlOf(src, src.file))));
      const f = dx7Zip.get(src.id).find(x => x.name.replace(/\.syx$/i, '') === it.id.split('/')[0]);
      bytes = f.bytes.buffer;
    } else bytes = await fetchBytes(it.url);
    const r = G.DX7.parseSysex(new Uint8Array(bytes));
    return r.voices[it.index];
  }
  async function load(uid, ctx, onProgress) {
    const it = typeof uid === 'object' ? uid : await item(uid);
    if (!it) throw new Error('unknown patch ' + uid);
    if (it.category === 'fm' || ['dx7', 'dx7zip'].includes((source(it.source) || {}).kind) || it.kind === 'dx7') return { kind: 'dx7', voice: await loadDx7(it), item: it };
    return { kind: 'sampler', inst: await loadSampler(it, ctx, onProgress), item: it };
  }
  async function createDevice(ctx, uid, opts = {}) {
    const r = await load(uid, ctx, opts.onProgress);
    let dev;
    if (r.kind === 'dx7') {
      if (!G.DX7Synth) throw new Error('dx7_synth.js is not loaded');
      dev = new G.DX7Synth(ctx, { output: opts.output, maxVoices: opts.maxVoices });
      await dev.init(); dev.loadVoice(r.voice);
    } else {
      if (!G.SampleInstrument) throw new Error('sampler.js is not loaded');
      dev = new G.SampleInstrument(ctx, { output: opts.output, maxVoices: opts.maxVoices, fetchBytes });
      await dev.init(); await dev.load(r.inst, { id: r.item.uid, fetchBytes });
      if (r.inst.normGainDb) dev.set('gain', r.inst.normGainDb);
    }
    dev.patchId = r.item.uid; dev.patchName = r.item.name; dev.keymap = r.inst && r.inst.keymap;
    return dev;
  }
  async function isCached(uid) {
    const it = await item(uid); if (!it) return false;
    const src = source(it.source);
    if (it.source === 'local') return true;
    if (['sf2', 'dx7', 'dx7zip'].includes(src.kind)) return dynIndex.has(src.id);
    const probe = src.kind === 'midijs' || src.kind === 'sfz' ? urlOf(src, it.path) : src.kind === 'waveforms' ? urlOf(src, it.dir + it.file) : urlOf(src, it.dir + it.files[0]);
    if (memHit.has(probe)) return true;
    const hit = await tx('files', 'readonly', s => s.getKey(probe)).catch(() => null);
    if (hit) memHit.add(probe);
    return !!hit;
  }

  // ── credits / licences ────────────────────────────────────────────
  const RANK = { free: 0, credit: 1, 'share-alike': 2 };
  function creditSync(it) {
    const src = source(it.source) || LOCAL, lic = LIC[it.licence || src.licence] || LIC.own;
    let line = src.credit || src.name;
    if (it.credit) line += ' — ' + it.credit;
    if (it.bank && src.kind !== 'sf2') line += ' (' + it.bank + ')';
    return { line, licence: lic.name, game: lic.game, url: lic.url, note: lic.note, source: src.id };
  }
  async function credit(uid) { const it = typeof uid === 'object' ? uid : await item(uid); return it ? creditSync(it) : null; }
  async function credits(uids) {
    const lines = new Map(); let worst = 'free';
    for (const u of uids) {
      const c = await credit(u); if (!c) continue;
      const key = c.source + (c.line);
      if (!lines.has(key)) lines.set(key, c);
      if (RANK[c.game] > RANK[worst]) worst = c.game;
    }
    const list = [...lines.values()];
    const text = list.map(c => c.line + (c.licence ? ' — ' + c.licence : '')).join('\n');
    return { lines: list, worst, text };
  }

  // ── favourites ────────────────────────────────────────────────────
  async function fav(uid, on) { if (on) await tx('favs', 'readwrite', s => s.put({ id: uid, t: Date.now() })); else await tx('favs', 'readwrite', s => s.delete(uid)); emit('change', { fav: uid }); }
  async function favs() { return ((await tx('favs', 'readonly', s => s.getAll()).catch(() => [])) || []).map(f => f.id); }

  // ── local imports ─────────────────────────────────────────────────
  const AUDIO = /\.(wav|flac|ogg|mp3|aif|aiff)$/i;
  async function filesFrom(input) {      // FileList | File[] | FileSystemDirectoryHandle → [{path, file}]
    const out = [];
    if (input && input.kind === 'directory') {
      const walk = async (dir, prefix) => { for await (const [name, h] of dir.entries()) { if (h.kind === 'directory') await walk(h, prefix + name + '/'); else out.push({ path: prefix + name, file: await h.getFile() }); } };
      await walk(input, '');
    } else for (const f of input) out.push({ path: f.webkitRelativePath || f.name, file: f });
    return out;
  }
  async function putLocal(path, file, batch) {
    // local://<batch>/<path>: hierarchical, so SFZ sample paths resolve against it with new URL()
    const url = 'local://' + batch + '/' + path.split('/').map(encodeURIComponent).join('/');
    const bytes = await file.arrayBuffer();
    await tx('files', 'readwrite', s => s.put({ url, bytes, size: bytes.byteLength, t: Date.now(), src: 'local' }));
    memHit.add(url);
    return url;
  }
  async function importFiles(input, onProgress) {
    const files = await filesFrom(input), batch = Date.now().toString(36);
    const added = [], loc = (await metaGet('local:items')) || [];
    const urls = {};
    let n = 0;
    for (const { path, file } of files) { urls[path] = await putLocal(path, file, batch); onProgress && onProgress({ phase: 'import', done: ++n, total: files.length }); }
    const dirOf = p => p.includes('/') ? p.slice(0, p.lastIndexOf('/') + 1) : '';
    for (const { path, file } of files) {
      const ext = (path.match(/\.([a-z0-9]+)$/i) || [])[1] || '';
      const base = path.split('/').pop().replace(/\.[^.]+$/, '');
      if (/^sf2$/i.test(ext)) {
        const sf = G.SampleFormats.parseSF2(await file.arrayBuffer());
        sf2Cache.set('local:' + path, sf);
        for (const p of sf.presets) added.push({ id: batch + '/' + base + '/' + p.bank + '.' + p.program, name: p.name, category: p.bank >= 120 ? 'drums' : GM_CAT(p.program), kind: 'sf2', file: path, url: urls[path], index: p.index, bank: base });
      } else if (/^syx$/i.test(ext)) {
        const r = G.DX7.parseSysex(new Uint8Array(await file.arrayBuffer()));
        r.voices.forEach((v, i) => added.push({ id: batch + '/' + base + '/' + i, name: (G.DX7.voiceName ? G.DX7.voiceName(v) : v.name || ('voice ' + (i + 1))).trim(), category: 'fm', kind: 'dx7', url: urls[path], index: i, bank: base }));
      } else if (/^sfz$/i.test(ext)) {
        // samples resolve relative to the .sfz inside the imported folder: rewrite to the stored local: urls
        added.push({ id: batch + '/' + path, name: base.replace(/[_-]+/g, ' '), category: 'other', kind: 'sfz', url: urls[path] });
      } else if (/^js$/i.test(ext)) {
        added.push({ id: batch + '/' + base, name: base.replace(/-mp3|-ogg/, '').replace(/_/g, ' '), category: 'other', kind: 'midijs', url: urls[path] });
      }
    }
    // loose audio (no .sfz in the import — an SFZ's samples belong to it) → one instrument per folder:
    // note-named files → pitched, anything else → a one-shot kit
    const hasSfz = files.some(f => /\.sfz$/i.test(f.path));
    const byDir = {};
    if (!hasSfz) for (const { path } of files) if (AUDIO.test(path)) (byDir[dirOf(path)] = byDir[dirOf(path)] || []).push(path);
    for (const [dir, ps] of Object.entries(byDir)) {
      const name = (dir.replace(/\/$/, '').split('/').pop() || ps[0].split('/').pop().replace(/\.[^.]+$/, '')).replace(/[_-]+/g, ' ');
      const list = ps.map(p => ({ name: p.split('/').pop(), url: urls[p] }));
      const pitched = list.filter(f => /(?:^|[_\- ])[A-Ga-g][#sb]?-?\d(?=[_\-. ]|$)/.test(f.name)).length >= Math.min(3, list.length) && list.length > 1;
      added.push({ id: batch + '/' + dir + '*', name, category: pitched ? 'other' : 'percussion', kind: 'files', urls: list, pitched });
    }
    loc.push(...added); await metaSet('local:items', loc); LOCAL.items = loc;
    emit('change', { imported: added.length });
    return added.map(it => decorate(LOCAL, it));
  }
  async function removeLocal(uid) {
    const id = uid.replace(/^local:/, '');
    const loc = ((await metaGet('local:items')) || []).filter(x => x.id !== id);
    await metaSet('local:items', loc); LOCAL.items = loc; emit('change', { removed: uid });
  }

  const API = { sources, source, items, all, item, prepare, load, createDevice, credit, credits, creditSync, isCached, usage, forget, persist,
    fav, favs, importFiles, removeLocal, fetchBytes, fetchText, urlOf, licences: LIC, on: (t, f) => { (listeners[t] = listeners[t] || []).push(f); return () => { listeners[t] = listeners[t].filter(x => x !== f); }; } };
  root.PatchBank = API;
})(typeof window !== 'undefined' ? window : globalThis);
