#!/usr/bin/env python3
"""Build godot/tools/patch_sources.js — the PATCH BANK's catalog of public instruments.

Every source is a public GitHub repository (served by raw.githubusercontent.com, which
sends CORS * so the file:// tool pages can fetch from it). Nothing is vendored: the
browser downloads what you pick and caches it in IndexedDB.

    python3 -I godot/tools/patch_sources_build.py [--cache DIR]

Needs git + network. Uses blob-less clones (file lists only, a few MB) in --cache
(default: ~/.cache/mm_patch_sources). Re-run to pick up upstream additions; pin
commits by editing SOURCES[*]['ref'].
"""
import argparse, json, os, re, subprocess, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'patch_sources.js')

# ── licences: what each one means for music that ends up in the game ─────────
LICENCES = {
    'cc0':          {'name': 'CC0 1.0 (public domain)', 'game': 'free', 'url': 'https://creativecommons.org/publicdomain/zero/1.0/',
                     'note': 'No conditions. Credit is kind, not required.'},
    'cc-by-3.0':    {'name': 'CC BY 3.0', 'game': 'credit', 'url': 'https://creativecommons.org/licenses/by/3.0/',
                     'note': 'Free for any use; put the credit line in the game credits.'},
    'cc-by-sa-3.0': {'name': 'CC BY-SA 3.0', 'game': 'share-alike', 'url': 'https://creativecommons.org/licenses/by-sa/3.0/',
                     'note': 'Credit required, and adaptations of the samples must stay BY-SA. Music made with them is widely treated as fine, but it is debated — prefer a CC0/BY source for shipped game music.'},
    'generaluser':  {'name': 'GeneralUser GS licence v2.0', 'game': 'free', 'url': 'https://github.com/mrbumpy409/GeneralUser-GS/blob/main/documentation/LICENSE.txt',
                     'note': 'Use without restriction for music, private or commercial. Credit appreciated.'},
    'music-cc0':    {'name': 'Music made with it: CC0 (samples: CC BY-NC 4.0)', 'game': 'free', 'url': 'https://github.com/sfzinstruments/jlearman.jRhodes3d/blob/master/LICENSE',
                     'note': 'Anything you play and record with it is yours. Do not redistribute the raw samples commercially.'},
    'mixed-free':   {'name': 'Mixed: CC0 / free-use / CC BY (per instrument)', 'game': 'credit', 'url': 'https://github.com/nbrosowsky/tonejs-instruments/blob/master/sample-source-info.txt',
                     'note': 'Most instruments are VSCO-2 CE (CC0), Karoryfer (CC0) or Univ. of Iowa MIS (free use); a few come from Freesound users — credit those (see the instrument).'},
    'gpl-3.0-bank': {'name': 'Distributed with Dexed (GPL-3.0)', 'game': 'free', 'url': 'https://github.com/asb2m10/dexed',
                     'note': 'Patch data shipped in Dexed. Patches are settings, not recordings: music you make with them is yours.'},
    'yamaha-rom':   {'name': 'Yamaha DX7 factory voices', 'game': 'free', 'url': 'https://github.com/mmontag/dx7-synth-js/tree/master/roms',
                     'note': 'Factory patch data © Yamaha, distributed freely for decades. Music made with them is yours; do not resell the bank.'},
}

