/* harness.js — shared helpers for the godot/tools browser-tool tests.
 *
 * Tests open the real pages from file:// in headless Chromium WITHOUT
 * --allow-file-access-from-files (that flag once hid a bug the Deck hit), and
 * fail on any page error or console error.
 *
 *   const { suite } = require('./harness');
 *   suite('name', async t => {
 *     const { p, errors } = await t.page('daw.html', { touch: true });
 *     await t.test('does a thing', async () => { t.ok(...); t.near(a, b, tol); });
 *   });
 *
 * Env: CHROME_PATH (browser binary), TEST_NETWORK=1 (tests that download from GitHub),
 *      HTTPS_PROXY (used by the browser when set — needed in the cloud sandbox).
 */
const path = require('path'), fs = require('fs');
const TOOLS = path.resolve(__dirname, '..');
const CANDIDATES = [process.env.CHROME_PATH, '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', '/opt/pw-browsers/chromium/chrome-linux/chrome'];

function playwright() {
  try { return require('playwright'); } catch (e) {
    try { return require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright'); }
    catch (e2) { console.error('playwright is not installed (npm i -g playwright)'); process.exit(2); }
  }
}

class Suite {
  constructor(name) { this.name = name; this.pass = 0; this.fail = 0; this.skipped = 0; this.browsers = []; }
  async browser(opts = {}) {
    const { chromium } = playwright();
    const exe = CANDIDATES.find(p => p && fs.existsSync(p));
    const args = ['--autoplay-policy=no-user-gesture-required'];
    if (opts.fakeMedia) args.push('--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream');
    const b = await chromium.launch({ executablePath: exe, args, proxy: opts.network && process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined });
    this.browsers.push(b);
    return b;
  }
  // open a tool page; returns { p, ctx, errors, cdp? }
  async page(file, opts = {}) {
    const b = opts.browser || await this.browser(opts);
    const ctx = await b.newContext({ viewport: { width: 1280, height: 800 }, hasTouch: !!opts.touch, ignoreHTTPSErrors: !!opts.network, permissions: opts.fakeMedia ? ['microphone'] : [] });
    // context-wide hooks reach pop-ups too (a page's own init script doesn't)
    for (const [name, fn] of Object.entries(opts.expose || {})) await ctx.exposeFunction(name, fn);
    if (opts.ctxInit) await ctx.addInitScript(opts.ctxInit);
    const p = await ctx.newPage();
    const errors = [];
    this.watch(p, errors, opts);
    if (opts.init) await p.addInitScript(opts.init);
    await p.goto('file://' + path.join(TOOLS, file));
    await p.waitForTimeout(opts.settle ?? 300);
    const out = { p, ctx, errors };
    if (opts.touch) out.cdp = await ctx.newCDPSession(p);
    if (opts.start) { await p.evaluate(() => document.getElementById('gatebtn') && document.getElementById('gatebtn').click()); await p.waitForTimeout(800); }
    return out;
  }
  // collect page errors and console errors of a page (also a pop-up) into `errors`
  watch(p, errors, opts = {}) {
    p.on('pageerror', e => errors.push('pageerror: ' + e.message));
    // network suites: GitHub rate-limits bursts (429) and PatchBank.fetchBytes retries — Chrome still logs them
    const transient = opts.network ? /ERR_TOO_MANY_RETRIES|status of (429|5\d\d)/ : /ERR_TOO_MANY_RETRIES/;
    p.on('console', m => { if (m.type() === 'error' && !transient.test(m.text())) errors.push('console: ' + m.text().slice(0, 300)); });
  }
  async test(name, fn) {
    const t0 = Date.now();
    try { await fn(); this.pass++; console.log(`  ✓ ${name} (${((Date.now() - t0) / 1000).toFixed(1)} s)`); }
    catch (e) { this.fail++; console.log(`  ✗ ${name}: ${e && e.message ? e.message : e}`); }
  }
  skip(name, why) { this.skipped++; console.log(`  · ${name} — skipped (${why})`); }
  ok(v, msg) { if (!v) throw new Error(msg || 'expected truthy'); }
  eq(a, b, msg) { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error((msg ? msg + ': ' : '') + `got ${JSON.stringify(a)}, want ${JSON.stringify(b)}`); }
  near(a, b, tol, msg) { if (!(Math.abs(a - b) <= tol)) throw new Error((msg ? msg + ': ' : '') + `got ${a}, want ${b} ± ${tol}`); }
  noErrors(errors) { if (errors.length) throw new Error(errors.slice(0, 3).join(' | ')); }
  // touch helpers (CDP)
  touch(cdp) {
    const T = (type, pts) => cdp.send('Input.dispatchTouchEvent', { type, touchPoints: pts });
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    return {
      tap: async (x, y) => { await T('touchStart', [{ x, y }]); await sleep(40); await T('touchEnd', []); await sleep(60); },
      hold: async (x, y, ms = 750) => { await T('touchStart', [{ x, y }]); await sleep(ms); await T('touchEnd', []); await sleep(60); },
      drag: async (x, y, dx, dy, steps = 10) => { await T('touchStart', [{ x, y }]); for (let i = 1; i <= steps; i++) { await T('touchMove', [{ x: x + dx * i / steps, y: y + dy * i / steps }]); await sleep(16); } await T('touchEnd', []); await sleep(60); },
    };
  }
  async done() {
    for (const b of this.browsers) { try { await b.close(); } catch (e) {} }
    console.log(`${this.fail ? '✗' : '✓'} ${this.name}: ${this.pass} passed, ${this.fail} failed${this.skipped ? ', ' + this.skipped + ' skipped' : ''}`);
    process.exitCode = this.fail ? 1 : 0;
  }
}

async function suite(name, body) {
  const s = new Suite(name);
  console.log('▸ ' + name);
  try { await body(s); } catch (e) { s.fail++; console.log('  ✗ suite crashed: ' + (e && e.stack || e)); }
  await s.done();
}

// Node side of the vendored Ogg Vorbis encoder (the same file AK.ogg loads), for fixture audio:
// channels: Float32Array[] (1 or 2) → Buffer (.ogg)
let oggMod = null;
async function oggEncode(channels, sr, quality = 4) {
  if (!oggMod) {
    require('vm').runInThisContext(fs.readFileSync(path.join(TOOLS, 'vendor/oggvorbis/ogg_vorbis_encoder.js'), 'utf8'));
    oggMod = await WebAssembly.compile(Buffer.from(globalThis.WasmMediaEncoderOggWasmB64, 'base64'));
  }
  const enc = await globalThis.WasmMediaEncoder.createEncoder('audio/ogg', oggMod);
  enc.configure({ channels: channels.length, sampleRate: sr, vbrQuality: quality });
  return Buffer.concat([Buffer.from(enc.encode(channels)), Buffer.from(enc.finalize())]);
}

module.exports = { suite, TOOLS, oggEncode, network: !!process.env.TEST_NETWORK };
