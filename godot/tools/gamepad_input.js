/* gamepad_input.js
 *
 * Tiny gamepad helper for the HTML synth tools (tarot_synth,
 * ambient_synth). Polls navigator.getGamepads() on rAF and emits:
 *
 *   gamepadinput-connected     CustomEvent — first gamepad detected
 *   gamepadinput-disconnected  CustomEvent — last gamepad lost
 *   gamepadinput-button        CustomEvent {detail: {idx, pressed, value}}
 *   gamepadinput-axis          CustomEvent {detail: {idx, value, prev}}
 *
 * Built specifically with the PDP Riffmaster (PS5) in mind but
 * generic enough for any HID gamepad. The mapping below describes
 * Riffmaster's conventional layout — you can override on the
 * GamepadInput instance via .setMapping() if your driver reports
 * different indices.
 *
 * Usage:
 *   const gp = new GamepadInput();
 *   gp.start();
 *   window.addEventListener('gamepadinput-button', e => {
 *     // e.detail.idx, e.detail.pressed, e.detail.value
 *   });
 *
 * Also exposes gp.snapshot() for a live readout (used by the
 * connection-status panel each tool draws).
 */
"use strict";

const RIFFMASTER_DEFAULT_MAPPING = {
  // Button indices. The exact mapping varies by browser + driver but
  // this is the typical layout for the PS5 Riffmaster (HID).
  frets:        [0, 1, 2, 3, 4],   // green/red/yellow/blue/orange (low→high)
  soloFrets:    [5, 6, 7, 8, 9],   // upper-neck "solo" frets
  strumUp:      12,                // d-pad up
  strumDown:    13,                // d-pad down
  faceCross:    10,
  faceCircle:   11,
  // Axes
  whammy:       3,                 // analog 0..1 (rest = 0)
  tilt:         5,                 // tilt sensor (driver-dependent)
  strumAxis:    1,                 // alternate strum on some drivers (-1=up, +1=down)
};

class GamepadInput {
  constructor() {
    this.mapping = { ...RIFFMASTER_DEFAULT_MAPPING };
    this._padIdx = -1;
    this._prevButtons = [];
    this._prevAxes    = [];
    this._running = false;
    this._raf = null;
    this._connectionListener   = e => this._onConnect(e);
    this._disconnectionListener = e => this._onDisconnect(e);
  }

  setMapping(partial) {
    this.mapping = { ...this.mapping, ...partial };
  }

  start() {
    if (this._running) return;
    this._running = true;
    window.addEventListener('gamepadconnected',    this._connectionListener);
    window.addEventListener('gamepaddisconnected', this._disconnectionListener);
    // Probe for already-connected pads. Chrome doesn't fire
    // gamepadconnected for pads attached before the page loaded
    // until they're touched.
    const pads = navigator.getGamepads();
    for (let i = 0; i < pads.length; i++) {
      if (pads[i]) { this._padIdx = i; break; }
    }
    this._loop();
  }

  stop() {
    this._running = false;
    if (this._raf) cancelAnimationFrame(this._raf);
    window.removeEventListener('gamepadconnected',    this._connectionListener);
    window.removeEventListener('gamepaddisconnected', this._disconnectionListener);
  }

  snapshot() {
    const pad = this._padIdx >= 0 ? navigator.getGamepads()[this._padIdx] : null;
    if (!pad) return { connected: false };
    // Use hysteresis-resolved state from _prevButtons rather than
    // raw b.pressed so the held-set readout matches what's actually
    // emitted as events.
    const stableButtons = [];
    for (let i = 0; i < pad.buttons.length; i++) {
      stableButtons.push(this._prevButtons[i] === true);
    }
    return {
      connected: true,
      id: pad.id,
      buttons: stableButtons,
      axes: pad.axes.slice(),
    };
  }

  _onConnect(e) {
    if (this._padIdx === -1) {
      this._padIdx = e.gamepad.index;
      window.dispatchEvent(new CustomEvent('gamepadinput-connected', {
        detail: { id: e.gamepad.id, idx: e.gamepad.index }
      }));
    }
  }

