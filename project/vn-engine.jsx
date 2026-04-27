// vn-engine.jsx — Core Visual Novel Engine for Modern Mythology
// Exports: GameScreen → window.GameScreen

// ── Audio Manager ─────────────────────────────────────────────────────────
class AudioMgr {
  constructor() { this.bgm = null; this.sfx = []; this.bgmVol = 0.7; this.masterVol = 0.8; }
  playBgm(src) {
    if (!src) return;
    if (this.bgm && !this.bgm.paused) {
      if (this.bgm._src === src) return;
      this.fadeBgm(() => this._startBgm(src));
    } else { this._startBgm(src); }
  }
  _startBgm(src) {
    const a = new Audio(src); a._src = src;
    a.loop = true; a.volume = 0;
    a.play().catch(() => {});
    this.bgm = a;
    this._fadeIn(a, this.bgmVol * this.masterVol);
  }
  fadeBgm(cb) {
    if (!this.bgm) { cb && cb(); return; }
    this._fadeOut(this.bgm, cb);
  }
  stopBgm() { this.fadeBgm(); this.bgm = null; }
  playSfx(src) {
    if (!src) return;
    const a = new Audio(src); a.volume = this.masterVol; a.play().catch(() => {});
  }
  setVolumes(master, bgm) {
    this.masterVol = master; this.bgmVol = bgm;
    if (this.bgm) this.bgm.volume = bgm * master;
  }
  _fadeIn(a, target, ms = 600) {
    const step = target / (ms / 40);
    const t = setInterval(() => {
      a.volume = Math.min(a.volume + step, target);
      if (a.volume >= target) clearInterval(t);
    }, 40);
  }
  _fadeOut(a, cb, ms = 600) {
    const start = a.volume; const step = start / (ms / 40);
    const t = setInterval(() => {
      a.volume = Math.max(0, a.volume - step);
      if (a.volume <= 0) { clearInterval(t); a.pause(); cb && cb(); }
    }, 40);
  }
}
const audioMgr = new AudioMgr();

// ── Save System ───────────────────────────────────────────────────────────
const SAVE_KEY = 'mm_saves';
function loadSaves() {
  try { return JSON.parse(localStorage.getItem(SAVE_KEY) || '[]'); } catch { return []; }
}
function writeSave(slots) {
  try { localStorage.setItem(SAVE_KEY, JSON.stringify(slots)); } catch {}
}

// ── Reducer ───────────────────────────────────────────────────────────────
const initState = (vol) => ({
  vol, nodeIndex: 0, sceneId: null,
  displayText: '', fullText: '', isTyping: false,
  speaker: null, speakerRole: null, textType: 'narration',
  choices: null, waitingForInput: false,
  characters: { left: null, center: null, right: null },
  background: null, bgm: null,
  skills: { empathy: 3, logic: 3, composure: 2, rhetoric: 2, signal: 55 },
  relationships: {}, flags: {}, inventory: [],
  log: [], overlay: null,
  textSpeed: 28, masterVol: 0.8, bgmVol: 0.7, fontSize: 18,
  stats: { heat: 7, rep: 3, cash: 43 },
  gameOver: false, endScene: false,
  currentScene: null,
  videoScene: null, // active interactive video node
});

function reducer(state, action) {
  switch (action.type) {
    case 'SET_TEXT': return { ...state, displayText: action.text, fullText: action.text, isTyping: true, waitingForInput: false };
    case 'FINISH_TYPING': return { ...state, isTyping: false, waitingForInput: true };
    case 'SKIP_TYPING': return { ...state, displayText: state.fullText, isTyping: false, waitingForInput: true };
    case 'SET_SPEAKER': return { ...state, speaker: action.speaker, speakerRole: action.role || null, textType: action.textType || 'dialogue' };
    case 'SET_CHOICES': return { ...state, choices: action.choices, waitingForInput: false, isTyping: false };
    case 'CLEAR_CHOICES': return { ...state, choices: null };
    case 'SHOW_CHAR': return { ...state, characters: { ...state.characters, [action.pos]: { name: action.name, expr: action.expr } } };
    case 'HIDE_CHAR': return { ...state, characters: { ...state.characters, [action.pos]: null } };
    case 'HIDE_ALL': return { ...state, characters: { left: null, center: null, right: null } };
    case 'SET_BG': return { ...state, background: action.src };
    case 'SET_BGM': return { ...state, bgm: action.src };
    case 'SET_FLAG': return { ...state, flags: { ...state.flags, [action.key]: action.val } };
    case 'ADD_LOG': return { ...state, log: [...state.log, action.entry].slice(-80) };
    case 'SET_OVERLAY': return { ...state, overlay: action.overlay };
    case 'SET_NODE': return { ...state, nodeIndex: action.idx, sceneId: action.sceneId || state.sceneId };
    case 'SET_SCENE': return { ...state, currentScene: action.scene, nodeIndex: 0, sceneId: action.scene?.id };
    case 'UPDATE_SPEED': return { ...state, textSpeed: action.val };
    case 'UPDATE_FONTSIZE': return { ...state, fontSize: action.val };
    case 'UPDATE_VOL': {
      const s = { ...state, masterVol: action.master ?? state.masterVol, bgmVol: action.bgm ?? state.bgmVol };
      audioMgr.setVolumes(s.masterVol, s.bgmVol);
      return s;
    }
    case 'LOAD_SAVE': return { ...action.save, overlay: null };
    case 'END_SCENE': return { ...state, endScene: true, choices: null, isTyping: false, waitingForInput: false };
    case 'SET_VIDEO_SCENE': return { ...state, videoScene: action.node, choices: null, isTyping: false, waitingForInput: false };
    case 'CLEAR_VIDEO_SCENE': return { ...state, videoScene: null };
    default: return state;
  }
}

