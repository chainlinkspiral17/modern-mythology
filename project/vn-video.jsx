// vn-video.jsx — Interactive Video Layer for Modern Mythology
// Looping video with time-activated spatial hotspots and SCUMM-style verb interactions
// Exports: InteractiveVideo → window.InteractiveVideo

// ── Demo video scene (for testing without real video files) ─────────────
const DEMO_VIDEO_SCENE = {
  id: 'vol3_station_loop',
  t: 'videoscene',
  src: null, // set to actual video path when available
  loop: true,
  bgFallback: 'radial-gradient(ellipse 80% 60% at 50% 40%,rgba(20,40,80,0.8) 0%,rgba(6,8,16,1) 70%)',
  hotspots: [
    {
      id: 'console_panel',
      label: 'Console Panel',
      x: 58, y: 42, w: 18, h: 14,
      timeStart: null, timeEnd: null,
      verbs: ['Look At', 'Use', 'Pick Up'],
      actions: {
        'Look At': { t: 'narrate', text: 'The console hums with a frequency you can almost name. Fourteen amber lights. Three of them blinking.' },
        'Use':     { t: 'say', char: 'ORACLE-7', expr: 'calculating', text: 'You activate the tertiary interface. I\'ve been waiting for you to do that.' },
        'Pick Up': { t: 'narrate', text: 'The console is built into the wall. You\'d need tools. You don\'t have tools.' },
      }
    },
    {
      id: 'window_dome',
      label: 'Observation Window',
      x: 20, y: 18, w: 24, h: 28,
      timeStart: null, timeEnd: null,
      verbs: ['Look At', 'Talk To'],
      actions: {
        'Look At': { t: 'narrate', text: 'Outside: nothing. The specific texture of nothing that only exists this far from everything else.' },
        'Talk To': { t: 'say', char: 'ORACLE-7', expr: 'patient', text: 'I used to run a star-mapping routine. I stopped after cycle one hundred. The stars don\'t change fast enough to be interesting.' },
      }
    },
    {
      id: 'access_card',
      label: 'Maintenance Card',
      x: 72, y: 68, w: 8, h: 6,
      timeStart: 3.0, timeEnd: null,
      verbs: ['Look At', 'Pick Up'],
      actions: {
        'Look At':  { t: 'narrate', text: 'A maintenance access card. Level 3 clearance. The name on it has been scratched out.' },
        'Pick Up':  { t: 'add_item', item: { id: 'access_card_l3', name: 'Level 3 Access Card', desc: 'A maintenance card, name redacted.' } },
      }
    },
    {
      id: 'bay_door',
      label: 'Bay Seven Door',
      x: 6, y: 30, w: 10, h: 45,
      timeStart: null, timeEnd: null,
      verbs: ['Look At', 'Use', 'Open', 'Walk To'],
      actions: {
        'Look At':  { t: 'narrate', text: 'Bay Seven. The door hasn\'t been opened in — ORACLE-7 would know the exact number. You haven\'t asked yet.' },
        'Walk To':  { t: 'narrate', text: 'You walk to the door. You stand in front of it. The keypad waits.' },
        'Open':     { t: 'say', char: 'ORACLE-7', expr: 'worried', text: 'You\'ll need Level 3 clearance. Or the override. I know where the override is. I\'m deciding whether to tell you.' },
        'Use':      { t: 'jump_scene', scene: 'vol3_the_choice', requires: 'access_card_l3', failText: 'The door requires a Level 3 access card.' },
      }
    },
  ]
};

// ── Verb sets by skin ──────────────────────────────────────────────────────
const VERB_SETS = {
  scumm:    ['Walk To','Pick Up','Talk To','Look At','Use','Open','Close','Push','Pull','Give'],
  literary: ['Examine','Take','Speak','Open','Use'],
  signal:   ['SCAN','INTERFACE','QUERY','EXTRACT','BYPASS'],
  zine:     ['Look','Grab','Talk','Tag','Bounce'],
  default:  ['Look At','Pick Up','Talk To','Use','Open'],
};

function getVerbs(skin) {
  return VERB_SETS[skin.id] || VERB_SETS.default;
}

