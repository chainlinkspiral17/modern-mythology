// vn-skins.jsx — Per-volume visual skin definitions for Modern Mythology
// Each skin provides CSS custom-property vars + a config object.
// Export: VOLUME_LIST, SKINS, getSkin, SkinCtx, useSkin

const VOLUME_LIST = [
  { vol: 1,  title: 'Modern Mythology',        subtitle: 'Prologue',   skin: 'literary',  unlocked: true,  progress: 'Chapter I'    },
  { vol: 2,  title: 'Small Wood Volumes',       subtitle: 'Volume II',  skin: 'literary',  unlocked: true,  progress: 'Chapter III'  },
  { vol: 3,  title: 'The Earthman Chronicles',  subtitle: 'Volume III', skin: 'signal',    unlocked: true,  progress: 'Unlocked'     },
  { vol: 4,  title: '#/Sharp',                  subtitle: 'Volume IV',  skin: 'zine',      unlocked: true,  progress: 'Unlocked'     },
  { vol: 5,  title: 'Major Arcana',             subtitle: 'Volume V',   skin: 'arcana',    unlocked: true,  progress: 'Chapter I'    },
  { vol: 6,  title: 'Planned Community',        subtitle: 'Volume VI',  skin: 'suburban',  unlocked: true,  progress: 'Chapter I'    },
  { vol: 7,  title: 'Land of Milk & Honey',     subtitle: 'Volume VII', skin: 'pastoral',  unlocked: true,  progress: 'Chapter VIII' },
  { vol: 8,  title: 'SCUMM',                    subtitle: 'Volume VIII',skin: 'scumm',     unlocked: false, progress: 'Locked'       },
  { vol: 9,  title: 'Por Puesto',               subtitle: 'Volume IX',  skin: 'caliente',  unlocked: false, progress: 'Locked'       },
  { vol: 10, title: 'ROFLcopter',               subtitle: 'Volume X',   skin: 'glitch',    unlocked: false, progress: 'Locked'       },
];

