#!/usr/bin/env python3
"""Restore MODERN_MYTHOLOGY_CLEANED_v2.txt into four per-volume markdown files.

Passes: strip running heads -> per-page lines -> hyphen joins -> split-word
repair -> garbage flagging -> reflow (prose) / keep lineation (verse, screenplay).
Every page keeps a <!-- p.N --> anchor (PDF page index) for checking.
"""
import re, json, sys, collections
from wordfreq import zipf_frequency as zf

SRC = 'v3.txt'
VOLS = {1: (1, 87), 2: (88, 176), 3: (177, 291), 4: (292, 413)}
OUT = 'out'

text = open(SRC).read()
parts = re.split(r'=== PAGE (\d+) ===', text)
pages = {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}
pdf = {int(k): v for k, v in json.load(open('pdf_pages.json')).items()}
pdf_blob = ' '.join(pdf.values()).lower().replace('$', "'")
pdf_vocab = collections.Counter(re.findall(r"[a-z]+", pdf_blob))

log = collections.Counter()
dropped = []
z = lambda w: zf(w.lower(), 'en')

# ---------- running heads ----------
HEAD_RES = [
    r'^page \d+$', r'^Page \d+$',
    r'^\d*\s*\[?\s*Small Wood Volumes\s*\]?\s*\d*$', r'^[a-z ]{0,4}od Volumes\]? ?\d*$', r'^Vood Volumes \d+$',
    r'^modern mythology\.$',
]
def strip_heads(pno, lines):
    out = []
    for i, l in enumerate(lines):
        s = l.strip()
        if any(re.match(r, s) for r in HEAD_RES) and not (pno <= 3):
            log['head'] += 1; continue
        if s == 'The Earthman Chronicles' and pno > 177 and i < 3:
            log['head'] += 1; continue
        out.append(l.rstrip())
    return out

# ---------- split-word repair ----------
SUFFIX = {'on', 'in', 'is', 'at', 'and', 'are', 'one', 'ate', 'by', 'ing', 'ion', 'ions', 'ation', 'ational',
          'inate', 'ina', 'ish', 'ise', 'ink', 'iss', 'ind', 'ine', 'ines', 'ision', 'isible', 'onal', 'ons', 'ongst',
          'onestly', 'm', 'n', 'se', 's', 'es', 'ats', 'ath', 'ar', 'ard', 'ately', 'atural', 'ather', 'iscover'}
KEEP_PAIRS = {('a', 'part'), ('a', 'way'), ('a', 'head'), ('any', 'one'), ('every', 'one'), ('some', 'one'),
              ('may', 'be'), ('in', 'to'), ('on', 'to'), ('no', 'one'), ('is', 'land'), ('for', 'ever'),
              ('at', 'one'), ('can', 'not'), ('all', 'ready'), ('all', 'together'), ('every', 'day'),
              ('some', 'times'), ('out', 'side'), ('in', 'side'), ('with', 'in'), ('up', 'on'), ('it', 'is'),
              ('is', 'in'), ('a', 'tone'), ('a', 'drift'), ('a', 'cross'), ('a', 'ware')}
def bigram_in_pdf(a, b):
    return pdf_blob.count(f' {a} {b} ')

STANDALONE = collections.Counter(re.findall(r"[A-Za-z]+", text))
ALLOW = {('be','fore'),('a','lone'),('to','ward'),('in','formation'),('our','selves'),('the','se'),('the','n'),('the','m'),
         ('comm','on'),('thous','and'),('but','ton'),('d','one'),('n','one'),('w','on'),('a','gain'),('a','gainst'),('be','cause'),
         ('be','tween'),('be','hind'),('be','yond'),('be','low'),('be','gan'),('be','gin'),('be','came'),('be','come'),('be','ing')}
def should_join(a, b):
    al, bl = a.lower(), b.lower()
    if (al, bl) in KEEP_PAIRS: return False
    if (al, bl) in ALLOW: return True
    ab = al + bl
    if len(ab) < 3: return False
    zab, za, zb = z(ab), z(al), z(bl)
    known = zab >= 2.0 or pdf_vocab.get(ab, 0) >= 1
    if not known:
        if a[:1].isupper() and bl in SUFFIX and za < 3.5 and len(ab) >= 5 and STANDALONE[a] < 4: return True
        return False
    if bigram_in_pdf(al, bl) > pdf_vocab.get(ab, 0): return False
    # protect names / real words that stand alone often (Faust is, Jacob and)
    if a[:1].isupper() and STANDALONE[a] >= 4 and za >= 2.5: return False
    if za >= 4.5 and zb >= 4.5 and len(al) > 1: return False
    if len(al) == 1 and al in 'ai': return False
    if len(al) == 1 and al in 'stdm' and zb >= 4.4 and not (bl in SUFFIX and zab >= 3.5): return False
    if bl in SUFFIX: return True
    return za < 3.0 or zb < 3.0 or len(al) == 1