// ── Typewriter Component ───────────────────────────────────────────────────
function Typewriter({ text, speed, skin, onDone, skip }) {
  const [displayed, setDisplayed] = React.useState('');
  const [done, setDone] = React.useState(false);
  const ref = React.useRef({ idx: 0, text: '', raf: null, last: 0 });

  React.useEffect(() => {
    if (skip) {
      cancelAnimationFrame(ref.current.raf);
      setDisplayed(text);
      setDone(true);
      return;
    }
    setDisplayed(''); setDone(false);
    ref.current = { idx: 0, text, last: 0 };
    const tick = (ts) => {
      const r = ref.current;
      if (!r.last) r.last = ts;
      const elapsed = ts - r.last;
      const steps = Math.floor(elapsed / speed);
      if (steps > 0) {
        r.last = ts;
        r.idx = Math.min(r.idx + steps, r.text.length);
        setDisplayed(r.text.slice(0, r.idx));
        if (r.idx >= r.text.length) { setDone(true); onDone && onDone(); return; }
      }
      r.raf = requestAnimationFrame(tick);
    };
    ref.current.raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(ref.current.raf);
  }, [text, speed, skip]);

  const cursorStyle = {
    display: 'inline-block', width: done ? 0 : 9, height: 15,
    background: 'var(--cursor)', marginLeft: 2, verticalAlign: 'middle',
    animation: done ? 'none' : 'vn-blink 1s steps(1) infinite', opacity: done ? 0 : 1,
  };

  return (
    <span>
      {displayed}
      <span style={cursorStyle}></span>
    </span>
  );
}

// ── Character Sprite ───────────────────────────────────────────────────────
function CharSprite({ name, expr, pos, skin }) {
  const [imgFailed, setImgFailed] = React.useState(false);
  const src = name ? `assets/characters/${name.toLowerCase()}/${name.toLowerCase()}_${expr || 'neutral'}.png` : null;

  const posStyle = {
    left: { left: '8%' }, center: { left: '50%', transform: 'translateX(-50%)' }, right: { right: '8%' }
  }[pos] || { left: '50%', transform: 'translateX(-50%)' };

  const silhouetteStyle = {
    position: 'absolute', bottom: 0,
    width: 220, height: 440,
    background: skin.charGradient,
    clipPath: 'polygon(37% 0%,63% 0%,68% 8%,74% 18%,76% 32%,72% 45%,64% 52%,88% 56%,96% 100%,4% 100%,12% 56%,36% 52%,28% 45%,24% 32%,26% 18%,32% 8%)',
    filter: `drop-shadow(0 0 40px ${skin.glowColor})`,
    ...posStyle,
  };

  const imgStyle = {
    position: 'absolute', bottom: 0, height: 440,
    objectFit: 'contain', objectPosition: 'bottom center',
    filter: `drop-shadow(0 0 30px ${skin.glowColor})`,
    ...posStyle,
  };

  if (!name) return null;
  if (!imgFailed && src) {
    return <img src={src} alt={name} style={imgStyle} onError={() => setImgFailed(true)} />;
  }
  return <div style={silhouetteStyle} title={`${name} (${expr})`}></div>;
}

// ── Background Layer ───────────────────────────────────────────────────────
function BgLayer({ src, skin }) {
  const style = {
    position: 'absolute', inset: 0,
    background: src ? `url(${src}) center/cover no-repeat` : skin.bgFallback,
    transition: 'opacity 0.4s',
  };
  return (
    <div style={style}>
      {skin.scanlines && (
        <div style={{
          position:'absolute',inset:0,pointerEvents:'none',
          background:'repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.13) 2px,rgba(0,0,0,0.13) 4px)',
        }}></div>
      )}
      {skin.halftone && (
        <div style={{
          position:'absolute',inset:0,pointerEvents:'none',
          backgroundImage:'radial-gradient(circle,rgba(255,255,255,0.04) 1px,transparent 1px)',
          backgroundSize:'18px 18px',
        }}></div>
      )}
    </div>
  );
}