# ── the sources ───────────────────────────────────────────────────────────────
SOURCES = [
    {'id': 'gugs', 'name': 'GeneralUser GS', 'author': 'S. Christian Collins', 'kind': 'sf2', 'repo': 'mrbumpy409/GeneralUser-GS', 'ref': 'main',
     'licence': 'generaluser', 'file': 'GeneralUser-GS.sf2', 'size': 32319396,
     'credit': 'GeneralUser GS by S. Christian Collins',
     'summary': 'A complete General MIDI bank: 259 instruments and 13 drum kits in one 32 MB SoundFont. The best single download.'},
    {'id': 'fluid', 'name': 'FluidR3 GM (per instrument)', 'author': 'Frank Wen · packaged by Benjamin Gleitzman', 'kind': 'midijs', 'repo': 'gleitz/midi-js-soundfonts', 'ref': 'gh-pages',
     'licence': 'cc-by-3.0', 'dir': 'FluidR3_GM', 'credit': 'FluidR3 GM SoundFont by Frank Wen (CC BY 3.0)',
     'summary': 'The 128 General MIDI melodic instruments, one small download each (≈1–2 MB).'},
    {'id': 'musyng', 'name': 'Musyng Kite GM (per instrument)', 'author': 'Musyng Kite · packaged by Benjamin Gleitzman', 'kind': 'midijs', 'repo': 'gleitz/midi-js-soundfonts', 'ref': 'gh-pages',
     'licence': 'cc-by-sa-3.0', 'dir': 'MusyngKite', 'credit': 'Musyng Kite SoundFont (CC BY-SA 3.0)',
     'summary': 'Richer GM set (from a 1.75 GB SoundFont), per instrument. Share-alike.'},
    {'id': 'fatboy', 'name': 'FatBoy GM (per instrument)', 'author': 'FatBoy · packaged by Benjamin Gleitzman', 'kind': 'midijs', 'repo': 'gleitz/midi-js-soundfonts', 'ref': 'gh-pages',
     'licence': 'cc-by-sa-3.0', 'dir': 'FatBoy', 'credit': 'FatBoy SoundFont (CC BY-SA 3.0)',
     'summary': 'Another full GM set with a vintage character, per instrument. Share-alike.'},
    {'id': 'salamander', 'name': 'Salamander Grand Piano', 'author': 'Alexander Holm (SFZ by kinwie)', 'kind': 'sfz', 'repo': 'sfzinstruments/SalamanderGrandPiano', 'ref': 'master',
     'licence': 'cc-by-3.0', 'credit': 'Salamander Grand Piano by Alexander Holm (CC BY 3.0)',
     'summary': 'Yamaha C5 grand, 16 velocity layers, release and pedal noises. Large (≈ 1 GB of FLAC — downloads the notes you need as you load).',
     'programs': [('main', 'Salamander Grand Piano', 'piano', 'Salamander Grand Piano V3.sfz')]},
    {'id': 'jrhodes', 'name': 'jRhodes3d', 'author': 'Jeff Learman', 'kind': 'sfz', 'repo': 'sfzinstruments/jlearman.jRhodes3d', 'ref': 'master',
     'licence': 'music-cc0', 'credit': 'jRhodes3d by Jeff Learman',
     'summary': '1977 Rhodes Mark I stage piano.',
     'programs': [('st', 'jRhodes3d stereo', 'keys', 'jRhodes3d-st.sfz'), ('mono', 'jRhodes3d mono', 'keys', 'jRhodes3d-mono.sfz'),
                  ('sv', 'jRhodes3d stereo vibrato', 'keys', 'jRhodes3d-sv.sfz')]},
    {'id': 'virtuosity', 'name': 'Virtuosity Drums', 'author': 'Versilian Studios / sfzinstruments', 'kind': 'sfz', 'repo': 'sfzinstruments/virtuosity_drums', 'ref': 'master',
     'licence': 'cc0', 'credit': 'Virtuosity Drums (CC0)', 'summary': 'Acoustic kit, multi-mic, GM-mapped.', 'glob': r'^Programs/[^/]+\.sfz$', 'category': 'drums'},
    {'id': 'rusty', 'name': 'Big Rusty Drums', 'author': 'Karoryfer Samples', 'kind': 'sfz', 'repo': 'sfzinstruments/karoryfer.big-rusty-drums', 'ref': 'main',
     'licence': 'cc0', 'credit': 'Big Rusty Drums by Karoryfer Samples (CC0)', 'summary': 'A big, trashy rock kit.', 'glob': r'^Programs/[^/]+\.sfz$', 'category': 'drums'},
    {'id': 'swirly', 'name': 'Swirly Drums', 'author': 'Karoryfer Samples', 'kind': 'sfz', 'repo': 'sfzinstruments/karoryfer.swirly-drums', 'ref': 'main',
     'licence': 'cc0', 'credit': 'Swirly Drums by Karoryfer Samples (CC0)', 'summary': 'A vintage-flavoured kit, bus programs.', 'glob': r'^Programs/[^/]+\.sfz$', 'category': 'drums'},
    {'id': 'bgguitars', 'name': 'Black and Green Guitars', 'author': 'Karoryfer Samples', 'kind': 'sfz', 'repo': 'sfzinstruments/karoryfer.black-and-green-guitars', 'ref': 'main',
     'licence': 'cc0', 'credit': 'Black and Green Guitars by Karoryfer Samples (CC0)', 'summary': 'Two cheap electric guitars, many articulations.', 'glob': r'^Programs/[^/]+\.sfz$', 'category': 'guitar'},
    {'id': 'emily', 'name': 'Emily Guitar', 'author': 'Karoryfer Samples', 'kind': 'sfz', 'repo': 'sfzinstruments/karoryfer.emilyguitar', 'ref': 'master',
     'licence': 'cc0', 'credit': 'Emily Guitar by Karoryfer Samples (CC0)', 'summary': 'Acoustic guitar, single notes and chords.', 'glob': r'^[^/]+\.sfz$', 'category': 'guitar'},
    {'id': 'meatbass', 'name': 'Meatbass', 'author': 'Karoryfer Samples', 'kind': 'sfz', 'repo': 'sfzinstruments/karoryfer.meatbass', 'ref': 'master',
     'licence': 'cc0', 'credit': 'Meatbass by Karoryfer Samples (CC0)', 'summary': 'Upright bass, arco and pizz.', 'glob': r'^Programs/(0\d_[^/]+)\.sfz$', 'category': 'bass'},
    {'id': 'growly', 'name': 'Growlybass', 'author': 'Karoryfer Samples', 'kind': 'sfz', 'repo': 'sfzinstruments/karoryfer.growlybass', 'ref': 'master',
     'licence': 'cc0', 'credit': 'Growlybass by Karoryfer Samples (CC0)', 'summary': 'Electric bass from clean to vicious.', 'glob': r'^[^/]+\.sfz$', 'category': 'bass'},
    {'id': 'dbass', 'name': 'Rubner Double Bass', 'author': 'D. Smolken', 'kind': 'sfz', 'repo': 'sfzinstruments/dsmolken.double-bass', 'ref': 'master',
     'licence': 'cc0', 'credit': 'Rubner double bass by D. Smolken (CC0)', 'summary': 'Orchestral double bass, arco and pizzicato.', 'glob': r'^[^/]+\.sfz$', 'category': 'strings'},
    {'id': 'bearsax', 'name': 'Bear Sax', 'author': 'Karoryfer Samples', 'kind': 'sfz', 'repo': 'sfzinstruments/karoryfer.bear-sax', 'ref': 'master',
     'licence': 'cc0', 'credit': 'Bear Sax by Karoryfer Samples (CC0)', 'summary': 'Baritone sax with personality, plus bearcussion.', 'glob': r'^Programs/[^/]+\.sfz$', 'category': 'woodwind'},
    {'id': 'weresax', 'name': 'Weresax', 'author': 'Karoryfer Samples', 'kind': 'sfz', 'repo': 'sfzinstruments/karoryfer.weresax', 'ref': 'master',
     'licence': 'cc0', 'credit': 'Weresax by Karoryfer Samples (CC0)', 'summary': 'Alto sax, saxcordion and the sxnth.', 'glob': r'^Programs/(Sax|saxcordion|sxnth)[^/]*\.sfz$', 'category': 'woodwind'},
    {'id': 'vcsl', 'name': 'VCSL — Versilian Community Sample Library', 'author': 'Versilian Studios (Sam Gossner)', 'kind': 'files', 'repo': 'sgossner/VCSL', 'ref': 'master',
     'licence': 'cc0', 'credit': 'VCSL by Versilian Studios (CC0)',
     'summary': '100+ real instruments: harpsichords, pianos, mallets, bells, recorders, harmonicas, world percussion, timpani, TX81Z.'},
    {'id': 'tonejs', 'name': 'Tone.js Instruments', 'author': 'Nicholaus Brosowsky (collected from VSCO-2, Karoryfer, Iowa MIS, Freesound)', 'kind': 'files', 'repo': 'nbrosowsky/tonejs-instruments', 'ref': 'master',
     'licence': 'mixed-free', 'credit': 'tonejs-instruments by Nicholaus Brosowsky',
     'summary': '19 orchestral and band instruments, one compact MP3 set each.'},
    {'id': 'akwf', 'name': 'AKWF single-cycle waveforms', 'author': 'Kristoffer Ekstrand (Adventure Kid)', 'kind': 'waveforms', 'repo': 'KristofferKarlAxelEkstrand/AKWF-FREE', 'ref': 'main',
     'licence': 'cc0', 'credit': 'AKWF waveforms by Kristoffer Ekstrand (CC0)',
     'summary': '4,000+ single-cycle waveforms (600 samples) — play them as looping oscillators: chip, organ, voice, FM, analog, bit-reduced…'},
    {'id': 'dexed', 'name': 'Dexed + SynprezFM DX7 banks', 'author': 'Dexed (asb2m10), SynprezFM', 'kind': 'dx7zip', 'repo': 'asb2m10/dexed', 'ref': 'master',
     'licence': 'gpl-3.0-bank', 'file': 'assets/builtin_pgm.zip', 'credit': 'DX7 patches from Dexed / SynprezFM',
     'summary': '33 DX7 cartridges, 1,056 voices. Play in the browser or send to the FM-1.'},
    {'id': 'rom1a', 'name': 'Yamaha DX7 ROM 1A', 'author': 'Yamaha (via dx7-synth-js)', 'kind': 'dx7', 'repo': 'mmontag/dx7-synth-js', 'ref': 'master',
     'licence': 'yamaha-rom', 'file': 'roms/ROM1A.SYX', 'credit': 'Yamaha DX7 factory voices',
     'summary': 'The original 32 factory voices: E.PIANO 1, BRASS 1, BASS 1, TUB BELLS, MARIMBA…'},
]

