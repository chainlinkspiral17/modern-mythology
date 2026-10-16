# FEY FAIRE · THE WARREN · DESIGN
### the party as a keyring · errands · a purpose for all 101 feys
### STATUS: BUILT · playable_v1 (2026-07)

User ask: "use all the fey, find a purpose, deepen the game and the
experience. maybe side quests and other ways to use the fey,
reasons for having them in a party."

The survey (see _FEY_FAIRE_MECHANICS.md thickening addendum) found
the party did four small things and 61 of 101 feys were unreachable.
This system answers both in one loop.

## THE PROBLEM IT SOLVES

- **61 unreached feys.** After the W3 booth pass, 40 feys sit on the
  midway. The other 61 are authored (name, court, request, gift,
  skills) and appear nowhere in play. There are not 61 spare booth
  cells, and there shouldn't be — walking to 101 booths is a chore,
  not a game.
- **The party had no purpose.** Recruited feys enabled rest, trickled
  gold, fed endings, and chattered. Nothing about WHICH feys you held
  mattered to WHAT you could do.

## THE LOOP · the party is a keyring

Recruited feys give the party purpose two ways, both legible from the
trailer:

### 1 · BOONS — passive reasons to hold a fey

Standing benefits the party grants, keyed to court and to type
coverage. Shown in the COTS roster so composition is a visible choice:

- **Any SEELIE in party** → OFFER costs 1 less gold (min 1). They
  know the stalls; they haggle for you.
- **Any UNSEELIE in party** → once per night, a tier-3 THREATEN that
  would drop into combat instead SUBMITS — the unseelie steps
  between you and vouches. (A dangerous friend is still a friend.)
- **Any WILDFEY in party** → once per night, one flap-closed / locked
  booth opens anyway. They know the ways under the fence.
- **Type coverage** → combat SECOND already lets the highest-tier
  ally strike; holding a fey of a given damage_type means that type
  is available when it's the one the enemy fears.
- **Any SONG-type fey** → one failed RECITE per negotiation may be
  re-attempted; the song fey hums you the scansion.

None of these are numbers-on-a-sheet; each is a sentence in the
roster ("Moth · SONG · she'll hum you a second try at a line").

### 2 · ERRANDS — fey-referral side quests · THE WARREN

The 61 unreached feys live BEYOND THE FENCE — the Warren. You do not
walk to them. A fey already in your party VOUCHES for one of its own
kind out there, and reaching that fey needs a specific capability the
rest of your party must field. This is the side-quest layer and the
reason a broad roster matters.

**Availability.** An errand for a Warren fey unlocks when your party
holds at least one fey of that fey's COURT (its own kind refers it).
So recruiting within a court opens that court's warren, errand by
errand.

**The requirement.** To WALK IN to a Warren fey you must bring the
thing it respects: the party must field a fey whose damage_type
equals the target's WEAKNESS. ("You do not approach a salt-weak
thing empty-handed; you bring someone salt-touched who knows the
courtesies.") Targets with no weakness fall back to needing a fey of
a different court than their own. This directly rewards a party broad
in courts AND in types — the whole ask.

**The run.** From the trailer's WARREN board you pick an available
errand and send the qualifying party fey. Success recruits the target
(same mutation as a booth recruit: +court, +disposition, joins the
roster) and often surfaces THAT fey's own errands next. The keyring
grows itself.

**The flavor is theirs.** Each errand card is composed at runtime
from the target's OWN authored fields — name, manifestation, and
`request` (the promise it will ask) — wrapped in one authored hook
line per entry in `errands.json`. So all 61 read specific and true to
feys.json without 61 pages of bespoke prose.

## WHAT THIS MAKES ALL 101 FEYS FOR

- 40 booth feys · the on-map cast you meet by walking and negotiating.
- 61 warren feys · reached only through the party, each a payoff for
  having recruited the right kinds and built a broad roster.
- Every fey, on joining, adds a boon (its court/type) AND vouches for
  its warren-kin (its errands). Holding a fey is now holding a key.

## MILESTONES / TOKENS

- `fey_faire_errand_first` · first warren fey brought in.
- `fey_faire_warren_court_<court>` · a court's warren fully emptied.
- `fey_faire_warren_emptied` · all 61 reached (the completionist beat).
- `fey_faire_full_court` · all 101 recruited across runs (compendium).

## BUILD

- `errands.json` · one entry per unreached fey: {target, giver_court,
  needs, hook}. Generated against feys.json so coverage is total and
  every `needs` is satisfiable.
- Trailer gains a WARREN fixture (`_render_warren_view`) — the errand
  board: available / locked-need / done, RUN dispatches.
- COTS roster gains the BOONS readout (what each fey grants).
- Boons wired into FeyFaireNegotiation (OFFER discount, wildfey
  booth-pass flag, RECITE retry, unseelie threaten-vouch) and the
  existing combat SECOND.
- Rides existing machinery: recruit mutation shape, run_state party,
  the trailer fixture pattern. No new scene.