// ── HUD Bar ────────────────────────────────────────────────────────────────
function HudBar({ vol, skin, state, onOverlay }) {
  const v = VOLUME_LIST.find(x => x.vol === vol);
  const h = skin.hud || {};
  const hudStyle = {
    position:'absolute',top:0,left:0,right:0,
    display:'flex',justifyContent:'space-between',alignItems:'center',
    padding:'10px 20px',
    borderBottom:`1px solid ${skin.vars['--dlg-border']}`,
    background: skin.variant === 'paper' ? 'rgba(0,0,0,0.65)' : `${skin.sceneBg}cc`,
    backdropFilter:'blur(4px)',
    fontFamily:'var(--hud-font)',fontSize:9,letterSpacing:'0.18em',
    color:'var(--hud-color)',textTransform:'uppercase',
    zIndex:10,
  };

  return (
    <div style={hudStyle}>
      <span>{v ? `${v.title} · ${v.subtitle}` : `Vol. ${vol}`}</span>
      <div style={{display:'flex',gap:16,alignItems:'center'}}>
        {h.skills && h.skills.map((sk, i) => (
          <div key={sk} style={{display:'flex',flexDirection:'column',alignItems:'center',gap:2}}>
            <span style={{fontSize:7,letterSpacing:'0.12em'}}>{sk.slice(0,3).toUpperCase()}</span>
            <div style={{display:'flex',gap:2}}>
              {[1,2,3,4,5].map(d => (
                <div key={d} style={{
                  width:5,height:5,borderRadius:'50%',
                  background: d <= (state.skills[sk.toLowerCase()] || 0) ? 'var(--accent)' : 'rgba(255,255,255,0.1)',
                }}></div>
              ))}
            </div>
          </div>
        ))}
        {h.meters && h.meterNames && h.meterNames.map((m, i) => (
          <div key={m} style={{display:'flex',flexDirection:'column',gap:2,alignItems:'flex-end'}}>
            <span style={{fontSize:7}}>{m} {state.skills[m.toLowerCase()] || 50}%</span>
            <div style={{width:44,height:2,background:'rgba(255,255,255,0.1)'}}>
              <div style={{width:`${state.skills[m.toLowerCase()] || 50}%`,height:'100%',background:h.meterCols?.[i]||'var(--accent)'}}></div>
            </div>
          </div>
        ))}
        {h.stats && state.stats && h.stats.map(s => (
          <span key={s} style={{fontSize:9,color:'var(--accent)',border:'1px solid var(--accent)',padding:'1px 5px',opacity:0.8}}>
            {s.toUpperCase()}: {state.stats[s.toLowerCase()] ?? '–'}
          </span>
        ))}
      </div>
      <div style={{display:'flex',gap:10}}>
        {['Log','Save','Menu'].map(btn => (
          <span key={btn}
            onClick={() => onOverlay(btn.toLowerCase())}
            style={{cursor:'pointer',padding:'2px 6px',border:'1px solid rgba(255,255,255,0.08)',opacity:0.6,transition:'opacity 0.15s'}}
            onMouseEnter={e => e.target.style.opacity=1}
            onMouseLeave={e => e.target.style.opacity=0.6}
          >{btn}</span>
        ))}
      </div>
    </div>
  );
}

// ── Dialogue Box — Standard ────────────────────────────────────────────────
function DialogueBoxStandard({ state, skin, onAdvance, onChoice, textSpeed, onTypingDone }) {
  const { speaker, textType, choices, displayText, isTyping, waitingForInput, endScene } = state;
  const isNarration = textType === 'narration';
  const isThought = textType === 'thought';

  return (
    <div style={{
      position:'absolute',bottom:0,left:0,right:0,
      background:'var(--dlg-bg)',
      borderTop:`1px solid var(--dlg-border)`,
      minHeight:'var(--dlg-min-h)',padding:'var(--dlg-pad)',
      cursor: (waitingForInput || isTyping) && !choices && !endScene ? 'pointer' : 'default',
    }} onClick={() => { if (!choices && !endScene) onAdvance(); }}>
      <div style={{position:'absolute',top:0,left:44,right:44,height:1,background:'var(--dlg-rule)'}}></div>
      {speaker && !isNarration && (
        <div style={{
          fontFamily:'var(--spk-font)',fontSize:'var(--spk-size)',
          color:'var(--spk-color)',letterSpacing:'var(--spk-tracking)',
          textTransform:'uppercase',marginBottom:10,fontStyle:'var(--spk-style)',
        }}>{speaker}</div>
      )}
      <div style={{
        fontFamily:'var(--txt-font)',fontSize:'var(--txt-size)',
        color:'var(--txt-color)',fontStyle: isThought ? 'italic' : 'var(--txt-style)',
        fontWeight:'var(--txt-weight)',lineHeight:'var(--txt-lh)',
        maxWidth:780,opacity: isThought ? 0.75 : 1,
      }}>
        {isThought && '( '}
        <Typewriter text={displayText} speed={textSpeed} skin={skin}
          skip={!isTyping} onDone={onTypingDone} />
        {isThought && ' )'}
      </div>
      {choices && (
        <div style={{display:'flex',flexDirection:'column',gap:7,marginTop:18}}>
          {choices.map((c, i) => (
            <div key={i}
              onClick={e => { e.stopPropagation(); onChoice(i); }}
              style={{
                display:'flex',alignItems:'center',gap:12,
                padding:'8px 16px',cursor:'pointer',
                border:'1px solid var(--ch-border)',background:'var(--ch-bg)',
                fontFamily:'var(--ch-font)',fontSize:'var(--ch-size)',
                color: c.locked ? 'rgba(128,128,128,0.4)' : 'var(--ch-color)',
                transition:'all 0.15s',
              }}
              onMouseEnter={e => { if (!c.locked) { e.currentTarget.style.borderColor='var(--ch-hborder)'; e.currentTarget.style.background='var(--ch-hbg)'; e.currentTarget.style.color='var(--ch-hcolor)'; }}}
              onMouseLeave={e => { e.currentTarget.style.borderColor='var(--ch-border)'; e.currentTarget.style.background='var(--ch-bg)'; e.currentTarget.style.color='var(--ch-color)'; }}
            >
              <span style={{color:'var(--accent)',fontSize:'0.85em',minWidth:20}}>{String.fromCharCode(65+i)}</span>
              <span>{c.text}</span>
              {c.locked && <span style={{marginLeft:'auto',fontSize:9,opacity:0.5}}>LOCKED</span>}
            </div>
          ))}
        </div>
      )}
      {!choices && (
        <div style={{position:'absolute',bottom:14,right:40,display:'flex',gap:20,fontFamily:'var(--hud-font)',fontSize:9,letterSpacing:'0.18em',color:'var(--nav-color)',textTransform:'uppercase'}}>
          {waitingForInput && !endScene && <span style={{animation:'vn-pulse 1.5s ease-in-out infinite'}}>▼ Continue</span>}
          {endScene && <span>End of Demo</span>}
        </div>
      )}
    </div>
  );
}

