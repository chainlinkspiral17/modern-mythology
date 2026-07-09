# THE PATIENT MISTER GLASS · DESIGN
### RANCH · 2004 · SLOW DETECTIVE
### fourteen evenings · one suspect · one kitchen

RANCH's answer to the question their whole catalog begged: what
else does patience monetize? The ex-Oneironautics founders
reaching back toward the studio they left — reviewers called it
"RANCH's Estuary," and both studios hated that. Ines Rocha named
it her favorite stick of 2004, the year of her own Tideline.
That is the rivalry's détente, and this is the game that earned
it.

Olaf bought it new, finished it once, never replayed:
*"you don't reread a confession."*

---

## THE LOOK

RANCH's red-band chrome, dimmed to evening. One location for
fourteen sessions: the kitchen of ALBERT GLASS, retired ferry
clerk, seventy-one. The room is drawn once and lit fourteen
ways — RANCH's first real art direction, and visibly the point:
early evenings are amber and steam; the middle stretch goes
colder and bluer as October leans in; evening 13 is lit only by
the stove.

    #100c0a  kitchen dark      #e8a038  bulb amber
    #6a4a30  cabinet brown     #8a98a8  october window
    #c8442c  RANCH red (chrome + the kettle · the one red object)
    #d8ccb8  steam / crockery  #3a4438  wool cardigan green

**Glass himself:** one portrait, aging fourteen days in tiny
ways — the cardigan buttons differently after evening 6; the
reading glasses migrate. He is always COOKING; what he cooks is
the calendar (chowder week, the bread days, jam at the end —
players learn his menu is October on the coast, and one meal is
someone else's recipe).

**HeroImages:** the kitchen at evening 1 and evening 13 (same
angle · the pair is the whole game) · the ledger page · the
ferry from the water, 1974.

## THE SOUND

Kitchen foley carries it: the kettle, the knife board, rain
starting mid-interview some nights (real-time, changes his
mood). One theme — a patient 3/4 on the soft-sine — that never
plays during interviews, only over the drive-home cards between
evenings. On evening 14 it finally plays in the kitchen, very
quietly, and the player realizes Glass is humming it, and has
been the source all along.

## THE PLAYSTYLE

**Fourteen evenings, ~15 minutes each.** You are an insurance
investigator reopening a thirty-year-old file: $31,000 missing
from the Northwind–Anchor Bay ferry accounts, 1971–1974, clerk
of record A. GLASS. He agreed to the interviews by return post.
He always answers. That is the problem.

- **THE QUESTION DECK.** Twelve standing questions (the fare
  box, the second ledger, the Anchor Bay run, the week the
  auditor came, his late wife, why he never left...). Any can be
  asked any evening — and the same question on different
  evenings returns DIFFERENT answers: not contradictions at
  first, but rotations — the anecdote picks up a detail, drops
  a name, moves a date. What he is cooking modulates candor;
  rain modulates memory; trust (built by which questions you
  DON'T press) modulates length.
- **THE LEDGER.** The core mechanic — the promise-reckoning UI
  inverted into suspicion: pin any two answers against each
  other. A true contradiction becomes a FINDING (there are
  nine). A false pin (rotation, not contradiction) costs an
  evening of trust — he saw you take the bait. Findings unlock
  three deck questions that cannot be asked cold.
- **THE SOLUTION** (fixed, discoverable, devastatingly mundane):
  the money is real and Glass took it. From 1976 to 1979 it
  went, in cash, in envelopes, to four families up the coast —
  the ferry's own settlement fund having been denied by the
  county after the Camp Sweetgum summer collapsed the season
  and the camp's insurers with it. Glass clerked the ferry that
  took the families to and from that summer's hearings. He kept
  a second ledger of every envelope. It balances to the cent.
  He has been waiting thirty years for someone to ASK.
- **Evening 14 · the verdict:** ACCUSE (the file closes ·
  recovery proceedings against a man with $61 in savings · the
  winter card shows the kitchen dark) · CLEAR (falsify the
  findings you earned · the file closes · he thanks you and
  both of you know) · **CLOSE THE LEDGER** (the third thing:
  file the finding that the account balances — because it does,
  just not in the column anyone audited. Not innocence, not
  guilt: settled). The game grades nothing. The drive-home
  theme plays over the coast road, and for the only time, it
  resolves.

## THE AMBITION

- Prove the slow-detective thesis: the mystery genre without a
  single new location, chase, or corpse — the entire case is one
  man's willingness to keep answering, and the investigation's
  real object is the investigator's patience.
- RANCH grows the soul the schism said they'd traded away — and
  does it by building an Estuary-shaped game about a ledger,
  which is the apology neither studio would say aloud.
- Bind 1976 into the web a FOURTH way — economically, through
  ferry accounts and settlement envelopes, no ghost required.
  Glass's ferry is the one visible from Pirate Summer's north
  bluff; a young Glass holds the letter in Northwind Harbor
  chapter 4.
- Tokens out: `glass_verdict_<accuse|clear|closed>` ·
  `glass_second_ledger_seen` (Pirate Summer: one bulletin-board
  clipping gains a correction; Sweetgum: the palimpsest log
  gains one authored 1979 entry, initials A.G.). Tokens in:
  `sweetgum_watch_stood` — evening 9's rain answer adds one
  sentence.

## BUILD

SSS loop shape (14 sessions) + the question deck (JSON: question
× evening × cooking × trust → answer variants) + the ledger UI
(pin-two-answers, adapted from the promise reckoning). One
portrait with 14 micro-states, two kitchen heroes, one theme +
foley set. Cheap-to-moderate; the answer-variant writing is the
bulk, and it is the good kind of bulk. Priority #4.
