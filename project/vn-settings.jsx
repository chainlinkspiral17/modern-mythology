// vn-settings.jsx — Persistent settings store + Settings panel UI
// Exports to window: SettingsStore, useSettings, SettingsPanel,
//                    TEXT_SIZE_PX, TEXT_SPEED_MS, MM_SETTINGS_DEFAULTS

// ── Constants ──────────────────────────────────────────────────────────────
const MM_SETTINGS_KEY = 'mm_settings_v1';
const MM_SETTINGS_DEFAULTS = {
  textSize:  'normal',  // 'small' | 'normal' | 'large'
  textSpeed: 'normal',  // 'slow'  | 'normal' | 'fast'
  bgmVol:    0.65,
  sfxVol:    0.80,
  voiceVol:  0.80,
};

// Preset → numeric values
const TEXT_SIZE_PX  = { small: 14, normal: 18, large: 23 };
const TEXT_SPEED_MS = { slow: 60,  normal: 28, fast: 10 };
// Relative scale applied on top of each skin's base text size, so per-skin
// design intent (terminal/zine want tighter type) is preserved.
const TEXT_SIZE_SCALE = { small: 0.82, normal: 1.0, large: 1.30 };

// ── Persistence ────────────────────────────────────────────────────────────
function _loadMM() {
  try {
    const raw = localStorage.getItem(MM_SETTINGS_KEY);
    if (!raw) return { ...MM_SETTINGS_DEFAULTS };
    return { ...MM_SETTINGS_DEFAULTS, ...JSON.parse(raw) };
  } catch { return { ...MM_SETTINGS_DEFAULTS }; }
}
function _saveMM(s) {
  try { localStorage.setItem(MM_SETTINGS_KEY, JSON.stringify(s)); } catch {}
}

// ── Store (singleton) ──────────────────────────────────────────────────────
const SettingsStore = (() => {
  let state = _loadMM();
  const subs = new Set();
  const emit = () => {
    subs.forEach(fn => { try { fn(state); } catch {} });
    try { window.dispatchEvent(new CustomEvent('mm-settings-change', { detail: state })); } catch {}
  };
  return {
    get: () => state,
    set: (patch) => {
      state = { ...state, ...patch };
      _saveMM(state);
      emit();
    },
    reset: () => {
      state = { ...MM_SETTINGS_DEFAULTS };
      _saveMM(state);
      emit();
    },
    subscribe: (fn) => { subs.add(fn); return () => subs.delete(fn); },
    derived: () => ({
      textSizePx:    TEXT_SIZE_PX[state.textSize]    ?? 18,
      textSizeScale: TEXT_SIZE_SCALE[state.textSize] ?? 1.0,
      textSpeedMs:   TEXT_SPEED_MS[state.textSpeed]  ?? 28,
      bgmVol: state.bgmVol, sfxVol: state.sfxVol, voiceVol: state.voiceVol,
    }),
  };
})();

function useSettings() {
  const [s, setS] = React.useState(SettingsStore.get());
  React.useEffect(() => SettingsStore.subscribe(setS), []);
  return [s, SettingsStore.set];
}

// ── Visual constants (literary skin — settings panel is game chrome) ───────
const SP = {
  bg:        'rgba(8,6,4,0.985)',
  panelBg:   'linear-gradient(180deg,rgba(20,16,10,0.65) 0%,rgba(10,7,4,0.85) 100%)',
  border:    'rgba(180,140,60,0.28)',
  borderDim: 'rgba(180,140,60,0.10)',
  hairline:  'rgba(180,140,60,0.18)',
  txt:       '#d4c9b0',
  txtDim:    '#8a7e66',
  accent:    '#c8a84a',
  accentDim: 'rgba(200,168,74,0.55)',
  faint:     'rgba(180,140,60,0.35)',
  hudFont:   "'Cinzel', serif",
  bodyFont:  "'IM Fell English', serif",
};

