# MRS. WU'S GARDEN · DESIGN
### Oneironautics Inc. · Portland OR · October 2003 · GARDEN TENDING / NEIGHBOR STORY
### one backyard · nine beds · one fall · the frost is coming
### STATUS: BUILT · playable_v1 (2026-07) · host + WuGarden scene,
### six evenings, three actions each, tea stories, the frost
### triage, the unnamed visitor, the hummed melody

Ines Rocha welded Estuary 3 together over Labor Day weekend,
2003. Then — canon, fixed — she made THIS, the same October,
solo, in stolen evenings. It is the smallest thing Oneironautics
ever shipped and the one the studio's own people bring up first
when they talk about what the Slowstick was for.

**The setting resolves an existing breadcrumb:** Pirate Summer's
mess-hall bulletin board carries a flier — *"Mrs. Wu's Garden ·
fall open house · June 15, 1995 · Corvallis."* So: the game is
set in **Corvallis, Oregon, fall 1995**. The flier's wrongness
(a fall open house dated June) is kept and made diegetic: the
printer got the date wrong and Mrs. Wu kept the fliers, because
the fliers were free.

**The lattice fit (all pre-planted, none invented):**
- **Jenny Copeland** — counselors.json canon: *"In Mrs. Wu's
  Garden she reappears as an adult, unnamed at first."* One
  evening, a woman around forty stands at the fence with a
  whistle on a red lanyard gone soft with age. Mrs. Wu calls her
  "the camp girl." She is never named. Fires only when the
  cross-stick bus carries `pirate_summer_finished`.
- **The Rocha melodies** — Mrs. Wu hums while she works. Sit
  with her enough evenings and she hums the whole thing. The
  manual says nothing. The melody is one of the Rocha melodies;
  the catalog keeps braiding it and never explains it.
- 2048 footnote (roadmap): Meridian Heritage licensed the
  catalog; there is no Mrs. Wu remake. Tem has theories about
  why some gardens can't be relicensed.

## THE PLAYER

You are the new neighbor. Never named, never shown. Mrs. Wu is
eighty-one and her garden is a 3×3 of raised beds behind a house
on a Corvallis side street, and in your first week there she
knocks on your door with a plate of moon cakes and a request
phrased as an observation: "you have good evenings free."

## THE PLAYSTYLE

**Six evenings, October into November. Three actions an evening.**

- The garden is one screen: nine beds + the porch. Every bed
  holds one planting with a NEED that evening (water · weed ·
  mulch · cut back · tie up · just look) and a person sewn into
  it — the dahlias are her husband's, still his after nine
  years; the camellia came west with her mother; the pumpkin
  belongs to the boy two doors down who has never once watered
  it; and so on, nine beds, nine stories.
- **TEND** a bed (1 action): meet its need and the bed steadies.
  Miss a bed two evenings running and it declines. Beds carry a
  quiet 0–3 condition; the text describes it, no numbers shown.
- **SIT** (1 action): tea on the porch. One story per evening,
  keyed to whichever bed you tended last — the garden is the
  index of her life. Sitting is mechanically "wasted" and is
  the entire point. Sit three or more evenings and the humming
  resolves into the whole melody.
- **Evening 5 · THE FROST WARNING.** The radio says tonight.
  You get four actions and there are nine beds and the sheets
  only cover so much. Mrs. Wu will not choose ("they are all
  somebody's"). The triage is the thesis: what you cover is
  what you have learned to love, and there is not enough of you.
- **Evening 6 · after the frost.** The walk-through. What was
  covered stands; what was strong survived anyway; what was
  neglected and bare went black. Then the ending: the spring
  flier for the next open house, and whether your name is on
  the back in her handwriting as "ask the neighbor."

## ENDINGS (one screen, read from state)

- **THE GARDEN GOES ON** — 7+ beds alive AND 3+ stories heard.
- **HALF-SLEPT** — 4-6 beds alive.
- **A GOOD NEIGHBOR ANYWAY** — fewer, but you sat 3+ evenings.
  ("gardens die back. company doesn't.")
- Fallback: **THE FLIERS STAY IN THE DRAWER.**

## TOKENS

Out: `mrs_wus_garden_finished` ·
`wu_garden_all_beds_saved` (9/9 through the frost) ·
`wu_garden_hummed_melody` (sat 3+ · the whole tune) ·
`wu_garden_the_counselor_visited` (the fence visitor spoken to).
In: `pirate_summer_finished` gates the visitor evening.

## THE LOOK

`oneironautics` preset (field-guide gouache, paper tooth) per
the aesthetic bible — modern rendering through SlowstickLook,
no retro cosplay, font floor 12. One screen, text-forward, the
nine beds as a 3×3 of soft-toned panels whose colors carry
condition (green-gold thriving → grey-brown gone). Title:
plain type over dusk-garden colors + TitleMotion. Art budget
deliberately near zero — it was made in stolen evenings and
should look loved, not produced.

## THE SOUND

Deferred to a future audio wave: one composition ("the porch,
October") and the hummed melody as a 12-note monophonic line —
which MUST be one of the Rocha melody variants when authored.
Until then the scene runs quiet with existing UI SFX.

## BUILD

MrsWuHost + WuGarden scene (sweetgum-pattern minimal stick:
`_state` dict + OneironauticsTokens, uniform host contract).
Data: `garden.json` (nine beds · needs schedule per evening ·
nine stories + variants) · manifest + scrapbook. The shelf slot
and unlock were ALREADY scaffolded (shelf 0, slot 12 · Olaf,
from a garage sale in 2007 · unlock wave 3, by Estuary 2 or
Pirate Summer) — that provenance is prior canon and stands; only
FULL_MANIFESTS + SlowstockBoot registration were missing. BGM
borrows hnn/autumn.wav until the audio wave; the third-sit
melody plays hnn/one_melody.wav — the same tune in two carts,
which IS the Rocha-melody braid, now audible.
