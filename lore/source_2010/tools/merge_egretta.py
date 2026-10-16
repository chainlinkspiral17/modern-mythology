"""Second reconciliation pass: Andy's own typed text in Egretta Society (2013-15)
covers much of Small Wood + early Earthman + some poems. Use it to fix OCR
tokens on overlapping pages (conservative: only where it reads better)."""
import re, difflib, collections
from wordfreq import zipf_frequency as zf
z=lambda w: zf(w.lower(),'en')
BAN = re.compile(r"♥|Bright Falls|Alan Wake|Wake\b|Zane|Jagger|Night Springs|Mutter", re.I)
eg_raw=open('meta/egretta_society.txt').read()
eg_toks=eg_raw.split()
key=lambda t: re.sub(r"[^a-z0-9']","",t.lower())
ek=[key(t) for t in eg_toks]
index=collections.defaultdict(list)
for i in range(len(ek)-4): index[tuple(ek[i:i+5])].append(i)
t=open('v3.txt').read(); parts=re.split(r'(=== PAGE \d+ ===)',t)
corpus=collections.Counter(re.findall(r"[a-z]+",t.lower()))
def score(ws):
    ws=[re.sub(r"[^A-Za-z']","",w) for w in ws]; ws=[w for w in ws if w]
    if not ws: return 0
    return sum(1 for w in ws if z(w.strip("'"))>=2.5 or corpus[w.lower()]>=3)/len(ws)-0.02*len(ws)
log=open('merge_egretta_log.tsv','w'); st=collections.Counter(); out=[parts[0]]
for i in range(1,len(parts),2):
    head,body=parts[i],parts[i+1]; out.append(head)
    vs=[(m.start(),m.end(),m.group()) for m in re.finditer(r'\S+',body)]
    vk=[key(x[2]) for x in vs]
    hits=collections.Counter()
    for j in range(len(vk)-4):
        for pos in index.get(tuple(vk[j:j+5]),[]): hits[(pos-j)//50]+=1
    if not hits or hits.most_common(1)[0][1]<8: out.append(body); continue
    off=hits.most_common(1)[0][0]*50
    a0=max(0,off-60); seg=eg_toks[a0:a0+len(vs)+160]; sk=ek[a0:a0+len(vs)+160]
    sm=difflib.SequenceMatcher(None,vk,sk,autojunk=False); edits=[]
    for op,i1,i2,j1,j2 in sm.get_opcodes():
        if op!='replace' or i2-i1>3 or j2-j1>3: continue
        vw=[x[2] for x in vs[i1:i2]]; pw=seg[j1:j2]
        if BAN.search(' '.join(pw)): st['banned']+=1; continue
        same=''.join(vk[i1:i2]).replace("'","")==''.join(sk[j1:j2]).replace("'","")
        sv,sp=score(vw),score(pw)
        if (same and len(pw)<len(vw) and sp>=sv-0.01) or (not same and len(pw)==len(vw) and sp>sv+0.3 and not any(k in ' '.join(pw) for k in ['Alsace'])):
            new=' '.join(pw).replace('’',"'")
            if vw[-1][-1:] in '.,;:!?"' and new[-1:] not in '.,;:!?"': new+=vw[-1][-1]
            edits.append((vs[i1][0],vs[i2-1][1],new)); st['fix']+=1
            log.write(f"{head[9:-4]}\t{' '.join(vw)}\t{new}\n")
    for s_,e_,n_ in sorted(edits,reverse=True): body=body[:s_]+n_+body[e_:]
    out.append(body); st['pages']+=1
open('v3.txt','w').write(''.join(out)); print(dict(st))
