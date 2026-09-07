# THE PSYCHEDELIC DESIGN BIBLE · THE TRIP (2026-09-07 · draft 2)

The project-wide theme, in the user's words:

> "Big project theme, psychedelic art and visuals. Realism but
> trippy, I always wanted this running through the game at all
> times, in lines and backgrounds, synced to the music currently
> playing."
>
> "Slowstick games, too. Jeff Minter like design and visuals. Only
> using current hardware. And game design."
>
> "Major Arcana is swampy and arcade inspired. Planned Community:
> retro video games and zines and stoner sludge meta punk rock.
> Land of Milk and Honey is SCUMM game inspired, psychedelic wall
> of sound classic rock but sci-fi."

Read this before touching `godot/autoload/TripSync.gd`,
`godot/assets/shaders/trip_sync.gdshader`, any pillar's look, or
any pillar's game-design direction. Companion to
`_SHADER_VISUALS_PLAYBOOK.md` (the stack) and
`_SLOWSTICK_AESTHETIC_BIBLE.md` (the no-retro-cosplay doctrine,
which this document extends to the whole game).

## Core rules

0. **THE MOTION RULE (draft 3).** Draft 1 was "mostly nausea
   inducing"; draft 2 (a still image) then 2B (faint) "lost all the
   best parts." The balance: the flats may drift — slowly, like
   water under glass — but the motion is NEAR-CONSTANT and NEVER
   SYNCED TO THE BEAT. What made draft 1 sick was pumping: a
   displacement amplitude that jumped with the bass (7 + 22·bass px,
   breathing on the bar), a ripple that wobbled the whole frame on
   every kick, a zoom thump, a chromatic split, a brightness dip.
   All of those stay gone for good. What lives: a 6 + 6·energy px
   liquid drift in the OPEN regions only (edges and text never move),
   a field that moves at a fraction of draft 1's rate; the beat is a
   ring of LIGHT, never a displacement; the pulse has a 45 ms attack;
   hue rotation on large areas is capped (±0.55 rad) and slow. The
   player holds the FLOW dial (Settings.trip_flow) — 0 is a still
   image — beside LINES, COLOUR and BEAT.
1. **Realism but trippy.** The picture stays the picture. THE TRIP
   never crushes a palette, never ASCII-fies, never fills. It rides
   on the lines (edge aura) and the backgrounds (flat-region flow,
   capped hue drift) and leaves geometry outlines and text sharp.
   If a pass makes a wall unreadable or a face green, it failed.
2. **At all times.** One autoload (TripSync), one shader
   (trip_sync.gdshader), one global layer (CanvasLayer 60 —
   above every scene PostProcess stack at 50, below the slowstick
   look at 80 and HUD at 100). Text-heavy surfaces that must keep
   their type clean join `"trip_local"` and attach the same shader
   in texture mode to their backgrounds (the VN does). Nothing
   opts out entirely; the dial is `Settings.trip_amount`.
3. **Synced to the music currently playing.** Everything moves to
   the BGM bus spectrum: energy, three bands, a low-band beat
   pulse, a tempo-locked beat/bar phase, a music-paced flow clock.
   No visual clock runs free of the track except the idle breath
   when nothing plays.
4. **Current hardware only.** The Minter register is made of what a
   2026 GPU does well — additive glow, particle storms, feedback
   buffers, a screen that thumps — never of simulated 1980s
   failure. No scanline loops, no phosphor fiction, no 8-bit
   palette clamps as "authenticity." (The slowstick bible's rule,
   now global.) Period flavour comes from palette, composition,
   type, and game grammar.
5. **Registers, not per-host uniforms.** A pillar's look is a
   named entry in `TripSync.REGISTERS`. Hosts push a register with
   themselves as owner (`TripSync.push_register("arcana", self)`);
   it pops by itself when the owner leaves the tree. Nobody sets
   trip uniforms inline. New pillar, new register.
6. **Game design carries the register too.** The visual register
   is the half we can ship from the container; each pillar also
   has a GAME grammar below that every design pass should pull
   toward. A pass that only adds shader dials is half a pass.

