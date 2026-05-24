// ── Music: catalog, heard-tracking, queue picker ──────────────────────────
// Single source of truth for the soundtrack. Loaded by:
//   • Modern Mythology.html (game) — feeds AudioMgr's heard-marking + queue
//   • Gallery.html (Music Room) — feeds the track list + unlock state
//
// Contract:
//   window.MM_MUSIC                  — curated catalog (array of tracks)
//   window.MM_MUSIC_HEARD            — heard set with .get/.has/.mark/.clear
//   window.MM_MUSIC_findEntry(src)   — catalog lookup by src
//   window.MM_MUSIC_buildTrackForSrc(src) — entry for any src (heard fallback)
//   window.MM_MUSIC_pickNext(currentSrc, opts) — next track id for the queue
//   window.MM_MUSIC_inferVol(src)    — extract vol number from filename
//   window.MM_MUSIC_humanizeTitle(s) — pretty title from filename
//
// Heard set is persisted to localStorage at key `mm_music_heard` and shared
// across the game + Music Room. It is *not* tied to a particular save slot:
// once you've heard a track, it stays unlocked.

// ── Curated catalog (all tracks actually referenced in vn-scenes.jsx) ────
// Each entry: { id, vol, title, src, [duration], [composer], [unlock], [desc], [clue] }
//   unlock: { type:'heard' }   → appears once played in-game (default)
//           { type:'always' }  → always visible, even before heard
//           { type:'flag', key } → legacy: unlocks via save flag
const MM_MUSIC = [
  // ── Vol 1 · Modern Mythology ─────────────────────────────────────────
  { id:'vol1_ambient',         vol:1, title:'The Diner at the Crossroads', src:'assets/audio/bgm/vol1_ambient.mp3',
    composer:'—', desc:'The diner. The stranger. The choice that starts everything.' },
  { id:'vol1_diner_ambient',   vol:1, title:'The Missing Link',             src:'assets/audio/bgm/vol1_diner_ambient.mp3',
    composer:'—', desc:'Bus depot. Rain. No clock.' },
  { id:'vol1_drive_night',     vol:1, title:'Driving Around · Night',       src:'assets/audio/bgm/vol1_drive_night.mp3',
    composer:'—', desc:'EXT. Judgement Day. Headlights, then more headlights.' },
  { id:'vol1_club_thump',      vol:1, title:'The Underworld',               src:'assets/audio/bgm/vol1_club_thump.mp3',
    composer:'—', desc:'Intercut. Dancing. Loud music.' },
  { id:'vol1_dream_drone',     vol:1, title:'Dream States',                 src:'assets/audio/bgm/vol1_dream_drone.mp3',
    composer:'—', desc:"Faust's bedroom. The room behind the room." },

  // ── Vol 2 · Small Wood Volumes ────────────────────────────────────────
  { id:'vol2_ambient',         vol:2, title:'Small Wood Variations',        src:'assets/audio/bgm/vol2_ambient.mp3',
    composer:'—', desc:'The sound of trees that have been standing longer than the town.' },
  { id:'vol2_rest_stop_wind',  vol:2, title:'Rest Stop · Wind',             src:'assets/audio/bgm/vol2_rest_stop_wind.mp3',
    composer:'—', desc:'Briar Falls. Mid-nineties. Twelve hours from anywhere.' },
  { id:'vol2_seagash_drone',   vol:2, title:'The Siren of Seagash',         src:'assets/audio/bgm/vol2_seagash_drone.mp3',
    composer:'—', desc:'A history, with interludes.' },

  // ── Vol 3 · The Earthman Chronicles ───────────────────────────────────
  { id:'vol3_ambient',         vol:3, title:'Station Omega-14',             src:'assets/audio/bgm/vol3_ambient.mp3',
    composer:'—', desc:'The hum of life support and the silence of deep space.' },

  // ── Vol 4 · #/Sharp ───────────────────────────────────────────────────
  { id:'vol4_ambient',         vol:4, title:'Five AM, No One Around',       src:'assets/audio/bgm/vol4_ambient.mp3',
    composer:'—', desc:"The city before it remembers you're not supposed to be there." },

  // ── Vol 5 · Major Arcana ──────────────────────────────────────────────
  { id:'vol5_ambient',         vol:5, title:"D'Ambrosio's at Dawn",         src:'assets/audio/bgm/vol5_ambient.mp3',
    composer:'—', desc:'Open 24 hours. Technically.' },
  { id:'vol5_warehouse_drone', vol:5, title:'Cathedral of Rust and Code',   src:'assets/audio/bgm/vol5_warehouse_drone.mp3',
    composer:'—', desc:'Chapter I — The Magician.' },
  { id:'vol5_cicadas_dusk',    vol:5, title:'Cicadas at Dusk',              src:'assets/audio/bgm/vol5_cicadas_dusk.mp3',
    composer:'—', desc:'Chapter II — The High Priestess.' },
  { id:'vol5_riverboat_drone', vol:5, title:'Static Bloom',                 src:'assets/audio/bgm/vol5_riverboat_drone.mp3',
    composer:'—', desc:'Chapter III — The Empress.' },

  // ── Vol 6 · Planned Community ─────────────────────────────────────────
  { id:'vol6_ambient',         vol:6, title:'Harmony Creek Estates',        src:'assets/audio/bgm/vol6_ambient.mp3',
    composer:'—', desc:'Sixty-eight degrees, year-round, by corporate decree.' },

  // ── Vol 7 · Land of Milk & Honey ──────────────────────────────────────
  { id:'vol7_ambient',         vol:7, title:'Smolvud Ambient',              src:'assets/audio/bgm/vol7_ambient.mp3',
    composer:'—', desc:'The kind of town that knows when you have arrived before you do.' },
  { id:'vol7_apartment_rain',  vol:7, title:"Lena's Apartment · Rain",      src:'assets/audio/bgm/vol7_apartment_rain.mp3',
    composer:'—', desc:'Six o\'clock. Four coats on four hooks.' },
  { id:'vol7_rain_on_roof',    vol:7, title:'Rain on Roof',                 src:'assets/audio/bgm/vol7_rain_on_roof.mp3',
    composer:'—', desc:'With two of them left in it the apartment was hers again.' },
];

