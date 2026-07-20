# THE TIDELINE · DESIGN
### Oneironautics Inc. · Portland OR · 2004 · SURVEY WALK / MEASUREMENT-AS-ATTENTION
### one king-tide morning · twelve stations · a notebook with room for less than you'll see
### STATUS: BUILT · playable_v1 (2026-07) · host + TidelineWalk,
### twelve stations, two-line notebook discipline, the seal, the
### 220 Hz buoy, the report in four registers — AND the Meridian
### Heritage remake (Tideline Survey, 2048) on the same engine,
### demonstrating in play exactly what the remake got wrong

Ines Rocha, solo, 2004 — the year after Mrs. Wu's Garden, the
year before she pitched Estuary 4. The E1/E2 DNA matured: Estuary
1 was one lever watched for twelve weeks; Estuary 2 was species
math; THE TIDELINE is the synthesis — a survey walk where the
instrument is your attention and the attention is finite.

Canon fixed points honored: Ines solo 2004 (lattice) · Olaf's
copy came "on Ines Rocha's insistence via a mutual friend"
(shelf_layout, prior canon) · Meridian Heritage Interactive
licensed the catalog in 2041 and shipped TIDELINE SURVEY in 2048
(lattice) — meaning the original mattered, and Tem's copy of the
remake sits three slots from Olaf's original on the same shelf.

## THE PLAYER

A volunteer on the annual king-tide wrack-line survey. One
morning in December 2003, one beach on the Oregon coast — the
stretch between the creek mouth and the point, never named more
than that. The county gives volunteers a pencil and a printed
notebook. The notebook has TWO ruled lines per station. That
ratio — two lines, four or five things worth a line at every
station — is the entire game.

## THE PLAYSTYLE

**Twelve stations, walked in order. Two notebook lines each.**

- Arrive at a station: a paragraph of what's there, then the
  observable things as a list — a dead gull mid-disassembly by
  live ones, a Japanese float twenty years at sea, the wrack line
  itself doing something the manual has a code for and the beach
  doesn't. RECORD one (one line, one slot) or WALK ON with slots
  unspent — unspent lines stay blank forever; the notebook keeps
  your restraint as faithfully as your attention.
- Observations carry a quiet category — THE LIVING · THE LOST ·
  THE LINE — never shown as a tag, only felt in the writing.
- **Recurrences:** the same gull works the whole beach (stations
  2, 5, 9 — the lines evolve if you keep choosing it). The seal
  surfaces at 3, at 7, and finally at 11.
- **Station 6 · the bell buoy.** The notebook is pre-printed:
  "buoy, bell, tone (A3 · 220 Hz)". The notebook is right. That
  is all the game ever says about it.
- **Station 11 · the seal, close.** A third option that is not
  an observation: PUT THE PENCIL DOWN AND WATCH. It spends both
  remaining lines and writes nothing. Some entries are not
  entries. (Token: `tideline_the_seal`.)
- **Station 12 · the point. THE REPORT.** The walk ends and the
  survey reads your notebook back as a coastline — your 24 (or
  fewer) lines assembled in order. The register comes from what
  you attended to: THE LIVING SHORE · THE SHORE OF LOST THINGS ·
  THE LINE ITSELF · or, balanced, THE WHOLE BEACH. Last line
  always: "Filed with the county. Read, later, by exactly one
  person, carefully." (Who reads the county's files carefully is
  a question Estuary 4's pitch year will care about.)

## TIDELINE SURVEY (Meridian Heritage, 2048) · the remake · same engine

Tem's cart. Same twelve stations, same beach, rebuilt "faithfully"
by Meridian Heritage — and the build DEMONSTRATES the thesis by
deleting it:

- **Auto-record.** At every station the sensor suite logs every
  observation instantly — "4 observations · 0.3 s · confidence
  99.2%" — and the only button is CONTINUE. Nothing is chosen,
  so nothing is attended. The walk takes three minutes.
- **The metrics strip** counts coverage and efficiency the whole
  way, proudly.
- **Station 11 survives.** One manual prompt remains — flagged
  in-product as *HERITAGE COMPLIANCE · original interaction
  preserved per license §4(c)* — the pencil, the seal, the watch.
  It is the only choice in the cart, it is Ines's, and the
  license made them keep it. (Token: `tideline_2048_the_seal_still`.)
- **The report:** SURVEY COMPLETE · 41/41 · NOTHING WAS MISSED —
  complete, exhaustive, and empty of anyone. Register: THE
  COMPLETE RECORD.
- Finishing BOTH carts drops `tideline_original_compared` — the
  scrapbook entry that says out loud what the shelf has been
  arguing all along.

**What the remake got wrong, stated for the record:** it kept
every station, every observation, every string — and removed the
two-line limit, because limits test poorly. The limit was the
game. Completeness is not attention; a sensor cannot put the
pencil down.

## TOKENS

Original: `the_tideline_finished` · `tideline_full_notebook`
(all 24 lines spent) · `tideline_the_seal`.
Remake: `tideline_survey_2048_finished` ·
`tideline_2048_the_seal_still`.
Both: `tideline_original_compared`.
In: none. (The buoy's 220 Hz is an out-braid only; it resolves
nothing and never will.)

## THE LOOK

Original: `oneironautics` (field-guide gouache) — grey-green
December light, text-forward stations, the notebook rendered as
ruled lines that fill in your hand.
Remake: NEW `meridian` preset added house-wide per the aesthetic
bible (extend, don't fork): palette_size 48, dither 0, scanlines
0, aberration 0 — perfectly, wrongly clean. The sterility is the
period rendering of 2048, not retro cosplay of it.

## THE SOUND

Deferred to a future audio wave ("the wrack line" · gulls, bell
buoy at true 220 Hz, gray surf). Until then the original runs on
e2/e1 shore ambience if present, else quiet; the remake runs
SILENT except UI ticks, which is correct for it.

## BUILD

TidelineHost + TidelineWalk (sweetgum-pattern minimal stick),
`remake_mode` flag set by SlowstockBoot before add_child (the
Counselor Mode pattern). Shared data `tideline.json` under
the_tideline; the remake's manifest points at the same walk
scene. Both shelf slots and unlock waves were pre-scaffolded
(the_tideline: wave 4, Olaf's copy · tideline_survey_2048:
wave 5, Tem's copy) — FULL_MANIFESTS + SlowstockBoot + manifests
are the new pieces, plus the `meridian` preset in SlowstickLook
and StickTheme.