// ── Mini Typewriter (for the preview line) ─────────────────────────────────
function MiniTyper({ text, speed, fontSize }) {
  const [shown, setShown] = React.useState('');
  React.useEffect(() => {
    let i = 0; let cancelled = false; let raf, last;
    const tick = (ts) => {
      if (cancelled) return;
      if (!last) last = ts;
      const steps = Math.floor((ts - last) / speed);
      if (steps > 0) { last = ts; i = Math.min(i + steps, text.length); setShown(text.slice(0, i)); }
      if (i < text.length) raf = requestAnimationFrame(tick);
    };
    setShown('');
    raf = requestAnimationFrame(tick);
    return () => { cancelled = true; cancelAnimationFrame(raf); };
  }, [text, speed]);
  return (
    <span style={{
      fontFamily: SP.bodyFont, fontStyle: 'italic',
      fontSize, lineHeight: 1.55, color: SP.txt,
    }}>
      {shown}
      <span style={{
        display:'inline-block',
        width: shown.length < text.length ? Math.max(6, fontSize * 0.45) : 0,
        height: fontSize * 0.85,
        background: SP.accent, marginLeft: 3, verticalAlign: '-3px',
        animation: shown.length < text.length ? 'vn-blink 0.9s steps(1) infinite' : 'none',
        opacity: shown.length < text.length ? 1 : 0,
      }}></span>
    </span>
  );
}

// ── Reusable sub-components ────────────────────────────────────────────────
function SectionHeader({ children, count }) {
  return (
    <div style={{
      display:'flex', alignItems:'center', gap:14, marginBottom: 14,
    }}>
      <span style={{
        fontFamily: SP.hudFont, fontSize: 9, letterSpacing: '0.42em',
        color: SP.accent, textTransform: 'uppercase',
      }}>{children}</span>
      <span style={{ flex: 1, height: 1, background:
        `linear-gradient(90deg, ${SP.hairline} 0%, transparent 100%)` }}></span>
      {count != null && (
        <span style={{
          fontFamily: SP.hudFont, fontSize: 8, letterSpacing: '0.2em',
          color: SP.faint, textTransform: 'uppercase',
        }}>{count}</span>
      )}
    </div>
  );
}

function FieldLabel({ children, hint }) {
  return (
    <div style={{ display:'flex', alignItems:'baseline', justifyContent:'space-between', marginBottom: 8 }}>
      <span style={{
        fontFamily: SP.hudFont, fontSize: 9, letterSpacing: '0.3em',
        color: SP.txtDim, textTransform: 'uppercase',
      }}>{children}</span>
      {hint != null && (
        <span style={{
          fontFamily: SP.bodyFont, fontStyle:'italic', fontSize: 11, color: SP.accentDim,
        }}>{hint}</span>
      )}
    </div>
  );
}

function SegBtns({ value, onChange, options }) {
  return (
    <div style={{
      display:'grid',
      gridTemplateColumns: `repeat(${options.length}, 1fr)`,
      gap: 0,
      border: `1px solid ${SP.borderDim}`,
    }}>
      {options.map((o, i) => {
        const active = value === o.value;
        return (
          <div key={o.value}
            onClick={() => onChange(o.value)}
            onMouseEnter={e => { if (!active) e.currentTarget.style.background = 'rgba(200,168,74,0.05)'; }}
            onMouseLeave={e => { if (!active) e.currentTarget.style.background = 'transparent'; }}
            style={{
              padding: '12px 10px',
              borderLeft: i === 0 ? 'none' : `1px solid ${SP.borderDim}`,
              background: active ? 'rgba(200,168,74,0.10)' : 'transparent',
              cursor: 'pointer',
              transition: 'background 0.15s',
              textAlign:'center', position:'relative',
            }}
          >
            {/* Active top tick mark */}
            {active && (
              <div style={{
                position:'absolute', top: -1, left: '50%', transform:'translateX(-50%)',
                width: 22, height: 1, background: SP.accent,
              }}></div>
            )}
            <div style={{
              fontFamily: SP.bodyFont, fontStyle:'italic',
              fontSize: o.fontSize || 16,
              color: active ? SP.txt : SP.txtDim,
              lineHeight: 1, marginBottom: 4,
              transition: 'color 0.15s',
            }}>{o.preview || o.label}</div>
            <div style={{
              fontFamily: SP.hudFont, fontSize: 7.5, letterSpacing: '0.28em',
              color: active ? SP.accent : SP.faint, textTransform: 'uppercase',
              transition: 'color 0.15s',
            }}>{o.label}</div>
          </div>
        );
      })}
    </div>
  );
}

