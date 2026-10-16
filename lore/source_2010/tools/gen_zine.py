#!/usr/bin/env python3
"""Rebuild the 2010 zine "weep (FOR THE FUTURE!)" issue six (book pp 309-316)
as clean xerox-style page images. Text comes from recovered/backmatter.md;
photos are cropped from Andy's own page scans (zine/crops). The corporate-logo
parody on p.311 is replaced by an original seal."""
import re, os, html, asyncio, random
from PIL import Image, ImageFilter, ImageOps, ImageChops

ROOT = '/home/claude/mm_src'
FONTS = '/home/claude/modern-mythology/godot/resources/fonts'
OUT = f'{ROOT}/zine/build'
os.makedirs(OUT, exist_ok=True)
W, H = 1650, 2550  # 5.5 x 8.5 in @ 300 dpi

src = open(f'{ROOT}/recovered/backmatter.md').read()
pages = dict((int(a), b) for a, b in re.findall(r'<!-- p\.(\d+) -->\n(.*?)(?=\n<!-- p\.|\Z)', src, re.S))

def blocks(p):
    out = []
    for m in re.finditer(r'\[(block|image): ([^\]]*)\]\s*(.*?)(?=\n\[(?:block|image):|\Z)', pages[p], re.S):
        out.append((m.group(1), m.group(2).strip(), m.group(3).strip()))
    return out

