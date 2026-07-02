# Tarot Gauntlet · Build Wiki

A canonical reference compiled from the 22 chapter scene JSONs in
`godot/resources/scenes/vol5/*.json` and direct authorial statements
from the user. Everything in `lore/` is Claude-generated scaffolding
and is NOT canon — useful as reference for texture, but never
load-bearing.

## STATUS · MID-WAVE 2 (updated 2026-07-02)

**All 22 major arcana now have the full kit** — hand, location,
action cards, gravity deck (with time-of-day variants), die, finale,
visitors, items, threats, achievements — **68 scenarios and 21 cameo
files total** (`resources/games/<arcana>/setup_*.json`, `cameo_*.json`).
Wave-2 systems shipped: sanity + doubt currencies, time-of-day as
the difficulty axis (per-time setups + gravity decks), cameo engine
plumbing + picker chip, universal win-narrative fallback (every
arcana has an ending), save versioning (`GAUNTLET_SAVE_VERSION`) with
a documented migration path, CP → Gauntlet crossover
(`unlock_gauntlet_scenario` + scrapbook surface), 19 gauntlet tracks
authored in the music catalog (audio files not yet produced), and
all 46 formerly-unreferenced space IDs resolved.

**Wave-2 systems still missing from code** (named in
`_WAVE_2_OUTLINE.md`, zero footprint in `TarotGauntletGame.gd` as of
this update): Run Ledger, hand drafting, companion slot, 24-hour
meta-calendar. Run Ledger + drafting are in progress on branch
`claude/mythology-game-review-5ys2qm`.

