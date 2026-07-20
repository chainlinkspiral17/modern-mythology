# ESTUARY 4 · DESIGN
### Oneironautics Inc. · Portland OR · 2005 · RESTORATION CAMPAIGN
### set in 2016 · the archive, the water, the hunter, the king tide
### STATUS: BUILT · playable_v1 (2026-07) · host + EstuaryFour
### chapter scene (beat-sequence pattern), four chapters, the
### 2003 notebook read back from the archive when the token bus
### carries it, Ashford Cade back in the spring, endings read
### from the plan you chose and the line you walked

The last Oneironautics stick of the classic run. Ines Rocha
pitched it in 2005 after The Tideline; E3's own design doc calls
it "the studio's course-correct after Estuary 3's cult
reception. Bigger budget, more species, a proper narrative
campaign. ~14 hours." And the strangest fact about it, canon
since Pirate Summer shipped its east forest: **Estuary 4 is set
in 2016** — eleven years ahead of its own release. A 2005 studio
imagining a near future where somebody finally goes back and
fixes the water. The cabin note on the hunter's door ("back in
the spring · Ashford Cade · 2016") was always this game's
door.

Canon fixed points honored: pitched by Ines 2005 (lattice) ·
shipped 2005 (studio line) · shelf slot pre-scaffolded, wave 4
unlock, provenance "Tem's grandfather" · Ashford Cade "a hunter
who reappears in Estuary 4 (in the year 2016)" (PS dialogue
web) · the island triangle (the federal boat, Station 1600,
Cade's note) stays open — one nod, no resolution.

## THE PLAYER

A watershed restoration officer, spring 2016, assigned the
estuary between the creek mouth and the point — the same water
the whole Estuary line has been circling since 2001. Your first
week is spent where every honest restoration starts: **the
county archive**, reading decade-old volunteer surveys,
carefully, one person, exactly as The Tideline's last line
promised somebody someday would.

## THE CAMPAIGN · four chapters (beat-sequence pattern)

**CHAPTER ONE · THE ARCHIVE.** The reading room. Three
volunteer survey files from the 2000s to build the plan on —
each pulls the restoration toward an emphasis:
- the 2001 tide-gate logbook (THE LINE · hydrology first)
- the 2002 species censuses (THE LIVING · habitat first)
- the 2006 debris-field photographs (THE LOST · cleanup first)
And — when `the_tideline_finished` rides the token bus — a
fourth folder: **the December 2003 king-tide notebook**, two
ruled lines per station, in a volunteer's hand. YOUR hand. The
register you filed (carried in canon as `tideline_report`)
is read back to you, eleven years later, by the one person the
game always said would read it carefully. Choosing it sets the
plan to the register you walked. (Token:
`e4_read_the_2003_notebook`.)

**CHAPTER TWO · THE WATER.** The working season, condensed to
its three hard calls: the tide gate (repair the 2001 gate or
breach it for good), the channel (dredge the shallows bar or
let the point keep rearranging its doorstep), the plantings
(eelgrass at scale or the slow native seedbank). Each call is
argued by the plan emphasis you chose — the campaign talks back
in the vocabulary of the file you trusted.

**CHAPTER THREE · THE HUNTER.** The cabin in the east forest,
door note gone — because he's back; it's spring. **Ashford
Cade**, seventies, has hunted this watershed since before the
county kept files on it, and he walks the restoration line with
you for one long chapter. He is not a mystic and not an
obstacle; he is a second archive, oral, and he disagrees with
the county's paper in exactly two places, and he is right about
one of them (which one depends on your plan). One line, once,
about the island offshore and the people who watch it —
answered with "different organization. long story. wrong
season." — and never again. (Token: `e4_cade_walked_the_line`.)

**CHAPTER FOUR · THE KING TIDE.** December 2016. The year's
highest water arrives to inspect the work. What holds and what
goes is read from the three calls and the plan emphasis; the
ending is the survey you file afterward — because the campaign
ends the way the whole line always ends, with somebody walking
the wrack line writing things down. Endings:
- **THE ESTUARY REMEMBERS** (plan-consistent calls · the water
  takes the shape you argued for)
- **THE WATER DECIDES** (mixed calls · half the plan holds and
  the estuary edits the rest, not unkindly)
- **THE SECOND SURVEY** (contrarian calls · the work partly
  fails and the failure is the most valuable data the county
  has collected in a decade)
Last line, always: *"Filed with the county. Someone will read
it. Someone always does — it just takes the county a while to
grow the right someone."*

## TOKENS

Out: `estuary_4_finished` · `e4_read_the_2003_notebook`
(archive chapter, gated on `the_tideline_finished`) ·
`e4_cade_walked_the_line`. In: `the_tideline_finished` +
`canon.tideline_report` (the register read-back) — the first
time a stick reads another stick's CANON VAR, not just a token.

## THE LOOK

`oneironautics` preset. 2016 rendered from 2005's imagination:
the same field-guide gouache, no product chrome — Oneironautics
imagined the future looking like better weather, not better
screens. Text-forward chapters, the archive folders as the one
list UI.

## THE SOUND

Deferred to the audio wave ("the gate, opened" · "Cade's
watershed" · a king-tide reprise of the E1 stems). Until then:
e3/e1 water beds where present, else quiet.

## BUILD

EstuaryFourHost + EstuaryFour scene (beat-sequence chapter
pattern per the authoring playbook), data `estuary_4.json`
(chapters, calls, Cade's walk, endings), manifest + scrapbook.
Shelf slot and wave-4 unlock pre-scaffolded ("Tem's
grandfather"); FULL_MANIFESTS + SlowstockBoot registration new.
The in-fiction ~14 hours is condensed to the campaign's
decision spine — same treatment every big stick on this shelf
gets.