// ── Dialogue Box — Paper/Zine ──────────────────────────────────────────────
function DialogueBoxPaper({ state, skin, onAdvance, onChoice, textSpeed, onTypingDone }) {
  const { speaker, choices, displayText, isTyping, waitingForInput, endScene } = state;
  return (
    <div style={{
      position:'absolute',bottom:0,left:0,right:0,
      background:'var(--dlg-bg)',minHeight:'var(--dlg-min-h)',
      transform:'skewY(-0.3deg)',transformOrigin:'left',
      cursor: (waitingForInput || isTyping) && !choices && !endScene ? 'pointer' : 'default',
    }} onClick={() => { if (!choices && !endScene) onAdvance(); }}>
      {/* Tape strips */}
      {[{left:'60px',rot:'-1.5deg'},{right:'120px',rot:'2deg'}].map((t,i)=>(
        <div key={i} style={{
          position:'absolute',top:-11,width:76,height:22,
          background:'rgba(255,220,100,0.5)',transform:`rotate(${t.rot})`,
          ...(t.left ? {left:t.left} : {right:t.right}),
        }}></div>
      ))}
      <div style={{padding:'var(--dlg-pad)',transform:'skewY(0.3deg)'}}>
        {speaker && (
          <div style={{
            fontFamily:'var(--spk-font)',fontSize:'var(--spk-size)',
            color:'var(--spk-color)',letterSpacing:'var(--spk-tracking)',
            lineHeight:1,marginBottom:8,
          }}>{speaker}</div>
        )}
        <div style={{
          fontFamily:'var(--txt-font)',fontSize:'var(--txt-size)',
          color:'var(--txt-color)',lineHeight:'var(--txt-lh)',maxWidth:700,
        }}>
          <Typewriter text={displayText} speed={textSpeed} skin={skin} skip={!isTyping} onDone={onTypingDone} />
        </div>
        {choices && (
          <div style={{display:'flex',flexWrap:'wrap',gap:8,marginTop:14}}>
            {choices.map((c,i)=>(
              <div key={i} onClick={e=>{e.stopPropagation();onChoice(i);}} style={{
                padding:'6px 14px',background:'var(--ch-bg)',color:'var(--ch-color)',
                fontFamily:'var(--ch-font)',fontSize:'var(--ch-size)',cursor:'pointer',
                letterSpacing:'0.06em',transition:'background 0.15s',
              }}
              onMouseEnter={e=>e.currentTarget.style.background='var(--ch-hbg)'}
              onMouseLeave={e=>e.currentTarget.style.background='var(--ch-bg)'}
              >› {c.text}</div>
            ))}
          </div>
        )}
        {!choices && waitingForInput && !endScene && (
          <div style={{marginTop:10,fontFamily:'var(--hud-font)',fontSize:11,color:'var(--accent)',letterSpacing:'0.1em'}}>
            ▼
          </div>
        )}
      </div>
    </div>
  );
}