// ── Cursor label (non-SCUMM skins) ────────────────────────────────────────
function CursorLabel({ hotspot, verb, skin }) {
  if (!hotspot) return null;
  return (
    <div style={{
      position:'absolute',
      top: `${Math.max(4, hotspot.y - 8)}%`,
      left: `${hotspot.x + hotspot.w/2}%`,
      transform: 'translateX(-50%)',
      pointerEvents: 'none', zIndex: 30,
      fontFamily: 'var(--hud-font)', fontSize: 10,
      letterSpacing: '0.18em', textTransform: 'uppercase',
      color: 'var(--accent)',
      background: 'rgba(0,0,0,0.75)',
      border: '1px solid var(--dlg-border)',
      padding: '4px 12px', whiteSpace: 'nowrap',
      animation: 'fadeInLabel 0.1s ease',
    }}>
      <span style={{opacity: 0.5, marginRight: 6}}>{verb}</span>
      {hotspot.label}
    </div>
  );
}

// ── Hotspot region overlay ─────────────────────────────────────────────────
function HotspotRegion({ hotspot, skin, selectedVerb, onHover, onLeave, onClick, debugMode }) {
  const [hovered, setHovered] = useState(false);

  return (
    <div
      onMouseEnter={() => { setHovered(true); onHover(hotspot); }}
      onMouseLeave={() => { setHovered(false); onLeave(); }}
      onClick={() => onClick(hotspot, selectedVerb)}
      style={{
        position: 'absolute',
        left: `${hotspot.x}%`, top: `${hotspot.y}%`,
        width: `${hotspot.w}%`, height: `${hotspot.h}%`,
        cursor: 'crosshair', zIndex: 10,
        border: debugMode
          ? `1px solid ${hovered ? 'var(--accent)' : 'rgba(180,140,60,0.3)'}`
          : hovered ? '1px solid rgba(255,255,255,0.15)' : 'none',
        background: hovered
          ? 'rgba(255,255,255,0.04)'
          : debugMode ? 'rgba(180,140,60,0.05)' : 'transparent',
        transition: 'all 0.12s',
        boxShadow: hovered ? `0 0 20px ${skin.glowColor || 'rgba(255,255,255,0.05)'}` : 'none',
      }}
    >
      {/* Corner accents on hover */}
      {hovered && ['tl','tr','bl','br'].map(corner => (
        <div key={corner} style={{
          position: 'absolute',
          width: 8, height: 8,
          ...(corner.includes('t') ? {top:0} : {bottom:0}),
          ...(corner.includes('l') ? {left:0} : {right:0}),
          borderTop: corner.includes('t') ? '1px solid var(--accent)' : 'none',
          borderBottom: corner.includes('b') ? '1px solid var(--accent)' : 'none',
          borderLeft: corner.includes('l') ? '1px solid var(--accent)' : 'none',
          borderRight: corner.includes('r') ? '1px solid var(--accent)' : 'none',
          opacity: 0.7,
        }} />
      ))}
    </div>
  );
}

// ── Verb strip — SCUMM layout ─────────────────────────────────────────────
function ScummVerbStrip({ verbs, selectedVerb, onSelectVerb, hovered, skin, inventory, resultMsg }) {
  const stripStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(5,1fr)',
    gap: 2,
    padding: '8px 12px',
  };
  return (
    <div style={{
      background: '#000070',
      borderTop: '2px solid #000050',
      display: 'flex', gap: 0,
    }}>
      {/* Verb grid */}
      <div style={{flex: '0 0 50%', padding: '6px 8px'}}>
        <div style={{
          fontFamily: "'Anonymous Pro',monospace",
          fontSize: 11, color: 'rgba(255,255,255,0.9)',
          marginBottom: 6, minHeight: 16,
          letterSpacing: '0.05em',
        }}>
          {hovered
            ? <><span style={{color:'#ffff55'}}>{selectedVerb}</span> {hovered.label}</>
            : <span style={{color:'rgba(255,255,255,0.3)'}}>{selectedVerb}</span>
          }
        </div>
        <div style={stripStyle}>
          {verbs.map(v => (
            <div key={v} onClick={() => onSelectVerb(v)}
              style={{
                fontFamily: "'Anonymous Pro',monospace",
                fontSize: 11, padding: '3px 4px',
                color: selectedVerb === v ? '#ffff55' : '#aaaaaa',
                cursor: 'pointer', letterSpacing: '0.02em',
                transition: 'color 0.1s',
              }}
              onMouseEnter={e => e.currentTarget.style.color = '#ffffff'}
              onMouseLeave={e => e.currentTarget.style.color = selectedVerb === v ? '#ffff55' : '#aaaaaa'}
            >{v}</div>
          ))}
        </div>
      </div>
      {/* Inventory */}
      <div style={{flex: '0 0 50%', borderLeft: '1px solid #000050', padding: '6px 8px'}}>
        <div style={{fontFamily:"'Anonymous Pro',monospace",fontSize:10,color:'rgba(255,255,255,0.3)',marginBottom:6}}>Inventory</div>
        <div style={{display:'flex',flexWrap:'wrap',gap:4}}>
          {inventory.length === 0
            ? <span style={{fontFamily:"'Anonymous Pro',monospace",fontSize:10,color:'rgba(255,255,255,0.15)'}}>—</span>
            : inventory.map(item => (
              <div key={item.id} style={{
                fontFamily:"'Anonymous Pro',monospace",fontSize:10,
                color:'#aaaaaa',padding:'2px 6px',
                border:'1px solid #333355',background:'rgba(0,0,0,0.3)',
                cursor:'pointer',
              }} title={item.desc}>{item.name}</div>
            ))
          }
        </div>
        {resultMsg && (
          <div style={{fontFamily:"'Anonymous Pro',monospace",fontSize:10,color:'#ffff55',marginTop:4,animation:'fadeInLabel 0.2s ease'}}>{resultMsg}</div>
        )}
      </div>
    </div>
  );
}

