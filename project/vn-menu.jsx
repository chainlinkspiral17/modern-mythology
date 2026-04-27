// vn-menu.jsx — Main Menu for Modern Mythology
// Exports: MainMenu → window.MainMenu

function MainMenu({ onPlay }) {
  const [hoveredVol, setHoveredVol] = React.useState(null);
  const [screen, setScreen] = React.useState('main'); // 'main' | 'volumes'
  const skin = SKINS.literary;
  const vars = skin.vars;

  const css = {
    '--dlg-bg': vars['--dlg-bg'],
    '--spk-color': vars['--spk-color'],
    '--spk-font': vars['--spk-font'],
    '--txt-color': vars['--txt-color'],
    '--txt-font': vars['--txt-font'],
    '--accent': vars['--accent'],
    '--hud-font': vars['--hud-font'],
    '--nav-color': vars['--nav-color'],
    '--ov-border': vars['--ov-border'],
  };

  const menuStyle = {
    width: '100%', height: '100%',
    background: '#0d0b09',
    position: 'relative', overflow: 'hidden',
    fontFamily: "'IM Fell English', serif",
    ...css,
  };

  const bg = {
    position: 'absolute', inset: 0,
    background: 'radial-gradient(ellipse 80% 100% at 50% 100%,rgba(20,15,5,0.9) 0%,transparent 70%),radial-gradient(ellipse 60% 40% at 20% 20%,rgba(180,140,60,0.05) 0%,transparent 60%),linear-gradient(180deg,#060504 0%,#0d0b09 40%,#12100a 100%)',
  };

  const rule = {
    position: 'absolute', left: '50%', top: '8%', bottom: '8%',
    width: 1,
    background: 'linear-gradient(180deg,transparent,rgba(180,140,60,0.22) 25%,rgba(180,140,60,0.22) 75%,transparent)',
  };

  const MENU_ITEMS = [
    { label: 'Continue', sub: 'Small Wood Volumes · Ch. III', action: () => onPlay(2) },
    { label: 'New Game', action: () => setScreen('volumes') },
    { label: 'Load', action: () => {} },
    { label: 'Gallery', action: () => { window.location.href = 'Gallery.html'; } },
    { label: 'Music Room', action: () => { window.location.href = 'Gallery.html#music'; } },
    { label: 'Settings', action: () => {} },
    { label: 'Scene Editor', sub: 'Dev tool', action: () => { window.location.href = 'Scene Editor.html'; } },
  ];

  const hovered = hoveredVol ? VOLUME_LIST.find(v => v.vol === hoveredVol) : null;

  return (
    <div style={menuStyle}>
      <div style={bg}></div>

      {/* Grain texture overlay */}
      <div style={{
        position:'absolute',inset:0,pointerEvents:'none',
        backgroundImage:"url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E\")",
        mixBlendMode:'overlay',
      }}></div>

      {/* Vertical rule */}
      {screen === 'main' && <div style={rule}></div>}

      {screen === 'main' && (
        <>
          {/* Left panel — title + menu */}
          <div style={{
            position:'absolute',left:0,top:0,bottom:0,width:'50%',
            display:'flex',flexDirection:'column',justifyContent:'center',
            padding:'40px 64px',
          }}>
            <div style={{fontFamily:"'Cinzel',serif",fontSize:9,letterSpacing:'0.35em',color:'rgba(180,140,60,0.4)',textTransform:'uppercase',marginBottom:22}}>
              A Visual Novel Series · Ten Volumes
            </div>
            <div style={{fontFamily:"'IM Fell English',serif",fontSize:58,lineHeight:1.1,color:'#d4c9b0',fontStyle:'italic',marginBottom:10}}>
              Modern<br/>Mythology
            </div>
            <div style={{fontFamily:"'Cinzel',serif",fontSize:9,letterSpacing:'0.28em',color:'rgba(180,140,60,0.38)',textTransform:'uppercase',marginBottom:44}}>
              Ten Volumes · One Story
            </div>
            <div style={{display:'flex',flexDirection:'column',gap:2}}>
              {MENU_ITEMS.map((item, i) => (
                <div key={i}
                  onClick={item.action}
                  style={{
                    display:'flex',alignItems:'baseline',gap:12,
                    padding:'9px 0',
                    borderBottom:'1px solid rgba(180,140,60,0.08)',
                    cursor:'pointer', transition:'all 0.15s',
                  }}
                  onMouseEnter={e => { e.currentTarget.style.paddingLeft='10px'; }}
                  onMouseLeave={e => { e.currentTarget.style.paddingLeft='0'; }}
                >
                  <span style={{color:'rgba(180,140,60,0.35)',fontSize:11}}>›</span>
                  <span style={{fontFamily:"'IM Fell English',serif",fontSize: i===0?17:15,color: i===0?'#d4c9b0':'#a89870',fontStyle:'italic',transition:'color 0.15s'}}>
                    {item.label}
                  </span>
                  {item.sub && <span style={{fontFamily:"'Cinzel',serif",fontSize:8,color:'rgba(180,140,60,0.35)',letterSpacing:'0.12em',textTransform:'uppercase'}}>{item.sub}</span>}
                </div>
              ))}
            </div>
          </div>

          {/* Right panel — volume list */}
          <div style={{
            position:'absolute',right:0,top:0,bottom:0,width:'50%',
            display:'flex',flexDirection:'column',justifyContent:'center',
            padding:'40px 44px 40px 64px',
          }}>
            <div style={{fontFamily:"'Cinzel',serif",fontSize:8,letterSpacing:'0.3em',color:'rgba(180,140,60,0.28)',textTransform:'uppercase',marginBottom:16}}>
              Volumes
            </div>
            {VOLUME_LIST.map(v => (
              <div key={v.vol}
                onMouseEnter={() => setHoveredVol(v.vol)}
                onMouseLeave={() => setHoveredVol(null)}
                onClick={() => v.unlocked && onPlay(v.vol)}
                style={{
                  display:'flex',alignItems:'center',gap:14,
                  padding:'7px 10px',marginBottom:3,
                  border:`1px solid ${hoveredVol===v.vol && v.unlocked ? 'rgba(180,140,60,0.3)' : 'rgba(180,140,60,0.07)'}`,
                  background: hoveredVol===v.vol && v.unlocked ? 'rgba(180,140,60,0.05)' : 'transparent',
                  opacity: v.unlocked ? 1 : 0.35,
                  cursor: v.unlocked ? 'pointer' : 'default',
                  transition:'all 0.15s',
                }}
              >
                <span style={{fontFamily:"'Cinzel',serif",fontSize:8,letterSpacing:'0.1em',color:'rgba(180,140,60,0.38)',minWidth:36}}>
                  Vol. {v.vol < 10 ? `0${v.vol}` : v.vol}
                </span>
                <span style={{fontFamily:"'IM Fell English',serif",fontSize:14,color: hoveredVol===v.vol&&v.unlocked?'#c8b888':'#7a6e54',fontStyle:'italic',flex:1,transition:'color 0.15s'}}>
                  {v.title}
                </span>
                <span style={{fontFamily:"'Cinzel',serif",fontSize:7,letterSpacing:'0.1em',color:'rgba(180,140,60,0.28)',textTransform:'uppercase'}}>
                  {v.progress}
                </span>
                {v.unlocked && hoveredVol===v.vol && (
                  <span style={{fontFamily:"'Cinzel',serif",fontSize:8,color:'rgba(180,140,60,0.5)'}}>›</span>
                )}
              </div>
            ))}
          </div>
        </>
      )}

      {screen === 'volumes' && (
        <div style={{
          position:'absolute',inset:0,
          display:'flex',flexDirection:'column',justifyContent:'center',alignItems:'center',
        }}>
          <div style={{fontFamily:"'Cinzel',serif",fontSize:9,letterSpacing:'0.35em',color:'rgba(180,140,60,0.4)',textTransform:'uppercase',marginBottom:8}}>
            Select a Volume
          </div>
          <div style={{fontFamily:"'IM Fell English',serif",fontSize:28,color:'#d4c9b0',fontStyle:'italic',marginBottom:36}}>
            Where do you begin?
          </div>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,width:700}}>
            {VOLUME_LIST.filter(v=>v.unlocked).map(v => {
              const s = SKINS[v.skin];
              return (
                <div key={v.vol}
                  onClick={() => onPlay(v.vol)}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = s.vars['--accent']; e.currentTarget.style.background = s.vars['--dlg-bg']; }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(180,140,60,0.12)'; e.currentTarget.style.background = 'rgba(0,0,0,0.3)'; }}
                  style={{
                    padding:'18px 22px',border:'1px solid rgba(180,140,60,0.12)',
                    background:'rgba(0,0,0,0.3)',cursor:'pointer',transition:'all 0.2s',
                  }}
                >
                  <div style={{fontFamily:"'Cinzel',serif",fontSize:8,letterSpacing:'0.2em',color: s.vars['--accent'],textTransform:'uppercase',marginBottom:6}}>
                    Vol. {v.vol < 10 ? `0${v.vol}` : v.vol} · {v.subtitle}
                  </div>
                  <div style={{fontFamily:"'IM Fell English',serif",fontSize:18,color:'#d4c9b0',fontStyle:'italic',marginBottom:4}}>
                    {v.title}
                  </div>
                  <div style={{fontFamily:"'Cinzel',serif",fontSize:7,letterSpacing:'0.12em',color:'rgba(180,140,60,0.3)',textTransform:'uppercase'}}>
                    {v.progress} · {v.skin} skin
                  </div>
                </div>
              );
            })}
          </div>
          <div onClick={() => setScreen('main')} style={{
            marginTop:30,fontFamily:"'Cinzel',serif",fontSize:8,letterSpacing:'0.25em',
            color:'rgba(180,140,60,0.4)',textTransform:'uppercase',cursor:'pointer',
            border:'1px solid rgba(180,140,60,0.15)',padding:'8px 20px',transition:'opacity 0.15s',
          }}
          onMouseEnter={e=>e.currentTarget.style.opacity=1}
          onMouseLeave={e=>e.currentTarget.style.opacity=0.6}
          >← Back</div>
        </div>
      )}

      {/* Footer */}
      <div style={{
        position:'absolute',bottom:16,left:0,right:0,
        display:'flex',justifyContent:'center',
        fontFamily:"'Cinzel',serif",fontSize:7,letterSpacing:'0.2em',
        color:'rgba(180,140,60,0.18)',textTransform:'uppercase',
      }}>
        © Modern Mythology · All Rights Reserved · Ver. 0.1 Demo
      </div>
    </div>
  );
}

Object.assign(window, { MainMenu });