GM_CATS = ['piano'] * 8 + ['mallets'] * 8 + ['organ'] * 8 + ['guitar'] * 8 + ['bass'] * 8 + ['strings'] * 8 + ['ensemble'] * 8 + ['brass'] * 8 + \
          ['woodwind'] * 16 + ['lead'] * 8 + ['pad'] * 8 + ['synth fx'] * 8 + ['world'] * 8 + ['percussion'] * 8 + ['fx'] * 8

NOTE_TOKEN = re.compile(r'(?:^|[_\- ])([A-Ga-g])([#sb]?)(-?\d)(?=[_\-. ]|$)')

def sh(*a, cwd=None):
    return subprocess.run(a, cwd=cwd, check=True, capture_output=True, text=True).stdout

def tree(cache, repo, ref):
    d = os.path.join(cache, repo.replace('/', '__'))
    if not os.path.isdir(d):
        sh('git', 'clone', '-q', '--filter=blob:none', '--no-checkout', '--depth', '1', '--branch', ref, f'https://github.com/{repo}', d)
    commit = sh('git', 'rev-parse', 'HEAD', cwd=d).strip()
    names = sh('git', 'ls-tree', '-r', '--name-only', 'HEAD', cwd=d).splitlines()
    return d, commit, names

def show(d, path):
    return subprocess.run(['git', 'show', f'HEAD:{path}'], cwd=d, check=True, capture_output=True).stdout

