#!/usr/bin/env python3
"""Assemble the four deliverable volume files from:
  out/volN_raw_restored.md      (cleaned OCR, per-page anchors)
  recovered/backmatter.md       (hand transcriptions of missing/garbled pages)
  driftwood_new/selection.md    (replacement comic block for pp 157-176)
  zine/zine.md                  (reproduced zine block for pp 309-316)
  expansions/*.md               (marked light expansions, inserted after a page)
"""
import re, json, os, glob

VOLS = {1: ('vol1_faust.md', 'Volume I — Faust 3', 'night-city Americana', (1, 87)),
        2: ('vol2_small_wood.md', 'Volume II — Small Wood Volumes', 'storybook folk', (88, 176)),
        3: ('vol3_earthman.md', 'Volume III — The Earthman Chronicles', 'retro-future signal', (177, 291)),
        4: ('vol4_back_matter.md', 'Volume IV — Scraps, Screenplays & Daddy', 'xerox zine punk', (292, 413))}
cov = {int(k): v for k, v in json.load(open('coverage.json')).items()}

def split_pages(md):
    parts = re.split(r'\n<!-- p\.(\d+)(?:: [^>]*)? -->\n', '\n' + md)
    return {int(parts[i]): parts[i + 1].strip() for i in range(1, len(parts), 2)}

def load_blocks(path):
    if not os.path.exists(path): return {}
    return split_pages(open(path).read())

recovered = load_blocks('recovered/backmatter.md')
recovered.update(load_blocks('recovered/p200.md'))
expansions = {}
for f in sorted(glob.glob('expansions/*.md')):
    txt = open(f).read()
    m = re.search(r'^after: p\.(\d+)', txt, re.M)
    if m: expansions.setdefault(int(m.group(1)), []).append(re.sub(r'^after: p\.\d+\n', '', txt, flags=re.M).strip())

REPLACE_RANGES = [((157, 176), 'driftwood_new/selection.md', 'DRIFT WOOD — replaces the 2010 photo-comic "driftwood" (pp 157–176)'),
                  ((309, 316), 'zine/zine.md', 'weep (FOR THE FUTURE!) — reproduced zine (pp 309–316)')]

PLATES = {1: ('mm2010_cover.png', 'Cover — four-panel painting, "modern mythology. a fiction by andy link"'),
          2: ('mm2010_title_plate.png', 'Title plate — three figures (painting)'),
          87: ('vol2_plate_small_wood.png', 'Small Wood Volumes — By D.N. Dean (painting: violet tower / ship over blue water)'),
          177: ('vol3_plate_earthman.png', 'The Earthman Chronicles — by Lafayette Hubbard (painting: pale figure)'),
          178: (None, 'Spine strip of the Earthman plate (no text)'),
          292: ('vol4_plate_glyph.png', 'Back-matter plate (painting: white glyph on black)')}
def illegible(t): return '[[ILLEGIBLE' in t
os.makedirs('final', exist_ok=True)
for v, (fname, title, register, (a, b)) in VOLS.items():
    pages = split_pages(open(f'out/vol{v}_raw_restored.md').read())
    in_game = [p for p in range(a, b + 1) if cov.get(p, 0) > 0.25]
    head = [f'# {title}', '',
            f'*Modern Mythology* (2010) — restored text for the visual novel. Register: **{register}**. Source pages {a}–{b} (PDF page index; printed folio = index + 1).',
            '']
    if in_game:
        head.append(f'> Already adapted in the Godot build: pp {in_game[0]}–{in_game[-1]} (marked ✓ below). Everything after is new material for the game.')
        head.append('')
    head += ['Conventions: `<!-- p.N -->` page anchors · **CUE** speaker lines · `####` sluglines · '
             '`> [[RECOVERED …]]` text transcribed from the page image · fenced `:::expansion` blocks are new connective material (not in the 2010 book) — keep, cut or rewrite.', '', '---', '']
    body = []
    done_ranges = set()
    for p in range(a, b + 1):
        rr = next((r for r in REPLACE_RANGES if r[0][0] <= p <= r[0][1]), None)
        if rr:
            if rr[0] not in done_ranges:
                done_ranges.add(rr[0])
                block = open(rr[1]).read().strip() if os.path.exists(rr[1]) else f'> PENDING: {rr[2]}'
                body.append(f'\n<!-- p.{rr[0][0]}–{rr[0][1]} -->\n\n## {rr[2]}\n\n{block}\n')
            continue
        if p in PLATES:
            img, cap = PLATES[p]
            body.append(f'\n<!-- p.{p} -->\n' + (f'![{cap}](images/plates/{img})\n\n*Plate: {cap}*\n' if img else f'*{cap}*\n'))
            continue
        txt = pages.get(p)
        if os.path.exists(f'proof/p{p}.md'): txt = open(f'proof/p{p}.md').read().strip()
        mark = ' ✓' if cov.get(p, 0) > 0.25 else ''
        if p in recovered and (txt is None or illegible(txt) or len(re.findall(r'\w+', txt or '')) < 0.6 * len(re.findall(r'\w+', recovered[p]))):
            txt = '> [[RECOVERED from page image]]\n\n' + recovered[p]
        if txt is None: continue
        body.append(f'\n<!-- p.{p}{mark} -->\n{txt}\n')
        for e in expansions.get(p, []):
            body.append(f'\n:::expansion\n{e}\n:::\n')
    # rejoin words hyphenated across a page break
    joined = ''.join(body)
    HY = re.compile(r"([A-Za-z]+)-\s*\n\n<!-- p\.(\d+)( ✓)? -->\n(> \[\[RECOVERED[^\n]*\n\n)?([a-z][A-Za-z']*)([.,;:!?\"]*)")
    joined = HY.sub(lambda m: m.group(1) + m.group(5) + m.group(6) + "\n\n<!-- p." + m.group(2) + (m.group(3) or "") + " -->\n" + (m.group(4) or ""), joined)
    for a_, b_ in [("Nathanielress", "mattress"), ("Nathanieler", "matter")]: joined = joined.replace(a_, b_)
    # E3_MOVE: chapter seven belongs right before 'viii. stories within stories', not mid-sentence after p.132
    m = re.search(r'\n:::expansion\n\*\*\[expansion E3.*?\n:::\n', joined, re.S)
    if m:
        blk = m.group(0); joined = joined.replace(blk, '\n')
        joined = re.sub(r'(\nviii\. stories within stories)', lambda mm: blk + mm.group(1), joined, count=1)
    out = '\n'.join(head) + joined
    out = re.sub(r'\n{3,}', '\n\n', out)
    open(f'final/{fname}', 'w').write(out)
    print(fname, len(re.findall(r'\w+', out)), 'words', 'illegible:', out.count('[[ILLEGIBLE'))