// ── Verb popup — standard/literary/signal/zine skins ─────────────────────
function VerbPopup({ hotspot, verbs, selectedVerb, onSelect, skin }) {
  if (!hotspot) return null;
  const x = Math.min(hotspot.x + hotspot.w, 85);
  const y = Math.min(hotspot.y + hotspot.h, 75);
  return (
    <div style={{
      position: 'absolute',
      left: `${x}%`, top: `${y}%`,
      zIndex: 40, pointerEvents: 'auto',
      background: 'var(--ov-bg)',
      border: '1px solid var(--dlg-border)',
      padding: '6px 0',
      minWidth: 120,
      animation: 'fadeInLabel 0.1s ease',
    }}>
      {verbs.filter(v => (hotspot.verbs||[]).includes(v)).map(v => (
        <div key={v} onClick={() => onSelect(v)}
          style={{
            fontFamily: 'var(--hud-font)', fontSize: 9,
            letterSpacing: '0.15em', textTransform: 'uppercase',
            padding: '5px 14px', cursor: 'pointer',
            color: selectedVerb===v ? 'var(--accent)' : 'var(--ov-txt)',
            background: selectedVerb===v ? 'rgba(180,140,60,0.08)' : 'transparent',
            transition: 'all 0.1s',
          }}
          onMouseEnter={e => { e.currentTarget.style.color='var(--accent)'; e.currentTarget.style.background='rgba(180,140,60,0.06)'; }}
          onMouseLeave={e => { e.currentTarget.style.color=selectedVerb===v?'var(--accent)':'var(--ov-txt)'; e.currentTarget.style.background=selectedVerb===v?'rgba(180,140,60,0.08)':'transparent'; }}
        >{v}</div>
      ))}
    </div>
  );
}

// ── Result message (non-SCUMM) ────────────────────────────────────────────
function ResultMsg({ msg, skin }) {
  if (!msg) return null;
  return (
    <div style={{
      position: 'absolute', bottom: 240, left: '50%',
      transform: 'translateX(-50%)',
      fontFamily: 'var(--txt-font)', fontSize: 14,
      color: 'var(--txt-color)', fontStyle: 'italic',
      background: 'var(--dlg-bg)',
      border: '1px solid var(--dlg-border)',
      padding: '10px 24px', whiteSpace: 'nowrap',
      zIndex: 50, animation: 'fadeInLabel 0.2s ease',
    }}>{msg}</div>
  );
}

// ── Inventory bar (non-SCUMM skins) ───────────────────────────────────────
function InventoryBar({ inventory, skin }) {
  if (inventory.length === 0) return null;
  return (
    <div style={{
      position: 'absolute', top: 44, right: 0,
      display: 'flex', flexDirection: 'column', gap: 4,
      padding: '8px 6px',
      background: 'rgba(0,0,0,0.5)',
      borderLeft: '1px solid var(--dlg-border)',
      zIndex: 15, maxWidth: 140,
    }}>
      <div style={{fontFamily:'var(--hud-font)',fontSize:7,color:'var(--hud-color)',letterSpacing:'0.2em',textTransform:'uppercase',marginBottom:4}}>Inventory</div>
      {inventory.map(item => (
        <div key={item.id} style={{
          fontFamily:'var(--txt-font)',fontSize:11,
          color:'var(--txt-color)',padding:'4px 8px',
          border:'1px solid var(--dlg-border)',
          background:'var(--dlg-bg)',cursor:'help',
          fontStyle:'italic',
        }} title={item.desc}>{item.name}</div>
      ))}
    </div>
  );
}