def md(t):
    t = html.escape(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', t)
    t = re.sub(r'~~(.+?)~~', r'<s>\1</s>', t)
    return t

def paras(t):
    return ''.join(f'<p>{md(x.strip())}</p>' for x in re.split(r'\n\s*\n|\n(?=\*\*\()', t) if x.strip())

CSS = f'''
@font-face{{font-family:Elite;src:url(file://{FONTS}/SpecialElite-Regular.ttf)}}
@font-face{{font-family:Bebas;src:url(file://{FONTS}/BebasNeue-Regular.ttf)}}
@font-face{{font-family:Courier;src:url(file://{FONTS}/CourierPrime-Regular.ttf)}}
@font-face{{font-family:Fell;src:url(file://{FONTS}/IMFellEnglish-Regular.ttf)}}
@font-face{{font-family:FellI;src:url(file://{FONTS}/IMFellEnglish-Italic.ttf)}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{W}px;height:{H}px;background:#f3f1ea;overflow:hidden}}
body{{position:relative;color:#111;font-family:"GFS Baskerville","FreeSerif",serif}}
.abs{{position:absolute}}
.box{{background:#f6f4ee;border:3px solid #111;padding:28px 32px}}
.fit p{{margin:0 0 .55em}}
.tape{{background:rgba(235,232,220,.92);box-shadow:0 0 0 2px #222 inset;padding:6px 16px;font-family:"Inter";font-weight:900;letter-spacing:-1px}}
.folio{{position:absolute;top:60px;width:100%;text-align:center;font:44px "FreeSerif";color:#555}}
img.ph{{position:absolute;object-fit:cover;filter:contrast(1.15)}}
.col{{column-gap:60px}}
'''
FIT_JS = '''
for (const el of document.querySelectorAll('.fit')) {
  let fs = parseFloat(getComputedStyle(el).fontSize);
  while ((el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1) && fs > 9) {
    fs -= 0.5; el.style.fontSize = fs + 'px';
  }
}
'''
def page(body, folio=''):
    f = f'<div class="folio">{folio}</div>' if folio else ''
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{f}{body}</body></html>'

C = f'file://{ROOT}/zine/crops'
docs = {}

# ---------- p.309 cover + hasslein interview ----------
b = blocks(309)
get = lambda bs, key: next(t for k, lab, t in bs if key in lab)
facts = get(b, 'sidebar, right').split('\n')
cols = [get(b, f'interview column {i}') for i in (1, 2, 3)]
docs[309] = page(f'''
<img class="ph" src="{C}/309_mast_texture.png" style="left:0;top:150px;width:1650px;height:300px;opacity:.85">
<div class="abs" style="left:70px;top:170px;font:250px/1 'Fell';letter-spacing:-8px;color:#111;background:#f3f1ea;padding:0 24px 10px">weep</div>
<div class="abs" style="left:640px;top:250px;font:96px/1 'Fell';letter-spacing:-2px;background:#f3f1ea;padding:4px 14px"><s style="text-decoration-thickness:8px">(FOR THE FUTURE!)</s></div>
<div class="abs tape" style="left:700px;top:395px;font-size:44px;line-height:1;transform:rotate(-2deg)">distribute<br>at your<br>own peril</div>
<div class="abs tape" style="left:1010px;top:420px;font-family:Bebas;font-weight:400;font-size:96px;letter-spacing:2px;transform:rotate(1.5deg);background:#111;color:#eee">issue six</div>
<img class="ph" src="{C}/309_helmet.png" style="left:780px;top:600px;width:800px;height:560px">
<div class="abs" style="left:70px;top:610px;width:250px;font:900 74px/0.95 'Inter';letter-spacing:-2px;color:#222">seven facts about our subject</div>
<div class="abs fit" style="left:290px;top:615px;width:450px;height:420px;text-align:right;font:700 34px/1.35 'FreeSerif'">{'<br>'.join(md(x) for x in facts if x.strip())}</div>
<div class="abs" style="left:900px;top:1170px;font:900 150px/1 'Inter';letter-spacing:-6px;background:#f3f1ea;padding:0 20px">hasslein</div>
<div class="abs" style="left:910px;top:1120px;font:44px 'FreeSerif';background:#f3f1ea;padding:0 10px">interview with</div>
<div class="abs fit box" style="left:70px;top:1090px;width:760px;height:760px;font-size:32px;line-height:1.3">{paras(cols[0])}</div>
<img class="ph" src="{C}/309_gun.png" style="left:70px;top:1890px;width:760px;height:590px">
<div class="abs fit box" style="left:860px;top:1340px;width:720px;height:1140px;font-size:30px;line-height:1.3">{paras(cols[1] + chr(10)*2 + cols[2])}</div>
''', '//')

# ---------- p.310 letter from the editor + plannED commUNITY ----------
b = blocks(310)
letter = get(b, 'typewriter-face column'); sig = get(b, 'signature'); boxed = get(b, 'boxed text')
stars = ''.join(f'<div class="abs" style="left:{random.Random(i).randint(40,520)}px;top:{random.Random(i*7).randint(1800,2450)}px;font:{random.Random(i*3).randint(60,120)}px FreeSerif;color:#777;transform:rotate({random.Random(i*5).randint(-30,30)}deg)">☆</div>' for i in range(14))
docs[310] = page(f'''
<div class="abs" style="left:0;top:1750px;width:820px;height:800px;background:repeating-linear-gradient(-12deg,#d9d6cc 0 70px,#f3f1ea 70px 140px)"></div>{stars}
<div class="abs tape" style="left:90px;top:200px;font:400 40px 'Courier';letter-spacing:0">letter from the editor</div>
<div class="abs fit box" style="left:90px;top:290px;width:720px;height:1450px;font:34px/1.42 'Courier';transform:rotate(-1.2deg)">{paras(letter)}<p style="text-align:right;font-family:Elite;font-size:1.3em">{md(sig)}</p></div>
<img class="ph" src="{C}/310_engraving.png" style="left:300px;top:1790px;width:290px;height:360px;border:6px solid #111;transform:rotate(-3deg)">
<div class="abs" style="left:850px;top:200px;font:900 68px/1 'Inter';letter-spacing:-3px;white-space:nowrap;background:#111;color:#f3f1ea;padding:8px 18px">plannED commUNITY</div>
<div class="abs fit box" style="left:880px;top:360px;width:700px;height:820px;font-size:36px;line-height:1.36">{paras(boxed)}</div>
<img class="ph" src="{C}/310_collage.png" style="left:870px;top:1240px;width:720px;height:1220px;transform:rotate(2deg)">
''', '311')

# ---------- p.311 review / religion / corporations + original seal ----------
b = blocks(311)
left = get(b, 'left column'); right = get(b, 'right column')
seal = '''<svg class="abs" style="left:575px;top:1900px" width="500" height="500" viewBox="0 0 200 200">
<defs><path id="ring" d="M100,100 m-74,0 a74,74 0 1,1 148,0 a74,74 0 1,1 -148,0"/></defs>
<circle cx="100" cy="100" r="98" fill="#111"/><circle cx="100" cy="100" r="62" fill="#f3f1ea"/>
<text font-family="Inter" font-weight="900" font-size="30" fill="#f3f1ea" letter-spacing="3"><textPath href="#ring" startOffset="0" textLength="460">★ FUCK OFF ★ FUCK OFF</textPath></text>
<g fill="none" stroke="#111" stroke-width="5"><path d="M62,100 Q100,62 138,100 Q100,138 62,100Z"/><circle cx="100" cy="100" r="15" fill="#111"/></g>
<path d="M100,40 L100,78 M100,122 L100,160 M40,100 L56,100 M144,100 L160,100" stroke="#111" stroke-width="4"/>
<text x="100" y="146" text-anchor="middle" font-family="Bebas" font-size="15" fill="#111">E / D</text></svg>'''
docs[311] = page(f'''
<img class="ph" src="{C}/311_bg.png" style="left:0;top:180px;width:1650px;height:2200px;opacity:.9">
<div class="abs fit box" style="left:110px;top:300px;width:680px;height:1560px;font-size:34px;line-height:1.36">{paras(left)}</div>
<div class="abs fit box" style="left:860px;top:300px;width:680px;height:1560px;font-size:34px;line-height:1.36">{paras(right)}</div>
{seal}
''', '#')

# ---------- pp.312-315 "rote" ----------
def rote_text(p):
    out = []
    for k, lab, t in blocks(p):
        if k == 'block' and ('story' in lab or 'epigraph' in lab):
            out.append(t)
    return '\n\n'.join(out)
for p, folio in zip([312, 313, 314, 315], ['313', '#', '315', '#']):
    bs = blocks(p)
    title = '<div class="abs" style="left:110px;top:150px;font:96px Elite">rote</div>' if p == 312 else ''
    note = ''
    if p == 315:
        n = next((t for k, lab, t in bs if 'contributor' in lab), '')
        note = f'<div class="abs box" style="left:950px;top:2240px;width:600px;font-size:28px;line-height:1.3">{md(n)}</div>'
    top = 280 if p == 312 else 170
    bottom = 2190 if p == 315 else 2420
    docs[p] = page(f'''
<img class="ph" src="{C}/{p}_bg.png" style="left:0;top:120px;width:1650px;height:2330px;opacity:.85">
{title}
<div class="abs fit" style="left:110px;top:{top}px;width:1430px;height:{bottom-top}px;font:30px/1.38 'Courier';column-count:2;column-gap:70px;text-align:justify;hyphens:auto">{paras(rote_text(p))}</div>
{note}''', folio)

# ---------- p.316 triptych / kinesthesia (rotated) ----------
b = blocks(316)
panels = [get(b, f'rotated panel {i}') for i in (1, 2, 3)]
inner = ''.join(f'<div class="fit" style="width:640px;height:1240px;background:#f3f1ea;border:4px solid #111;padding:34px;font:32px/1.36 Inter;flex:none">{paras(t)}</div>' for t in panels)
docs[316] = page(f'''
<img class="ph" src="{C}/316_bg.png" style="left:110px;top:200px;width:1430px;height:2260px;opacity:1">
<div class="abs" style="left:{W/2-1080}px;top:{H/2-700}px;width:2160px;height:1400px;transform:rotate(90deg);transform-origin:center;display:flex;gap:40px;align-items:center;justify-content:center">
  <div style="font:900 120px Inter;writing-mode:vertical-rl;transform:rotate(180deg);letter-spacing:-3px">triptych</div>{inner}
  <div style="font:900 120px Inter;writing-mode:vertical-rl;transform:rotate(180deg);letter-spacing:-3px">kinesthesia</div>
</div>''', '317')

for p, d in docs.items():
    open(f'{OUT}/zine_p{p}.html', 'w').write(d)

async def render():
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--allow-file-access-from-files'])
        pg = await br.new_page(viewport={'width': W, 'height': H})
        for p in docs:
            await pg.goto(f'file://{OUT}/zine_p{p}.html'); await pg.wait_for_timeout(300)
            await pg.evaluate(FIT_JS); await pg.wait_for_timeout(100)
            await pg.screenshot(path=f'{OUT}/raw_p{p}.png')
        await br.close()
asyncio.run(render())

def xerox(path_in, path_out, seed):
    rnd = random.Random(seed)
    im = Image.open(path_in).convert('L')
    noise = Image.effect_noise(im.size, 28).filter(ImageFilter.GaussianBlur(0.6))
    im = ImageChops.multiply(im, ImageOps.autocontrast(noise).point(lambda v: 210 + v * 45 // 255))
    im = im.point(lambda v: 0 if v < 70 else (255 if v > 228 else int((v - 70) * 255 / 158)))
    # toner streak + edge darkening
    streak = Image.new('L', im.size, 255)
    x = rnd.randint(200, im.size[0] - 200)
    for dx in range(-3, 4):
        streak.paste(235 + abs(dx) * 5, (x + dx, 0, x + dx + 1, im.size[1]))
    im = ImageChops.multiply(im, streak)
    im = im.filter(ImageFilter.UnsharpMask(1.2, 80, 2))
    im.save(path_out, optimize=True)

os.makedirs(f'{ROOT}/final/images/zine', exist_ok=True)
for i, p in enumerate(docs):
    xerox(f'{OUT}/raw_p{p}.png', f'{ROOT}/final/images/zine/vol4_zine_weep_p{p}.png', i)
print('rendered', list(docs))
