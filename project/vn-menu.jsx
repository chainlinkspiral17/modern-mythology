// vn-menu.jsx — Main Menu for Modern Mythology
// Screens: 'main' → 'volumes' → 'chapters' → game
// Exports: MainMenu → window.MainMenu

// ── Chapter catalog ─────────────────────────────────────────────────────────
// Each volume defines its chapters; unlocked ones are playable.
// Scene ID maps to a key in DEMO_SCENES.

const CHAPTER_CATALOG = {
  1: [
    { ch:0, title:'Title Page & Introduction', sceneId:'vol1_title',                  status:'complete', type:'chapter'   },
    { ch:'—', title:'The Missing Link',         sceneId:'vol1_missing_link',           status:'complete', type:'interlude' },
    { ch:2, title:'Act One — John Faust',      sceneId:'vol1_ch2_act_one',            status:'complete', type:'chapter'   },
    { ch:3, title:'Act One — Judgement Day',   sceneId:'vol1_ch3_judgement_day',      status:'complete', type:'chapter'   },
    { ch:4, title:'Act One — Dream States',    sceneId:'vol1_ch4_dream_states',       status:'complete', type:'chapter'   },
  ],
  2: [
    { ch:0, title:'Title Page & Preface',     sceneId:'vol2_title',                  status:'complete', type:'chapter'   },
    { ch:'—', title:'Briar Falls',            sceneId:'vol2_briar_falls_interlude', status:'complete', type:'interlude' },
    { ch:1, title:'i. A Brief History of Me, Part One', sceneId:'vol2_ch1_history_one', status:'complete', type:'chapter' },
    { ch:2, title:'ii. The Siren of Seagash',            sceneId:'vol2_ch2_seagash',     status:'complete', type:'chapter' },
  ],
  3: [
    { ch:1, title:'Station Omega-14',       sceneId:'vol3_station14',   status:'demo', type:'chapter' },
  ],
  4: [
    { ch:1, title:'The Underpass',          sceneId:'vol4_underpass',   status:'demo', type:'chapter' },
  ],
  5: [
    { ch:'0',  title:'The Fool — Between Acts',                        sceneId:'vol5_ch0_fool',         status:'complete', type:'chapter'   },
    { ch:'I',  title:'The Magician — Cathedral of Rust and Code',      sceneId:'vol5_ch1_magician',     status:'complete', type:'chapter'   },
    { ch:'II', title:'The High Priestess — Exit Through the Gift Shop',sceneId:'vol5_ch2_priestess',    status:'complete', type:'chapter'   },
    { ch:'III',title:'The Empress — Static Bloom',                     sceneId:'vol5_ch3_empress',      status:'complete', type:'chapter'   },
    { ch:'IV', title:'The Emperor — Thicker Than Water, Slower Than Time', sceneId:'vol5_ch4_emperor', status:'stub', type:'chapter'   },
    { ch:'V',  title:'The Hierophant — Sweaty Sunday Sermonettes',     sceneId:'vol5_ch5_hierophant',   status:'stub', type:'chapter'   },
    { ch:'VI', title:'The Lovers — Sanctuary on Cursed Ground',        sceneId:'vol5_ch6_lovers',       status:'stub', type:'chapter'   },
    { ch:'VII',title:'The Chariot — Two Horses, One Wreck',            sceneId:'vol5_ch7_chariot',      status:'stub', type:'chapter'   },
    { ch:'VIII',title:'Strength — The Ouroboros in the Ashtray',       sceneId:'vol5_ch8_strength',     status:'stub', type:'chapter'   },
    { ch:'IX', title:'The Hermit — Labyrinth of Scrawled Echoes',      sceneId:'vol5_ch9_hermit',       status:'stub', type:'chapter'   },
    { ch:'X',  title:'Wheel of Fortune — Closing Arguments Against Chaos', sceneId:'vol5_ch10_wheel',  status:'stub', type:'chapter'   },
    { ch:'XI', title:'Justice — Scales Already Shattered',             sceneId:'vol5_ch11_justice',     status:'stub', type:'chapter'   },
    { ch:'XII',title:'The Hanged Man — Gravity is Optional After Midnight', sceneId:'vol5_ch12_hanged', status:'stub', type:'chapter'  },
    { ch:'XIII',title:'Death — Walpurgisnacht in Ward C',              sceneId:'vol5_ch13_death',       status:'stub', type:'chapter'   },
    { ch:'XIV',title:'Temperance — The Moderate Temperature of Tuesday', sceneId:'vol5_ch14_temperance',status:'stub', type:'chapter'  },
    { ch:'XV', title:'The Devil — Gumbo Limbo',                        sceneId:'vol5_ch15_devil',       status:'stub', type:'chapter'   },
    { ch:'XVI',title:'The Tower — Evangeline in Render Queue',         sceneId:'vol5_ch16_tower',       status:'stub', type:'chapter'   },
    { ch:'XVII',title:'The Star — Glass Skin and Obsidian Ink',        sceneId:'vol5_ch17_star',        status:'stub', type:'chapter'   },
    { ch:'XVIII',title:'The Moon — Sigils in Static',                  sceneId:'vol5_ch18_moon',        status:'stub', type:'chapter'   },
    { ch:'XIX',title:'The Sun — Pattern Recognition in Dust Motes',    sceneId:'vol5_ch19_sun',         status:'stub', type:'chapter'   },
    { ch:'XX', title:'Judgement — The Stillness Breaks / The Sound Arrives', sceneId:'vol5_ch20_judgement', status:'stub', type:'chapter' },
    { ch:'XXI',title:'The World — Frog Knows Best, Mostly',            sceneId:'vol5_ch21_world',       status:'stub', type:'chapter'   },
  ],
  6: [
    { ch:1,  title:'Heat Haze & Humming Power Lines',  sceneId:'vol6_ch1_kwikstop',    status:'complete', type:'chapter' },
    { ch:2,  title:'Gas Station Oracles & Slushie Futures',  sceneId:'vol6_ch2_gas_oracles',  status:'complete', type:'chapter' },
    { ch:3,  title:'Last Seen at the Circle K (Or Was It?)',  sceneId:'vol6_ch3_circle_k',  status:'complete', type:'chapter' },
    { ch:4,  title:'Coming',  sceneId:'vol6_ch4_stub',  status:'stub', type:'chapter' },
    { ch:5,  title:'Coming',  sceneId:'vol6_ch5_stub',  status:'stub', type:'chapter' },
    { ch:6,  title:'Coming',  sceneId:'vol6_ch6_stub',  status:'stub', type:'chapter' },
    { ch:7,  title:'Coming',  sceneId:'vol6_ch7_stub',  status:'stub', type:'chapter' },
    { ch:8,  title:'Coming',  sceneId:'vol6_ch8_stub',  status:'stub', type:'chapter' },
    { ch:9,  title:'Coming',  sceneId:'vol6_ch9_stub',  status:'stub', type:'chapter' },
    { ch:10, title:'Coming',  sceneId:'vol6_ch10_stub', status:'stub', type:'chapter' },
    { ch:11, title:'Coming',  sceneId:'vol6_ch11_stub', status:'stub', type:'chapter' },
    { ch:12, title:'Coming',  sceneId:'vol6_ch12_stub', status:'stub', type:'chapter' },
    { ch:13, title:'Coming',  sceneId:'vol6_ch13_stub', status:'stub', type:'chapter' },
    { ch:14, title:'Coming',  sceneId:'vol6_ch14_stub', status:'stub', type:'chapter' },
    { ch:15, title:'Coming',  sceneId:'vol6_ch15_stub', status:'stub', type:'chapter' },
    { ch:16, title:'Coming',  sceneId:'vol6_ch16_stub', status:'stub', type:'chapter' },
    { ch:17, title:'Coming',  sceneId:'vol6_ch17_stub', status:'stub', type:'chapter' },
    { ch:18, title:'Coming',  sceneId:'vol6_ch18_stub', status:'stub', type:'chapter' },
    { ch:19, title:'Coming',  sceneId:'vol6_ch19_stub', status:'stub', type:'chapter' },
    { ch:20, title:'Coming',  sceneId:'vol6_ch20_stub', status:'stub', type:'chapter' },
    { ch:21, title:'Coming',  sceneId:'vol6_ch21_stub', status:'stub', type:'chapter' },
    { ch:22, title:'Coming',  sceneId:'vol6_ch22_stub', status:'stub', type:'chapter' },
    { ch:23, title:'Coming',  sceneId:'vol6_ch23_stub', status:'stub', type:'chapter' },
  ],
  7: [
    { ch:1,  title:'Smolvud',                sceneId:'vol7_ch1_smolvud',   status:'stub',     type:'chapter'   },
    { ch:2,  title:'The Daily Grind',        sceneId:'vol7_ch2_stub',      status:'stub',     type:'chapter'   },
    { ch:3,  title:'Board Lords',            sceneId:'vol7_ch3_stub',      status:'stub',     type:'chapter'   },
    { ch:4,  title:'The Cabin',              sceneId:'vol7_ch4_stub',      status:'stub',     type:'chapter'   },
    { ch:5,  title:"Brandon's Things",       sceneId:'vol7_ch5_stub',      status:'stub',     type:'chapter'   },
    { ch:6,  title:'Cale',                   sceneId:'vol7_ch6_cale_opening', status:'complete', type:'chapter' },
    { ch:7,  title:'Six O\'Clock',           sceneId:'vol7_ch8_six_oclock',status:'complete', type:'chapter'   },
    { ch:'—', title:'After Six',             sceneId:'vol7_int_after_six', status:'stub',     type:'interlude' },
    { ch:8,  title:'The Cabin at Noon',      sceneId:'vol7_ch9_stub',      status:'stub',     type:'chapter'   },
    { ch:9,  title:'Cale Comes Up',          sceneId:'vol7_ch10_stub',     status:'stub',     type:'chapter'   },
    { ch:'—', title:'The Estuary 7',         sceneId:'vol7_int_estuary7',  status:'stub',     type:'interlude' },
    { ch:10, title:'The Sixth Floor',        sceneId:'vol7_ch11_stub',     status:'stub',     type:'chapter'   },
    { ch:11, title:'Pattern Persistence',    sceneId:'vol7_ch12_stub',     status:'stub',     type:'chapter'   },
    { ch:12, title:'The Estuary 7',          sceneId:'vol7_ch13_stub',     status:'stub',     type:'chapter'   },
    { ch:13, title:"What Brandon Left",      sceneId:'vol7_ch14_stub',     status:'stub',     type:'chapter'   },
    { ch:'—', title:'The Crow',              sceneId:'vol7_int_the_crow',  status:'stub',     type:'interlude' },
    { ch:14, title:'The Wood at Midnight',   sceneId:'vol7_ch15_stub',     status:'stub',     type:'chapter'   },
    { ch:15, title:'Monday',                 sceneId:'vol7_ch16_stub',     status:'stub',     type:'chapter'   },
    { ch:16, title:'The Bench',              sceneId:'vol7_ch17_stub',     status:'stub',     type:'chapter'   },
    { ch:17, title:'Roy Again',              sceneId:'vol7_ch18_stub',     status:'stub',     type:'chapter'   },
    { ch:'—', title:'Roy',                   sceneId:'vol7_int_roy',       status:'stub',     type:'interlude' },
    { ch:18, title:'The Painting',           sceneId:'vol7_ch19_stub',     status:'stub',     type:'chapter'   },
    { ch:19, title:'Jorgen',                 sceneId:'vol7_ch20_stub',     status:'stub',     type:'chapter'   },
    { ch:20, title:'The Substrate',          sceneId:'vol7_ch21_stub',     status:'stub',     type:'chapter'   },
    { ch:21, title:"What the Crow Knows",    sceneId:'vol7_ch22_stub',     status:'stub',     type:'chapter'   },
    { ch:'—', title:'End',                   sceneId:'vol7_int_end',       status:'stub',     type:'interlude' },
    { ch:22, title:'Land of Milk & Honey',   sceneId:'vol7_ch23_stub',     status:'stub',     type:'chapter'   },
  ],
  8:  [],
  9:  [],
  10: [],
};

