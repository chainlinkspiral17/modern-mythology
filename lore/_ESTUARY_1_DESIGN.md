# ESTUARY 1 · DESIGN
### Oneironautics Inc. · 2001 · SIMULATION / SCHOOL LIBRARY
### "the very small first one" · ~2 hours · one control

Team of three: Ines Rocha (tide-gate math, her first job), Marc
Ostrom (score, and the design's conscience), Sarah Delahaye
(every sprite). School-library run ~3,000 · OPB pledge run ~2,000.
Olaf's copy is OPB.

---

## THE LOOK

**A single fixed screen for the entire game.** The estuary seen
from the tide gate, slightly elevated, looking seaward. No
scrolling, no cuts, no second location. Two hours on one image
that will not stop changing.

Palette · six colors, total, everywhere:

    #2a3038  channel water (deep)
    #6a7a72  mudflat (exposed)
    #a8b4a0  sky (overcast · it is always overcast)
    #4a5a3a  reed line
    #b8c0c0  the heron
    #d8b048  tide-gold (the water when the light gets through ·
             used maybe forty pixels per week · earned)

The composition is thirds: sky, water/flat (the tide state swaps
which), reed line with the gate at frame-left. The LEVER is
diegetic — a drawn lever on the gate housing, not a UI widget.
The week number is carved into the gate post. That is the entire
HUD.

**The heron is the readout.** She stands somewhere new each week:
by the gate when passage is good, far out on the flat when the
shrimp beds are rich, hunched on the piling when the estuary is
hungry, absent exactly once (a bad week you caused). Players
learn to read her before they learn to read anything else — this
is deliberate and is the whole art direction: *state rendered as
behavior, never as number.*

Delahaye's sprite bill: heron (4 stances), chum fry (surface
shimmer band, 2 states), mud shrimp (burrow air-holes texture,
3 densities), the gate (3 positions), water at 4 tide states.
Fourteen drawings. The game.

**HeroImages:** the report card (ruled school stock, pencil
grades) · Week 13's night estuary (the six colors plus one
star).

## THE SOUND

One composition that is the whole score: a drone in D that gains
a voice per species doing well — fry add a high shimmer arp,
shrimp add a sub pulse, the heron adds a single held fifth when
she feeds. A thriving Week 9 is a chord; a wrecked one is the
bare drone. The player mixes the soundtrack with the lever and
is never told so.

SFX: `tide_gate_toggle` (exists) · a pencil-on-paper for the
report card · one heron call, used at most twice per run.

## THE PLAYSTYLE

Twelve weekly turns. Each week:

1. Read the screen (heron, shimmer, air-holes, water line).
2. Set the gate: OPEN · HALF · CLOSED.
3. One line of consequence text, in the voice of a field notebook
   ("wk 5 · fry moving at the ebb · counted more than hoped").
4. The screen re-renders. Next week.

The coupled math (reconstruction of Ines's sheets):

- FRY have an out-migration window, weeks 4–6. Passage each week
  = gate openness × tide luck. Miss the window and the cohort is
  stranded; the shimmer band thins for the rest of the game.
- SHRIMP score stability: every gate CHANGE costs bed density;
  two identical weeks in a row regrow it. The optimal shrimp
  summer touches the lever twice.
- HERON eats whichever is abundant; she is max(fry, shrimp)
  rendered as a standing position. She never starves to death.
  She just isn't there one week. That lands harder.

The tension is the design: fry want the gate worked, shrimp want
it left alone, and both are right. There is no setting that wins.
There is only a summer you are responsible for.

**The report card.** The ending screen grades the ESTUARY, not
the player: WATER (channel health), PASSAGE (cohort out), and
PATIENCE (12 minus lever touches, curved). Signed "the estuary"
in Delahaye's 3×5 font. Teachers loved it; the 2001 press called
the game "a screensaver you're responsible for." The design doc's
one surviving sentence, Ostrom's hand: *"the player should end
the game knowing they were RESPONSIBLE for something, without
once being told they were."*

**Week 13 (hidden).** Gate touched ≤ 2 times all game: one extra
screen after the card. Night. No UI. The full chord. One line —
*"it was doing this before you, too."* Then the title. The fifth
season of Estuary 3, seeded three games early.

## THE AMBITION

- Make the studio's thesis PLAYABLE in two hours: attention as
  the verb, responsibility without praise.
- Embody the RANCH schism: the two designers who left in 2000
  wanted a score and a park-ranger frame. Kwik Stop Manager is
  Estuary 1 with the score attached. A player who finishes both
  should be able to articulate the argument the studio had.
- Give Tem's grandfather's loyalty ("he was an Estuary 1 person")
  a felt referent.
- Tokens out: `estuary_1_finished`, `estuary_1_patience_a`
  (PATIENCE grade A · consumed by E3 Act 2, one line from Jules),
  `estuary_1_week_13_seen` (E3 fifth season opens a beat early).

## BUILD

SSS host shape: host + one loop scene, 12 turns, hidden meters.
Fourteen sprites via SlowstockSprite JSONs (some reusable from E3
Act 2). One composition with stem-mixing (render 4 stems, play
additively — AudioMgr supports layering? if not, render the 8
combinations). Two HeroImages. Scope: the smallest full stick in
the catalog. Priority #1.