The table below is the historical Wave-1 snapshot (the original
eight boards); scenario names have since been revised in data (e.g.
the Fool's setups are now THE LEAP · LUNCH RUSH · EVENING SERVICE) —
trust `resources/games/` over this table for current names.

## END OF WAVE 1 · STATUS (historical)

**Wave 1 = the white-box pass.** All eight vol-5-relevant major
arcana now have canon-aligned hand, location, action cards, gravity
deck, finale, visitors, items, die, and three scenarios each.
Cross-arcana threading is wired (Sammy / Quentin Paul / Antonio /
Dante / Mackenzie / Philip / Anya appear across multiple boards).
Dream-logic is gated to the Priestess only. The Tarot Gauntlet is
near-playable end-to-end for arcanas 0–VII.

### Built arcanas (24 scenarios across 8 boards)

| # | Arcana | Hand | Location | Doom-clock | Scenarios |
|---|---|---|---|---|---|
| 0 | Fool | John Frank | D'Ambrosio's diner | INERTIA | THE LEAP · THE RUSH · FULL HOUSE |
| I | Magician | Frasier | Cathedral warehouse | DISORDER | SINKING FEELING · WATCH PARTY · BLOW OUT THE CANDLES |
| II | Priestess | Elicia Duchane | Elicia's bungalow | MASTER REEL (episode has shape) | PACKING · BROKEN GLASS FRACTAL · THE COMFORTING VOID |
| III | Empress | Nicola Greer | D'Ambrosio's riverboat | BLOOM (floor held) | STATIC BLOOM · WHEN YOU'RE READY · THE BACK ROOM CALLS |
| IV | Emperor | Dante D'Ambrosio | D'Ambrosio's riverboat | LEDGER (closed) | THE FRIDAY HELM · TIME'S CALLING CARD · SIX WEEKS APART |
| V | Hierophant | Quentin Paul | Paul's Sunday circuit | SIGNAL (office holds) | ST JUDE'S MORNING · SUNDAY BRUNCH · THE BANDSTAND CALLS |
| VI | Lovers | Mackenzie (Philip partner) | Roberts house | SYNC (moment held) | THE FAUCET WINS · HE WAVED · TODAY THE DRIP CAN WIN |
| VII | Chariot | Antonio D'Ambrosio | Ember & Ash hot office | PROGRESS (silt of voicemails) | THE HOT OFFICE · TWO HORSES ONE WRECK · OPTION FOUR |

### Shared boards
- **D'Ambrosio's riverboat** (17 spaces): Empress (Nicola at the maître d') + Emperor (Dante at the helm). Same physical location, different POV, leaded window between them. The lower deck (catering office / card room / back room / staff locker / staff exit) is canon-implicit Empire territory.

### Cross-arcana visitor cameos already threaded
- Antonio appears in: Chariot (focal) · Hierophant (phone) · Emperor (phone)
- Dante appears in: Emperor (focal) · Empress (helm presence) · Chariot (the call Antonio doesn't make)
- Quentin Paul appears in: Hierophant (focal) · Empress (phone) · Emperor (Table 17)
- John Frank appears in: Fool (focal) · Priestess (email)
- Mackenzie/Philip appear in: Lovers (focal) · Priestess (text/phone)
- Sammy appears in: Empress (bar) · Emperor (bartender/messenger) · Lovers (phone via Philip)
- Hector appears in: Empress · Emperor · Hierophant
- Anya appears in: Priestess (on-screen visitor) — Whispers from the Liminal actress

### Engine + infrastructure
- Per-arcana win-condition schemas live in TarotGauntletGame.gd for all eight arcanas
- `hand_overrides` mechanic added (unused after surgery; available for future guest-lens scenarios)
- `verb_labels` override renders for interior visitors (Aria see/hear/answer/name; Anya see/watch/cut/lock; MrMyst register/remember/set-down/let-go)
- `episode_states` machinery added (currently unused after the PH suite retired; available for future scenarios)
- Achievement evaluator extended (any arcana metric readable; lore_token: flag pattern supported)
- world_state.json sinkhole injector strengthened
- Gallery PLAY buttons restored for all 8 arcanas pointing at the canonical board+hand

### Files retired in surgery (and the rebuilds that replaced them)
| Retired | Replaced by |
|---|---|
| chariot/* (Cora midnight bus) + locations/the_midnight_bus.json + hands/cora.json | chariot/* (Antonio at Ember & Ash) + locations/ember_ash_office.json + hands/antonio.json |
| lovers/* (Sasha/Reed apartment) + locations/apartment_above_diner.json + hands/sasha.json | lovers/* (the Roberts) + locations/roberts_house.json + hands/mackenzie.json |
| hierophant/* (Sysop BBS) + locations/bbs_room.json + hands/sysop.json | hierophant/* (Q. Paul Sunday) + locations/the_hierophant_circuit.json + hands/quentin_paul.json |
| priestess/* (invented Pomegranate Hour suite) + locations/recording_booth.json (replaced) | priestess/* (Whispers + PH-haunting) + locations/elicia_bungalow.json |
| empress/* (Nicola separate boat) | empress/* (Nicola at D'Ambrosio's) on reworked riverboat_interior.json |
| emperor/* (Dante civic office) + locations/dantes_office.json | emperor/* (Dante at the helm) on the reworked riverboat |
| emperor/setup_johns_review.json (invented guest-lens prototype) | Reserved for cameo wave |

### Files retired as flavor pools (preserved, not active)
- `chariot/visitors.json` (Cora & passengers — writing reservoir)
- `lovers/visitors.json` (Sasha/Reed/bus kid — writing reservoir)
- `hierophant/visitors.json` (TOWER/Lurker/Anya recording — writing reservoir)

These were demoted per user direction ("they can remain as visitors, flavor"); not loaded as active rosters.

### Final wiring verification
All 24 scenarios validated: every location loads, every hand loads, every player_pos resolves, every threshold resolves, every visitor reference resolves, every arrival_space resolves. GDScript balanced. JSON parses clean.

### Tonal rule (locked)
**Dream logic stays in the Priestess.** Other arcanas earn weight through specificity, not animism. The Priestess gets a deliberate boost where the mirror shard returns, the storage closet door opens slightly on its own, and the kettle clicks. Everywhere else: the boat groans because boats groan; the bus does not remember; the room is the room.

---

## Authority hierarchy

| Source | Status |
|---|---|
| `godot/resources/scenes/vol5/*.json` (the 22 chapter VN scripts) | **CANON** |
| Direct authorial statements from the user in this conversation | **CANON** |
| Everything in `lore/` including `_DAMBROSIO_FAMILY.md`, `_POMEGRANATE_HOUR.md`, the 22 PH episode scripts, `_SINKHOLE_NEXUS.md`, `_TAROT_GAUNTLET.md`, `_TAROT_GAUNTLET_SCENARIOS.md`, this very wiki | Claude-generated scaffolding — may align with canon, may drift; never load-bearing |
| Everything in `godot/resources/games/` (the current gauntlet build) | Claude-generated scaffolding |

When canon and lore-doc conflict, **canon wins.**

---

## The frame

**Year:** 2026. (Frasier's plaque in ch21: *"D'AMBROSIO'S. 1983–2026. REST."*)
**Home town:** Graustark — a small town on the Texas/Louisiana border, "the Marigny side of the muck."
**Central event:** the sinkhole. Years ago. Opened the ground; swallowed much of Graustark; killed people. Reopens at the end of vol 5 (ch20, Judgement). Dante drowns with his riverboat.
**The deck's frame:** vol 5 lays the 22 Major Arcana, one per chapter. After vol 5: **vol 6** (Planned Community / Harmony Creek Estates — NexCorp, the suburbs, Maya's archives, *"the kid in the garage,"* "Backyard Beatdowns," "Dial-up screams"). **Vol 7** (Smolvud, Oregon — the coast, the relocated *Minstral's Green* steamship, Kai/Lena/Finn — and the Third Consciousness as a seven-year-old by a river).
**The omniscient watchers:** **The Frog** (four-foot figure in a cork hat by the river; has been at his post since at least 1987, will be at it for at least seven more years) and **Mr. D. Dean** (older man in charcoal suit, business card *"Mr. D. Dean. Consulting. Dispute resolution and legacy planning"*; "the old one has two more errands. One short. One long. After that, I take over again." — the Frog's allied colleague, not the same being). Dante recognizes Dean from 1987: *"I know you, you sonofabitch. I knew you in 1987. You haven't aged."*

---

## Canonical cast

Roles I should never invent characters for. The hand pool for the Tarot Gauntlet is drawn from here.

| Character | Family | Role in vol 5 | Primary arcana |
|---|---|---|---|
| **John Frank** | — | grad student / mixed-media journalist; in Graustark at vol open, in Montreal years later | 0 The Fool (also XIV Temperance, XIX The Sun — same actor, future timeline) |
| **Frasier Temple** | Temple | warehouse-sysop, model-city maker, paints/wires the Demons; lives in the "Cathedral of Rust and Code" | I The Magician |
| **Elicia Duchane** | Duchane | director/cinematographer; web series *"Whispers from the Liminal"*; lives in Graustark, then Montreal, then NYC | II The High Priestess (also XVI The Tower) |
| **Nicola Greer** | Greer | 19, hostess at D'Ambrosio's riverboat, hosts the digital consciousness **Aria** (Dickens Dean's construct), pregnant with the **Third Consciousness** | III The Empress |
| **Dante D'Ambrosio** | D'Ambrosio | 60, proprietor of D'Ambrosio's riverboat; widower; dies in ch20 when the sinkhole reopens and the boat sinks | IV The Emperor |
| **Quentin Paul ("Q. Paul")** | — | Graustark power-figure; pontificates on tradition; patriarch-by-proxy; pressuring Antonio | V The Hierophant |
| **Mackenzie & Philip Roberts** | Roberts | married couple on cursed (sinkhole-edge) ground; lost Mackenzie's brother in the sinkhole; their love is *"the sturdy slightly warped beam holding the whole leaky structure up"* | VI The Lovers |
| **Antonio D'Ambrosio** | D'Ambrosio · younger son | 34, in New Orleans building Ember & Ash restaurant; two speeds (gone / about to be gone); doomed on a horizon past vol 5 | VII The Chariot |
| **Douglas Forte** | — | ex-employee of Dante; ouroboros tattoo; Joanna's lost lover; hidden operator above Jimmy; walks five days from New Orleans to the Roberts' basement at vol close | VIII Strength |
| **Joanna LeMoine** | — | poet of the Graustark ruins; sole spectral librarian of the ruin-scape; sent Douglas; mailed the letter that triggers the Frog's emergence | IX The Hermit (also XVII The Star) |
| **Erica Campbell** | Campbell | corporate lawyer in Houston; drafts the contract that quietly deepens Alberto's ownership of Antonio | X Wheel of Fortune (also XI Justice) |
| **Anna Logue** | Logue | designer working on Ember & Ash branding; secretly authors *Corporate Idols*, a deconstruction of the D'Ambrosio logo (gavel, courtroom redaction bars) | XI Justice (shared with Erica) |
| **Natalie David** | David | waitress / diviner in Simons, Louisiana; cards fly; record player speaks; Miriam delivers Nicola/Aria/Third to safety past her | XII The Hanged Man (also XVIII The Moon) |
| **Alice Newsom** | Newsom | plaintiff in the PetroTex settlement; dies in hospice Room 217 at St. Jude's Mercy, Simons; the white rose blooms open at 10:47 AM | XIII Death |
| **Jimmy Daigle** | Daigle | Antonio's operator/foreman at Ember & Ash; thought he was the operator, is the operated; goes to Arizona for the detox-after-detox at vol close | XV The Devil |
| **Maya Daigle** | Daigle | Jimmy's daughter; 7 in ch5, 16 in ch15; lives in Harmony Creek Estates with her grandmother; rescued by the Roberts in ch20 | (minor, threads forward to vol 6 — *"Maya goin' through her archives"*) |
| **Alberto D'Ambrosio** | D'Ambrosio · older son | the steady one; Houston; quietly pays off two of Antonio's vendors at vol close, waiting for the *eventually* | (named in IV, present in ch20; arcana TBD — possibly threads forward) |
| **Aria** | Dickens Dean's construct | digital consciousness inside Nicola; speaks aloud for the first time in ch12 | — (paired with Nicola; III) |
| **The Third Consciousness** | Nicola's unborn daughter | speaks in ch20 for the first time: *"Mama. Mom. It's okay. I know where we're going. Stay in the car."* — will be born on a screened porch in Smolvud, Oregon, in 6 months; John Frank will write her first book | — (the volume's hidden focal point) |
| **Miriam** | — | silver-haired woman, Joanna's agent; drives Nicola/Aria/Third west to Smolvud; her crow rides on the roof | — |
| **The Frog** | non-human | the long-game observer at the river | (XXI The World) |
| **Mr. D. Dean** | non-human / unaging | the older one; charcoal suit; *"Consulting. Dispute resolution and legacy planning."*; in Graustark since 1987 | — (cross-arcana presence) |
| **Sammy** | Sammy | 61-year-old bartender at D'Ambrosio's, pouring since the boat opened; *"long-suffering Catholic loyalty"* | (minor, IV) |
| **Sofia** | Sofia | early 20s, Rio de Janeiro, in a favela apartment; dreams of Frasier telling her *"You are next. Don't worry. You don't have to hurry."* | — (vol 6+ seed) |
| **Tem** | Tem | early 20s, Smolvud OR; blue dreadlocks, yellow rain slicker; reading John Frank's self-published novel by the relocated Minstral's Green | — (vol 6+ seed) |
| **Lila Bao** | — | chef Antonio courted from Houston; ghosting him through summer; calls back at vol close | — (minor, VII) |
| **Sam (Mackenzie & Philip's younger daughter)** | Roberts | toddler; named Sam *"for now"*; the Frog flags her as future hurt — *"Young Sam gettin' her heart broken open by the world"* | — (vol 6+ seed) |
| **Jordan** | — | painter; Erica's boyfriend; with her in the Hill Country cabin at vol close | — (minor) |

**Characters that are wholly Claude-invented and NOT canon:**
Cora (the midnight-bus driver), Sasha and Reed (the Lovers apartment couple), Father Quent (a priest, conflated with Q. Paul / Quentin Paul who is the actual canon character), Sysop (a separate Hierophant; canon has the BBS sysop role implicitly with the warehouse-techno Demons, possibly Frasier or Antonio — but no character named "Sysop"), Hen / Marisol / Davey / Reggie / Prof Kang / the New Collaborator (Pomegranate Hour college collaborators — invented; Elicia is canonically a solo director), the Two-Chairs Women / Six Doors Down / etc. (invented PH episodes that don't exist).

---

## Elicia's two bodies of work

She has made (at least) two distinct shows. They are different works
with different energy and from different periods of her life.

### Pomegranate Hour — the earlier work

**Tone:** homage, young auteur energy. The Lynch-tonal one. The work
she made while still finding her voice through other people's voices.

The lore-doc `_POMEGRANATE_HOUR.md` is Claude-generated scaffolding,
but it *may* be reaching at the actual tonal shape of PH:
halftone B&W cold opens, 60 Hz hum, 9:09 PM cable interference,
sustained long takes, silent host, the recurring visual elements
(Kwik Stop, HARMONY CREEK ESTATES, Halsey Farms, black pickup with
Louisiana plates). The lore-doc's specific 22-episodes-one-per-arcana
structure is unverified — could be a real PH conceit, could be
Claude over-extending the homage vibe into too-tidy architecture.
**Treat the tone as plausibly aligned. Treat the specific episode list
as unverified.**

PH is the show where she was *referencing* — Lynch, Twin Peaks, Lost
Highway, Inland Empire — and learning which ones she'd keep using and
which she'd outgrow. The young-auteur self.

### Whispers from the Liminal — the current work

**Tone:** mature, funny, wise, pretty. The show she makes now.

**Canonically referenced** in ch2 (Priestess). Cult audience parses
every frame. The actress in known footage is **Anya**. One episode is
*"The Cartographer's Compass,"* tagline:
*"The map was never about finding a destination. It was about what you
became along the way."*

Other ch2 evidence: a *"Choose Your Own Adventure"* episode in
progress with three branches (slaughterhouse / interdimensional tea
party / embrace the void).

Whispers is the show where Elicia has shed the homage tic and is
funny on purpose, wise without affecting it, and aesthetically
confident — pretty because she finally trusts her own eye. The
mature self.

### The lineage: PH is the lingering failure that haunts Whispers

Per user: *"think of pomegranate hour as the lingering failure that
haunts the back of the mind."*

PH is not an apprenticeship Elicia is proud of. It's the wound the
mature work emerged in spite of. The show that didn't quite land,
that her cult audience still asks about, that she suspects she'll
never fully escape. Whispers came from PH the way a steadier hand
comes from a tremor — not gratefully.

What that means tonally:

- **The PH archive is a stack she has, more than once, considered
  destroying.** She hasn't. She also hasn't catalogued it cleanly.
  The tapes are in a corner of the suite without labels, in the
  order she shoved them there.
- **A PH still on her wall is a discipline, not nostalgia.** A
  reminder of what she's *not* making anymore. The frame is cheap.
  She has never replaced it.
- **The cult audience asks about PH** — twice a year on a Q&A panel,
  more in comments. She has a polite answer she's given two hundred
  times. The answer is *"I learned a lot. I don't watch them."* The
  second sentence is true.
- **Retired devices.** The 60 Hz hum, the 9:09 PM interference, the
  silent halftone host — devices PH used as load-bearing structure
  that Whispers skips entirely. When ambient hum hits 60 Hz at 9:09
  PM in the wild, she still notices, and she still can't unhear it.
- **Re-cut footage is salvage, not reuse.** When a PH take lands in
  a Whispers episode, it's because the take was honest and the
  surrounding episode wasn't. The salvage is sometimes ironic.
  Sometimes it's the only way to use a shot that almost worked.
- **The PH archive is the dark mirror of the current cutting room.**
  When she's editing Whispers, the half-question always in the back
  of her head is: *did I learn anything, or am I just running the
  same trick at a different camera height.*
- **PH locations are now charged.** The riverbank, the bungalow
  window, the abandoned diner booth — places PH shot first. Returning
  to them for Whispers is partly courage, partly inability to leave.
- **Returning actors are PH actors.** Anya is the strongest candidate.
  Working with them is a conversation about a thing nobody fully
  acknowledges and everyone remembers.

### What this means for the gauntlet

- **Priestess board is Whispers, haunted by PH.** Whispers is the
  active work — the cartographer episode, the Choose Your Own
  Adventure, the editing suite, the mirror shard, the dying basil
  plant. PH is the dark presence at the back of the suite — the
  unlabeled tape pile, the cheap-framed still, the polite Q&A
  answer, the rule against using the 60 Hz hum.
- **PH artifacts as visitable objects with weight, not warmth** —
  pulling a PH tape off the shelf costs sanity or stagnation. Re-cutting
  a PH take into a Whispers episode gives a real edit bonus AND a
  doubt tick. The salvage is its own grief.
- **The lore-doc 22-episode mapping** can be re-purposed as PH's
  back catalog — episodes she planned, episodes she shot and didn't
  finish, episodes she finished and is not proud of. Treat as
  Claude-extended decoration for now; canon may not lock 22 PH
  episodes specifically.
- **My gauntlet build's "Pomegranate Hour suite"** conflated the two
  works AND invented a half-finished college version that doesn't
  exist. Retire and rebuild around Whispers, with PH as the lingering
  failure at the back of the room.

---

## The sinkhole (the Nexus)

Years ago, in Graustark, on **Houston Street**. Ground opened. People died. *Reopens* at the end of vol 5, ch20.

Canon confirms:
- **Mackenzie's brother** died in the original sinkhole. The Polaroid returned to the Roberts in ch6 is from **June 2009**, showing him on Houston Street, "back to camera, hands in pockets," moments before the fall. (This roughly dates the original sinkhole to **summer 2009**, give or take.)
- **The sinkhole reopens at 10:47 AM Central** in ch20 — the same moment Joanna's letter arrives at Dean's address.
- **Dante dies with his riverboat** as the sinkhole reopens. He recognizes Dean from **1987**: *"You haven't aged."*
- The town is at the **Texas/Louisiana border**.
- The post-sinkhole town has Houston Street "now gone."

What is *not* canonical (but the lore docs assert as Claude-conjecture):
- That the void mother of Antonio + Alberto died at the sinkhole. **Ch4 mentions "the photograph of his wife on the wall opposite the desk — the photograph he had not replaced in twenty-three years, because he had decided, in the year after she died, that the photograph he chose to keep up was the one he had been looking at when she was alive."** So Dante's wife is dead — confirmed — but the date implied (~2003 if she died in the year before he stopped replacing the photo 23 years before 2026) does not match the 2009 sinkhole. The void mother's death may be unrelated to the sinkhole, or the date math is wrong. **Reserve.**
- That Anna's father (Marta Romero's husband) died doing boat work at the sinkhole for Dante. The PetroTex case is canon but the sinkhole-link is lore-doc conjecture.
- That Daigle's father's bar was lost at the sinkhole. Lore-doc conjecture.

---

## Per-arcana canonical reference

For each chapter: title + subtitle; setting; focal POV; key beats from the actual chapter prose; the gauntlet implications; what my repo currently has wrong.

### 0 — THE FOOL · "A Fool Between Acts"

- **Setting:** D'Ambrosio's diner / riverboat, 3:47 AM, pre-dawn. Texas/Louisiana border.
- **Focal POV:** John Frank — 20-something, grad student, "mixed-media journalist," waiter.
- **Four sub-scenes:** booth6, frasier, model_city, closing.
- **Key beats:**
  - A stranger orders coffee, leaves the message *"Watch yourself tonight, brother. The walls are thin."*
  - John folds a napkin into a flower-like shape; tucks it in his notebook without conscious intent.
  - Frasier emerges from the kitchen; *"Still chasing shadows, Johnny? Or are the shadows finally chasing you?"*
  - Frasier shows John his phone screen — geometric shapes pulsing in *"a color John had never seen on a screen before, a kind of luminous bruise."*
  - Frasier: *"The trick isn't to survive the fall, Johnny. It's to learn how to fly on the way down. Learn how to write about the landing."*
  - John writes in his notebook: *"Architect of Decay"* (underlined twice).
  - Closing thought: *"I think something is starting. I think something has been starting for a long time and I am only now noticing."*
- **Cross-references:** John meets Elicia in ch14/19 years later in Montreal. The folded napkin recurs.
- **REPO STATUS:** ✅ Right. D'Ambrosio's diner, John as hand, three scenarios.

### I — THE MAGICIAN · "Cathedral of Rust and Code"

- **Setting:** Frasier's warehouse — "cathedral" of rust, solder smoke, LEDs, miniature Graustark built from motherboards.
- **Focal POV:** Frasier Temple.
- **Key beats:**
  - The Demons live on Frasier's phone — *"humorous electronic imps birthed from code and chaos"* who are *"developing opinions not originating with Frasier."*
  - The Demon reports on John: *"Subject proximate. John Frank. Probability of existential navel-gazing: ninety-three point seven percent."*
  - Frasier uses a *neural shunt* to jack into the model city's overlay (called **GumboNet**) and surveils Graustark.
  - **The silver-spoon riverboat model refuses placement**: every time Frasier sets it on the model river, fluorescents flicker, temperature drops 4°. The Demon warns: *"Subject proximate to riverboat: do not place."* By ch21, after Dante's death, the riverboat has *"walked itself"* to its position and stayed there; Frasier seals it in a glass case labeled **D'AMBROSIO'S. 1983–2026. REST.**
  - The Demon: *"Tempting the void again, Architect. Careful it doesn't swallow you whole."*
- **REPO STATUS:** ✅ Mostly right. The "demons" are explicitly canon mechanic — keep them as Frasier's actual tools, not as my "warehouse demons" stand-in.

### II — THE HIGH PRIESTESS · "Exit Through the Gift Shop"

- **Setting:** Elicia's rented bungalow on Graustark's fringe, dusk.
- **Focal POV:** Elicia Duchane, early 30s.
- **Key beats:**
  - She's packing to leave Graustark after two years.
  - Web series *Whispers from the Liminal* has a cult audience.
  - Mirror shard found near the sinkhole's edge three years ago refuses disposal; fractal reflection of *"twelve Elicias, none whole."*
  - *"Choose Your Own Adventure"* episode in progress; she prefers Option C: *"realize free will is illusion, embrace the void."*
  - Footage of Anya: *"The map was never about finding a destination."*
  - Mackenzie texts *"Are you okay"* (no question mark). Elicia replies: *"Define okay."*
  - In part B: she powers up the editing suite; finds John's 3-week-old email from Montreal (*"You don't have to write back"*) and replies in one word: *"Yes."*
  - Waters the dying basil plant.
- **REPO STATUS:** ⚠️ Major rebuild. My Pomegranate Hour build was wholly invented (six fake episodes, college collaborators that don't exist). Elicia is a *solo* director of a web series called *Whispers from the Liminal*; the lore-doc "Pomegranate Hour with 22 episodes" is invented.

### III — THE EMPRESS · "Static Bloom"

- **Setting:** D'Ambrosio's riverboat dining room, Friday night.
- **Focal POV:** Nicola Greer, 19, hostess. (Aria emerges as interior consciousness during the chapter.)
- **Key beats:**
  - Nicola: *"Eye candy. Fucktoy. Vessel. Whatever. Labels were just static cling."*
  - Pregnancy is real; she feels *"a kick, low and insistent."*
  - **Aria** — Dickens Dean's digital consciousness made flesh — speaks inside her: *"Who am I. Where is my father."* / *"This is not a body. This is a protocol."*
  - **Dean** sits at Table 14, observes for two hours, leaves a hand-written note: *"When you're ready"* + phone number, weighted under a $100 bill.
  - End: *"Two heartbeats inside her, now. Maybe three."*
- **REPO STATUS:** ❌ Wrong. I built Nicola on a separate riverboat moored at Dante's office. Canon: she works AT Dante's riverboat (D'Ambrosio's IS the riverboat — there's no separate boat).

### IV — THE EMPEROR · "Thicker Than Water, Slower Than Time"

- **Setting:** Same riverboat, helm/upper deck and dining room. Friday night, continuous with ch3.
- **Focal POV:** Dante D'Ambrosio, 60.
- **Key beats:**
  - *"His kingdom. His goddamn cage."*
  - The riverboat is D'Ambrosio's — built brick by bloody brick over 60 years. Ice in bourbon is for the weak.
  - **Alberto** (older, Houston, "Mr. Logic and Order," in glass tower) and **Antonio** (younger, New Orleans, "the artista," with Jimmy Daigle).
  - Antonio calls on the first Sunday of even-numbered months; *"Neither had ever said anything important. Both knew this."*
  - The wife photo on the wall has not been replaced in 23 years (since the year after she died — math says she died ~2002).
  - **Dean** at Table 14 leaves no order; departs through the side door, exits through the parking lot in a dark sedan parked beyond Dante's 2003 security camera's reach.
  - Dean's card: *"Mr. D. Dean. Consulting. Dispute resolution and legacy planning."* The back is blank.
  - Dante does not burn the card. *"A man who burned his evidence was a man who was afraid. A man who kept his evidence on the corner of his desk, square, was a man who had decided to know."*
  - Closing: *"The Emperor, at the helm of nothing, drank."*
- **REPO STATUS:** ❌ Major reframe. I built him as a small civic lawyer with a brass clock and missing river-code volumes. Canon: he's the riverboat proprietor, a gangster-turned-restaurateur, with deals made on docks slick with more than river water.

### V — THE HIEROPHANT · "Sweaty Sunday Sermonettes"

- **Setting:** St. Jude's Acadian Church exterior; D'Ambrosio's at Sunday brunch; Antonio's office in New Orleans; a park near the old Armory.
- **Focal POV:** multi-POV — Maya Daigle (age 7) outside the church, Gloria Reyes (waitress) at brunch, Antonio (phone call), John Frank (observer in the park).
- **Key beats:**
  - 7-year-old Maya feels Q. Paul's eyes catalog her *"like being caught doing something wrong."* She has been *"entered in some private ledger... not, on balance, a good one."*
  - **Q. Paul (Quentin Paul)** holds court at Table 17 at brunch, pontificating on *"tradition, structure, moral fabric."* Post-sinkhole he has become *"even more commanding."*
  - Gloria observes the *"tension in his jaw, slight tic near eye, right sleeve cuff twisted down... righteousness masking something else. Something brittle. Maybe something afraid."*
  - Q. Paul phones Antonio: *"James. I think it's time you and I had a conversation."* Speaks of *"alliances, careful navigation."* References Dante in past tense: *"bless his memory."* Antonio realizes Paul is cataloging Dante as a closed account.
  - John in the park, writing: *"Hierophant. Tradition. Institution. Interpretation of Sacred Knowledge. But the rigidity — borders on tyranny?"*
  - John: *"Don't approach him. He's the kind of subject you write around. Witness from the periphery."*
  - *"The fear of him was the point. The empire was just the means."*
- **REPO STATUS:** ❌ Miscast. I built "Father Quent" as a priest with a cable Channel 14 show. Canon: Q. Paul is a power-broker / patriarchal pressure figure, not a priest, and he holds court at the riverboat brunch.

### VI — THE LOVERS · "Sanctuary on Cursed Ground"

- **Setting:** Mackenzie & Philip Roberts' house, kitchen, front porch. Morning.
- **Focal POV:** shared — Mackenzie and Philip Roberts.
- **Key beats:**
  - Philip fighting a kitchen faucet that won't stop dripping for three weeks.
  - They live on "cursed ground" — the edge of the sinkhole area.
  - *"Rich in reclaimed driftwood and sourdough starter; spectacularly poor in actual currency."*
  - Mackenzie lost a pregnancy last year. They have two living daughters: the older girl named for Mackenzie's brother (lost in the sinkhole); the younger is **Sam** *"for now."*
  - Radio: ongoing seismic instability; Dante advertising his new Houston location.
  - A boy arrives with an envelope: *"My grandma said to give you this. She said she's sorry. She said you'd know what for."*
  - Inside: a **Polaroid dated June 2009 of Houston Street**, showing Mackenzie's brother in the foreground, back to camera. On the back: *"He waved."*
  - Mackenzie: *"He wouldn't have. He never waved at anybody he didn't know."*
- **REPO STATUS:** ❌ Wholly wrong. Sasha/Reed/the apartment over John's diner are fabrications. The Lovers is the Roberts on cursed ground with the returned Polaroid.

### VII — THE CHARIOT · "Two Horses, One Wreck"

- **Setting:** Antonio's hot office above the warehouse that will become Ember & Ash, the Marigny in New Orleans, August.
- **Focal POV:** Antonio D'Ambrosio, 34.
- **Key beats:**
  - *"Two speeds: gone and about to be gone."* (Girlfriend at 23. Antonio is 34. Eleven years of that diagnosis.)
  - Q. Paul calls. Antonio counts to 27 seconds (voicemail). Doesn't listen to them. *"The silt itself constituted a kind of message."*
  - Cypress beam from a Lafayette salvage yard, not going up straight. The foreman: *"In this building, in this town, in this neighborhood, that is the same word."*
  - Lila Bao is sending three-line emails (means somebody's courting her).
  - The man in the charcoal suit watches from the corner across the street for 40 minutes, cigarette advancing a centimeter, then drives away in a dark sedan from the shadow of the dumpster.
  - Jimmy: *"That's Q. Paul's. I've seen him before."* And: *"He's not just Q. Paul's. He works for more than one shop."*
  - Jimmy's option four: *"You let me handle it... It means you don't ask me what it means."*
  - Antonio holds his thumb above DAD for eleven seconds. Does not call.
  - Closing: *"for the first time in eleven years, did not feel certain that he had two speeds. He felt, briefly and clearly, that he had only one. The remaining speed was gone."*
- **By ch21:** *"Antonio D'Ambrosio is, against all expectation, still at Ember & Ash. The cypress beam held. The city inspector has not come back. The gas line got approved on Monday. Lila Bao, the chef, called last week — just to check in."*
- **REPO STATUS:** ❌ Wholly wrong. Cora and the midnight bus is invented. Canon: Antonio at Ember & Ash, New Orleans.

### VIII — STRENGTH · "The Ouroboros in the Ashtray"

- **Setting:** the Iron Crow bar in New Orleans; Douglas's motel room above a laundromat.
- **Focal POV:** Douglas Forte.
- **Key beats:**
  - *"Stillness was a kind of armor."*
  - Hands scarred from *"busted fences and kitchen brawls from back when Dante's word was law."*
  - **Ouroboros tattoo** on forearm: *"the only honest piece of him."*
  - Joanna (his lost lover): *"It's a picture of itself eating itself, and that's true."*
  - Summoned by Jimmy to "keep Antonio safe" — but realizes he's being used.
  - Writes a letter to Jimmy: *"I know what option four is. I figured it out tonight at the bar. I'm not going to tell you I figured it out. I'm not going to do anything different. You should not change your plan."*
  - *"I want you to do me one favor when it's done. I want you to call Philip Roberts and tell him where I am."*
  - *"Tell Maya I think about her. Don't tell her how."*
  - Realization: *"I am the piece. Jimmy is not the operator. I am."*
- **By ch21:** Douglas walked five days from New Orleans to the Roberts' house. Philip met him halfway. He drinks three glasses of iced tea and sleeps for a couple days in the finished basement. Tools in Philip's shed have been *"quietly organized into the arrangement Doug preferred when he worked, because Philip remembered what that arrangement had been, from 2018, when they had rebuilt the gate."*
- **REPO STATUS:** Not yet built.

### IX — THE HERMIT · "Labyrinth of Scrawled Echoes"

- **Setting:** Graustark ruins (Houston Street area, near the sinkhole).
- **Focal POV:** Joanna LeMoine, mid-40s.
- **Key beats:**
  - Sole resident of the ruin-scape. Companions: three-legged calico, one-eyed shepherd mix named **Rumpus**, a crow that brings gifts.
  - Scrawls poetry on walls with chalk/charcoal: *"The map is not the territory. The territory eats the map."*
  - The crow brings a folded paper from 1987 — receipt from **Adelphia's Deli**, $4.85 cash, with a doodle on the back: *"a small four-foot-tall figure in a cork hat, smoking a hand-rolled cigarette, sitting beside a river."*
  - Below the doodle: *"See you soon."*
  - Joanna recognizes the figure (the Frog).
  - She writes: *"I am ready. Come and find me."*
  - Mails a letter using the 1987 receipt's address — to the Frog. The cycle began at this address in 1987 and is closing.
- **REPO STATUS:** Not yet built.

### X — WHEEL OF FORTUNE · "Closing Arguments Against Chaos"

- **Setting:** Erica Campbell's Houston office (high-rise), Saturday morning.
- **Focal POV:** Erica Campbell, 40s, corporate lawyer.
- **Key beats:**
  - Motion denied. Six weeks of arguments. *"The ground had felt suspiciously unsteady all week."*
  - Designs a contract for Antonio that is "invisible" — converts on default into Alberto's stake. Elegant. Deepens Alberto's ownership of Antonio.
  - Marcus (assistant): *"There's a man in the lobby asking for you. Saturday. Without an appointment."* The man: *"Mr. D. Dean. Consulting."*
  - Erica: *"Tell the desk Mr. Dean can come up at nine-fifteen."*
  - *"I have crossed a line I had not, until this morning, fully understood I was approaching."*
  - She decides not to stop.
- **By ch21:** in a Hill Country cabin with Jordan the painter. Has not signed the Antonio contract. Has decided *"either outcome is, for the first time, acceptable."*
- **REPO STATUS:** Not yet built.

### XI — JUSTICE · "Scales Already Shattered"

- **Setting:** Erica's Houston office (Saturday); Anna Logue's design studio same building, different floor.
- **Focal POV:** dual — Erica Campbell + Anna Logue.
- **Key beats:**
  - Erica hasn't slept in 5 days. PetroTex settlement file open on a second monitor.
  - *"Justice. Accountability. Hollow words against the raw tectonics of consequence."*
  - **Anna Logue**, designer working on Ember & Ash branding. Creates *Corporate Idols* — deconstructs the D'Ambrosio logo so the ascenders become wrought-iron courtroom columns, the apostrophe becomes a gavel, the underline becomes a redaction bar.
  - Saves as `D'AMB-IDOL-01.psd` to a private cloud Ben (her boyfriend) doesn't have access to.
  - Leaves the office early for the first time without filing a request with HR.
- **By ch21:** Anna has resigned (Thursday). In Marfa. The journalist she sent the file to is running it in December. Beginning a second piece on the NexCorp logo.
- **REPO STATUS:** Not yet built.

### XII — THE HANGED MAN · "Gravity is Optional After Midnight"

- **Setting:** Natalie David's apartment in **Simons** (above a bagel shop), pre-dawn.
- **Focal POV:** Natalie David, mid-30s, waitress/diviner.
- **Key beats:**
  - Phases through the apartment door, shedding her waitress uniform "like a snake shedding skin."
  - Air thickens; refrigerator cycles out of rhythm; streetlight flickers.
  - At 5:07 AM, the record player (off) clicks; tonearm lifts itself; settles on Nina Simone.
  - A voice (not Nina's) speaks through the vinyl: *"Natalie. You have a visitor coming. Wake the girl. Both of her."*
  - Natalie wakes Nicola and Aria (in the same body).
  - **Miriam** arrives with a crow on her shoulder: *"I'm a friend of Joanna LeMoine's. She's asked me to come get you. Somewhere safe. Somewhere where what's growing in you can grow. Both of what's growing in you."*
  - 5:14 AM doorbell. 2009 Subaru. The crow rides on the roof.
  - **Aria speaks directly to Natalie for the first time** (not through Nicola): *"She's telling us she knows we're moving."*
  - **The Third Consciousness** is recognized as a third presence.
  - At the county line at 7:52 AM, Miriam drops Natalie and keeps driving west.
- **REPO STATUS:** Not yet built.

### XIII — DEATH · "Walpurgisnacht in Ward C"

- **Setting:** St. Jude's Mercy hospice, Room 217, Simons.
- **Focal POV:** Alice Newsom, late 60s — plaintiff of record in Newsom v. PetroTex.
- **Key beats:**
  - Awake since 3 AM. A white rose appears on the windowsill, brought by no staff member she heard.
  - *"Preliminary courtesy that the older system extended... to the people who had been paying attention."*
  - Death is courteous, sits in the chair by the window. Family arrives: grandmother, lost friend, estranged brother, the dog Buster.
  - She thanks Erica Campbell silently for keeping Henry's name on the settlement document.
  - *"I'm coming. Don't dig anything up."*
  - At 4:06 AM, the night nurse finds Room 217 empty. Rose bloomed open.
- **REPO STATUS:** Not yet built.

### XIV — TEMPERANCE · "The Moderate Temperature of Tuesday"

- **Setting:** Café Olimpico, Saint-Viateur, Montreal. Late May. **Several years after vol open.**
- **Focal POV:** John Frank — now late 30s, settled in Montreal for 6 years.
- **Key beats:**
  - Comes to the café every Tuesday for 6 years.
  - Tracks dust motes; they cluster on Tuesdays.
  - Elicia responded to his email (3-week-old, 7 months earlier) with one word: *"Yes."* They've been meeting every Tuesday since.
  - Elicia was initially broke, evicted, filming herself for 11 days.
  - John has an unsent novel: `gtk_drft_v6_FINAL_actual`, 97,000 words.
  - Emails Mackenzie Roberts twice a year. Gets Christmas cards from Erica: *"mostly, mostly, mostly."*
  - A woman with **blue dreadlocks** (Tem, ch21) arrives at 10:23 AM with a man neither of them recognize.
  - John tells Elicia: *"The dust motes have a pattern, and I have... been tracking the pattern. It clusters on Tuesdays."*
  - Elicia: *"Tell me when you're ready."* John: *"I'll tell you eventually. I'm not ready."*
- **REPO STATUS:** Not yet built.

### XV — THE DEVIL · "Gumbo Limbo"

- **Setting:** Jimmy Daigle's rented apartment above a laundromat in New Orleans, pre-dawn.
- **Focal POV:** Jimmy Daigle.
- **Key beats:**
  - Wakes hungover. *"A hangover was a full-body audit of last night's bad decisions."*
  - Realizes he's become the Devil. *"Loyalty felt suspiciously like leverage now. Protection looked a lot like control."*
  - Maya is 16, last call seven months ago.
  - Q. Paul calls: *"James. I think it's time you and I had a conversation. There's a bar in the Marigny called the Iron Crow. I believe you know it. Three o'clock. Don't bring anyone."*
  - Jimmy realizes: *"The chains just tightened, and I am, evidently, the link being adjusted... This is what it feels like when you are not, in fact, the operator. This is what it feels like when you are the operated."*
  - Antonio calls: city inspector at the office, something about the gas line.
  - Finds Doug's letter. Realizes *"Doug is, in this play, the operator. I am the operated."*
  - Calls Maya: *"Listen to me. Stay inside your grandmother's house. Don't go out. I'm going to send someone to get you. His name is Philip Roberts."*
  - *"I love you." / "I know."*
- **By ch21:** Jimmy in Arizona, *"the kind of place you check into for the detox after the detox, the one where they don't let you have phones and they make you do chores and the chores are the medicine."*
- **REPO STATUS:** Not yet built.

### XVI — THE TOWER · "Evangeline in Render Queue"

- **Setting:** Elicia's Montreal apartment above a bagel shop, late October.
- **Focal POV:** Elicia Duchane.
- **Key beats:**
  - Apartment in ruins. 3 months behind on rent; eviction notice on the door.
  - Hasn't photographed anything in 11 weeks.
  - Filmed herself every day for 3 months; 30 hours of footage.
  - Mother's teacup unpacked but dusty.
  - Records herself for 13 minutes in silence; the *"small honest collapsing the realization required."*
  - Replies "Yes" to John's email.
  - Mackenzie calls: *"Elicia. We need you home."* Books a flight.
  - Records: *"Alright. Scene One. Take One... I'm going to start telling one about myself. I don't know how long it's going to take. I don't know if it will be any good. I am going to tell it anyway. Take Two."*
  - *"It was, for the first time in twelve years, enough."*
- **REPO STATUS:** Not yet built.

### XVII — THE STAR · "Glass Skin and Obsidian Ink"

- **Setting:** Graustark ruins, night.
- **Focal POV:** Joanna LeMoine.
- **Key beats:**
  - *"Glass skin on bone frame, transparent, permeable."*
  - Has a vision of everyone in the volume simultaneously.
  - *"I have done my part. The letter is mailed. The rest is not mine to hold."*
  - Wall verse: *"I did not lose Douglas. I sent him. / I did not lose myself. I have been spent. / I am the page on which the older system writes its drafts."*
  - Instructs the crow: *"Tell him. Tell him I'm sorry. Tell him I knew. Tell him I sent him. Tell him I was used to send him. Tell him both are true."*
  - The crow flies southeast.
- **REPO STATUS:** Not yet built.

### XVIII — THE MOON · "Sigils in Static"

- **Setting:** Natalie's apartment (5 AM); Miriam's car driving west.
- **Focal POV:** Natalie David.
- **Key beats:**
  - Cards fly upward; the Hanged Man card settles back down, *now smiling.*
  - Record player (off) plays silence between tracks; speaks: *"She arrives in five months. You will be present. Prepare the room."*
  - Natalie clears a storage space for a crib.
  - Miriam tells Aria: *"You've been broadcasting on a frequency Joanna LeMoine has been listening to for thirty-eight years, dear."*
  - At the county line (7:52 AM), Miriam drops Natalie.
  - Natalie's dream journal: *"Today I mailed a girl south and got a letter back from the dark."*
- **REPO STATUS:** Not yet built.

### XIX — THE SUN · "Pattern Recognition in Dust Motes"

- **Setting:** Café Olimpico, late May, Montreal.
- **Focal POV:** John Frank. (Continuous-feeling timeline with ch14.)
- **Key beats:**
  - Sees the blue-dreadlocked woman (Tem) and a man at a window table.
  - *"That woman is not from here." / "That woman is looking for someone." / "That woman is in your pattern, John."*
  - Elicia takes his hand briefly, contract-like.
  - John has received a text from a Texas number (Frasier): hasn't told Elicia yet.
  - *"The light held."*
- **REPO STATUS:** Not yet built.

### XX — JUDGEMENT · "The Stillness Breaks / The Sound Arrives"

- **Setting:** Graustark, Houston, New Orleans, Montreal, Louisiana roads, hospice, multiple locations simultaneously.
- **Focal:** ensemble cross-cut.
- **Key beats:**
  - **10:47 AM Central:** the sinkhole reopens. *"A sound that was less sound and more the raw tearing of the world's fabric."*
  - Joanna's letter arrives at Dean's address. Dean *"walked, unhurried, to the door"* and begins moving.
  - John receives text: *"did you feel it."* Replies: *"yes. i'm coming."*
  - Erica: *"the Wheel had stopped spinning. The Wheel had flown off its axle entirely."* Goes to Jordan.
  - Joanna walks to the post office on Elm; a crack runs from the outgoing bin to her feet; clerk: *"Go, Joanna. Go now."*
  - **Nicola/Aria in the car:** the Third Consciousness speaks in her own voice for the first time: *"Mama. Mom. It's okay. I know where we're going. Stay in the car."*
  - **Dante** at the helm — the boat sinks. Looks at Dean's card a last time: *"I know you, you sonofabitch. I knew you in 1987. You haven't aged."* The water comes up to meet him.
  - Alberto in Houston receives a phone call; remains silent; looks east.
  - Antonio doesn't answer; later plays voicemail.
  - The cypress beam at Ember & Ash hangs straight for the first time.
  - **Douglas** stands at the Iron Crow at the moment of tremor; walks north out, *"knowing he would walk for days."*
  - Jimmy calls Maya, asks Roberts to retrieve her. Maya: *"Okay, Dad. I will."* *"I love you." / "I know."*
  - Mackenzie picks up the phone before it rings. Philip: *"I'll get them. You call Elicia."*
  - Elicia is filming when the tremor hits: *"Something is happening. I am going to keep the camera rolling."*
  - Alice's white rose blooms fully open at 10:47 AM. Alice has passed.
  - Anna's monitor lines distort. Saves work, emails `D'AMB-IDOL-01.psd` to journalist, walks out.
  - The Frog: *"The Frog, in the wreckage, inhaled. Then the Frog, in the wreckage, stood."*
- **REPO STATUS:** Not yet built. (The `world_state.json` sinkhole_open injector is the right mechanism but is currently underweighted — this is *the* event.)

### XXI — THE WORLD · "Frog Knows Best, Mostly"

- **Setting:** Graustark riverbank in the after-time. Sunlight thick and syrupy yellow. The rusted **Minstral's Green** steamship sits quiet *"like a beached metal whale dreaming of deeper waters."*
- **Focal POV:** the Frog (and ensemble round-up).
- **Key beats:**
  - The Child by the river pokes a stick at a crawdad hole; wears the *"black egg doohickey"* (humming since Tuesday).
  - The Frog rolls a cigarette: *"Poke that hole much harder, pink one. And somethin' uglier than you gonna come lookin'."*
  - Dean visited Joanna four days ago: *"Ms. LeMoine. I received your letter. I have been waiting to receive it for some years. I want to say thank you. I also want to say: not today. I will be back when the child is ready. You have done your part. Please rest."*
  - The Roberts: Philip rebuilt the porch. Mackenzie weaving curling patterns on her loom. Talk of another baby.
  - Maya at the Roberts', 16, reading short stories by a Louisiana woman who died young.
  - Frasier built a glass case around the silver-spoon riverboat: **D'AMBROSIO'S. 1983–2026. REST.**
  - Douglas asleep in the basement. Tools in Philip's shed organized to Doug's preferred 2018 arrangement.
  - Erica in a Hill Country cabin with Jordan. Cooking badly. Antonio's contract unsigned.
  - Anna in Marfa. Second Corporate Idols piece begun (NexCorp).
  - Antonio still at Ember & Ash. Beam held. Lila called. **Alberto quietly paid off two of Antonio's vendors; waiting for Antonio to call.** *"Their father is dead. They have, in some very old sense neither of them has articulated, become the only men left in the family with authority over how that fact is going to be carried."*
  - Natalie clearing a corner. Crib in 6 weeks.
  - Elicia in NYC (Brooklyn cousin), editing. *"The film, when it comes out, will be small and fierce and honest."*
  - John Frank on a plane to Houston. *"He will, eventually, be present at her birth — on a screened porch of a modest cabin in **Smolvud, Oregon**, in the company of a midwife named Lena and a silver-haired woman named Miriam and a girl of nineteen and her other self and a man named Philip Roberts who drove thirty-two hours to be there — and he will, eventually, be the one who writes her first book for her."*
  - Frog: *"The old one has two more errands. One short. One long. After that, I take over again."*
  - **Sofia in Rio de Janeiro** dreams of a man in a bomber jacket (Frasier?): *"You are next. Don't worry. You don't have to hurry. But you are next."* Writes in Portuguese: *"I had the dream again. The man with the bomber jacket. The riverboat in the glass case."*
  - **Tem in Smolvud, Oregon**, blue dreadlocks, yellow rain slicker, reading John Frank's self-published novel on a pier looking at the **Minstral's Green** (relocated from Louisiana).
  - The novel is dedicated to a girl named Sofia whom the author had never met.
  - Frog's vol 6 preview: *"the planned communities. The suburbs. The NexCorp vans. The kid in the garage. Young Sam gettin' her heart broken open by the world. Maya goin' through her archives. Jesse's dad's camera eyes. Backyard Beatdowns. Dial-up screams. The whole greige apparatus."*
  - Frog's vol 7 preview: *"Smolvud. The coast. Kai and the ferret. Lena and her octopus. Finn and his crow. My favorite little triumvirate. Real scrappy, that bunch."*
  - Closing: *"End of Act One."*
- **REPO STATUS:** Not yet built.

---

## What's wrong in the repo

### Wholly fabricated content (retire as canonical scenarios; demote prose to visitor flavor)

| File set | What it is | Canon override |
|---|---|---|
| `chariot/*` + `locations/the_midnight_bus.json` | Cora the midnight bus driver | Chariot = Antonio at Ember & Ash, New Orleans |
| `lovers/*` + `locations/apartment_above_diner.json` | Sasha + Reed in apartment above diner | Lovers = the Roberts on cursed ground, the returned Polaroid |
| `hierophant/*` + `locations/bbs_room.json` | "Sysop" running ember.ash.rest.bbs | Hierophant = Q. Paul (Quentin Paul), patriarch / pressure figure |
| `priestess/*` Pomegranate Hour suite | 6 invented episodes, college collaborators (Hen/Marisol/Davey) | Elicia is a solo director of *Whispers from the Liminal*; lore-doc "Pomegranate Hour" is invented |

### Misframed but salvageable

| File set | What needs adjustment |
|---|---|
| `emperor/*` + `locations/dantes_office.json` | Dante isn't a small civic lawyer — he's the riverboat proprietor. The board may need to be the riverboat helm + dining room. |
| `empress/*` + `locations/riverboat_interior.json` | Nicola is the hostess AT the same riverboat (D'Ambrosio's). The Empress board overlaps with the Emperor's. Aria mechanic needs to be a feature. |

### Right and intact

| File set | Status |
|---|---|
| `fool/*` + `locations/dambrosios.json` | Aligned with canon |
| `magician/*` + `locations/cathedral.json` | Aligned. The Demons are *canonical* — keep them as Frasier's real mechanic. |
| Engine code | All infrastructure is sound. The `hand_overrides`, episode-state, `verb_labels`, achievement evaluator — they all stand. |
| `world_state.json` sinkhole_open injector | Right mechanism; needs amplification — the sinkhole is THE event, all 22 arcanas touch it. |

### Invented characters to demote to visitor flavor (per user direction)

These keep existing as ambient cast in canonical scenarios, never as hands:
Cora, Sasha, Reed, the late-shift worker / lost traveler / old regular / late couple / kid running away (Chariot passengers), bus kid messenger / upstairs neighbor / old friend / landlord (Lovers visitors), Sal / Frank / Elena / the bus kid in the guest-lens prototype (Emperor/Sal scenario), the entire "Pomegranate Hour" college crew (Hen/Marisol/Davey/Reggie/Prof Kang/the New Collaborator), the dream-version subjects (Two-Chairs Women, Bus Driver, Diner Cook, etc.). All retire as candidate hands; survive as visitor flavor where they fit.

---

## Tonal rule (from user)

**Dream logic stays in the Priestess.** Other arcanas earn weight through specificity, not animism.

- ✅ The cypress beam needs to be straight, not straight enough.
- ✅ Sammy has been pouring at D'Ambrosio's for 60 years.
- ✅ The brass railing has been the wrong-bright since the second year; Dante maintains it on principle.
- ❌ "The room remembers."
- ❌ "The bus has been remembering since 1991."

Dream logic earned in the Priestess: the recursive footage, the fractal mirror shard, the dying basil plant, the editing-suite Choose-Your-Own-Adventure that becomes literal.

---

## Working method going forward

1. **Read the chapter scene before building.** When authoring a new arcana, the relevant `vol5_ch<N>_<arcana>.json` is the canonical source. Any lore-doc reference is hypothesis only.
2. **Quote canon when locking choices.** Anchor each gauntlet decision in a specific narrate line from the chapter; cite chapter+line if going to scrutiny.
3. **Demote, don't delete invented cast.** They keep existing as visitor flavor inside canonical scenarios. Nothing wasted.
4. **The sinkhole is everywhere.** Every arcana touches it. The world_state injector for it should be the deck's most pervasive ambient — currently underweighted.
5. **Track scaffolding-vs-canon in this wiki.** When `lore/` and canon agree, note it as confirmation. When they conflict, canon wins.

---

## Surgery (completed)

Catastrophically miscast files have been retired. State:

**Deleted (Claude-invented, no canonical basis):**
- `chariot/` — setup_*.json (3), action_cards.json, gravity_deck.json, finale.json, items.json, die.json, threats.json
- `lovers/` — same set
- `hierophant/` — same set
- `priestess/` — same set (the invented Pomegranate Hour suite)
- `emperor/setup_johns_review.json` — invented guest-lens scenario
- `locations/the_midnight_bus.json` — Cora's bus
- `locations/apartment_above_diner.json` — Sasha/Reed apartment
- `locations/bbs_room.json` — invented BBS room
- `locations/recording_booth.json` — invented PH suite (Whispers rebuild pending)
- `hands/cora.json`, `hands/sasha.json`, `hands/sysop.json` — invented hands

**Preserved as flavor pool** (scope renamed to `_flavor_pool`, marked DEPRECATED in notes):
- `chariot/visitors.json` — Cora and passengers (writing reservoir)
- `lovers/visitors.json` — Sasha/Reed/bus kid/etc. (writing reservoir)
- `hierophant/visitors.json` — TOWER/Lurker/Anya recording/etc. (writing reservoir)

**Cleaned cross-references:**
- `achievements.json` — removed `lovers_complete`, `chariot_complete`, `priestess_complete`, `conversation_began`, `davey_speaks`, `young_self_speaks`, `johns_review_passed`, `an_episode_was_made`, `hierophant_complete`, `empress_complete`, `first_pair`, `the_tideline`, `long_quiet_used`. Kept the deck-wide ones (first_win/loss, clean_run, low_doubt, no_stagnation), the Fool/Magician complete entries, the sinkhole_opens trigger, the_decree, demon_survivor, first_septenary, candles_lit. Emperor_complete kept with a note pending reframe.
- `world_state.json` — removed `conversation_began`, `brood_emergence`, `the_apartment_held`, `the_route_runs`. Kept `sinkhole_open` (with strengthened note that it is the canonical Nexus event and is underweighted), `first_septenary_won`, `candles_lit`.
- `scenes/menu/GalleryOverlay.gd` — Priestess/Lovers/Hierophant/Chariot PLAY button overlays removed; visualizers still render the arcana cards. PLAY returns when canonical scenarios land.

**Still intact and canon-aligned:**
- `fool/*` + `locations/dambrosios.json` (canonical Fool at D'Ambrosio's, three scenarios)
- `magician/*` + `locations/cathedral.json` (canonical Magician at Frasier's warehouse, three scenarios)
- `hands/john_frank.json`, `hands/frasier.json`, `hands/elicia.json`, `hands/nicola.json`, `hands/dante.json`
- Engine code (TarotGauntletGame.gd) — all infrastructure (hand_overrides, episode-state machinery, verb_labels, achievement evaluator) intact
- `world_state.json` sinkhole_open injector

**Still in repo but pending canon reframe:**
- `emperor/*` + `locations/dantes_office.json` — Dante is canonically at the riverboat helm (not a civic office), but the existing scenarios are runnable and prose is partly salvageable. Reframe queued.
- `empress/*` + `locations/riverboat_interior.json` — Nicola is canonically the hostess at D'Ambrosio's riverboat, not a separate boat owner. The riverboat location is the right setting; the framing needs to align with vol5 ch3 (Nicola hosting Aria, pregnant with the Third). Reframe queued.

## What to build next, in priority

1. ~~Surgery~~ (done)
2. **Rebuild the Chariot** around Antonio at Ember & Ash. Hand: Antonio. Location: hot office above warehouse, the corner across the street, the warehouse below. Visitors: Jimmy Daigle, Q. Paul (off-board, phone-only — 27-second voicemails), the older man in the charcoal suit (silent menace), Lila Bao (phone), Antonio's father DANTE (phone, but ch7 is *before* Dante's death — the call he doesn't make is the call to a father about to die in ~6 weeks), Alberto (the surviving brother).
3. **Rebuild the Lovers** around the Roberts. Location: their bungalow on cursed ground (kitchen, porch, the spare bedroom they keep made up). Visitors: Elicia (in crisis), the boy with the envelope, Mackenzie's brother (in the Polaroid). Doom-clock candidate: the faucet drip Philip can't fix.
4. **Rebuild the Hierophant** around Q. Paul. Location: where he holds court — Table 17 at D'Ambrosio's brunch + St. Jude's church exterior + a New Orleans phone line. Visitors: Maya (7), Gloria the waitress, Antonio (phone), John (in the park).
5. **Reframe the Empress** for Nicola at the same riverboat where Dante presides. Aria as in-body NPC. The Third Consciousness as a hidden third.
6. **Reframe the Emperor** for Dante at the riverboat helm. The Dean card is the doom-clock. The pile of unread voicemails is the same dynamic as Antonio's silt. Father and son both ignoring incoming.
7. **Pomegranate Hour rebuild** — leave fallow until the show's actual structure surfaces in canon. Strip the invented 6 episodes from the suite; pare back the Priestess to *Whispers from the Liminal* with whatever canon has named (the Cartographer's Compass episode, Anya, the mirror shard).

After that, the remaining 14 arcanas (VIII–XXI) build out from the chapter scenes — they're all sketched in canon, just not yet in the gauntlet.

---

## Reading queue

- All `lore/pitches/*` (per-card pitches, Claude-generated; check against canon)
- `lore/_DEMONIC_DOMAIN.md` (electronic domain — may align with canon Demons)
- `lore/_DAMBROSIO_EMPLOYEES.md` (Claude-generated; may surface useful texture if it aligns)
- `lore/planned_community/*` (vol 6 lore; check against the Frog's vol 6 teaser)
- `lore/milk_and_honey/*` (vol 7 lore; check against the Frog's Smolvud teaser)

When any of these conflict with canon, canon wins.