// Custom slider with gold track and ruler ticks
function VolSlider({ label, value, onChange }) {
  const [drag, setDrag] = React.useState(false);
  const trackRef = React.useRef(null);

  const setFromEvent = (e) => {
    const r = trackRef.current.getBoundingClientRect();
    const cx = e.touches ? e.touches[0].clientX : e.clientX;
    const v = Math.max(0, Math.min(1, (cx - r.left) / r.width));
    onChange(Math.round(v * 100) / 100);
  };

  React.useEffect(() => {
    if (!drag) return;
    const move = (e) => setFromEvent(e);
    const up = () => setDrag(false);
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', up);
    window.addEventListener('touchmove', move);
    window.addEventListener('touchend', up);
    return () => {
      window.removeEventListener('mousemove', move);
      window.removeEventListener('mouseup', up);
      window.removeEventListener('touchmove', move);
      window.removeEventListener('touchend', up);
    };
  }, [drag]);

  const pct = Math.round(value * 100);
  const ticks = Array.from({ length: 21 }, (_, i) => i); // 0..20 (5% steps)

  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ display:'flex', alignItems:'baseline', justifyContent:'space-between', marginBottom: 8 }}>
        <span style={{
          fontFamily: SP.hudFont, fontSize: 9, letterSpacing: '0.3em',
          color: SP.txtDim, textTransform: 'uppercase',
        }}>{label}</span>
        <span style={{
          fontFamily: SP.hudFont, fontSize: 9, letterSpacing: '0.18em',
          color: SP.accent, minWidth: 36, textAlign:'right',
        }}>{pct.toString().padStart(2,'0')}%</span>
      </div>

      <div
        ref={trackRef}
        onMouseDown={(e) => { setDrag(true); setFromEvent(e); }}
        onTouchStart={(e) => { setDrag(true); setFromEvent(e); }}
        style={{
          position: 'relative',
          height: 26, cursor: 'pointer',
          display:'flex', alignItems:'center',
        }}
      >
        {/* Tick ruler */}
        <div style={{
          position:'absolute', left:0, right:0, top: '50%',
          height: 10, transform:'translateY(-50%)',
          display:'flex', justifyContent:'space-between', alignItems:'center',
          pointerEvents:'none',
        }}>
          {ticks.map(i => {
            const isMajor = i % 5 === 0;
            const filled = (i / 20) <= value + 0.001;
            return (
              <div key={i} style={{
                width: 1,
                height: isMajor ? 10 : 5,
                background: filled
                  ? (isMajor ? SP.accent : 'rgba(200,168,74,0.55)')
                  : (isMajor ? 'rgba(180,140,60,0.30)' : 'rgba(180,140,60,0.12)'),
              }}></div>
            );
          })}
        </div>
        {/* Center hairline track */}
        <div style={{
          position:'absolute', left:0, right:0, top:'50%', height:1,
          transform:'translateY(-0.5px)',
          background: `linear-gradient(90deg,
            ${SP.accent} 0%, ${SP.accent} ${pct}%,
            rgba(180,140,60,0.15) ${pct}%, rgba(180,140,60,0.15) 100%)`,
          pointerEvents:'none',
        }}></div>
        {/* Handle — diamond */}
        <div style={{
          position:'absolute', top:'50%', left:`${pct}%`,
          transform:'translate(-50%,-50%) rotate(45deg)',
          width: 10, height: 10,
          background: '#0a0805',
          border: `1.5px solid ${SP.accent}`,
          boxShadow: `0 0 8px rgba(200,168,74,${drag ? 0.7 : 0.35})`,
          transition: drag ? 'none' : 'box-shadow 0.15s',
          pointerEvents:'none',
        }}></div>
      </div>
    </div>
  );
}