## Direction: the three dials the director holds (draft 4)

The player's PSYCHEDELIA slider is the ceiling (default **75 %**,
the user's call 2026-09-07: "75 percent seems about right for me
right now as default"). Under it, direction sets the level per beat:

1. **Per mood** — every `MoodCycler` preset carries a `trip_scale`.
   Dark and dreaming moods run hot (dream_blur 1.35, liminal_interior
   1.35, arcana_neon 1.3, arcana_cool 1.25, macro_haze 1.2, smoky_bar
   1.2, candlelight_low 1.15, tv_glow_blue 1.15, 3_47_am / precipice
   1.4); bright, plain daylight runs cool (day_bright 0.7,
   morning_bright 0.7, fluorescent_corridor 0.7, studio 0.6, lunch
   0.75, kitchen_practical 0.8, dawn_warm 0.85); night / dusk sit at
   1.0. Edge and ASCII moods without a key auto-scale to 0.35.
2. **Per beat** — a `[trip:X]` cue in the chapter JSON, next to
   `[mood:]` and `[shot:]`: `[trip:1.3]` pushes the layer for the
   line, `[trip:0.4]` pulls it, `[trip:off]`, `[trip:full]` (1.5),
   `[trip:reset]`. Every scene opens at reset; the cue is replayed on
   load like mood and shot.
3. **Per surface** — the registers (below) and the `trip_soft` group.