// ── Dialogue Box — Terminal/Signal ─────────────────────────────────────────
function DialogueBoxTerminal({ state, skin, onAdvance, onChoice, textSpeed, onTypingDone }) {
  const { speaker, speakerRole, choices, displayText, isTyping, waitingForInput, endScene } = state;
  return (
    <div style={{
      position:'absolute',bottom:0,left:0,right:0,
      background:'var(--dlg-bg)',borderTop:'1px solid var(--dlg-border)',
      minHeight:'var(--dlg-min-h)',padding:'var(--dlg-pad)',
      cursor: (waitingForInput || isTyping) && !choices && !endScene ? 'pointer' : 'default',
    }} onClick={() => { if (!choices && !endScene) onAdvance(); }}>
      <div style={{position:'absolute',top:0,left:0,right:0,height:1,background:'var(--dlg-rule)'}}></div>
      {speaker && (
        <div style={{display:'flex',alignItems:'center',gap:10,marginBottom:10}}>
          <span style={{color:'rgba(0,200,255,0.4)',fontFamily:'var(--spk-font)',fontSize:12}}>›_</span>
          <span style={{fontFamily:'var(--spk-font)',fontSize:'var(--spk-size)',color:'var(--spk-color)',letterSpacing:'var(--spk-tracking)',textTransform:'uppercase'}}>{speaker}</span>
          {speakerRole && <span style={{fontSize:8,border:'1px solid var(--accent2)',padding:'1px 5px',color:'var(--accent2)',opacity:0.7}}>{speakerRole}</span>}
        </div>
      )}
      <div style={{fontFamily:'var(--txt-font)',fontSize:'var(--txt-size)',color:'var(--txt-color)',lineHeight:'var(--txt-lh)',maxWidth:780}}>
        <Typewriter text={displayText} speed={textSpeed} skin={skin} skip={!isTyping} onDone={onTypingDone} />
      </div>
      {choices && (
        <div style={{display:'flex',flexDirection:'column',gap:5,marginTop:14}}>
          {choices.map((c,i)=>(
            <div key={i} onClick={e=>{e.stopPropagation();!c.locked&&onChoice(i);}} style={{
              display:'flex',alignItems:'center',gap:10,padding:'6px 12px',
              border:'1px solid var(--ch-border)',background:'var(--ch-bg)',
              fontFamily:'var(--ch-font)',fontSize:'var(--ch-size)',
              color: c.locked ? 'rgba(128,128,128,0.35)' : 'var(--ch-color)',
              cursor: c.locked ? 'not-allowed' : 'pointer',transition:'all 0.15s',
            }}
            onMouseEnter={e=>{if(!c.locked){e.currentTarget.style.borderColor='var(--ch-hborder)';e.currentTarget.style.color='var(--ch-hcolor)';}}}
            onMouseLeave={e=>{e.currentTarget.style.borderColor='var(--ch-border)';e.currentTarget.style.color=c.locked?'rgba(128,128,128,0.35)':'var(--ch-color)';}}
            >
              <span style={{color:'var(--accent)',fontSize:10,minWidth:24}}>{String(i+1).padStart(2,'0')}.</span>
              <span>{c.text}</span>
              {c.locked && <span style={{marginLeft:'auto',fontSize:8,color:'var(--accent2)'}}>LOCKED · {c.lockLabel}</span>}
            </div>
          ))}
        </div>
      )}
      {!choices && waitingForInput && !endScene && (
        <div style={{position:'absolute',bottom:12,right:36,fontFamily:'var(--hud-font)',fontSize:9,color:'var(--nav-color)',letterSpacing:'0.18em',textTransform:'uppercase',animation:'vn-pulse 1.5s ease-in-out infinite'}}>
          ▼ continue
        </div>
      )}
    </div>
  );
}

// ── Overlays ───────────────────────────────────────────────────────────────
function Backlog({ log, skin, onClose }) {
  return (
    <div style={{position:'absolute',inset:0,background:'var(--ov-bg)',zIndex:50,overflow:'auto',padding:'40px 60px'}}>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:30}}>
        <span style={{fontFamily:'var(--hud-font)',fontSize:10,letterSpacing:'0.25em',color:'var(--accent)',textTransform:'uppercase'}}>Dialogue Log</span>
        <span onClick={onClose} style={{cursor:'pointer',fontFamily:'var(--hud-font)',fontSize:9,color:'var(--nav-color)',letterSpacing:'0.15em',textTransform:'uppercase',border:'1px solid var(--ov-border)',padding:'4px 10px'}}>Close</span>
      </div>
      {log.length === 0 && <div style={{fontFamily:'var(--txt-font)',color:'var(--ov-txt)',opacity:0.4,fontStyle:'italic'}}>No dialogue recorded yet.</div>}
      {[...log].reverse().map((entry,i)=>(
        <div key={i} style={{marginBottom:18,opacity: i===0?1:0.65-i*0.02,transition:'opacity 0.2s'}}>
          {entry.speaker && <div style={{fontFamily:'var(--spk-font)',fontSize:'var(--spk-size)',color:'var(--spk-color)',letterSpacing:'var(--spk-tracking)',textTransform:'uppercase',marginBottom:4}}>{entry.speaker}</div>}
          <div style={{fontFamily:'var(--txt-font)',fontSize:'var(--txt-size)',color:'var(--ov-txt)',lineHeight:'var(--txt-lh)',fontStyle:entry.type==='narration'?'italic':'var(--txt-style)'}}>{entry.text}</div>
        </div>
      ))}
    </div>
  );
}

