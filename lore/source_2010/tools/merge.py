#!/usr/bin/env python3
"""Reconcile v2 (visual OCR, ligatures intact, split-word errors) with the PDF
text layer (correct word boundaries, ligatures dropped, $ for apostrophes).
Keeps v2 layout; swaps in PDF tokens where they read as better English.
Writes v3.txt in the same === PAGE N === format plus merge_log.tsv."""
import re, json, difflib, collections
from wordfreq import zipf_frequency as zf

z = lambda w: zf(w.lower(), 'en')
t = open('v2.txt').read()
parts = re.split(r'(=== PAGE \d+ ===)', t)
pdf = {int(k): v for k, v in json.load(open('pdf_pages.json')).items()}
corpus_vocab = collections.Counter(re.findall(r"[A-Za-z]+", t.lower()))

def norm_pdf(s):
    s = s.replace('$', "'").replace('’', "'").replace('ñ', 'fl')
    s = re.sub(r'\|\s*:-:\s*\|', ' ', s)
    s = re.sub(r'\[\*\*Page \d+\*\*\]\(\)', ' ', s)
    s = re.sub(r'(^|\s)[|\-]+(?=\s|$)', ' ', s)
    s = re.sub(r'-\s*\n+\s*', '-', s)  # keep soft hyphen marker for line-end splits
    return s

LIG = ['fi', 'fl', 'ff', 'ffi', 'ffl']
def fix_lig(tok):
    m = re.match(r"^([^A-Za-z]*)([A-Za-z']+)([^A-Za-z]*)$", tok)
    if not m: return tok
    pre, w, post = m.groups()
    if z(w) >= 2.5 or len(w) < 2: return tok
    best, bz = w, z(w)
    for i in range(len(w) + 1):
        for lg in LIG:
            c = w[:i] + lg + w[i:]
            if z(c) > bz + 0.5: best, bz = c, z(c)
    if best != w and bz >= 2.5:
        if w[:1].isupper() and best[:1] == 'f' and False: pass
        return pre + best + post
    return tok

def key(tok):
    return re.sub(r"[^a-z0-9']", '', tok.lower())

def score(words):
    ws = [re.sub(r"[^A-Za-z']", '', w) for w in words]
    ws = [w for w in ws if w]
    if not ws: return 0
    ok = sum(1 for w in ws if z(w.strip("'")) >= 2.5 or (w[:1].isupper() and corpus_vocab[w.lower()] >= 3))
    return ok / len(ws) - 0.02 * len(ws)  # mild preference for fewer tokens (joined words)

log = open('merge_log.tsv', 'w')
stats = collections.Counter()
out = [parts[0]]
for i in range(1, len(parts), 2):
    head, body = parts[i], parts[i + 1]
    pno = int(re.search(r'\d+', head).group())
    out.append(head)
    ptxt = pdf.get(pno, '')
    ptoks = [fix_lig(x) for x in norm_pdf(ptxt).split()]
    ptoks = [x.replace('-', '') if re.match(r'^[a-z]+-[a-z]+[.,;:!?"]*$', x) and z(x.replace('-', '').strip('.,;:!?"')) >= 3 else x for x in ptoks]
    vspans = [(m.start(), m.end(), m.group()) for m in re.finditer(r'\S+', body)]
    if len(ptoks) < 0.8 * len(vspans) or not vspans:
        stats['page_skipped'] += 1; out.append(body); continue
    a = [key(s[2]) for s in vspans]; b = [key(x) for x in ptoks]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    edits = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != 'replace' or (i2 - i1) > 4 or (j2 - j1) > 4:
            if op != 'equal': stats['op_' + op] += 1
            continue
        vw = [s[2] for s in vspans[i1:i2]]; pw = ptoks[j1:j2]
        # same letters, different segmentation (r are -> rare) or a real word fix
        same_letters = ''.join(a[i1:i2]).replace("'", '') == ''.join(b[j1:j2]).replace("'", '')
        sv, sp = score(vw), score(pw)
        if same_letters and len(pw) < len(vw) and sp >= sv - 0.01:
            choose = True
        elif same_letters and len(pw) > len(vw) and sp > sv + 0.2:
            choose = True   # v2 wrongly glued words (undercovers -> under covers)
        elif not same_letters and sp > sv + 0.3:
            choose = True
        else:
            choose = False
        if choose:
            # keep v2 surrounding punctuation if pdf lost it
            new = ' '.join(pw)
            if vw[-1][-1:] in '.,;:!?"' and new[-1:] not in '.,;:!?"': new += vw[-1][-1]
            edits.append((vspans[i1][0], vspans[i2 - 1][1], new))
            stats['fix_seg' if same_letters else 'fix_word'] += 1
            log.write(f"{pno}\t{' '.join(vw)}\t{new}\n")
    for s, e, new in sorted(edits, reverse=True):
        body = body[:s] + new + body[e:]
    out.append(body)
open('v3.txt', 'w').write(''.join(out))
print(dict(stats))