**Bright scenes get INK, not light.** The Deck verdict: "whiter or
brighter scenes are too plain and humdrum, it really only looks good
on darker scenes." Light laid on a bright picture adds nothing, so
where the picture is bright the shader cross-fades to a colour-print
treatment: the aura becomes coloured ink (the lines darken toward the
register's hue), the flats take a soft multiplied tint instead of a
glow, and the hue drift runs 1.7× — the one thing that reads on
white. Dark scenes keep the glow. The cross-fade is by scene
luminance per pixel, so a lit window in a dark room still glows.

## The four registers

| Register | Pillar | Sound (the brief) | Visual register (shipped, draft 1) | Game grammar (the queue) |
|---|---|---|---|---|
| `arcana` | Vol 5 · MAJOR ARCANA · TAROT GAUNTLET · Graustark bayou | swampy + arcade | bayou-water flow (slow, wide); phosphor-green → cyan lines with sodium amber bleeding in on the kick; the cabinet dips its power on the beat; hue drift low so the operator-noir stays noir | ARCADE: attract mode on the gauntlet board when idle (the deck shuffles itself); score bursts and chain multipliers as rounds link; named loss conditions already read as "insert coin" — make the bookends literal (a credit, a continue); per-arcana high-score table; time-of-day difficulty axis becomes TEMPO (dawn slow, 3 am fast); visitor arrivals land on the beat |
| `community` | Vol 6 · PLANNED COMMUNITY · COMMUNITY PLANNED · Harmony Creek | retro video games, zines, stoner sludge meta punk rock | two risograph inks on the lines (fluorescent pink + teal, hard-edged, no rainbow); photocopy grain; the pulse HANGS (decay 2.6 — sludge); flow slow and heavy; hue drift near zero | ZINE ISSUE: mission stages as pages, the BBS as the letters column, the summer pressure curve (W6/W12/W18) as tempo drops; META: the game already knows it sits in a book's pause — let it say so in the zine's voice; RETRO GAMES as in-fiction objects (cartridges, cabinet flyers, a review column) not as rendering; STONER pacing: long holds rewarded, nothing punishes patience |
| `milk_honey` | Vol 7 · LAND OF MILK AND HONEY · Smolvud · the substrate · the slowstock shelf's cabin | SCUMM game, psychedelic wall-of-sound classic rock, sci-fi | liquid light show — the oil-projector palette (amber / rose / violet / one cold blue); the densest flow and hue drift of the four (the wall of sound); a sparse starfield of sparks in the dark; big soft ripples | SCUMM: verb-object interaction in the VN chapters (look at / pick up / talk to / use … on — the cabin, the tower, the Daily Grind), an inventory that matters, dialogue trees with wrong answers that are funny not fatal; SCI-FI: the substrate is the engine under a small-town point-and-click — the strange thing is always one room away; WALL OF SOUND: beds + BGM + practicals all breathing together (practicals pulse with the bar at ~10% of lightshow_extreme) |
| `slowstick` | every slowstick under the shelf | Jeff Minter | the FAINTEST register (draft 2B · "ugly and strobey" as an overlay): a faint neon breath on the lines, nothing on the flats, no sparks. The Minter look lives INSIDE each stick's own rendering — its particles, its glow, its beat-lit lines — never as a screen overlay on a 2D game's type | MINTER: score as spectacle (every point is a particle), escalation by DENSITY not punishment, bonus rounds as pure light synth, the whimsy where a studio's fiction allows it; feedback trails via a SubViewport history buffer (current hardware — Godot does this natively), particles via GPUParticles2D |
| `base` | menus, vols 1–4, anything unregistered | — | rainbow aura, moderate everything | — |

The values live in `TripSync.REGISTERS`; float dials cross-fade
over 0.9 s when the register changes, the palette snaps at the
midpoint. `pulse_decay` is per register — it is the single number
that most changes how a pillar FEELS on the beat (arcade snaps,
sludge hangs).

## Who pushes what

- `GameEngine._apply_skin(vol)` → `register_for_volume(vol)`
  (5 arcana · 6 community · 7 milk_honey · else base), owner the
  engine (pops on quit to menu).
- `TarotGauntletGame._ready` → `arcana`; `CommunityPlannedGame._ready`
  → `community`. Owner the game root.
- `SlowstickLook.apply(host, preset)` → `slowstick`, owner the look
  layer (dies with the host; the shelf falls back to the VN's or
  the menu's register underneath).
- Pirate Summer's console games boot inside a layer-90 CanvasLayer
  — above the global layer. Draft-2 item: SlowstickLook already
  climbs to enclosing+5 for its own layer; TripSync's global layer
  should do the same when a `"trip_raise"` owner is present.

## Game grammar · shipped rows

- **arcana · ATTRACT MODE (draft 1, 2026-09-07).** The gauntlet board
  left alone for 45 s runs an arcade attract loop: a banner cycles
  the scenario's title, subtitle, INSERT COIN and the turn count;
  the locale's mood strata step every 9 s (the cabinet's colour
  cycle); THE TRIP pushes to 1.3. Any key, button or real mouse move
  wakes it and everything returns. Next: score bursts on chained
  rounds; tempo as the difficulty axis; a per-arcana high-score card.
- **community · THE LETTERS COLUMN (draft 1, 2026-09-07).** RUST_CODE
  gains a public board, THE_LETTERS (`N`): NEWS FROM HARMONY CREEK's
  letters to the editor, nine threads W2–W16 in the zine register —
  lot 14's cookies, Sam's correction to the back-cooler strip, Carla's
  47 Hz, PHASE III's "a zine with a letters column is a newspaper",
  the NexCorp Voice's courteous note, F.T.'s "the pause" at the
  book's seam (issue #20: eight blank pages, one dollar), the storm-
  window letter in three lines, 892's grey sedan again, "for the
  fund". The pressure curve is the tempo: letters lengthen to W6, go
  terse at W13–14, ease by W16. Data only — no engine change; the
  phosphor-green rule holds. Next: the BBS masthead for that board
  set in the zine's hand (Cosmic Comics paper stock as the board's
  colour), a reader letter that answers a `[trip:]` beat.
- **direction · [trip:] cues (draft 1).** 190 interlude beats across
  vols 5–7 carry `[trip:1.2]` (the structural turn pushes the layer,
  the way `[mood:]` cues were placed on interludes), plus three
  authored beats: the river past the parking lot, Lena's charcoal
  letters, the tower's substrate line.

## What draft 1 does NOT do (honest)