// Default every entry to heard-based unlock unless explicitly overridden.
MM_MUSIC.forEach(t => { if (!t.unlock) t.unlock = { type: 'heard' }; });

// ── Heard set ────────────────────────────────────────────────────────────
const MM_MUSIC_HEARD_KEY = 'mm_music_heard';
const MM_MUSIC_HEARD = {
  _cache: null,
  _load() {
    try { this._cache = new Set(JSON.parse(localStorage.getItem(MM_MUSIC_HEARD_KEY) || '[]')); }
    catch { this._cache = new Set(); }
    return this._cache;
  },
  get() { return this._cache || this._load(); },
  has(src) { return this.get().has(src); },
  mark(src) {
    if (!src) return false;
    const set = this.get();
    if (set.has(src)) return false;
    set.add(src);
    try { localStorage.setItem(MM_MUSIC_HEARD_KEY, JSON.stringify([...set])); } catch {}
    try { window.dispatchEvent(new CustomEvent('mm-music-heard', { detail: src })); } catch {}
    return true;
  },
  clear() {
    this._cache = new Set();
    try { localStorage.removeItem(MM_MUSIC_HEARD_KEY); } catch {}
    try { window.dispatchEvent(new CustomEvent('mm-music-heard', { detail: null })); } catch {}
  },
};

// Cross-tab sync (Music Room open while game plays in another tab)
try {
  window.addEventListener('storage', (e) => {
    if (e.key === MM_MUSIC_HEARD_KEY) {
      MM_MUSIC_HEARD._cache = null;
      try { window.dispatchEvent(new CustomEvent('mm-music-heard', { detail: '*' })); } catch {}
    }
  });
} catch {}

// ── Helpers ──────────────────────────────────────────────────────────────
function MM_MUSIC_inferVol(src) {
  const m = (src || '').match(/vol(\d+)_/);
  return m ? parseInt(m[1], 10) : null;
}

function MM_MUSIC_humanizeTitle(src) {
  const name = (src || '').split('/').pop().replace(/\.[^.]+$/, '');
  const noVol = name.replace(/^vol\d+_/, '');
  return noVol.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function MM_MUSIC_findEntry(src) {
  if (!src) return null;
  return MM_MUSIC.find(t => t.src === src) || null;
}

// Returns an entry for any src — falls back to a synthesized "discovered"
// entry when the track was heard in-game but isn't in the curated catalog.
function MM_MUSIC_buildTrackForSrc(src) {
  const known = MM_MUSIC_findEntry(src);
  if (known) return known;
  return {
    id: 'heard_' + (src || '').split('/').pop().replace(/\W+/g, '_'),
    vol: MM_MUSIC_inferVol(src) || 1,
    title: MM_MUSIC_humanizeTitle(src),
    src,
    composer: '—',
    unlock: { type: 'heard' },
    __discovered: true, // not in curated catalog
  };
}

// Pick the next track to queue when the currently playing one ends.
// Order of preference:
//   1. A heard catalog track in the same vol as the current one, in catalog
//      order rotating from the current position (so the user hears variety,
//      not the same two tracks ping-ponging).
//   2. Any other heard catalog track.
//   3. null — caller should fall back to looping.
function MM_MUSIC_pickNext(currentSrc, opts = {}) {
  const heard = MM_MUSIC_HEARD.get();
  const currentEntry = MM_MUSIC_findEntry(currentSrc);
  const preferVol = opts.preferVol ?? currentEntry?.vol ?? MM_MUSIC_inferVol(currentSrc);
  const heardOthers = MM_MUSIC.filter(t => t.src !== currentSrc && heard.has(t.src));
  if (!heardOthers.length) return null;

  // 1. Same-vol rotation
  if (preferVol != null) {
    const sameVolHeard = heardOthers.filter(t => t.vol === preferVol);
    if (sameVolHeard.length) {
      const baseIdx = MM_MUSIC.findIndex(t => t.src === currentSrc);
      const start = baseIdx >= 0 ? baseIdx : 0;
      for (let i = 1; i <= MM_MUSIC.length; i++) {
        const cand = MM_MUSIC[(start + i) % MM_MUSIC.length];
        if (!cand) continue;
        if (cand.vol === preferVol && cand.src !== currentSrc && heard.has(cand.src)) {
          return cand.src;
        }
      }
    }
  }

  // 2. Any heard
  return heardOthers[0].src;
}

Object.assign(window, {
  MM_MUSIC,
  MM_MUSIC_HEARD,
  MM_MUSIC_findEntry,
  MM_MUSIC_buildTrackForSrc,
  MM_MUSIC_humanizeTitle,
  MM_MUSIC_inferVol,
  MM_MUSIC_pickNext,
});