def title(s):
    s = re.sub(r'\.sfz$', '', s)
    s = re.sub(r'^\d+[-_]', '', s)
    return re.sub(r'[_\-]+', ' ', s).strip()

def vcsl_category(path):
    p = path.lower()
    if 'piano' in p: return 'piano'
    if 'harpsichord' in p or 'tx81z' in p: return 'keys'
    if 'organ' in p: return 'organ'
    if 'harp' in p or 'psaltery' in p or 'strumstick' in p: return 'plucked'
    if 'dan tranh' in p or 'didgeridoo' in p or 'kalimba' in p or 'mbira' in p or 'nyunga' in p or 'balafon' in p: return 'world'
    if 'bells' in p or 'chimes' in p or 'glock' in p: return 'bells'
    if any(k in p for k in ('marimba', 'xylophone', 'vibraphone', 'wine glasses')): return 'mallets'
    if 'recorder' in p or 'ocarina' in p or 'whistle' in p or 'harmonica' in p or 'sax' in p: return 'woodwind'
    if 'siren' in p or 'ratchet' in p or 'flexatone' in p or 'vibraslap' in p or 'ocean' in p: return 'fx'
    if 'membranophones' in p and 'timpani' not in p: return 'drums'
    return 'percussion'

def tonejs_category(n):
    return {'piano': 'piano', 'organ': 'organ', 'harmonium': 'organ', 'guitar-acoustic': 'guitar', 'guitar-electric': 'guitar', 'guitar-nylon': 'guitar',
            'bass-electric': 'bass', 'contrabass': 'strings', 'cello': 'strings', 'violin': 'strings', 'harp': 'plucked', 'xylophone': 'mallets',
            'flute': 'woodwind', 'clarinet': 'woodwind', 'bassoon': 'woodwind', 'saxophone': 'woodwind',
            'trumpet': 'brass', 'trombone': 'brass', 'french-horn': 'brass', 'tuba': 'brass'}.get(n, 'other')

TONEJS_CREDIT = {  # per sample-source-info.txt
    'cello': 'cello samples: Freesound 12408 by flcellogrl', 'guitar-nylon': 'nylon guitar samples: Freesound 11573 by quartertone',
    'harmonium': 'harmonium samples: Freesound 330410 by donyaquick', 'guitar-acoustic': 'acoustic guitar: Univ. of Iowa MIS',
    'bass-electric': 'electric bass: Karoryfer (CC0)', 'guitar-electric': 'electric guitar: Karoryfer (CC0)', 'saxophone': 'saxophone: Karoryfer (CC0)',
}