- No game-design change has shipped. The GAME GRAMMAR column is the
  authored direction and the queue; every pillar's next design
  pass should land one row of it (attract mode on the gauntlet
  board · the BBS as letters column · a verb coin on the cabin
  chapter · a Minter bonus round in one stick).
- No feedback-trail buffer yet. The Minter register's trails are
  faked by spark halos and the thump; the real thing is a
  SubViewport with `render_target_clear_mode = NEVER` and a decay
  quad, driven by the same pulse.
- Draft 1 was seen on the Deck ("mostly nausea inducing", then "I
  like it, but it's rough"); draft 2 has not. The Minter thump and
  the cabinet power dip died with the motion rule; the Minter
  register keeps its neon, sparks and white cores.

## Recent lessons

### 2026-09-07 · draft 2 · "mostly nausea inducing" → "I like it, but it's rough"

- **Music-synced displacement is motion sickness, full stop.** A
  few pixels of warp in the flats felt subtle in the maths and was
  the first thing the eye rejected: continuous, involuntary, audio-
  driven movement of the whole picture. The fix was not a smaller
  amplitude — it was zero. Colour and light carry the trip now
  (rule 0 above). The beat "ripple" became a ring of LIGHT that
  lights the lines as it passes.
- **"Rough" was the edge finder reading the dither.** The global
  layer sits above demoscene_post, so a single-scale Sobel saw the
  Bayer dither as a thousand tiny edges — speckled rainbow noise
  on every surface. Three Sobel scales (1.5 / 2.5 / 4 px) averaged,
  with a higher floor, leave only real silhouettes with an anti-
  aliased falloff.
- **Add clips; screen rolls off.** Adding the aura on top of a lit
  scene blew highlights to white with a hard clamp edge. Screen
  blend (`1 − (1−a)(1−b)`) for the aura, the wash and the sparks
  keeps highlights soft.
- **A beat needs an attack.** `pulse` snapping to 1.0 on the hit
  read as a strobe even at low amounts. It now follows the
  envelope through a 45 ms attack; band smoothing rises slower too.
- **The dial is not the fix (draft 3: "find a balance").** 2B cut
  the coefficients so far that the PSYCHEDELIA slider at full was
  "still too muted." Subtlety lives in WHAT moves and how it is
  synced, not in scaling everything down: draft 3 restores draft 1's
  colour and line weight and a slow, unsynced liquid, defaults the
  dial to 0.6, and hands the player four mix sliders (FLOW · LINES
  · COLOUR · BEAT) so the balance is found on the Deck, not guessed
  in a container.
- **Screen overlays do not belong on 2D game screens.** The Deck
  verdict on the slowstick register: "ugly and strobey." A 2D game
  has UI edges everywhere and no lit flats, so an edge aura smears
  the type and a beat-lit anything reads as strobe. The slowstick
  overlay is now the faintest register; the Minter direction is a
  per-game RENDER task inside the stick (its own particles and
  glow, its own beat-lit geometry), scheduled under game grammar.

### 2026-09-07 · draft 1 · registers + the three pillars

- **Name the pillar's SOUND first, derive the look from it.** The
  brief gave a sound per pillar (arcade / sludge / wall of sound /
  Minter). Every visual dial fell out of the sound: sludge = long
  pulse decay + heavy slow flow; arcade = fast decay + a cabinet
  power dip; wall of sound = dense flow + dense hue drift; Minter =
  additive, thumping, still flats. Start there next time too.
- **The register is owned, not set.** A stack of (name, owner)
  where a freed or exited owner pops itself means no host ever has
  to remember to restore the previous look — the VN under a
  slowstick under the shelf under the menu unwinds by itself.
- **Static builders push before add_child.** SlowstickLook pushes
  from a static function before the layer is in the tree; the
  stack therefore only prunes an owner once it has been SEEN
  inside the tree and then left. Without that flag the register
  was popped on the very next frame.

### TEMPLATE for next session

```markdown
### YYYY-MM-DD · <session focus>

- **<headline lesson>.** <what went wrong / what we learned, plus
  the rule that came out of it>.
```