def triple_join(l):
    def rep(m):
        a, b, c = m.group(1), m.group(2), m.group(3)
        j = a + b + c
        if z(j) >= 2.0 and min(z(a), z(b), z(c)) < 3.0 and len(j) >= 6:
            log['triple'] += 1; return j
        return m.group(0)
    return re.sub(r"\b([A-Za-z]{1,6}) ([a-z]{1,6}) ([a-z]{1,8})\b", rep, l)

APOS = re.compile(r"\b(i|you|we|they|he|she|it|that|there|what|who|let|don|can|won|isn|wasn|didn|doesn|couldn|wouldn|shouldn)\s(m|ve|ll|d|re|s|t)\b", re.I)
POSS = re.compile(r"\b(it|that|what|there|he|she|who|let|here|where|everyone|nobody|[A-Z][a-z]+)\s(s)\b(?=\s+[A-Za-z])")
def repair_line(l):
    l = APOS.sub(lambda m: f"{m.group(1)}'{m.group(2)}", l)
    l = POSS.sub(lambda m: f"{m.group(1)}'s", l)
    l = re.sub(r"\b(I|you|we|they|he|she|it) 1l\b", r"\1'll", l)
    l = re.sub(r"(?<=[a-z,] )1(?= [a-z])|^1(?= [a-z])", "I", l)
    l = triple_join(l)
    toks = re.split(r'(\s+)', l)
    out = []
    i = 0
    while i < len(toks):
        t = toks[i]
        if i + 2 < len(toks) and toks[i + 1] == ' ':
            a, b = t, toks[i + 2]
            ma = re.match(r"^(.*?)([A-Za-z]+)$", a); mb = re.match(r"^([A-Za-z]+)(.*)$", b)
            if ma and mb and should_join(ma.group(2), mb.group(1)):
                toks[i + 2] = ma.group(1) + ma.group(2) + mb.group(1) + mb.group(2)
                log['join'] += 1; log[f'J:{ma.group(2).lower()}+{mb.group(1).lower()}'] += 1
                i += 2; continue
        out.append(t); i += 1
    l = ''.join(out)
    l2 = APOS.sub(lambda m: f"{m.group(1)}'{m.group(2)}", l)
    if l2 != l: log['apos'] += 1
    l2 = re.sub(r"\b(d|c)\s(on't|an't)\b", r"\1\2", l2)
    return l2

# ---------- garbage detection ----------
def garbage(l):
    s = l.strip()
    if not s: return False
    words = re.findall(r"[A-Za-z]+", s)
    sym = len(re.findall(r"[^A-Za-z0-9\s.,'\"!?;:\-—()&/]", s))
    if not words: return len(s) > 2 and not re.match(r'^[\-—–*#.…!?"\'()\[\]0-9 ]+$', s)
    good = sum(1 for w in words if (len(w) > 1 and z(w) >= 2.0) or w[:1].isupper() and len(w) > 3 or w.lower() in ('a', 'i', 'o'))
    shorty = sum(1 for w in words if len(w) <= 2)
    if sym > 3: return True
    if len(words) >= 3 and good / len(words) < 0.45: return True
    if len(words) <= 2 and good == 0 and all(len(w) <= 3 for w in words): return True
    return False

# ---------- line classing ----------
CUE = re.compile(r"^(THE [A-Z ]+|[A-Z][A-Z .'\-]{1,30})(\s*\([^)]*\))?$")
SLUG = re.compile(r"^(INT\.|EXT\.|INT\. AND EXT\.|INSERT:|MONTAGE|INFOGRAPHIC|PICTURE AND TEXT|CRUDE ANIMATION|VOICE OVER|DISCLAIMER|A TRAILER|FAUSTS NARRATION)")
CHAT = re.compile(r"^[a-z]{2,10}:\s")

def is_cue(s):
    return bool(CUE.match(s)) and len(s) < 45 and not s.endswith('.') or s in ('THE FOOL',)

