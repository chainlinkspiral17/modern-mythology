/* touch_controls.js — finger controls for the MM tools (the Steam Deck touchscreen).
 *
 *   Sliders: every <input type=range> on the page (including ones created later)
 *     press anywhere on it and slide — up or right raises, down or left lowers.
 *     Relative: the value never jumps to where the finger landed.
 *     A second finger down while sliding = fine control (1/5 speed).
 *     Double-tap = back to its starting value (data-default="…" overrides).
 *     The mouse keeps the browser's normal slider behaviour.
 *
 *   TouchControls.gesture(el, opts) — tap / double-tap / long-press / drag / pan on a
 *     canvas or any element, for touch and pen only (opts.mouse: true includes the mouse).
 *       opts.grab(ev)       → truthy if the press landed on something draggable (then move/end follow it)
 *       opts.move(ev)       while dragging a grabbed thing
 *       opts.end(ev)        drag finished
 *       opts.tap(ev)        quick press-release with no movement
 *       opts.doubleTap(ev)  second tap within 320 ms near the first
 *       opts.longPress(ev)  held still 550 ms (cancels the grab)
 *       opts.scroller       element to pan when the press grabbed nothing (default: el.parentElement)
 *     `ev` is the PointerEvent (clientX/clientY are what handlers use).
 *
 *   TouchControls.fine()   → true while two or more fingers are down (knobs use it for fine moves)
 *   TouchControls.dragAmount(dx, dy) → dx − dy: right and up both count positive (knob convention)
 */