// ── Chapter Select Screen ──────────────────────────────────────────────────
function ChapterSelect({ vol, onPlay, onBack }) {
  const [hovered, setHovered] = React.useState(null);
  const v = VOLUME_LIST.find(x => x.vol === vol);
  const skin = SKINS[v?.skin] || SKINS.literary;
  const chapters = CHAPTER_CATALOG[vol] || [];
  const accent = skin.vars['--accent'] || 'rgba(220,180,90,0.8)';
  const accentBorder = skin.vars['--accent-border'] || 'rgba(220,180,90,0.4)';

  const canPlay = (ch) => {
    if (ch.status === 'complete' || ch.status === 'demo') return true;
    return false;
  };

  return (
    <div style={{
      position:'absolute', inset:0,
      background: skin.sceneBg || '#0d0b09',
      display:'flex', flexDirection:'column',
      fontFamily:"'IM Fell English',serif",
    }}>
      {/* Gradient overlay */}
      <div style={{position:'absolute',inset:0,background:skin.bgFallback,opacity:0.6,pointerEvents:'none'}}></div>

      {/* Header */}
      <div style={{
        position:'relative', zIndex:2,
        padding:'32px 60px 24px',
        borderBottom:`1px solid ${accentBorder}44`,
        display:'flex', alignItems:'flex-end', gap:24,
      }}>
        <div>
          <div style={{fontFamily:"'Cinzel',serif",fontSize:12,letterSpacing:'0.3em',color:`${accent}88`,textTransform:'uppercase',marginBottom:8}}>
            Vol. {vol < 10 ? `0${vol}` : vol} · {v?.subtitle}
          </div>
          <div style={{fontSize:38,lineHeight:1.1,color:'#d4c9b0',fontStyle:'italic'}}>
            {v?.title}
          </div>
        </div>
        <div style={{marginLeft:'auto',display:'flex',gap:12,alignItems:'center',paddingBottom:4}}>
          <div onClick={onBack} style={{
            fontFamily:"'Cinzel',serif",fontSize:12,letterSpacing:'0.22em',
            color:`${accent}55`,textTransform:'uppercase',cursor:'pointer',
            border:`1px solid ${accent}22`,padding:'6px 16px',transition:'all 0.15s',
          }}
          onMouseEnter={e=>{e.currentTarget.style.color=accent;e.currentTarget.style.borderColor=accentBorder;}}
          onMouseLeave={e=>{e.currentTarget.style.color=`${accent}55`;e.currentTarget.style.borderColor=`${accent}22`;}}
          >← Back</div>
        </div>
      </div>

      {/* Chapter list */}
      <div style={{
        position:'relative', zIndex:2,
        flex:1, overflowY:'auto',
        padding:'24px 60px 40px',
        display:'flex', flexDirection:'column', gap:3,
      }}>
        {chapters.length === 0 && (
          <div style={{
            fontFamily:"'Cinzel',serif",fontSize:13,letterSpacing:'0.25em',
            color:`${accent}35`,textTransform:'uppercase',
            textAlign:'center',marginTop:80,
          }}>
            No chapters yet
          </div>
        )}

        {chapters.map((ch, i) => {
          const playable = canPlay(ch);
          const isHovered = hovered === i;
          const isInterlude = ch.type === 'interlude';

          return (
            <div key={i}
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
              onClick={() => playable && onPlay(vol, ch.sceneId)}
              style={{
                display:'flex', alignItems:'center', gap:20,
                padding: isInterlude ? '6px 16px' : '10px 16px',
                border:`1px solid ${isHovered && playable ? accentBorder : 'rgba(220,180,90,0.07)'}`,
                background: isHovered && playable ? skin.vars['--dlg-bg'] : 'transparent',
                cursor: playable ? 'pointer' : 'default',
                opacity: !playable ? 0.38 : 1,
                transition:'all 0.12s',
                marginLeft: isInterlude ? 40 : 0,
                marginRight: isInterlude ? 40 : 0,
              }}
            >
              {/* Chapter number */}
              <div style={{
                fontFamily:"'Cinzel',serif",
                fontSize: isInterlude ? 11 : 13,
                letterSpacing:'0.15em',
                color: isInterlude ? `${accent}40` : `${accent}60`,
                textTransform:'uppercase',
                minWidth: isInterlude ? 60 : 60,
                textAlign:'right',
              }}>
                {isInterlude ? '✦' : `Ch. ${ch.ch < 10 ? `0${ch.ch}` : ch.ch}`}
              </div>

              {/* Divider */}
              <div style={{width:1,height: isInterlude?12:20,background:`${accent}20`,flexShrink:0}}></div>

              {/* Title */}
              <div style={{
                fontFamily:"'IM Fell English',serif",
                fontSize: isInterlude ? 17 : 21,
                color: isHovered && playable ? '#d4c9b0' : isInterlude ? `${accent}55` : '#a89870',
                fontStyle: isInterlude ? 'normal' : 'italic',
                flex:1,
                transition:'color 0.12s',
              }}>
                {ch.title}
              </div>

              {/* Status badge */}
              <div style={{
                fontFamily:"'Cinzel',serif",
                fontSize:11,letterSpacing:'0.12em',textTransform:'uppercase',
                color: ch.status === 'complete' ? `${accent}80`
                     : ch.status === 'demo' ? `${accent}60`
                     : 'rgba(220,180,90,0.2)',
                border:`1px solid ${
                  ch.status === 'complete' ? `${accent}30`
                  : ch.status === 'demo' ? `${accent}20`
                  : 'rgba(220,180,90,0.08)'}`,
                padding:'2px 8px',
              }}>
                {ch.status === 'complete' ? 'Written'
                : ch.status === 'demo' ? 'Demo'
                : ch.status === 'stub' ? 'Coming'
                : ch.status}
              </div>

              {/* Play arrow */}
              {playable && isHovered && (
                <div style={{color:accent,fontSize:15,marginLeft:4}}>›</div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div style={{
        position:'relative',zIndex:2,
        padding:'12px 60px',
        borderTop:`1px solid ${accentBorder}22`,
        display:'flex',justifyContent:'space-between',alignItems:'center',
      }}>
        <span style={{fontFamily:"'Cinzel',serif",fontSize:11,letterSpacing:'0.2em',color:`${accent}25`,textTransform:'uppercase'}}>
          {chapters.filter(c=>c.status==='complete'||c.status==='demo').length} / {chapters.filter(c=>c.type==='chapter').length} chapters written
        </span>
        <span style={{fontFamily:"'Cinzel',serif",fontSize:11,letterSpacing:'0.2em',color:`${accent}20`,textTransform:'uppercase'}}>
          Modern Mythology · {v?.title}
        </span>
      </div>
    </div>
  );
}

// ── Main Menu ───────────────────────────────────────────────────────────────
function MainMenu({ onPlay: onPlayScene }) {
  const [hoveredVol, setHoveredVol] = React.useState(null);
  const [screen, setScreen] = React.useState('main'); // 'main' | 'volumes' | 'chapters'
  const [selectedVol, setSelectedVol] = React.useState(null);
  const [settingsOpen, setSettingsOpen] = React.useState(false);

  const onPlay = (vol, sceneId) => onPlayScene(vol, sceneId || null);

  const skin = SKINS.literary;
  const vars = skin.vars;
  const css = {
    '--dlg-bg': vars['--dlg-bg'],
    '--spk-color': vars['--spk-color'],
    '--txt-color': vars['--txt-color'],
    '--accent': vars['--accent'],
    '--hud-font': vars['--hud-font'],
    '--nav-color': vars['--nav-color'],
    '--ov-border': vars['--ov-border'],
  };

  const menuStyle = {
    width:'100%', height:'100%',
    background:'#0d0b09',
    position:'relative', overflow:'hidden',
    fontFamily:"'IM Fell English',serif",
    ...css,
  };

  const bg = {
    position:'absolute', inset:0,
    background:'radial-gradient(ellipse 80% 100% at 50% 100%,rgba(20,15,5,0.9) 0%,transparent 70%),radial-gradient(ellipse 60% 40% at 20% 20%,rgba(220,180,90,0.05) 0%,transparent 60%),linear-gradient(180deg,#060504 0%,#0d0b09 40%,#12100a 100%)',
  };

  const rule = {
    position:'absolute', left:'50%', top:'8%', bottom:'8%',
    width:1,
    background:'linear-gradient(180deg,transparent,rgba(220,180,90,0.22) 25%,rgba(220,180,90,0.22) 75%,transparent)',
  };

  const MENU_ITEMS = [
    { label:'Continue',    sub:'Land of Milk & Honey · Ch. VII', action:()=> onPlay(7, 'vol7_ch8_six_oclock') },
    { label:'New Game',    action:()=>setScreen('volumes') },
    { label:'Load',        action:()=>{} },
    { label:'Gallery',     action:()=>{ window.location.href='Gallery.html'; } },
    { label:'Music Room',  action:()=>{ window.location.href='Gallery.html#music'; } },
    { label:'Settings',    action:()=>setSettingsOpen(true) },
    { label:'Scene Editor',sub:'Dev tool', action:()=>{ window.location.href='Scene Editor.html'; } },
  ];

  const openVol = (vol) => {
    setSelectedVol(vol);
    setScreen('chapters');
  };

  return (
    <div style={menuStyle}>
      <div style={bg}></div>

      {/* Grain */}
      <div style={{position:'absolute',inset:0,pointerEvents:'none',backgroundImage:"url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E\")",mixBlendMode:'overlay'}}></div>

      {/* Chapter select overlay */}
      {screen === 'chapters' && selectedVol && (
        <ChapterSelect
          vol={selectedVol}
          onPlay={onPlay}
          onBack={()=>setScreen('volumes')}
        />
      )}

      {/* Volume picker overlay */}
      {screen === 'volumes' && (
        <div style={{position:'absolute',inset:0,display:'flex',flexDirection:'column',justifyContent:'center',alignItems:'center'}}>
          <div style={{fontFamily:"'Cinzel',serif",fontSize:13,letterSpacing:'0.35em',color:'rgba(220,180,90,0.4)',textTransform:'uppercase',marginBottom:8}}>Select a Volume</div>
          <div style={{fontFamily:"'IM Fell English',serif",fontSize:28,color:'#d4c9b0',fontStyle:'italic',marginBottom:36}}>Where do you begin?</div>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,width:700}}>
            {VOLUME_LIST.filter(v=>v.unlocked).map(v => {
              const s = SKINS[v.skin];
              const accent = s?.vars['--accent'] || 'rgba(220,180,90,0.7)';
              return (
                <div key={v.vol}
                  onClick={() => openVol(v.vol)}
                  onMouseEnter={e=>{e.currentTarget.style.borderColor=accent;e.currentTarget.style.background=s?.vars['--dlg-bg']||'rgba(0,0,0,0.4)';}}
                  onMouseLeave={e=>{e.currentTarget.style.borderColor='rgba(220,180,90,0.12)';e.currentTarget.style.background='rgba(0,0,0,0.3)';}}
                  style={{padding:'18px 22px',border:'1px solid rgba(220,180,90,0.12)',background:'rgba(0,0,0,0.3)',cursor:'pointer',transition:'all 0.2s'}}
                >
                  <div style={{fontFamily:"'Cinzel',serif",fontSize:12,letterSpacing:'0.2em',color:accent,textTransform:'uppercase',marginBottom:6}}>
                    Vol. {v.vol < 10 ? `0${v.vol}` : v.vol} · {v.subtitle}
                  </div>
                  <div style={{fontFamily:"'IM Fell English',serif",fontSize:22,color:'#d4c9b0',fontStyle:'italic',marginBottom:6}}>{v.title}</div>
                  <div style={{fontFamily:"'Cinzel',serif",fontSize:11,letterSpacing:'0.12em',color:'rgba(220,180,90,0.3)',textTransform:'uppercase'}}>
                    {(CHAPTER_CATALOG[v.vol]||[]).filter(c=>c.status==='complete'||c.status==='demo').length} chapters written · Select chapter →
                  </div>
                </div>
              );
            })}
          </div>
          <div onClick={()=>setScreen('main')} style={{marginTop:30,fontFamily:"'Cinzel',serif",fontSize:12,letterSpacing:'0.25em',color:'rgba(220,180,90,0.4)',textTransform:'uppercase',cursor:'pointer',border:'1px solid rgba(220,180,90,0.15)',padding:'8px 20px'}}
          onMouseEnter={e=>e.currentTarget.style.opacity=1} onMouseLeave={e=>e.currentTarget.style.opacity=0.6}>← Back</div>
        </div>
      )}

      {/* Main menu */}
      {screen === 'main' && <>
        <div style={rule}></div>
        {/* Left: title + menu */}
        <div style={{position:'absolute',left:0,top:0,bottom:0,width:'50%',display:'flex',flexDirection:'column',justifyContent:'center',padding:'40px 64px'}}>
          <div style={{fontFamily:"'Cinzel',serif",fontSize:13,letterSpacing:'0.35em',color:'rgba(220,180,90,0.4)',textTransform:'uppercase',marginBottom:22}}>A Visual Novel Series · Ten Volumes</div>
          <div style={{fontFamily:"'IM Fell English',serif",fontSize:58,lineHeight:1.1,color:'#d4c9b0',fontStyle:'italic',marginBottom:10}}>Modern<br/>Mythology</div>
          <div style={{fontFamily:"'Cinzel',serif",fontSize:13,letterSpacing:'0.28em',color:'rgba(220,180,90,0.38)',textTransform:'uppercase',marginBottom:44}}>Ten Volumes · One Story</div>
          <div style={{display:'flex',flexDirection:'column',gap:2}}>
            {MENU_ITEMS.map((item,i)=>(
              <div key={i} onClick={item.action} style={{display:'flex',alignItems:'baseline',gap:12,padding:'9px 0',borderBottom:'1px solid rgba(220,180,90,0.08)',cursor:'pointer',transition:'all 0.15s'}}
                onMouseEnter={e=>e.currentTarget.style.paddingLeft='10px'}
                onMouseLeave={e=>e.currentTarget.style.paddingLeft='0'}>
                <span style={{color:'rgba(220,180,90,0.35)',fontSize:11}}>›</span>
                <span style={{fontFamily:"'IM Fell English',serif",fontSize:i===0?21:18,color:i===0?'#d4c9b0':'#c4b78c',fontStyle:'italic',transition:'color 0.15s'}}>{item.label}</span>
                {item.sub&&<span style={{fontFamily:"'Cinzel',serif",fontSize:12,color:'rgba(220,180,90,0.35)',letterSpacing:'0.12em',textTransform:'uppercase'}}>{item.sub}</span>}
              </div>
            ))}
          </div>
        </div>
        {/* Right: volume list */}
        <div style={{position:'absolute',right:0,top:0,bottom:0,width:'50%',display:'flex',flexDirection:'column',justifyContent:'center',padding:'40px 44px 40px 64px'}}>
          <div style={{fontFamily:"'Cinzel',serif",fontSize:12,letterSpacing:'0.3em',color:'rgba(220,180,90,0.28)',textTransform:'uppercase',marginBottom:16}}>Volumes</div>
          {VOLUME_LIST.map(v=>(
            <div key={v.vol}
              onMouseEnter={()=>setHoveredVol(v.vol)}
              onMouseLeave={()=>setHoveredVol(null)}
              onClick={()=>v.unlocked && openVol(v.vol)}
              style={{display:'flex',alignItems:'center',gap:14,padding:'7px 10px',marginBottom:3,border:`1px solid ${hoveredVol===v.vol&&v.unlocked?'rgba(220,180,90,0.3)':'rgba(220,180,90,0.07)'}`,background:hoveredVol===v.vol&&v.unlocked?'rgba(220,180,90,0.05)':'transparent',opacity:v.unlocked?1:0.35,cursor:v.unlocked?'pointer':'default',transition:'all 0.15s'}}>
              <span style={{fontFamily:"'Cinzel',serif",fontSize:12,letterSpacing:'0.1em',color:'rgba(220,180,90,0.38)',minWidth:36}}>Vol. {v.vol<10?`0${v.vol}`:v.vol}</span>
              <span style={{fontFamily:"'IM Fell English',serif",fontSize:17,color:hoveredVol===v.vol&&v.unlocked?'#c8b888':'#9c8d68',fontStyle:'italic',flex:1,transition:'color 0.15s'}}>{v.title}</span>
              <span style={{fontFamily:"'Cinzel',serif",fontSize:11,letterSpacing:'0.1em',color:'rgba(220,180,90,0.28)',textTransform:'uppercase'}}>{v.progress}</span>
              {v.unlocked&&hoveredVol===v.vol&&<span style={{fontFamily:"'Cinzel',serif",fontSize:12,color:'rgba(220,180,90,0.5)'}}>›</span>}
            </div>
          ))}
        </div>
      </>}

      {/* Footer */}
      <div style={{position:'absolute',bottom:16,left:0,right:0,display:'flex',justifyContent:'center',fontFamily:"'Cinzel',serif",fontSize:11,letterSpacing:'0.2em',color:'rgba(220,180,90,0.18)',textTransform:'uppercase'}}>
        © Modern Mythology · All Rights Reserved · Ver. 0.1 Demo
      </div>

      {/* Settings overlay */}
      {settingsOpen && (typeof SettingsPanel !== 'undefined') && (
        <SettingsPanel onClose={() => setSettingsOpen(false)} />
      )}
    </div>
  );
}

Object.assign(window, { MainMenu, CHAPTER_CATALOG });
