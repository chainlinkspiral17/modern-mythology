# NORTHWIND HARBOR · DESIGN
### Oneironautics Inc. · 1988 · PUZZLE / ADVENTURE
### seven mornings · a boy, a dog, a harbor · the founding text

The studio's first stick. Amélie Rocha's second credit (junior ·
she wrote the fish-cleaning station dialogue and one poster).
Canon constraint: this is the cart at Camp Sweetgum, and Sam's
1988 save of Chapter One survives on it — Chapter One must match
that save beat for beat.

---

## THE LOOK

**Static tableau screens, no scrolling.** Each location is one
held wide shot, adventure-game style — the 1988 in-fiction
hardware sells the constraint, and the constraint sells the
stillness. Twelve locations along one harbor: the jetty, the
fuel dock, the fish-cleaning station, the cannery wall, the
chandlery, the ferry slip, the breakwater, the bait shop, the
church steps, the co-op ice house, the seiner CLARA B., and
uncle Maddox's porch where every morning starts.

Palette · 5:47 AM, all game long:

    #16202e  pre-dawn blue-black     #d88a30  sodium lamp orange
    #7a8894  fog grey                #c8ccd4  gull / wavecap white
    #4a5a52  wet piling green        #30281e  creosote dark

The light never finishes rising — each chapter ends at the boat
horns, right before full day. The sodium lamps are the only warm
color; standing in a lamp pool is where dialogue happens, a rule
the game never states.

**BOSUN the dog is always on screen.** Uncle Maddox's black-mouth
cur. He is the hint system: what he sniffs, noses, or stands
pointedly beside is live. He has 6 sprites and more animation
frames than the boy. This is correct.

**HeroImages:** the harbor from the breakwater (title) · the
CLARA B. going out · the cannery wall poster, half torn,
CARNIVAL · SEVEN YEARS · 1976 (chapter 7).

## THE SOUND

Almost none, which in 1988 was a choice: water slap, lamp buzz,
gull cries (`gull_cry` exists), boot on plank, one concertina
theme that plays ONLY over chapter cards — eight bars, Ostrom's
first paid work, hummable to this day in-fiction. The boat horns
that end each chapter are the loudest thing in the game.

## THE PLAYSTYLE

**Seven chapters = seven consecutive mornings, 5:47–7:00.**
Fey-Faire-midway cell navigation across the twelve tableaux,
plus POCKETS: five inventory slots, drawn as an open coat lining.

The core mechanic is **listening**. Working people talk AT you —
haulers, the ice man, the ferry clerk — one or two lines each,
while doing their jobs. Every puzzle's hint was said aloud, once,
by someone two screens away. Overheard lines land in a HEARD
list (the studio's first journal). Puzzles are soft chains of
ordinary kindness: find the glove that fits the hauler whose
hands are cracking; get the flask filled before the CLARA B.
goes out; return a key that fits nothing until you learn whose
door stopped locking in 1979.

The seven mornings:

1. **THE GLOVE** — orientation; one screen locked; Sam's save
   ends here, mid-pocket, holding the glove. (Fixed. Canon.)
2. **THE FLASK** — the coffee chain; learn the boat horns.
3. **THE SCALE** — the fish-cleaning station's rigged scale;
   Amélie's dialogue; the game's funniest and saddest screen.
4. **THE LETTER** — the ferry clerk (a young MR. GLASS — see
   _PATIENT_MISTER_GLASS_DESIGN.md) holds a letter addressed to
   a boat that hasn't docked in years. You find who it belongs
   to. Nobody opens it on screen.
5. **THE ENGINE** — the CLARA B. won't start; a chain across all
   twelve screens; Bosun finds the part in the ice house.
6. **THE FOG** — visibility two screens; navigation by sound
   only; the listening mechanic graduates to literal.
7. **THE POSTER** — the shortest morning. Nothing is wrong. You
   walk the dog. At the cannery wall, the half-torn poster:
   CARNIVAL · SEVEN YEARS. Bosun will not go near the wall. The
   horns blow. Title card. No explanation, then or ever.

No fail states. The horn ends the morning whether or not the
chain closed; unfinished chains carry over, and the town notices
("still got my glove, then"). Completing all chains in seven
mornings is quietly tracked as THE GOOD WEEK.

## THE AMBITION

- Be the medium's founding text in-fiction: the first slowstick,
  and the source of the studio's unofficial motto (the manual's
  last line): *"a game you cannot be good at, only present for."*
- Chapter 7 plants the 1976 Faire two years before Fey Faire
  ships and eleven years before anyone asks Amélie why the
  poster is there. Nobody at the studio asked. The doc's answer:
  she was 23 and it was the only place she could put it.
- Tie the coast together: Glass's ferry, the trucker route from
  Sam's Summer Shifts, estuary country a day's drive south.
- Tokens out: `northwind_harbor_finished`, `nh_good_week`,
  `nh_poster_seen` (consumed by Fey Faire — Cricket's NG+ line
  gains "you have seen our poster before"). Tokens in: none —
  it is 1988; nothing predates it except Earthman, another
  publisher.

## BUILD

Cheap and high priority (#2): midway-cell navigation + pockets
(5-slot inventory = keepsake list with a UI row) + HEARD list
(fact list reskin). Twelve tableau backgrounds as HeroImages
(the big art bill — twelve 160×90 scenes, all in the six-color
dawn palette, so each is fast). Concertina theme + 4 SFX.
Chapter One must be checked against Pirate Summer's
`sam_played_northwind_harbor_chapter_one` fact text.