  _onDisconnect(e) {
    if (e.gamepad.index === this._padIdx) {
      this._padIdx = -1;
      this._prevButtons = [];
      this._prevAxes = [];
      window.dispatchEvent(new CustomEvent('gamepadinput-disconnected', {}));
    }
  }

  _loop() {
    if (!this._running) return;
    if (this._padIdx >= 0) {
      const pad = navigator.getGamepads()[this._padIdx];
      if (pad) {
        // Buttons — use hysteresis on b.value rather than relying on
        // b.pressed. Touch-sensitive guitar frets (Riffmaster, Rock
        // Band Pro guitars) oscillate around the engine's threshold
        // while held, firing many press/release events per second.
        // We require the value to clearly cross PRESS_HI to flip on
        // and clearly fall under PRESS_LO to flip off — a stable
        // state changes only once per actual press.
        const PRESS_HI = 0.55;
        const PRESS_LO = 0.30;
        for (let i = 0; i < pad.buttons.length; i++) {
          const b = pad.buttons[i];
          const v = (b.value !== undefined) ? b.value : (b.pressed ? 1.0 : 0.0);
          const wasPressed = this._prevButtons[i] === true;
          let isPressed = wasPressed;
          if (!wasPressed && v > PRESS_HI) isPressed = true;
          if ( wasPressed && v < PRESS_LO) isPressed = false;
          if (wasPressed !== isPressed) {
            window.dispatchEvent(new CustomEvent('gamepadinput-button', {
              detail: { idx: i, pressed: isPressed, value: v }
            }));
            this._prevButtons[i] = isPressed;
          }
        }
        // Axes — emit when the value drifts more than the deadzone.
        const DEADZONE = 0.04;
        for (let i = 0; i < pad.axes.length; i++) {
          const v = pad.axes[i];
          const prev = this._prevAxes[i] ?? 0;
          if (Math.abs(v - prev) > DEADZONE) {
            window.dispatchEvent(new CustomEvent('gamepadinput-axis', {
              detail: { idx: i, value: v, prev }
            }));
            this._prevAxes[i] = v;
          }
        }
      }
    }
    this._raf = requestAnimationFrame(() => this._loop());
  }
}

// ── Strum-axis → synthetic button events ─────────────────────────
// Many guitar HID drivers report the strum bar as a momentary axis
// (e.g. axes[1] briefly swings to ±1 on each strum) instead of two
// d-pad buttons. This bridge listens for that axis and emits
// synthetic gamepadinput-button events with the strumUp / strumDown
// indices so chord-mode strum triggers fire regardless of whether
// the device reports strum-as-button or strum-as-axis.
function bindStrumAxis(gp, axisIdx, opts = {}) {
  const HI = opts.hi ?? 0.6;
  const LO = opts.lo ?? 0.3;
  let state = 0;   // -1 = strum-up armed, 0 = rest, +1 = strum-down armed
  window.addEventListener('gamepadinput-axis', e => {
    if (e.detail.idx !== axisIdx) return;
    const v = e.detail.value;
    if (Math.abs(v) < LO) { state = 0; return; }
    if (v >  HI && state !==  1) {
      state = 1;
      window.dispatchEvent(new CustomEvent('gamepadinput-button', {
        detail: { idx: gp.mapping.strumDown, pressed: true, value: 1, synthetic: true }
      }));
    } else if (v < -HI && state !== -1) {
      state = -1;
      window.dispatchEvent(new CustomEvent('gamepadinput-button', {
        detail: { idx: gp.mapping.strumUp, pressed: true, value: 1, synthetic: true }
      }));
    }
  });
}