function Settings({ state, dispatch, onClose }) {
  return (
    <div style={{position:'absolute',inset:0,background:'var(--ov-bg)',zIndex:50,display:'flex',alignItems:'center',justifyContent:'center'}}>
      <div style={{width:480,padding:'40px',border:'1px solid var(--ov-border)'}}>
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:30}}>
          <span style={{fontFamily:'var(--hud-font)',fontSize:10,letterSpacing:'0.25em',color:'var(--accent)',textTransform:'uppercase'}}>Settings</span>
          <span onClick={onClose} style={{cursor:'pointer',fontFamily:'var(--hud-font)',fontSize:9,color:'var(--nav-color)',letterSpacing:'0.15em',textTransform:'uppercase',border:'1px solid var(--ov-border)',padding:'4px 10px'}}>Close</span>
        </div>
        {[
          {label:'Text Speed',key:'textSpeed',min:5,max:80,step:1,val:state.textSpeed,action:(v)=>dispatch({type:'UPDATE_SPEED',val:v})},
          {label:'Master Volume',key:'masterVol',min:0,max:1,step:0.05,val:state.masterVol,action:(v)=>dispatch({type:'UPDATE_VOL',master:v})},
          {label:'Music Volume',key:'bgmVol',min:0,max:1,step:0.05,val:state.bgmVol,action:(v)=>dispatch({type:'UPDATE_VOL',bgm:v})},
          {label:'Font Size',key:'fontSize',min:14,max:24,step:1,val:state.fontSize,action:(v)=>dispatch({type:'UPDATE_FONTSIZE',val:v})},
        ].map(s=>(
          <div key={s.key} style={{marginBottom:20}}>
            <div style={{display:'flex',justifyContent:'space-between',marginBottom:6}}>
              <span style={{fontFamily:'var(--hud-font)',fontSize:9,letterSpacing:'0.15em',color:'var(--ov-txt)',textTransform:'uppercase',opacity:0.7}}>{s.label}</span>
              <span style={{fontFamily:'var(--hud-font)',fontSize:9,color:'var(--accent)'}}>{s.key.includes('Vol') ? Math.round(s.val*100)+'%' : s.val}</span>
            </div>
            <input type="range" min={s.min} max={s.max} step={s.step} value={s.val}
              onChange={e=>s.action(parseFloat(e.target.value))}
              style={{width:'100%',accentColor:'var(--accent)'}} />
          </div>
        ))}
      </div>
    </div>
  );
}

