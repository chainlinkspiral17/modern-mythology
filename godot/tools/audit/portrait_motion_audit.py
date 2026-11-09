#!/usr/bin/env python3
"""portrait_motion_audit.py — how the cast moves on the stage (2026-11-09, report).

Simulates CharLayer over every chapter's show / hide / bg nodes, as the
runtime now plays them: a "center" show over a 3D set stands at an edge slot
(and a hide at "center" finds it there); a portrait leaving a slot is held for
DISPLACE_LINES (2) lines, and comes back by SLIDING from where it stood.

  FRESH_REAPPEAR  a NEW portrait fades in for someone whose last one left
                  <= 3 lines ago, outside the hold (a jump the eye sees)
  SLIDES          moves the slide carries (were fade-out + fade-in jumps)
  POPS            a portrait on screen for one line or less

Report only (not a gate). Before the slide: 32 jumps; after: 4 + 43 slides.
(2026-11-09) the remap applies only over a 3D set (bg src 3d:…), and a
three-shot's remapped centre slides home when its edge's owner arrives.

    python3 tools/audit/portrait_motion_audit.py [N]     # the N worst chapters
"""

import json, glob, re, sys
def key(c): return re.sub(r'[^a-z0-9]+','_',str(c).lower()).strip('_')
mode3d = "--2d" not in sys.argv
tot = {"FRESH_REAPPEAR":0,"SLIDES":0,"POPS":0}; per=[]
for f in sorted(glob.glob('resources/scenes/**/*.json',recursive=True)):
    try: j=json.load(open(f))
    except Exception: continue
    if not isinstance(j,dict) or not isinstance(j.get('nodes'),list): continue
    slots={"left":None,"center":None,"right":None}   # -> [key, asked, line_shown]
    disp={}   # key -> [pos, lines]
    left_at={}  # key -> line it left
    line=0; c={"FRESH_REAPPEAR":0,"SLIDES":0,"POPS":0}; bg3d=False
    def displace(p):
        s=slots[p]; slots[p]=None
        if s: 
            disp[s[0]]=[p,0]; left_at[s[0]]=line
            if line-s[2]<=1: c["POPS"]+=1
    for n in j['nodes']:
        if not isinstance(n,dict): continue
        t=n.get('t')
        if t in('narrate','say','think'):
            line+=1
            for k in list(disp):
                disp[k][1]+=1
                if disp[k][1]>2: del disp[k]
        elif t=='bg':
            slots={"left":None,"center":None,"right":None}; disp={}; left_at={}
            bg3d=str(n.get('src','')).startswith('3d:')
        elif t=='show':
            k=key(n.get('char','')); pos=n.get('pos','center')
            if pos not in slots: pos='center'
            asked=pos
            if mode3d and bg3d and pos=='center':
                if slots['right'] is None or slots['right'][0]==k: pos='right'
                elif slots['left'] is None or slots['left'][0]==k: pos='left'
            cur=[p for p,s in slots.items() if s and s[0]==k]
            if k in disp:
                del disp[k]
                if slots[pos] and slots[pos][0]!=k: displace(pos)
                slots[pos]=[k,asked,line]; c["SLIDES"]+=1; continue
            if cur and cur[0]!=pos:
                old=cur[0]; s=slots[old]; slots[old]=None
                if slots[pos]: displace(pos)
                slots[pos]=[k,asked,s[2]]; c["SLIDES"]+=1; continue
            if cur:
                slots[cur[0]][1]=asked; continue      # re-placed here: `asked` follows
            o=slots[pos]
            if o and o[0]!=k and o[1]=='center' and pos!='center' and slots['center'] is None:
                slots['center']=o; slots[pos]=None; c["SLIDES"]+=1     # a three-shot: centre slides home
            if slots[pos]: displace(pos)
            if k in left_at and line-left_at[k]<=3: c["FRESH_REAPPEAR"]+=1
            slots[pos]=[k,asked,line]
        elif t=='hide':
            pos=n.get('pos','')
            if pos=='':
                for p in list(slots): displace(p)
            else:
                if slots.get(pos) is None and mode3d and bg3d and pos=='center':
                    for p,s in slots.items():
                        if s and s[1]=='center': pos=p; break
                if pos in slots: displace(pos)
    for k in tot: tot[k]+=c[k]
    if c["POPS"] or c["FRESH_REAPPEAR"]: per.append((c["POPS"]+c["FRESH_REAPPEAR"], j.get('id'), c))
per.sort(reverse=True)
for r in per[:int(sys.argv[1]) if len(sys.argv)>1 and sys.argv[1].isdigit() else 12]: print(r)
print(tot, "chapters", len(per))