def hyph_join(stem, first):
    st = re.sub(r"\W", "", stem); fi = re.sub(r"\W", "", first)
    j = st + fi
    if z(j) >= 1.5 or pdf_vocab.get(j.lower(), 0): return True
    return not (z(st) >= 3.0 and z(fi) >= 3.0)

FIXES = [("Nathanielress", "mattress"), ("Nathanieler", "matter")]

def reflow_block(lines, width):
    """Join wrapped prose lines; keep short lines that end a sentence as paragraph ends."""
    paras, cur = [], ''
    for l in lines:
        s = l.strip()
        if not s:
            if cur: paras.append(cur); cur = ''
            continue
        if CHAT.match(s) or is_cue(s) or SLUG.match(s):
            if cur: paras.append(cur); cur = ''
            paras.append(s); continue
        if cur.endswith('-') and re.search(r'[a-z]-$', cur):
            stem = cur[:-1].split()[-1] if cur[:-1].split() else ''
            first = s.split()[0]
            if hyph_join(stem, first):
                cur = cur[:-1] + s; log['hyph'] += 1
            else:
                cur = cur + s
        else:
            cur = (cur + ' ' + s) if cur else s
        if len(s) < width * 0.62 and re.search(r'[.!?"”:)]$', s):
            paras.append(cur); cur = ''
    if cur: paras.append(cur)
    return paras

def block_is_wrapped(lines):
    ls = [len(l.strip()) for l in lines if l.strip()]
    if len(ls) < 2: return False, 0
    long = [x for x in ls if x >= 48]
    return len(long) / len(ls) >= 0.5, (max(ls) if ls else 60)

def render_page(pno, raw):
    lines = strip_heads(pno, raw.split('\n'))
    lines = [repair_line(l) for l in lines]
    for a_, b_ in FIXES: lines = [l.replace(a_, b_) for l in lines]
    # flag garbage runs
    flagged, run = [], 0
    for l in lines:
        if garbage(l):
            run += 1; log['garbage_line'] += 1
            if run == 1: flagged.append('[[ILLEGIBLE IN SOURCE — recover from PDF p.%d]]' % pno)
            dropped.append((pno, l))
            continue
        run = 0; flagged.append(l)
    # blocks separated by blank lines
    blocks, cur = [], []
    for l in flagged:
        if l.strip() == '':
            if cur: blocks.append(cur); cur = []
        else: cur.append(l)
    if cur: blocks.append(cur)
    out = []
    for b in blocks:
        wrapped, width = block_is_wrapped(b)
        if wrapped:
            out.extend(reflow_block(b, width)); out.append('')
        else:
            # verse / screenplay: keep lineation, but mend trailing hyphen breaks
            merged = []
            for l in b:
                s = l.rstrip()
                if merged and re.search(r'[a-z]-$', merged[-1]) and s and s[0].islower():
                    stem = merged[-1][:-1].split()[-1]; first = s.split()[0]
                    if hyph_join(stem, first):
                        merged[-1] = merged[-1][:-1] + s; log['hyph'] += 1; continue
                merged.append(s)
            out.extend(merged); out.append('')
    return out

def to_markdown(lines):
    md = []
    for s in lines:
        t = s.strip()
        if not t: md.append(''); continue
        if t.startswith('[[ILLEGIBLE'): md.append(f'> {t}'); continue
        if SLUG.match(t): md.append(f'\n#### {t}\n'); continue
        if is_cue(t) and t.upper() == t:
            md.append(f'\n**{t}**  '); continue
        md.append(t + ('  ' if not t.endswith('  ') else ''))
    s = '\n'.join(md)
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s

def build(vol):
    a, b = VOLS[vol]
    chunks = []
    for p in range(a, b + 1):
        if p not in pages: chunks.append(f'\n<!-- p.{p}: missing from v2 extraction -->\n'); log['missing_page'] += 1; continue
        body = to_markdown(render_page(p, pages[p]))
        chunks.append(f'\n<!-- p.{p} -->\n' + body.strip() + '\n')
    return ''.join(chunks)

if __name__ == '__main__':
    import os; os.makedirs(OUT, exist_ok=True)
    for v in VOLS:
        open(f'{OUT}/vol{v}_raw_restored.md', 'w').write(build(v))
    top = [(k, n) for k, n in log.most_common() if k.startswith('J:')][:40]
    open('dropped_lines.tsv','w').write(''.join(f'{p}\t{l}\n' for p,l in dropped))
    print({k: n for k, n in log.items() if not k.startswith('J:')})
    print(top)