// ── Settings Panel ─────────────────────────────────────────────────────────
const PREVIEW_LINES = [
  "The crows were halfway through their evening rosary when the train came in slow.",
  "He had not slept in three nights, and the cabin began to hum with intent.",
  "She set the bowl down. The cat watched her, the way cats watch a god they barely tolerate.",
  "Somewhere, a screen door slammed. Somewhere else, a long bell.",
];

function SettingsPanel({ onClose }) {
  const [s, setS] = useSettings();
  const sizePx  = TEXT_SIZE_PX[s.textSize]   ?? 18;
  const speedMs = TEXT_SPEED_MS[s.textSpeed] ?? 28;

  // Preview line cycles when settings change so user can re-watch the type-on
  const [previewIdx, setPreviewIdx] = React.useState(0);
  const previewKey = `${s.textSize}-${s.textSpeed}-${previewIdx}`;
  const previewText = PREVIEW_LINES[previewIdx % PREVIEW_LINES.length];

  // ESC to close
  React.useEffect(() => {
    const fn = (e) => { if (e.key === 'Escape') onClose && onClose(); };
    window.addEventListener('keydown', fn);
    return () => window.removeEventListener('keydown', fn);
  }, [onClose]);

  return (
    <div
      onClick={e => e.stopPropagation()}
      data-no-advance
      style={{
        position:'absolute', inset:0, zIndex: 60,
        background: SP.bg,
        display:'flex', alignItems:'center', justifyContent:'center',
        fontFamily: SP.bodyFont,
        animation: 'vn-fadein 0.18s ease-out',
      }}
    >
      {/* Grain */}
      <div style={{
        position:'absolute', inset:0, pointerEvents:'none',
        backgroundImage:"url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E\")",
        mixBlendMode:'overlay',
      }}></div>

      <div style={{
        position:'relative',
        width: 640, maxHeight: '94%',
        padding: '24px 40px 20px',
        background: SP.panelBg,
        border: `1px solid ${SP.border}`,
        boxShadow: '0 30px 90px rgba(0,0,0,0.8), inset 0 0 0 1px rgba(0,0,0,0.4)',
        overflowY:'auto',
      }}>

        {/* Corner ornaments */}
        {[['top:8px;left:8px','top:1;left:1'],
          ['top:8px;right:8px','top:1;right:1'],
          ['bottom:8px;left:8px','bottom:1;left:1'],
          ['bottom:8px;right:8px','bottom:1;right:1']].map(([pos], i) => {
          const style = {};
          pos.split(';').forEach(p => { const [k,v] = p.split(':'); style[k.trim()] = v.trim(); });
          return (
            <div key={i} style={{
              position:'absolute', ...style, width: 14, height: 14,
              borderTop: style.top ? `1px solid ${SP.accentDim}` : 'none',
              borderBottom: style.bottom ? `1px solid ${SP.accentDim}` : 'none',
              borderLeft: style.left ? `1px solid ${SP.accentDim}` : 'none',
              borderRight: style.right ? `1px solid ${SP.accentDim}` : 'none',
              pointerEvents:'none',
            }}></div>
          );
        })}

        {/* Header */}
        <div style={{
          display:'flex', alignItems:'flex-end', justifyContent:'space-between',
          marginBottom: 20, paddingBottom: 14,
          borderBottom: `1px solid ${SP.hairline}`,
        }}>
          <div>
            <div style={{
              fontFamily: SP.hudFont, fontSize: 8, letterSpacing: '0.4em',
              color: SP.faint, textTransform: 'uppercase', marginBottom: 6,
            }}>✦ &nbsp; Modern Mythology</div>
            <div style={{
              fontFamily: SP.bodyFont, fontStyle:'italic',
              fontSize: 28, color: SP.txt, lineHeight: 1,
            }}>Settings</div>
          </div>
          <div
            onClick={onClose}
            onMouseEnter={e=>{ e.currentTarget.style.color = SP.txt; e.currentTarget.style.borderColor = SP.border; }}
            onMouseLeave={e=>{ e.currentTarget.style.color = SP.txtDim; e.currentTarget.style.borderColor = SP.borderDim; }}
            style={{
              cursor:'pointer',
              fontFamily: SP.hudFont, fontSize: 8, letterSpacing: '0.3em',
              color: SP.txtDim, textTransform:'uppercase',
              border: `1px solid ${SP.borderDim}`, padding: '7px 14px',
              transition: 'all 0.15s', userSelect:'none',
            }}
          >Close  &nbsp;×</div>
        </div>

        {/* DISPLAY */}
        <div style={{ marginBottom: 18 }}>
          <SectionHeader>Display</SectionHeader>

          <div style={{ marginBottom: 14 }}>
            <FieldLabel hint={`${sizePx}px`}>Text Size</FieldLabel>
            <SegBtns
              value={s.textSize}
              onChange={v => setS({ textSize: v })}
              options={[
                { value:'small',  label:'Small',  preview:'Aa', fontSize: 14 },
                { value:'normal', label:'Normal', preview:'Aa', fontSize: 19 },
                { value:'large',  label:'Large',  preview:'Aa', fontSize: 25 },
              ]}
            />
          </div>

          <div style={{ marginBottom: 14 }}>
            <FieldLabel hint={`${speedMs}ms / char`}>Text Speed</FieldLabel>
            <SegBtns
              value={s.textSpeed}
              onChange={v => setS({ textSpeed: v })}
              options={[
                { value:'slow',   label:'Slow' },
                { value:'normal', label:'Normal' },
                { value:'fast',   label:'Fast' },
              ]}
            />
          </div>

          {/* Live preview */}
          <div
            onClick={() => setPreviewIdx(i => i + 1)}
            style={{
              position:'relative',
              padding: '11px 16px 13px',
              border: `1px dashed ${SP.borderDim}`,
              background: 'rgba(0,0,0,0.25)',
              cursor:'pointer',
              minHeight: 60,
            }}
            title="Click to replay preview"
          >
            <div style={{
              position:'absolute', top: -7, left: 14,
              padding: '0 8px', background: '#100c08',
              fontFamily: SP.hudFont, fontSize: 7, letterSpacing: '0.3em',
              color: SP.faint, textTransform:'uppercase',
            }}>Preview</div>
            <MiniTyper key={previewKey} text={previewText} speed={speedMs} fontSize={sizePx} />
          </div>
        </div>

        {/* AUDIO */}
        <div style={{ marginBottom: 14 }}>
          <SectionHeader>Audio</SectionHeader>
          <VolSlider label="Music & Video" value={s.bgmVol}   onChange={v => setS({ bgmVol: v })} />
          <VolSlider label="Sound Effects" value={s.sfxVol}   onChange={v => setS({ sfxVol: v })} />
          <VolSlider label="Voices"        value={s.voiceVol} onChange={v => setS({ voiceVol: v })} />
        </div>

        {/* Footer */}
        <div style={{
          display:'flex', alignItems:'center', justifyContent:'space-between',
          paddingTop: 12, borderTop: `1px solid ${SP.hairline}`,
        }}>
          <span style={{
            fontFamily: SP.hudFont, fontSize: 7, letterSpacing: '0.28em',
            color: SP.faint, textTransform:'uppercase',
          }}>Saved automatically · Esc to close</span>
          <div
            onClick={() => SettingsStore.reset()}
            onMouseEnter={e=>{ e.currentTarget.style.color = SP.accent; e.currentTarget.style.borderColor = SP.border; }}
            onMouseLeave={e=>{ e.currentTarget.style.color = SP.txtDim; e.currentTarget.style.borderColor = SP.borderDim; }}
            style={{
              cursor:'pointer',
              fontFamily: SP.hudFont, fontSize: 8, letterSpacing: '0.28em',
              color: SP.txtDim, textTransform: 'uppercase',
              border: `1px solid ${SP.borderDim}`, padding: '7px 16px',
              transition: 'all 0.15s', userSelect:'none',
            }}
          >Restore Defaults</div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, {
  SettingsStore, useSettings, SettingsPanel,
  TEXT_SIZE_PX, TEXT_SPEED_MS, TEXT_SIZE_SCALE, MM_SETTINGS_DEFAULTS,
});