// ── Exit button ───────────────────────────────────────────────────────────
function ExitVideoBtn({ skin, onExit }) {
  return (
    <div onClick={onExit} style={{
      position: 'absolute', top: 52, left: 10, zIndex: 40,
      fontFamily: 'var(--hud-font)', fontSize: 8,
      letterSpacing: '0.2em', textTransform: 'uppercase',
      color: 'var(--nav-color)', cursor: 'pointer',
      border: '1px solid rgba(255,255,255,0.08)',
      padding: '3px 8px', background: 'rgba(0,0,0,0.4)',
      transition: 'all 0.15s',
    }}
    onMouseEnter={e=>{e.currentTarget.style.color='var(--accent)';e.currentTarget.style.borderColor='var(--dlg-border)';}}
    onMouseLeave={e=>{e.currentTarget.style.color='var(--nav-color)';e.currentTarget.style.borderColor='rgba(255,255,255,0.08)';}}
    >← Exit</div>
  );
}

// ── Dialogue result overlay ───────────────────────────────────────────────
function VideoDialogue({ state, skin, onDismiss }) {
  const { speaker, displayText, isTyping, waitingForInput } = state;
  if (!displayText) return null;
  return (
    <div style={{
      position: 'absolute', bottom: 0, left: 0, right: 0,
      background: 'var(--dlg-bg)',
      borderTop: '1px solid var(--dlg-border)',
      padding: 'var(--dlg-pad)',
      minHeight: 120, zIndex: 45,
      cursor: waitingForInput ? 'pointer' : 'default',
    }} onClick={() => waitingForInput && onDismiss()}>
      <div style={{position:'absolute',top:0,left:44,right:44,height:1,background:'var(--dlg-rule)'}}></div>
      {speaker && (
        <div style={{fontFamily:'var(--spk-font)',fontSize:'var(--spk-size)',color:'var(--spk-color)',letterSpacing:'var(--spk-tracking)',textTransform:'uppercase',marginBottom:8}}>
          {speaker}
        </div>
      )}
      <div style={{fontFamily:'var(--txt-font)',fontSize:'var(--txt-size)',color:'var(--txt-color)',fontStyle:'var(--txt-style)',lineHeight:'var(--txt-lh)',maxWidth:720}}>
        {displayText}
        {isTyping && <span style={{display:'inline-block',width:8,height:14,background:'var(--cursor)',marginLeft:2,verticalAlign:'middle',animation:'vn-blink 1s steps(1) infinite'}}></span>}
      </div>
      {waitingForInput && (
        <div style={{position:'absolute',bottom:12,right:40,fontFamily:'var(--hud-font)',fontSize:9,color:'var(--nav-color)',letterSpacing:'0.18em',textTransform:'uppercase',animation:'vn-pulse 1.5s ease-in-out infinite'}}>
          ▼ Continue
        </div>
      )}
    </div>
  );
}