def build(cache):
    out_sources = []
    for s in SOURCES:
        print('·', s['id'], s['repo'], file=sys.stderr)
        d, commit, names = tree(cache, s['repo'], s['ref'])
        src = {k: v for k, v in s.items() if k not in ('glob', 'programs', 'category')}
        src['commit'] = commit
        src['base'] = f"https://raw.githubusercontent.com/{s['repo']}/{commit}/"
        src['homepage'] = f"https://github.com/{s['repo']}"
        items = []
        if s['kind'] == 'sfz':
            if 'programs' in s:
                for pid, nm, cat, path in s['programs']:
                    assert path in names, (s['id'], path)
                    items.append({'id': pid, 'name': nm, 'category': cat, 'path': path})
            else:
                rx = re.compile(s['glob'])
                for n in sorted(names):
                    if rx.match(n):
                        items.append({'id': re.sub(r'\W+', '_', n[:-4]).strip('_').lower(), 'name': title(os.path.basename(n)), 'category': s.get('category', 'other'), 'path': n})
        elif s['kind'] == 'midijs':
            gm = json.loads(show(d, f"{s['dir']}/names.json"))
            have = set(names)
            for prog, nm in enumerate(gm):
                f = f"{s['dir']}/{nm}-mp3.js"
                if f in have:
                    items.append({'id': nm, 'name': nm.replace('_', ' '), 'category': GM_CATS[prog], 'program': prog, 'path': f})
        elif s['kind'] == 'files' and s['id'] == 'vcsl':
            groups = {}
            for n in names:
                if not n.lower().endswith('.wav'): continue
                parts = n.split('/')
                if len(parts) < 4: continue
                groups.setdefault('/'.join(parts[:3]), []).append('/'.join(parts[3:]))
            for g, files in sorted(groups.items()):
                notes = {m.group(0) for f in files for m in [NOTE_TOKEN.search(os.path.basename(f))] if m}
                items.append({'id': re.sub(r'\W+', '_', g.split('/')[-1]).strip('_').lower(), 'name': g.split('/')[-1], 'category': vcsl_category(g),
                              'dir': g + '/', 'files': sorted(files), 'pitched': len(notes) >= 3})
        elif s['kind'] == 'files' and s['id'] == 'tonejs':
            groups = {}
            for n in names:
                m = re.match(r'^samples/([^/]+)/([^/]+\.(mp3|wav|ogg))$', n)
                if m: groups.setdefault(m.group(1), []).append(m.group(2))
            for g, files in sorted(groups.items()):
                mp3 = [f for f in files if f.endswith('.mp3')] or files
                it = {'id': g, 'name': g.replace('-', ' '), 'category': tonejs_category(g), 'dir': f'samples/{g}/', 'files': sorted(mp3), 'pitched': True}
                if g in TONEJS_CREDIT: it['credit'] = TONEJS_CREDIT[g]
                items.append(it)
        elif s['kind'] == 'waveforms':
            groups = {}
            for n in names:
                m = re.match(r'^AKWF/([^/]+)/([^/]+)\.wav$', n)
                if m: groups.setdefault(m.group(1), []).append(m.group(2))
            for g, files in sorted(groups.items()):
                pre = os.path.commonprefix(files)
                items.append({'id': g, 'name': g.replace('AKWF_', '').replace('_', ' '), 'category': 'waveform', 'dir': f'AKWF/{g}/',
                              'prefix': pre, 'waves': sorted(f[len(pre):] for f in files)})
        elif s['kind'] in ('sf2', 'dx7', 'dx7zip'):
            assert s['file'] in names, (s['id'], s['file'])
        src['items'] = items
        out_sources.append(src)
    return out_sources

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cache', default=os.path.expanduser('~/.cache/mm_patch_sources'))
    a = ap.parse_args()
    os.makedirs(a.cache, exist_ok=True)
    sources = build(a.cache)
    reg = {'generated': datetime.date.today().isoformat(), 'licences': LICENCES, 'sources': sources}
    body = json.dumps(reg, ensure_ascii=False, separators=(',', ':'))
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('/* patch_sources.js — GENERATED by patch_sources_build.py; do not hand-edit.\n'
                ' * Public instrument / patch sources for the PATCH BANK (patch_bank.js): licence, credit line,\n'
                ' * pinned commit, raw.githubusercontent base URL and the instrument list of each.\n */\n')
        f.write('const PATCH_SOURCES = /*PATCH-JSON-BEGIN*/' + body + '/*PATCH-JSON-END*/;\n')
        f.write("if (typeof window !== 'undefined') window.PATCH_SOURCES = PATCH_SOURCES;\n")
    n = sum(len(s['items']) for s in sources)
    print(f'wrote {OUT}: {len(sources)} sources, {n} items, {os.path.getsize(OUT) // 1024} KB', file=sys.stderr)

if __name__ == '__main__':
    main()