// ── Connection status overlay ─────────────────────────────────────
// Small mounted bottom-right panel showing live gamepad activity so
// the user can identify which Riffmaster button maps to which index.
function mountGamepadOverlay(gp, opts = {}) {
  const panel = document.createElement('div');
  panel.style.cssText = `
    position: fixed; bottom: 10px; right: 10px;
    background: rgba(0,0,0,0.78);
    color: #d8a060;
    font-family: "Courier New", monospace;
    font-size: 11px;
    padding: 8px 12px;
    border: 1px solid #553318;
    max-width: 280px;
    z-index: 999;
    pointer-events: auto;
    cursor: default;
  `;
  panel.innerHTML = `
    <div style="color:#ffd896;letter-spacing:0.12em;font-weight:bold;margin-bottom:4px;">RIFFMASTER</div>
    <div id="gpio-status">not connected.</div>
    <div id="gpio-held" style="color:#d8a060;font-size:10px;margin-top:4px;">held: —</div>
    <div id="gpio-last" style="color:#7a5828;font-size:10px;margin-top:2px;font-style:italic;">last event: —</div>
    <div id="gpio-axes" style="color:#7a5828;font-size:10px;margin-top:2px;"></div>
    <div style="margin-top:6px;display:flex;gap:4px;flex-wrap:wrap;">
      <button id="gpio-detect" style="background:#3a2614;color:#ffd896;border:1px solid #d8a060;padding:2px 8px;font-family:inherit;font-size:10px;cursor:pointer;">DETECT STRUM</button>
      <button id="gpio-clear-binds" style="background:transparent;color:#7a5828;border:1px solid #553318;padding:2px 8px;font-family:inherit;font-size:10px;cursor:pointer;">RESET</button>
    </div>
    <label style="display:flex;align-items:center;gap:4px;color:#7a5828;font-size:10px;margin-top:6px;cursor:pointer;">
      <input type="checkbox" id="gpio-arrows-as-strum" style="margin:0;">
      arrows = strum (off → D-pad navigates)
    </label>
    <div id="gpio-bind-msg" style="color:#88b87a;font-size:10px;margin-top:4px;"></div>
  `;
  document.body.appendChild(panel);
  const status   = panel.querySelector('#gpio-status');
  const heldEl   = panel.querySelector('#gpio-held');
  const last     = panel.querySelector('#gpio-last');
  const axesEl   = panel.querySelector('#gpio-axes');
  const detectBtn = panel.querySelector('#gpio-detect');
  const clearBtn  = panel.querySelector('#gpio-clear-binds');
  const bindMsg   = panel.querySelector('#gpio-bind-msg');

  // ── Strum calibration ────────────────────────────────────────────
  // When the user clicks DETECT STRUM, watch for the next significant
  // input (button press OR axis swing past ±0.5) and bind THAT as the
  // strum source. Cancels itself if nothing happens within 6 seconds.
  let detecting = false;
  let detectTimer = null;
  let detectAxisSeen = {};   // axis idx → max abs value seen during detect
  let _strumAxisBinder = null;

  function _setBindMsg(text, color) {
    bindMsg.textContent = text;
    bindMsg.style.color = color || '#88b87a';
  }

  function _bindStrumToButton(btnIdx) {
    gp.setMapping({ strumUp: btnIdx, strumDown: btnIdx });
    _setBindMsg('strum bound → button ' + btnIdx, '#ffd896');
  }
  function _bindStrumToAxis(axIdx) {
    gp.setMapping({ strumAxis: axIdx });
    if (_strumAxisBinder) {
      // Already bound to some axis; we can't easily unbind a previous
      // bindStrumAxis listener, but the new mapping makes the old
      // axis emit nothing (it checks e.detail.idx === mapping.strumAxis
      // at the time of event), so functionally we're fine.
    }
    if (typeof bindStrumAxis === 'function') {
      bindStrumAxis(gp, axIdx);
      _strumAxisBinder = axIdx;
    }
    _setBindMsg('strum bound → axis ' + axIdx, '#ffd896');
  }

  detectBtn.addEventListener('click', () => {
    if (detecting) return;
    detecting = true;
    detectAxisSeen = {};
    _setBindMsg('strum the bar now…', '#ffd896');
    detectBtn.textContent = 'WAITING…';
    detectTimer = setTimeout(() => {
      detecting = false;
      detectBtn.textContent = 'DETECT STRUM';
      // If we saw any axis swing > 0.5 during the window, bind the
      // one with the largest absolute swing.
      let bestAx = -1, bestVal = 0;
      for (const k in detectAxisSeen) {
        if (detectAxisSeen[k] > bestVal) { bestVal = detectAxisSeen[k]; bestAx = parseInt(k); }
      }
      if (bestAx >= 0 && bestVal > 0.5) {
        _bindStrumToAxis(bestAx);
      } else {
        _setBindMsg('nothing detected (timed out).', '#7a5828');
      }
    }, 6000);
  });

  clearBtn.addEventListener('click', () => {
    gp.mapping = { ...RIFFMASTER_DEFAULT_MAPPING };
    _setBindMsg('mapping reset to default.', '#7a5828');
  });

  // While detecting, intercept button presses + axis swings.
  window.addEventListener('gamepadinput-button', e => {
    if (!detecting || !e.detail.pressed || e.detail.synthetic) return;
    detecting = false;
    if (detectTimer) clearTimeout(detectTimer);
    detectBtn.textContent = 'DETECT STRUM';
    _bindStrumToButton(e.detail.idx);
  });
  window.addEventListener('gamepadinput-axis', e => {
    if (!detecting) return;
    const v = Math.abs(e.detail.value);
    if (v > (detectAxisSeen[e.detail.idx] || 0)) {
      detectAxisSeen[e.detail.idx] = v;
    }
    // If a swing is sharp enough, bind immediately and stop.
    if (v > 0.7) {
      detecting = false;
      if (detectTimer) clearTimeout(detectTimer);
      detectBtn.textContent = 'DETECT STRUM';
      _bindStrumToAxis(e.detail.idx);
    }
  });

  // ── Optional: arrow-key strum fallback ───────────────────────────
  // Some setups (Steam Input, vendor remap tools) translate the strum
  // bar into ArrowUp / ArrowDown keyboard events at the OS level —
  // the page treats those as focus-navigation and the strum "moves
  // the menu" instead of triggering chord mode. Toggle this on if
  // strumming moves the focus ring around. Off by default so the
  // Riffmaster's D-pad can navigate normally.
  const arrowsBox = panel.querySelector('#gpio-arrows-as-strum');
  let arrowsAsStrum = false;
  arrowsBox.addEventListener('change', () => {
    arrowsAsStrum = arrowsBox.checked;
    _setBindMsg(arrowsAsStrum
      ? 'arrows now treated as strum.'
      : 'arrows pass through (D-pad navigates).', '#7a5828');
  });
  window.addEventListener('keydown', e => {
    if (!arrowsAsStrum) return;
    if (gp._padIdx < 0) return;
    const tag = e.target.tagName;
    if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') return;
    let strumDir = null;
    if (e.key === 'ArrowUp'   || e.key === 'ArrowLeft')  strumDir = 'up';
    if (e.key === 'ArrowDown' || e.key === 'ArrowRight') strumDir = 'down';
    if (strumDir !== null) {
      e.preventDefault();
      const btn = strumDir === 'down' ? gp.mapping.strumDown : gp.mapping.strumUp;
      window.dispatchEvent(new CustomEvent('gamepadinput-button', {
        detail: { idx: btn, pressed: true, value: 1, synthetic: true, fromKeyboard: true }
      }));
      if (document.activeElement && document.activeElement !== document.body) {
        document.activeElement.blur();
      }
    }
  }, true);
  window.addEventListener('gamepadinput-connected', e => {
    status.textContent = 'connected: ' + (e.detail.id || '(unknown)').slice(0, 38);
  });
  window.addEventListener('gamepadinput-disconnected', () => {
    status.textContent = 'disconnected.';
  });
  window.addEventListener('gamepadinput-button', e => {
    if (e.detail.pressed) {
      last.textContent = 'button ' + e.detail.idx + ' pressed' + (e.detail.value && e.detail.value !== 1 ? ' (' + e.detail.value.toFixed(2) + ')' : '');
    }
  });
  // Sample axes 4x/sec for display so we don't spam the DOM.
  setInterval(() => {
    const snap = gp.snapshot();
    if (snap.connected) {
      const heldList = [];
      snap.buttons.forEach((p, i) => { if (p) heldList.push(i); });
      heldEl.textContent = heldList.length
        ? 'held: btn ' + heldList.join(', ')
        : 'held: —';
      const lines = [];
      snap.axes.forEach((v, i) => {
        if (Math.abs(v) > 0.04) lines.push('ax' + i + ' ' + v.toFixed(2));
      });
      axesEl.textContent = lines.join('  ') || ' ';
    } else {
      heldEl.textContent = 'held: —';
      axesEl.textContent = '';
    }
  }, 100);
  return panel;
}