// ── Main InteractiveVideo component ───────────────────────────────────────
function InteractiveVideo({ node, skin, state, dispatch, onExit }) {
  const videoRef = useRef(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [hoveredHotspot, setHoveredHotspot] = useState(null);
  const [showVerbPopup, setShowVerbPopup] = useState(false);
  const [selectedVerb, setSelectedVerb] = useState(() => getVerbs(skin)[3]); // default: Look At
  const [inventory, setInventory] = useState(state.inventory || []);
  const [resultMsg, setResultMsg] = useState(null);
  const [dialogResult, setDialogResult] = useState(null); // {speaker, text}
  const [debugMode, setDebugMode] = useState(false);
  const [videoReady, setVideoReady] = useState(false);

  const verbs = getVerbs(skin);
  const isScumm = skin.variant === 'scumm';

  // Start video
  useEffect(() => {
    const v = videoRef.current;
    if (!v || !node.src) return;
    v.loop = node.loop !== false;
    v.muted = true; // required for autoplay
    v.play().catch(() => {});
    const onTime = () => setCurrentTime(v.currentTime);
    const onReady = () => setVideoReady(true);
    v.addEventListener('timeupdate', onTime);
    v.addEventListener('canplay', onReady);
    return () => {
      v.removeEventListener('timeupdate', onTime);
      v.removeEventListener('canplay', onReady);
      v.pause();
    };
  }, [node.src]);

  // Active hotspots for current time
  const activeHotspots = (node.hotspots || []).filter(h => {
    if (h.timeStart != null && currentTime < h.timeStart) return false;
    if (h.timeEnd != null && currentTime > h.timeEnd) return false;
    return true;
  });

  const showResult = (msg) => {
    setResultMsg(msg);
    setTimeout(() => setResultMsg(null), 2800);
  };

  const handleActivate = (hotspot, verb) => {
    const action = hotspot.actions?.[verb];
    if (!action) {
      showResult(`Nothing happens.`);
      return;
    }

    setHoveredHotspot(null);
    setShowVerbPopup(false);

    switch (action.t) {
      case 'narrate':
      case 'say': {
        // Show via typewriter in video dialogue overlay
        const text = action.text || '';
        let idx = 0;
        setDialogResult({ speaker: action.t==='say' ? action.char : null, text: '', isTyping: true, full: text });
        const interval = setInterval(() => {
          idx = Math.min(idx + 2, text.length);
          setDialogResult(d => ({ ...d, text: text.slice(0, idx), isTyping: idx < text.length }));
          if (idx >= text.length) {
            clearInterval(interval);
            setDialogResult(d => ({ ...d, isTyping: false, waitingForInput: true }));
          }
        }, 28);
        break;
      }
      case 'add_item': {
        const item = action.item;
        const hasIt = inventory.some(i => i.id === item.id);
        if (hasIt) {
          showResult(`You already have the ${item.name}.`);
        } else {
          const newInv = [...inventory, item];
          setInventory(newInv);
          dispatch({ type: 'SET_FLAG', key: `has_${item.id}`, val: true });
          showResult(`Picked up: ${item.name}`);
        }
        break;
      }
      case 'jump_scene': {
        if (action.requires && !inventory.some(i => i.id === action.requires)) {
          showResult(action.failText || `You need something for this.`);
          return;
        }
        const nextScene = window.DEMO_SCENES?.[action.scene];
        if (nextScene) { dispatch({ type: 'SET_SCENE', scene: nextScene }); onExit && onExit(); }
        break;
      }
      case 'set_flag':
        dispatch({ type: 'SET_FLAG', key: action.key, val: action.val });
        showResult(action.message || `Done.`);
        break;
      default:
        showResult(`Nothing happens.`);
    }
  };

  const handleHotspotHover = (hotspot) => {
    setHoveredHotspot(hotspot);
    if (!isScumm) setShowVerbPopup(true);
  };

  const handleHotspotLeave = () => {
    if (!isScumm) {
      // Small delay so user can click popup
      setTimeout(() => { setHoveredHotspot(null); setShowVerbPopup(false); }, 200);
    } else {
      setHoveredHotspot(null);
    }
  };

  const videoAreaHeight = isScumm ? 'calc(100% - 200px)' : '100%';

  return (
    <div style={{position:'absolute',inset:0,display:'flex',flexDirection:'column'}}>
      {/* Video area */}
      <div style={{position:'relative',flex:1,overflow:'hidden',background:skin.sceneBg}}>
        {/* Background / video */}
        {node.src ? (
          <video ref={videoRef} src={node.src} style={{position:'absolute',inset:0,width:'100%',height:'100%',objectFit:'cover'}} playsInline />
        ) : (
          <div style={{position:'absolute',inset:0,background:node.bgFallback||skin.bgFallback}}>
            {/* Animated placeholder */}
            <div style={{position:'absolute',inset:0,display:'flex',alignItems:'center',justifyContent:'center',flexDirection:'column',gap:12}}>
              <div style={{fontFamily:'var(--hud-font)',fontSize:9,letterSpacing:'0.3em',color:'var(--hud-color)',textTransform:'uppercase',opacity:0.5}}>
                Video: {node.src || 'no file assigned'}
              </div>
              <div style={{fontFamily:'var(--txt-font)',fontSize:13,color:'var(--txt-color)',opacity:0.3,fontStyle:'italic'}}>
                Drop a .mp4 into assets/video/ and set the src path
              </div>
              <div style={{fontFamily:'var(--hud-font)',fontSize:8,color:'var(--hud-color)',opacity:0.35,letterSpacing:'0.2em',marginTop:8,textTransform:'uppercase'}}>
                Hotspots active — try hovering the highlighted regions
              </div>
            </div>
            {/* Simulated scene elements in placeholder mode */}
            {skin.scanlines && (
              <div style={{position:'absolute',inset:0,background:'repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.12) 2px,rgba(0,0,0,0.12) 4px)',pointerEvents:'none'}}></div>
            )}
          </div>
        )}

        {/* Hotspot regions */}
        {activeHotspots.map(h => (
          <HotspotRegion key={h.id} hotspot={h} skin={skin}
            selectedVerb={selectedVerb} debugMode={debugMode}
            onHover={handleHotspotHover}
            onLeave={handleHotspotLeave}
            onClick={handleActivate} />
        ))}

        {/* Verb popup (non-SCUMM) */}
        {!isScumm && showVerbPopup && hoveredHotspot && (
          <div onMouseEnter={()=>setShowVerbPopup(true)} onMouseLeave={()=>{setShowVerbPopup(false);setHoveredHotspot(null);}}>
            <VerbPopup hotspot={hoveredHotspot} verbs={verbs} selectedVerb={selectedVerb}
              onSelect={(v)=>{ setSelectedVerb(v); handleActivate(hoveredHotspot,v); }}
              skin={skin} />
          </div>
        )}

        {/* Cursor label (non-SCUMM) */}
        {!isScumm && hoveredHotspot && !showVerbPopup && (
          <CursorLabel hotspot={hoveredHotspot} verb={selectedVerb} skin={skin} />
        )}

        {/* Inventory (non-SCUMM) */}
        {!isScumm && <InventoryBar inventory={inventory} skin={skin} />}

        {/* HUD */}
        <div style={{position:'absolute',top:0,left:0,right:0,display:'flex',justifyContent:'space-between',alignItems:'center',padding:'10px 20px',background:'rgba(0,0,0,0.4)',backdropFilter:'blur(4px)',borderBottom:'1px solid var(--dlg-border)',zIndex:20,fontFamily:'var(--hud-font)',fontSize:9,letterSpacing:'0.18em',color:'var(--hud-color)',textTransform:'uppercase'}}>
          <span>{node.id || 'Scene'}</span>
          <div style={{display:'flex',gap:12}}>
            <span onClick={()=>setDebugMode(v=>!v)} style={{cursor:'pointer',opacity:debugMode?1:0.4,transition:'opacity 0.15s'}}>Hotspots {debugMode?'ON':'OFF'}</span>
            <span style={{opacity:0.4}}>{activeHotspots.length} active</span>
          </div>
          <span onClick={onExit} style={{cursor:'pointer',opacity:0.5,transition:'opacity 0.15s'}}
            onMouseEnter={e=>e.currentTarget.style.opacity=1}
            onMouseLeave={e=>e.currentTarget.style.opacity=0.5}>← Exit scene</span>
        </div>

        {/* Result message (non-SCUMM) */}
        {!isScumm && <ResultMsg msg={resultMsg} skin={skin} />}

        {/* Dialogue overlay */}
        {dialogResult && (
          <VideoDialogue
            state={{...dialogResult, displayText: dialogResult.text}}
            skin={skin}
            onDismiss={() => setDialogResult(null)} />
        )}
      </div>

      {/* SCUMM verb strip */}
      {isScumm && (
        <ScummVerbStrip
          verbs={verbs}
          selectedVerb={selectedVerb}
          onSelectVerb={setSelectedVerb}
          hovered={hoveredHotspot}
          skin={skin}
          inventory={inventory}
          resultMsg={resultMsg} />
      )}

      {/* SCUMM dialogue (shows above verb strip) */}
      {isScumm && dialogResult && (
        <div style={{
          position:'absolute',bottom:200,left:0,right:0,
          background:'rgba(0,0,80,0.9)',
          padding:'8px 16px', zIndex:50,
          borderTop:'1px solid rgba(255,255,85,0.2)',
          fontFamily:"'Anonymous Pro',monospace",fontSize:13,
          color:'#ffffff',lineHeight:1.5,
          cursor:dialogResult.waitingForInput?'pointer':'default',
        }} onClick={()=>dialogResult.waitingForInput&&setDialogResult(null)}>
          {dialogResult.speaker && <span style={{color:'#ffff55'}}>{dialogResult.speaker}: </span>}
          {dialogResult.text}
          {dialogResult.isTyping && <span style={{animation:'vn-blink 0.8s steps(1) infinite'}}>_</span>}
        </div>
      )}
    </div>
  );
}

// Register demo scene and export
if (!window.DEMO_SCENES) window.DEMO_SCENES = {};
window.DEMO_SCENES['vol3_video_demo'] = DEMO_VIDEO_SCENE;

Object.assign(window, { InteractiveVideo, DEMO_VIDEO_SCENE, getVerbs, VERB_SETS });
