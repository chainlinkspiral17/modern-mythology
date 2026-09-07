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

0. **THE IMAGE NEVER MOVES (the motion rule).** The user's verdict on
   draft 1: *"that's mostly nausea inducing."* Draft 1 warped the
   flats by up to 29 px, rippled the whole frame on every beat,
   zoomed the screen on the kick, split the chroma, and dipped the
   brightness. ALL of it is gone and none of it comes back. THE TRIP
   is colour and light laid on a still picture: every pixel is
   sampled exactly where it is; no UV displacement, no zoom, no
   chromatic split, no whole-frame brightness change, no flicker;
   hue rotation on large areas is small (±0.35 rad) and SLOW; beat
   responses live on the lines and in points, never across the
   frame; the beat envelope has an attack (~45 ms), never a pop.
   If a future pass wants displacement for a specific story moment,
   it is a `[mood:]`-gated beat of a few seconds, off by default,
   and it is never synced to a continuous music signal.
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

## The four registers

| Register | Pillar | Sound (the brief) | Visual register (shipped, draft 1) | Game grammar (the queue) |
|---|---|---|---|---|
| `arcana` | Vol 5 · MAJOR ARCANA · TAROT GAUNTLET · Graustark bayou | swampy + arcade | bayou-water flow (slow, wide); phosphor-green → cyan lines with sodium amber bleeding in on the kick; the cabinet dips its power on the beat; hue drift low so the operator-noir stays noir | ARCADE: attract mode on the gauntlet board when idle (the deck shuffles itself); score bursts and chain multipliers as rounds link; named loss conditions already read as "insert coin" — make the bookends literal (a credit, a continue); per-arcana high-score table; time-of-day difficulty axis becomes TEMPO (dawn slow, 3 am fast); visitor arrivals land on the beat |
| `community` | Vol 6 · PLANNED COMMUNITY · COMMUNITY PLANNED · Harmony Creek | retro video games, zines, stoner sludge meta punk rock | two risograph inks on the lines (fluorescent pink + teal, hard-edged, no rainbow); photocopy grain; the pulse HANGS (decay 2.6 — sludge); flow slow and heavy; hue drift near zero | ZINE ISSUE: mission stages as pages, the BBS as the letters column, the summer pressure curve (W6/W12/W18) as tempo drops; META: the game already knows it sits in a book's pause — let it say so in the zine's voice; RETRO GAMES as in-fiction objects (cartridges, cabinet flyers, a review column) not as rendering; STONER pacing: long holds rewarded, nothing punishes patience |
| `milk_honey` | Vol 7 · LAND OF MILK AND HONEY · Smolvud · the substrate · the slowstock shelf's cabin | SCUMM game, psychedelic wall-of-sound classic rock, sci-fi | liquid light show — the oil-projector palette (amber / rose / violet / one cold blue); the densest flow and hue drift of the four (the wall of sound); a sparse starfield of sparks in the dark; big soft ripples | SCUMM: verb-object interaction in the VN chapters (look at / pick up / talk to / use … on — the cabin, the tower, the Daily Grind), an inventory that matters, dialogue trees with wrong answers that are funny not fatal; SCI-FI: the substrate is the engine under a small-town point-and-click — the strange thing is always one room away; WALL OF SOUND: beds + BGM + practicals all breathing together (practicals pulse with the bar at ~10% of lightshow_extreme) |
| `slowstick` | every slowstick under the shelf | Jeff Minter | pure additive neon on the lines with white cores on the kick; spark storms; the whole screen thumps in on the beat; flats stay STILL (no warp, no hue drift — the game must be readable) | MINTER: score as spectacle (every point is a particle), escalation by DENSITY not punishment, bonus rounds as pure light synth, the whimsy where a studio's fiction allows it; feedback trails via a SubViewport history buffer (current hardware — Godot does this natively), particles via GPUParticles2D |
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
- **Default amount 0.45, not 0.6.** Half the dial is the right
  starting point for "at all times."

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