(function (root) {
  "use strict";
  const SLIDE_PX = 220;          // finger travel for a slider's full range
  const TAP_MOVE = 8, LONG_MS = 550, DOUBLE_MS = 320;
  const touches = new Set();

  const TC = {
    fine: () => touches.size > 1,
    dragAmount: (dx, dy) => dx - dy,
  };

  // ── finger count (for fine mode) ──────────────────────────────────
  function trackTouches() {
    const on = e => { if (e.pointerType !== 'mouse') touches.add(e.pointerId); };
    const off = e => touches.delete(e.pointerId);
    document.addEventListener('pointerdown', on, true);
    document.addEventListener('pointerup', off, true);
    document.addEventListener('pointercancel', off, true);
  }

  // ── sliders ───────────────────────────────────────────────────────
  function rangeOf(el) {
    const min = el.min === '' ? 0 : +el.min, max = el.max === '' ? 100 : +el.max;
    const step = el.step === 'any' ? 0 : (el.step === '' ? 1 : +el.step);
    return { min, max, step };
  }
  function setRange(el, v) {
    const { min, max, step } = rangeOf(el);
    if (step) v = min + Math.round((v - min) / step) * step;
    v = Math.max(min, Math.min(max, v));
    const s = step ? String(+v.toFixed(6)) : String(v);
    if (s === el.value) return false;
    el.value = s;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    return true;
  }
  function sliders() {
    const css = document.createElement('style');
    css.textContent = `input[type=range] { touch-action: none; }
@media (any-pointer: coarse) { input[type=range] { min-height: 22px; cursor: grab; } }`;
    document.head.appendChild(css);
    // stop the browser's own touch handling (jump-to-finger) on sliders; pointer events still arrive
    document.addEventListener('touchstart', e => {
      if (e.target && e.target.matches && e.target.matches('input[type=range]')) e.preventDefault();
    }, { passive: false, capture: true });
    let drag = null, last = { el: null, t: 0 };
    document.addEventListener('pointerdown', e => {
      if (e.pointerType === 'mouse') return;
      const el = e.target && e.target.closest && e.target.closest('input[type=range]');
      if (!el || el.disabled) return;
      e.preventDefault();
      const now = performance.now();
      if (last.el === el && now - last.t < DOUBLE_MS) {
        last = { el: null, t: 0 };
        const def = el.dataset.default !== undefined ? +el.dataset.default : +el.defaultValue;
        if (setRange(el, def)) el.dispatchEvent(new Event('change', { bubbles: true }));
        drag = null; return;
      }
      last = { el, t: now };
      drag = { el, id: e.pointerId, x: e.clientX, y: e.clientY, v: +el.value, moved: false };
      try { el.setPointerCapture(e.pointerId); } catch (err) { /* ok */ }
    }, true);
    document.addEventListener('pointermove', e => {
      if (!drag || e.pointerId !== drag.id) return;
      e.preventDefault();
      const { min, max } = rangeOf(drag.el);
      const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
      // fine mode re-bases so switching speed doesn't jump
      const speed = TC.fine() ? 0.2 : 1;
      if (drag.speed !== speed) { drag.speed = speed; drag.x = e.clientX; drag.y = e.clientY; drag.v = +drag.el.value; return; }
      const v = drag.v + TC.dragAmount(dx, dy) / SLIDE_PX * (max - min) * speed;
      if (setRange(drag.el, v)) drag.moved = true;
    }, true);
    const end = e => {
      if (!drag || e.pointerId !== drag.id) return;
      if (drag.moved) { drag.el.dispatchEvent(new Event('change', { bubbles: true })); last = { el: null, t: 0 }; }
      drag = null;
    };
    document.addEventListener('pointerup', end, true);
    document.addEventListener('pointercancel', end, true);
  }

  // ── canvas gestures ───────────────────────────────────────────────
  TC.gesture = function (el, o) {
    el.style.touchAction = 'none';
    let g = null, lastTap = { t: 0, x: 0, y: 0 };
    const scroller = () => o.scroller || el.parentElement;
    el.addEventListener('pointerdown', e => {
      if (e.pointerType === 'mouse' && !o.mouse) return;
      if (g) return;                                    // one finger drives; others only mean "fine"
      e.preventDefault();
      try { el.setPointerCapture(e.pointerId); } catch (err) { /* ok */ }
      g = { id: e.pointerId, x0: e.clientX, y0: e.clientY, x: e.clientX, y: e.clientY, moved: false, long: false, grabbed: !!(o.grab && o.grab(e)) };
      g.timer = setTimeout(() => {
        if (!g || g.moved) return;
        g.long = true;
        if (o.longPress) { o.longPress(e); g.grabbed = false; }
      }, LONG_MS);
    });
    el.addEventListener('pointermove', e => {
      if (!g || e.pointerId !== g.id) return;
      e.preventDefault();
      if (!g.moved && Math.hypot(e.clientX - g.x0, e.clientY - g.y0) > TAP_MOVE) { g.moved = true; clearTimeout(g.timer); }
      if (g.grabbed) { if (g.moved && o.move) o.move(e); }
      else if (g.moved && !g.long) { const s = scroller(); if (s) { s.scrollLeft -= e.clientX - g.x; s.scrollTop -= e.clientY - g.y; } }
      g.x = e.clientX; g.y = e.clientY;
    });
    const up = e => {
      if (!g || e.pointerId !== g.id) return;
      clearTimeout(g.timer);
      const was = g; g = null;
      if (was.grabbed && o.end) o.end(e);
      if (e.type === 'pointercancel' || was.moved || was.long) return;
      const now = performance.now();
      if (o.doubleTap && now - lastTap.t < DOUBLE_MS && Math.hypot(e.clientX - lastTap.x, e.clientY - lastTap.y) < 24) { lastTap = { t: 0, x: 0, y: 0 }; o.doubleTap(e); return; }
      lastTap = { t: now, x: e.clientX, y: e.clientY };
      if (o.tap) o.tap(e);
    };
    el.addEventListener('pointerup', up);
    el.addEventListener('pointercancel', up);
    el.addEventListener('contextmenu', e => e.preventDefault());
  };

  if (typeof document !== 'undefined') {
    const go = () => { trackTouches(); sliders(); };
    if (document.head) go(); else document.addEventListener('DOMContentLoaded', go);
  }
  root.TouchControls = TC;
})(typeof window !== 'undefined' ? window : globalThis);