function SaveLoad({ state, dispatch, onClose }) {
  const saves = loadSaves();
  const doSave = (slot) => {
    const existing = saves.filter(s=>s.slot!==slot);
    const entry = { slot, vol: state.vol, sceneId: state.sceneId, nodeIndex: state.nodeIndex, flags: state.flags, skills: state.skills, stats: state.stats, relationships: state.relationships, timestamp: Date.now() };
    writeSave([...existing, entry].slice(0,8));
  };
  const doLoad = (save) => {
    dispatch({ type: 'LOAD_SAVE', save: { ...initState(save.vol), ...save } });
  };
  const slots = Array.from({length:6},(_,i)=>i+1).map(s=>({ slot:s, ...(saves.find(sv=>sv.slot===s)||null) }));
  return (
    <div style={{position:'absolute',inset:0,background:'var(--ov-bg)',zIndex:50,display:'flex',alignItems:'center',justifyContent:'center'}}>
      <div style={{width:520,padding:'40px',border:'1px solid var(--ov-border)'}}>
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:28}}>
          <span style={{fontFamily:'var(--hud-font)',fontSize:10,letterSpacing:'0.25em',color:'var(--accent)',textTransform:'uppercase'}}>Save / Load</span>
          <span onClick={onClose} style={{cursor:'pointer',fontFamily:'var(--hud-font)',fontSize:9,color:'var(--nav-color)',letterSpacing:'0.15em',textTransform:'uppercase',border:'1px solid var(--ov-border)',padding:'4px 10px'}}>Close</span>
        </div>
        {slots.map(s=>(
          <div key={s.slot} style={{display:'flex',alignItems:'center',gap:14,padding:'10px 14px',border:'1px solid var(--ov-border)',marginBottom:8}}>
            <span style={{fontFamily:'var(--hud-font)',fontSize:9,color:'var(--accent)',minWidth:60,textTransform:'uppercase',letterSpacing:'0.1em'}}>Slot {s.slot}</span>
            <span style={{fontFamily:'var(--txt-font)',fontSize:13,color:'var(--ov-txt)',flex:1,opacity: s.sceneId ? 1 : 0.3}}>
              {s.sceneId ? `Vol ${s.vol} · ${s.sceneId}` : '— Empty —'}
              {s.timestamp && <span style={{fontSize:10,opacity:0.4,marginLeft:8}}>{new Date(s.timestamp).toLocaleDateString()}</span>}
            </span>
            <span onClick={()=>doSave(s.slot)} style={{cursor:'pointer',fontFamily:'var(--hud-font)',fontSize:8,letterSpacing:'0.12em',color:'var(--accent)',textTransform:'uppercase',padding:'3px 8px',border:'1px solid var(--accent)',opacity:0.7}}
              onMouseEnter={e=>e.target.style.opacity=1} onMouseLeave={e=>e.target.style.opacity=0.7}>Save</span>
            {s.sceneId && <span onClick={()=>doLoad(s)} style={{cursor:'pointer',fontFamily:'var(--hud-font)',fontSize:8,letterSpacing:'0.12em',color:'var(--ov-txt)',textTransform:'uppercase',padding:'3px 8px',border:'1px solid var(--ov-border)',opacity:0.7}}
              onMouseEnter={e=>e.target.style.opacity=1} onMouseLeave={e=>e.target.style.opacity=0.7}>Load</span>}
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Scene Runner Hook ──────────────────────────────────────────────────────
function useSceneRunner(state, dispatch) {
  const advance = React.useCallback(() => {
    if (state.choices) return;
    if (state.isTyping) { dispatch({ type: 'SKIP_TYPING' }); return; }
    if (!state.waitingForInput || state.endScene) return;
    const scene = state.currentScene;
    if (!scene) return;
    const nextIdx = state.nodeIndex + 1;
    if (nextIdx >= scene.nodes.length) { dispatch({ type: 'END_SCENE' }); return; }
    dispatch({ type: 'SET_NODE', idx: nextIdx });
  }, [state, dispatch]);

  const selectChoice = React.useCallback((idx) => {
    if (!state.choices) return;
    const c = state.choices[idx];
    if (!c || c.locked) return;
    dispatch({ type: 'CLEAR_CHOICES' });
    const scene = state.currentScene;
    if (c.scene) {
      const nextScene = DEMO_SCENES[c.scene];
      if (nextScene) dispatch({ type: 'SET_SCENE', scene: nextScene });
    } else if (c.goto !== undefined) {
      dispatch({ type: 'SET_NODE', idx: c.goto });
    }
  }, [state, dispatch]);

  // Process current node
  React.useEffect(() => {
    const scene = state.currentScene;
    if (!scene || state.isTyping || state.waitingForInput || state.choices || state.endScene) return;
    const node = scene.nodes[state.nodeIndex];
    if (!node) { dispatch({ type: 'END_SCENE' }); return; }

    switch (node.t) {
      case 'narrate':
        dispatch({ type: 'SET_SPEAKER', speaker: null, textType: 'narration' });
        dispatch({ type: 'SET_TEXT', text: node.text });
        dispatch({ type: 'ADD_LOG', entry: { speaker: null, text: node.text, type: 'narration' } });
        break;
      case 'say':
        dispatch({ type: 'SET_SPEAKER', speaker: node.char, role: node.role, textType: 'dialogue' });
        dispatch({ type: 'SET_TEXT', text: node.text });
        dispatch({ type: 'ADD_LOG', entry: { speaker: node.char, text: node.text, type: 'dialogue' } });
        break;
      case 'think':
        dispatch({ type: 'SET_SPEAKER', speaker: node.char, textType: 'thought' });
        dispatch({ type: 'SET_TEXT', text: node.text });
        dispatch({ type: 'ADD_LOG', entry: { speaker: node.char || 'You', text: node.text, type: 'thought' } });
        break;
      case 'show':
        dispatch({ type: 'SHOW_CHAR', name: node.char, expr: node.expr || 'neutral', pos: node.pos || 'center' });
        dispatch({ type: 'SET_NODE', idx: state.nodeIndex + 1 });
        break;
      case 'hide':
        dispatch({ type: 'HIDE_CHAR', pos: node.pos });
        dispatch({ type: 'SET_NODE', idx: state.nodeIndex + 1 });
        break;
      case 'bg':
        dispatch({ type: 'SET_BG', src: node.src });
        dispatch({ type: 'SET_NODE', idx: state.nodeIndex + 1 });
        break;
      case 'bgm':
        dispatch({ type: 'SET_BGM', src: node.src });
        audioMgr.playBgm(node.src);
        dispatch({ type: 'SET_NODE', idx: state.nodeIndex + 1 });
        break;
      case 'sfx':
        audioMgr.playSfx(node.src);
        dispatch({ type: 'SET_NODE', idx: state.nodeIndex + 1 });
        break;
      case 'flag':
        dispatch({ type: 'SET_FLAG', key: node.key, val: node.val });
        dispatch({ type: 'SET_NODE', idx: state.nodeIndex + 1 });
        break;
      case 'choice': {
        const opts = node.opts.map(o => {
          if (o.check) {
            const skillVal = state.skills[o.check.skill] || 0;
            const pass = o.check.type === 'meter' ? skillVal >= o.check.diff : skillVal >= Math.ceil(o.check.diff / 2);
            return { ...o, locked: !pass, lockLabel: `${o.check.skill.toUpperCase()} ${skillVal}/${o.check.diff}` };
          }
          return o;
        });
        dispatch({ type: 'SET_CHOICES', choices: opts });
        break;
      }
      case 'videoscene':
        dispatch({ type: 'SET_VIDEO_SCENE', node });
        break;
      case 'jump': {
        const nextScene = DEMO_SCENES[node.scene];
        if (nextScene) dispatch({ type: 'SET_SCENE', scene: nextScene });
        else dispatch({ type: 'END_SCENE' });
        break;
      }
      case 'end':
        dispatch({ type: 'END_SCENE' });
        break;
      default:
        dispatch({ type: 'SET_NODE', idx: state.nodeIndex + 1 });
    }
  }, [state.currentScene, state.nodeIndex, state.isTyping, state.waitingForInput, state.choices, state.endScene]);

  return { advance, selectChoice };
}

// ── GameScreen ─────────────────────────────────────────────────────────────
function GameScreen({ vol, onReturn }) {
  const skin = getSkin(vol);
  const [state, dispatch] = React.useReducer(reducer, null, () => initState(vol));
  const { advance, selectChoice } = useSceneRunner(state, dispatch);

  // Load initial scene
  React.useEffect(() => {
    const scene = DEMO_SCENES[vol];
    if (scene) dispatch({ type: 'SET_SCENE', scene });
  }, [vol]);

  // Keyboard
  React.useEffect(() => {
    const handler = (e) => {
      if (e.code === 'Space' || e.code === 'Enter') { e.preventDefault(); advance(); }
      if (e.code === 'Escape') dispatch({ type: 'SET_OVERLAY', overlay: state.overlay ? null : 'save' });
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [advance, state.overlay]);

  const cssVars = Object.entries(skin.vars).reduce((acc,[k,v])=>({...acc,[k]:v}),{});

  const dlgProps = { state, skin, onAdvance: advance, onChoice: selectChoice, textSpeed: state.textSpeed, onTypingDone: () => dispatch({ type: 'FINISH_TYPING' }) };

  return (
    <div style={{ position:'relative', width:'100%', height:'100%', overflow:'hidden', background: skin.sceneBg, ...cssVars, fontSize: state.fontSize }}>
      <BgLayer src={state.background} skin={skin} />

      {/* Characters */}
      {Object.entries(state.characters).map(([pos, ch]) =>
        ch ? <CharSprite key={pos} name={ch.name} expr={ch.expr} pos={pos} skin={skin} /> : null
      )}

      <HudBar vol={vol} skin={skin} state={state} onOverlay={(o) => dispatch({ type: 'SET_OVERLAY', overlay: o })} />

      {/* Dialogue */}
      {skin.variant === 'paper' && <DialogueBoxPaper {...dlgProps} />}
      {skin.variant === 'terminal' && <DialogueBoxTerminal {...dlgProps} />}
      {(skin.variant === 'standard' || skin.variant === 'card') && <DialogueBoxStandard {...dlgProps} />}

      {/* Interactive Video Scene */}
      {state.videoScene && typeof InteractiveVideo !== 'undefined' && (
        <div style={{position:'absolute',inset:0,zIndex:30}}>
          <InteractiveVideo
            node={state.videoScene}
            skin={skin}
            state={state}
            dispatch={dispatch}
            onExit={() => {
              dispatch({ type: 'CLEAR_VIDEO_SCENE' });
              dispatch({ type: 'SET_NODE', idx: state.nodeIndex + 1 });
            }}
          />
        </div>
      )}

      {state.endScene && (
        <div style={{position:'absolute',inset:0,display:'flex',alignItems:'center',justifyContent:'center',background:'rgba(0,0,0,0.6)',zIndex:20}}>
          <div style={{textAlign:'center'}}>
            <div style={{fontFamily:'var(--spk-font)',fontSize:11,letterSpacing:'0.35em',color:'var(--accent)',textTransform:'uppercase',marginBottom:20}}>End of Demo</div>
            <div onClick={onReturn} style={{fontFamily:'var(--hud-font)',fontSize:9,letterSpacing:'0.25em',color:'var(--nav-color)',textTransform:'uppercase',border:'1px solid var(--ov-border)',padding:'10px 24px',cursor:'pointer',display:'inline-block'}}>
              Return to Menu
            </div>
          </div>
        </div>
      )}

      {/* Overlays */}
      {state.overlay === 'log' && <Backlog log={state.log} skin={skin} onClose={() => dispatch({ type: 'SET_OVERLAY', overlay: null })} />}
      {state.overlay === 'settings' && <Settings state={state} dispatch={dispatch} onClose={() => dispatch({ type: 'SET_OVERLAY', overlay: null })} />}
      {state.overlay === 'save' && <SaveLoad state={state} dispatch={dispatch} onClose={() => dispatch({ type: 'SET_OVERLAY', overlay: null })} />}
      {state.overlay === 'menu' && (
        <div style={{position:'absolute',inset:0,background:'rgba(0,0,0,0.7)',zIndex:50,display:'flex',alignItems:'center',justifyContent:'center'}}>
          <div style={{display:'flex',flexDirection:'column',gap:12,alignItems:'center'}}>
            {[['Resume',()=>dispatch({type:'SET_OVERLAY',overlay:null})],['Settings',()=>dispatch({type:'SET_OVERLAY',overlay:'settings'})],['Save / Load',()=>dispatch({type:'SET_OVERLAY',overlay:'save'})],['Return to Menu',onReturn]].map(([label,fn])=>(
              <div key={label} onClick={fn} style={{fontFamily:'var(--hud-font)',fontSize:10,letterSpacing:'0.25em',color:'var(--ov-txt)',textTransform:'uppercase',border:'1px solid var(--ov-border)',padding:'12px 36px',cursor:'pointer',minWidth:220,textAlign:'center',transition:'border-color 0.15s'}}
                onMouseEnter={e=>e.currentTarget.style.borderColor='var(--accent)'}
                onMouseLeave={e=>e.currentTarget.style.borderColor='var(--ov-border)'}
              >{label}</div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

Object.assign(window, { GameScreen });