const SKINS = {

  literary: {
    id: 'literary', variant: 'standard',
    sceneBg: '#0d0b09',
    bgFallback: 'radial-gradient(ellipse 80% 60% at 30% 40%,#1a1208 0%,transparent 70%),radial-gradient(ellipse 60% 80% at 75% 20%,#120a18 0%,transparent 60%),linear-gradient(160deg,#0d0b09 0%,#16100a 50%,#0a0d12 100%)',
    vars: {
      '--dlg-bg':'rgba(10,8,5,0.97)','--dlg-border':'rgba(180,140,60,0.35)',
      '--dlg-rule':'linear-gradient(90deg,transparent,rgba(180,140,60,0.6),rgba(220,180,80,0.8),rgba(180,140,60,0.6),transparent)',
      '--dlg-min-h':'210px','--dlg-pad':'28px 44px 24px',
      '--spk-color':'#c8a84a','--spk-font':"'Cinzel',serif",'--spk-size':'11px','--spk-tracking':'0.22em','--spk-style':'normal',
      '--txt-color':'#d4c9b0','--txt-font':"'IM Fell English',serif",'--txt-size':'18px','--txt-style':'italic','--txt-weight':'400','--txt-lh':'1.72',
      '--ch-border':'rgba(180,140,60,0.2)','--ch-bg':'rgba(180,140,60,0.05)','--ch-hborder':'rgba(180,140,60,0.5)','--ch-hbg':'rgba(180,140,60,0.1)',
      '--ch-color':'#b8a882','--ch-hcolor':'#d4c9b0','--ch-font':"'IM Fell English',serif",'--ch-size':'15px',
      '--hud-color':'rgba(180,140,60,0.45)','--hud-font':"'Cinzel',serif",
      '--cursor':'#c8a84a','--nav-color':'rgba(180,140,60,0.35)',
      '--ov-bg':'rgba(6,4,2,0.97)','--ov-border':'rgba(180,140,60,0.2)','--ov-txt':'#d4c9b0',
      '--accent':'#c8a84a','--accent2':'#8a6832','--scene-bg':'#0d0b09',
    },
    hud: { tag: true, skills: ['Empathy','Logic','Composure','Rhetoric'] },
    charGradient: 'linear-gradient(180deg,#1c1208 0%,#0d0b09 100%)',
    glowColor: 'rgba(200,168,74,0.12)',
  },

  signal: {
    id: 'signal', variant: 'terminal',
    sceneBg: '#060810',
    bgFallback: 'radial-gradient(ellipse 100% 60% at 50% 100%,rgba(20,40,80,0.6) 0%,transparent 60%),linear-gradient(180deg,#060810 0%,#080c18 60%,#060810 100%)',
    vars: {
      '--dlg-bg':'rgba(6,8,16,0.97)','--dlg-border':'rgba(0,180,255,0.25)',
      '--dlg-rule':'linear-gradient(90deg,transparent,rgba(0,180,255,0.5),rgba(100,80,255,0.3),transparent)',
      '--dlg-min-h':'220px','--dlg-pad':'20px 40px 20px',
      '--spk-color':'rgba(0,200,255,0.85)','--spk-font':"'Space Mono',monospace",'--spk-size':'11px','--spk-tracking':'0.15em','--spk-style':'normal',
      '--txt-color':'rgba(200,215,240,0.85)','--txt-font':"'Space Mono',monospace",'--txt-size':'13px','--txt-style':'normal','--txt-weight':'400','--txt-lh':'1.75',
      '--ch-border':'rgba(0,180,255,0.12)','--ch-bg':'rgba(0,180,255,0.04)','--ch-hborder':'rgba(0,180,255,0.35)','--ch-hbg':'rgba(0,180,255,0.08)',
      '--ch-color':'rgba(160,180,220,0.7)','--ch-hcolor':'rgba(0,200,255,0.9)','--ch-font':"'Space Mono',monospace",'--ch-size':'11px',
      '--hud-color':'rgba(0,180,255,0.35)','--hud-font':"'Space Mono',monospace",
      '--cursor':'rgba(0,200,255,0.7)','--nav-color':'rgba(0,180,255,0.3)',
      '--ov-bg':'rgba(4,6,14,0.97)','--ov-border':'rgba(0,180,255,0.15)','--ov-txt':'rgba(200,215,240,0.85)',
      '--accent':'rgba(0,200,255,0.85)','--accent2':'rgba(100,80,255,0.7)','--scene-bg':'#060810',
    },
    hud: { tag: true, meters: ['Trust','Fear','Signal'], meterCols: ['rgba(0,200,255,.7)','rgba(255,80,80,.7)','rgba(100,80,255,.7)'], rels: true },
    charGradient: 'linear-gradient(180deg,#0c1020 0%,#060810 100%)',
    glowColor: 'rgba(0,180,255,0.1)',
    scanlines: true,
  },

  zine: {
    id: 'zine', variant: 'paper',
    sceneBg: '#0a0a0a',
    bgFallback: 'radial-gradient(ellipse 60% 50% at 70% 20%,rgba(255,45,0,0.12) 0%,transparent 60%),linear-gradient(180deg,#0a0a0a,#141414)',
    vars: {
      '--dlg-bg':'#f0ebe0','--dlg-border':'transparent',
      '--dlg-rule':'none','--dlg-min-h':'240px','--dlg-pad':'24px 36px',
      '--spk-color':'#0a0a0a','--spk-font':"'Bebas Neue',sans-serif",'--spk-size':'28px','--spk-tracking':'0.08em','--spk-style':'normal',
      '--txt-color':'#1a1a1a','--txt-font':"'Special Elite',serif",'--txt-size':'15px','--txt-style':'normal','--txt-weight':'400','--txt-lh':'1.65',
      '--ch-border':'transparent','--ch-bg':'#0a0a0a','--ch-hborder':'transparent','--ch-hbg':'#ff2d00',
      '--ch-color':'#f0ebe0','--ch-hcolor':'#f0ebe0','--ch-font':"'Bebas Neue',sans-serif",'--ch-size':'13px',
      '--hud-color':'rgba(255,255,255,0.5)','--hud-font':"'Bebas Neue',sans-serif",
      '--cursor':'#ff2d00','--nav-color':'rgba(15,15,15,0.5)',
      '--ov-bg':'rgba(5,5,5,0.97)','--ov-border':'rgba(255,45,0,0.25)','--ov-txt':'#f0ebe0',
      '--accent':'#ff2d00','--accent2':'#0a0a0a','--scene-bg':'#0a0a0a',
    },
    hud: { tag: true, stats: ['Heat','Rep','Cash'] },
    charGradient: 'linear-gradient(180deg,#1a1a1a 0%,#0a0a0a 100%)',
    glowColor: 'rgba(255,45,0,0.08)',
    halftone: true,
  },

  arcana: {
    id: 'arcana', variant: 'standard',
    sceneBg: '#0a0610',
    bgFallback: 'radial-gradient(ellipse 80% 60% at 50% 70%,#1a0a28 0%,transparent 70%),linear-gradient(180deg,#0a0610 0%,#130920 50%,#0a0610 100%)',
    vars: {
      '--dlg-bg':'rgba(8,4,14,0.97)','--dlg-border':'rgba(160,100,220,0.35)',
      '--dlg-rule':'linear-gradient(90deg,transparent,rgba(160,100,220,0.6),rgba(220,180,80,0.5),rgba(160,100,220,0.6),transparent)',
      '--dlg-min-h':'210px','--dlg-pad':'28px 44px 24px',
      '--spk-color':'#c8a4e8','--spk-font':"'Cinzel',serif",'--spk-size':'11px','--spk-tracking':'0.22em','--spk-style':'normal',
      '--txt-color':'#d4c8e8','--txt-font':"'IM Fell English',serif",'--txt-size':'18px','--txt-style':'italic','--txt-weight':'400','--txt-lh':'1.72',
      '--ch-border':'rgba(160,100,220,0.2)','--ch-bg':'rgba(160,100,220,0.05)','--ch-hborder':'rgba(160,100,220,0.5)','--ch-hbg':'rgba(160,100,220,0.12)',
      '--ch-color':'#b8a8d8','--ch-hcolor':'#d4c8e8','--ch-font':"'IM Fell English',serif",'--ch-size':'15px',
      '--hud-color':'rgba(160,100,220,0.45)','--hud-font':"'Cinzel',serif",
      '--cursor':'#c8a4e8','--nav-color':'rgba(160,100,220,0.35)',
      '--ov-bg':'rgba(4,2,8,0.97)','--ov-border':'rgba(160,100,220,0.2)','--ov-txt':'#d4c8e8',
      '--accent':'#c8a4e8','--accent2':'#8a64a8','--scene-bg':'#0a0610',
    },
    hud: { tag: true, tarot: true },
    charGradient: 'linear-gradient(180deg,#18082a 0%,#0a0610 100%)',
    glowColor: 'rgba(160,100,220,0.1)',
  },

  suburban: {
    id: 'suburban', variant: 'card',
    sceneBg: '#d8d3ce',
    bgFallback: 'linear-gradient(180deg,#c4bfba 0%,#d8d3ce 40%,#e4e0db 100%)',
    vars: {
      '--dlg-bg':'rgba(252,250,248,0.98)','--dlg-border':'rgba(0,0,0,0.1)',
      '--dlg-rule':'none','--dlg-min-h':'200px','--dlg-pad':'24px 40px 20px',
      '--spk-color':'#2a2420','--spk-font':"'Rajdhani',sans-serif",'--spk-size':'14px','--spk-tracking':'0.15em','--spk-style':'normal',
      '--txt-color':'#3a3430','--txt-font':"'Courier Prime',monospace",'--txt-size':'15px','--txt-style':'normal','--txt-weight':'400','--txt-lh':'1.65',
      '--ch-border':'rgba(0,0,0,0.12)','--ch-bg':'rgba(0,0,0,0.03)','--ch-hborder':'rgba(0,0,0,0.3)','--ch-hbg':'rgba(0,0,0,0.07)',
      '--ch-color':'#5a5450','--ch-hcolor':'#1a1410','--ch-font':"'Courier Prime',monospace",'--ch-size':'14px',
      '--hud-color':'rgba(90,84,80,0.6)','--hud-font':"'Rajdhani',sans-serif",
      '--cursor':'#5a5450','--nav-color':'rgba(90,84,80,0.5)',
      '--ov-bg':'rgba(240,237,232,0.98)','--ov-border':'rgba(0,0,0,0.1)','--ov-txt':'#2a2420',
      '--accent':'#c85a3a','--accent2':'#8a7464','--scene-bg':'#d8d3ce',
    },
    hud: { tag: true },
    charGradient: 'linear-gradient(180deg,#b8b3ae 0%,#989390 100%)',
    glowColor: 'rgba(200,90,58,0.08)',
  },

  pastoral: {
    id: 'pastoral', variant: 'standard',
    sceneBg: '#0e1408',
    bgFallback: 'radial-gradient(ellipse 80% 50% at 50% 80%,#1e2c08 0%,transparent 70%),linear-gradient(180deg,#0e1408 0%,#161e0a 40%,#1a2410 100%)',
    vars: {
      '--dlg-bg':'rgba(8,12,4,0.98)','--dlg-border':'rgba(120,160,60,0.3)',
      '--dlg-rule':'linear-gradient(90deg,transparent,rgba(120,160,60,0.5),rgba(200,180,80,0.5),rgba(120,160,60,0.5),transparent)',
      '--dlg-min-h':'280px','--dlg-pad':'32px 60px 28px',
      '--spk-color':'#a8c864','--spk-font':"'Cinzel',serif",'--spk-size':'10px','--spk-tracking':'0.28em','--spk-style':'normal',
      '--txt-color':'#d4e0b8','--txt-font':"'IM Fell English',serif",'--txt-size':'20px','--txt-style':'italic','--txt-weight':'400','--txt-lh':'1.8',
      '--ch-border':'rgba(120,160,60,0.2)','--ch-bg':'rgba(120,160,60,0.05)','--ch-hborder':'rgba(120,160,60,0.5)','--ch-hbg':'rgba(120,160,60,0.1)',
      '--ch-color':'#98b480','--ch-hcolor':'#d4e0b8','--ch-font':"'IM Fell English',serif",'--ch-size':'17px',
      '--hud-color':'rgba(120,160,60,0.4)','--hud-font':"'Cinzel',serif",
      '--cursor':'#a8c864','--nav-color':'rgba(120,160,60,0.3)',
      '--ov-bg':'rgba(4,6,2,0.98)','--ov-border':'rgba(120,160,60,0.2)','--ov-txt':'#d4e0b8',
      '--accent':'#a8c864','--accent2':'#688040','--scene-bg':'#0e1408',
    },
    hud: { tag: true },
    charGradient: 'linear-gradient(180deg,#1c2410 0%,#0e1408 100%)',
    glowColor: 'rgba(120,160,60,0.1)',
  },

  scumm: {
    id: 'scumm', variant: 'scumm',
    sceneBg: '#000070',
    bgFallback: 'linear-gradient(180deg,#000060 0%,#000090 100%)',
    vars: {
      '--dlg-bg':'#000070','--dlg-border':'transparent',
      '--dlg-rule':'none','--dlg-min-h':'180px','--dlg-pad':'0',
      '--spk-color':'#ffff55','--spk-font':"'Anonymous Pro',monospace",'--spk-size':'13px','--spk-tracking':'0','--spk-style':'normal',
      '--txt-color':'#ffffff','--txt-font':"'Anonymous Pro',monospace",'--txt-size':'13px','--txt-style':'normal','--txt-weight':'400','--txt-lh':'1.5',
      '--ch-border':'transparent','--ch-bg':'transparent','--ch-hborder':'transparent','--ch-hbg':'transparent',
      '--ch-color':'#aaaaaa','--ch-hcolor':'#ffffff','--ch-font':"'Anonymous Pro',monospace",'--ch-size':'13px',
      '--hud-color':'#aaaaaa','--hud-font':"'Anonymous Pro',monospace",
      '--cursor':'#ffffff','--nav-color':'#888888',
      '--ov-bg':'rgba(0,0,80,0.98)','--ov-border':'rgba(255,255,85,0.4)','--ov-txt':'#ffffff',
      '--accent':'#ffff55','--accent2':'#aaaaaa','--scene-bg':'#000070',
    },
    hud: { tag: true, inventory: true },
    charGradient: 'linear-gradient(180deg,#000060 0%,#000040 100%)',
    glowColor: 'rgba(255,255,85,0.05)',
    verbs: ['Walk To','Pick Up','Talk To','Look At','Use','Open','Close','Push','Pull','Give'],
  },

  caliente: {
    id: 'caliente', variant: 'standard',
    sceneBg: '#140a04',
    bgFallback: 'radial-gradient(ellipse 80% 60% at 30% 60%,#281408 0%,transparent 70%),linear-gradient(180deg,#140a04 0%,#1e1008 50%,#281408 100%)',
    vars: {
      '--dlg-bg':'rgba(12,7,3,0.97)','--dlg-border':'rgba(220,120,40,0.35)',
      '--dlg-rule':'linear-gradient(90deg,transparent,rgba(220,120,40,0.6),rgba(255,200,60,0.6),rgba(220,120,40,0.6),transparent)',
      '--dlg-min-h':'210px','--dlg-pad':'28px 44px 24px',
      '--spk-color':'#e88040','--spk-font':"'Bebas Neue',sans-serif",'--spk-size':'22px','--spk-tracking':'0.12em','--spk-style':'normal',
      '--txt-color':'#e8d4b8','--txt-font':"'Courier Prime',monospace",'--txt-size':'15px','--txt-style':'normal','--txt-weight':'400','--txt-lh':'1.65',
      '--ch-border':'rgba(220,120,40,0.2)','--ch-bg':'rgba(220,120,40,0.05)','--ch-hborder':'rgba(220,120,40,0.5)','--ch-hbg':'rgba(220,120,40,0.12)',
      '--ch-color':'#c89868','--ch-hcolor':'#e8d4b8','--ch-font':"'Courier Prime',monospace",'--ch-size':'14px',
      '--hud-color':'rgba(220,120,40,0.45)','--hud-font':"'Bebas Neue',sans-serif",
      '--cursor':'#e88040','--nav-color':'rgba(220,120,40,0.35)',
      '--ov-bg':'rgba(8,4,2,0.97)','--ov-border':'rgba(220,120,40,0.2)','--ov-txt':'#e8d4b8',
      '--accent':'#e88040','--accent2':'#8a4820','--scene-bg':'#140a04',
    },
    hud: { tag: true },
    charGradient: 'linear-gradient(180deg,#281408 0%,#140a04 100%)',
    glowColor: 'rgba(220,120,40,0.1)',
  },

  glitch: {
    id: 'glitch', variant: 'glitch',
    sceneBg: '#050505',
    bgFallback: 'linear-gradient(180deg,#050505,#0a0a0a)',
    vars: {
      '--dlg-bg':'rgba(5,5,5,0.97)','--dlg-border':'rgba(0,255,0,0.35)',
      '--dlg-rule':'linear-gradient(90deg,transparent,rgba(0,255,0,0.4),rgba(255,0,255,0.3),rgba(0,255,0,0.4),transparent)',
      '--dlg-min-h':'220px','--dlg-pad':'20px 36px 20px',
      '--spk-color':'#00ff00','--spk-font':"'Anonymous Pro',monospace",'--spk-size':'13px','--spk-tracking':'0.1em','--spk-style':'normal',
      '--txt-color':'#c8ffc8','--txt-font':"'Anonymous Pro',monospace",'--txt-size':'13px','--txt-style':'normal','--txt-weight':'400','--txt-lh':'1.65',
      '--ch-border':'rgba(0,255,0,0.2)','--ch-bg':'rgba(0,255,0,0.04)','--ch-hborder':'rgba(255,0,255,0.4)','--ch-hbg':'rgba(255,0,255,0.06)',
      '--ch-color':'rgba(0,255,0,0.7)','--ch-hcolor':'#ffffff','--ch-font':"'Anonymous Pro',monospace",'--ch-size':'12px',
      '--hud-color':'rgba(0,255,0,0.4)','--hud-font':"'Anonymous Pro',monospace",
      '--cursor':'#00ff00','--nav-color':'rgba(0,255,0,0.3)',
      '--ov-bg':'rgba(2,2,2,0.98)','--ov-border':'rgba(0,255,0,0.15)','--ov-txt':'#c8ffc8',
      '--accent':'#00ff00','--accent2':'#ff00ff','--scene-bg':'#050505',
    },
    hud: { tag: true },
    charGradient: 'linear-gradient(180deg,#0a0a0a 0%,#050505 100%)',
    glowColor: 'rgba(0,255,0,0.06)',
  },
};

function getSkin(vol) {
  const v = VOLUME_LIST.find(x => x.vol === vol);
  if (!v) return SKINS.literary;
  return SKINS[v.skin] || SKINS.literary;
}

const SkinCtx = React.createContext(SKINS.literary);
function useSkin() { return React.useContext(SkinCtx); }

Object.assign(window, { VOLUME_LIST, SKINS, getSkin, SkinCtx, useSkin });
