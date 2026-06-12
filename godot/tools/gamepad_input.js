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
    return {
      connected: true,
      id: pad.id,
      buttons: pad.buttons.map(b => b.pressed),
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
        // Buttons — emit on edge changes (press / release).
        for (let i = 0; i < pad.buttons.length; i++) {
          const b = pad.buttons[i];
          const wasPressed = this._prevButtons[i] === true;
          const isPressed  = b.pressed;
          if (wasPressed !== isPressed) {
            window.dispatchEvent(new CustomEvent('gamepadinput-button', {
              detail: { idx: i, pressed: isPressed, value: b.value }
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
    <div id="gpio-last" style="color:#7a5828;font-size:10px;margin-top:4px;font-style:italic;">last event: —</div>
    <div id="gpio-axes" style="color:#7a5828;font-size:10px;margin-top:2px;"></div>
  `;
  document.body.appendChild(panel);
  const status = panel.querySelector('#gpio-status');
  const last   = panel.querySelector('#gpio-last');
  const axesEl = panel.querySelector('#gpio-axes');
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
      const lines = [];
      snap.axes.forEach((v, i) => {
        if (Math.abs(v) > 0.04) lines.push('ax' + i + ' ' + v.toFixed(2));
      });
      axesEl.textContent = lines.join('  ') || ' ';
    } else {
      axesEl.textContent = '';
    }
  }, 250);
  return panel;
}
