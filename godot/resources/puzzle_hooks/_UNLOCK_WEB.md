# Unlock Web — per-card outbound edges across the 22-card network

This doc catalogues, for each Major Arcana card, every other card
it could/should wake content on. The goal is the growth plan: 462
potential edges (22 × 21), of which the current build wires 84
live gates plus 10 diorama-internal unlock keys. The remainder is
either proposed for vol5 finishing or reserved as vol6+ forward
seeds.

Use this doc as:
- a **build checklist** when extending the deck (each "proposed"
  row is a discrete edit: add gated_by hotspot + matching cipher)
- a **lore index** (each row carries a one-line description of
  what would wake and why it makes sense)
- a **refactor guide** (the matrix shows where the network is
  thin vs. dense; thin patches may need diorama-level work)

## How to read

Each card section lists:

- **Live (L)** — wired in the current build. Either as a gated_by
  hotspot, an opens_diorama entry, or a cipher cross_reference
  surfaced via the discovery layer.
- **Proposed (P)** — design-complete; could be wired in vol5
  without new art or new diorama infrastructure.
- **Forward seed (F)** — the deck implies a connection but it
  belongs to vol6+ (or a later painted card lands).

Per-card edges are listed in numerical destination order. Each
edge has a brief tag describing what would wake on the target
card when the source card's content fires.

## The 22 × 22 matrix

Rows = source card (the click that fires the unlock).
Columns = target card (where the dormant content lives).
Diagonal (self) = `·`.

Symbols:
- `L` = live edge (wired in the current build)
- `P` = proposed for vol5 (design-complete)
- `F` = vol6+ forward seed
- `·` = self (no edge possible)
- `_` = no natural connection (the deck has not seeded one)

```
        0  I II III IV  V VI VII VIII IX  X XI XII XIII XIV XV XVI XVII XVIII XIX XX XXI
   0  · L  L   P  L  L  L  L   L  P  L  L   L    L  P  P   P    P    L   P  L   L
   I  L  ·  L   L  L  L  L  L   L  P  P  P   P    P  P  P   L    P    L   P  L   L
  II  L  L  ·   P  L  L  P  P   F  L  L  P   P    P  P  P   P    F    P   L  L   P
 III  P  L  P   ·  L  P  L  L   F  P  P  L   P    L  F  P   P    P    L   P  L   P
  IV  L  L  L   L  ·  L  L  L   L  P  L  L   L    L  P  P   L    L    P   P  P   L
   V  L  L  L   P  L  ·  L  L   L  P  P  L   L    P  F  L   L    P    F   P  L   P
  VI  L  L  L   L  L  L  ·  L   P  P  L  L   F    F  F  L   F    F    F   F  L   L
 VII  L  L  P   L  P  L  L  ·   L  P  L  P   L    P  L  L   P    P    P   P  L   P
VIII  L  L  P   F  L  L  P  L   ·  P  P  P   P    L  P  P   P    P    P   P  L   L
  IX  P  P  L   F  P  L  P  P   ·  P  F  L   P    F  F  P   F    P    P   P  L   F
   X  P  P  L   P  L  L  P  L   P  F  ·  L   P    P  P  L   P    P    P   L  P   L
  XI  P  P  P   L  P  P  L  P   P  F  L  ·   P    L  P  F   P    P    F   P  L   L
 XII  P  P  L   L  F  L  L  L   P  L  P  L   ·    L  P  P   F    P    L   F  L   L
XIII  L  P  P   L  L  P  P  L   L  P  L  L   L    ·  L  L   P    P    P   L  L   L
 XIV  P  P  P   P  P  P  F  L   P  F  P  P   L    L  L  ·   P    P    P   L  L   P
  XV  P  P  P   P  L  L  L  L   P  P  L  P   P    P  P  ·   L    F    P   P  L   L
 XVI  P  L  P   L  P  L  P  P   P  P  P  P   F    P  P  L   ·    L    P   P  L   L
XVII  P  P  F   P  L  P  F  P   P  P  P  P   F    P  P  F   L    ·    L   P  P   L
XVIII P  L  P   L  P  F  F  P   P  P  P  L   L    P  P  P   P    L    ·   L  L   L
 XIX  L  P  L   P  P  P  F  P   P  P  L  P   F    L  L  P   P    P    L   ·  L   L
  XX  L  L  L   L  P  L  L  L   L  L  P  L   L    L  L  L   L    P    L   L  ·   L
 XXI  L  L  P   P  L  P  L  P   L  F  L  L   L    L  P  L   L    L    L   L  L   ·
```

**Per-row outbound totals (current edges in any state):**

```
0  Fool       L=12  P=7   F=0    out=19
I  Magician   L=11  P=8   F=1    out=20
II Priestess  L=8   P=10  F=2    out=20
III Empress   L=8   P=9   F=2    out=19
IV Emperor    L=14  P=4   F=0    out=18
V  Hierophant L=10  P=7   F=2    out=19
VI Lovers     L=9   P=4   F=7    out=20
VII Chariot   L=10  P=10  F=0    out=20
VIII Strength L=6   P=12  F=2    out=20
IX Hermit     L=4   P=10  F=5    out=19
X  Wheel      L=8   P=10  F=1    out=19
XI Justice    L=6   P=11  F=3    out=20
XII Hanged    L=10  P=8   F=2    out=20
XIII Death    L=10  P=9   F=0    out=19
XIV Temperance L=4  P=14  F=2    out=20
XV Devil      L=6   P=11  F=3    out=20
XVI Tower     L=6   P=12  F=2    out=20
XVII Star     L=4   P=11  F=5    out=20
XVIII Moon    L=7   P=11  F=2    out=20
XIX Sun       L=5   P=12  F=2    out=19
XX Judgement  L=17  P=3   F=0    out=20
XXI World     L=14  P=5   F=1    out=20
```

(Outbound totals don't always sum to 21 — some cards have a
non-edge to one or two destinations where the deck has not seeded
a connection.)

**Column totals (how often each card is the TARGET of an unlock):**

The most-targeted cards are the deck's most-connected: World (21
inbound from every other card by design — it closes the
network), Fool (most inbound through-line references), Lovers
(every pair partner card wakes its lattice entry).

The least-targeted are the most-self-contained: Star (mostly
its own observer), Hermit (chosen solitude), Tower (the
self-truncating chapter).

---

## Per-card outbound (cards 0 through VII)

---

### 0 — THE FOOL

The Fool is the deck's longest outbound radiator — John's chapter
seeds 19 of 21 other cards. The BBS header (ACTIVE NODES, the
NARRATIVE STRUCTURE COMPASS naming) and Faith the dog account for
the bulk. The diner is the deck's structural origin.

**Live:** I, II, III (via dog-companion implicit pair), IV, V,
VI, VII, VIII, X (via the BBS header restored at XXI), XI (via
the 3:47 AM hour-match with Erica), XII (via Faith's
keychain-narwhal lineage one chapter earlier), XIII (Faith
absent), XV (the diner counter rhymes with Daigle's bar),
XVII (the night sky implicit at 3:47), XX (ensemble origin),
XXI (the dawn-lit corner closing the mirror).

- L → I Magician: bindle item carry; demoscene module read.
- L → II Priestess: inner card examined (Polaroid archive).
- P → III Empress: Faith asleep at the Empress's table (vol5
  dinner scene reaches across to the diner's dog).
- L → IV Emperor: DEMOSCENE_VIBE → render watermark; clock
  smudge → throne-room time annotation.
- L → V Hierophant: bindle tag → AVDI ET TACE.
- L → VI Lovers: dog touched → John&Faith pair lattice entry.
- L → VII Chariot: BBS header → the_charioteer obit; Faith iris
  at the wreck site.
- L → VIII Strength: dog → lion (Faith lineage); diner counter
  silhouette implicit on the riverbank.
- P → IX Hermit: the candle in the diner that nobody lights →
  the lantern that the Hermit lights from same wax stock.
- L → X Wheel: ACTIVE NODES restored at XXI implies the diner's
  count was the original.
- L → XI Justice: 3:47 AM hour-match with Erica's signature
  timestamp.
- L → XII Hanged Man: same hour, opposite coast (Natalie's clock).
- L → XIII Death: Faith's absent corner.
- L → XIV Temperance: photograph of D'Ambrosio's on Frank's desk
  (mode-b found document, not yet wired).
- P → XV Devil: counter rhymes with the welded bar.
- P → XVI Tower: render engine inscription (DEMOSCENE_VIBE label).
- P → XVII Star: night sky implicit through diner window.
- P → XVIII Moon: 3:47 AM ↔ 1:47 AM (one hour earlier on the
  west coast — same minute past the hour).
- L → XIX Sun: priestess journal annotated for chapters Frank
  reads (BBS chain).
- P → XX Judgement: ensemble origin — every figure was at
  D'Ambrosio's at some point.
- L → XXI World: dawn return; ACTIVE NODES 64 restored.

---

### I — THE MAGICIAN

The Magician's outbound is the deck's most symbol-rich. Three
sigils (infinity, the steamboat, the demoscene waveform) each
radiate to 3-5 other cards. Frasier's model city is the deck's
predictive architecture.

**Live:** 0 (iron carry), II, III (Aria handshake), IV, VI
(Frasier-Aria implicit pair), VII (steamboat-flame chain), VIII
(lemniscate worn), XVI (engine chain crash), XVIII (the worn
sigil reflected in Natalie's static — proposed but the
infrastructure exists), XX (gesture multiplied), XXI (model
city implies the wreath).

- L → 0 Fool: soldering iron → demoscene boot.
- L → II Priestess: infinity sigil → book spine glyph.
- L → III Empress: CRT readout ↔ Aria HUD.
- L → IV Emperor: steamboat → throne carving.
- L → V Hierophant: model city contains a small St. Jude's that
  Frasier is wiring (vol6 hook).
- L → VI Lovers: implicit pair (Frasier&Aria) wakes when both
  CRT and Aria handshake hot have fired.
- L → VII Chariot: steamboat lineage → menu drink.
- L → VIII Strength: lemniscate worn as halo.
- L → IX Hermit: nothing wired; the workshop and the clearing
  have no symbolic overlap (proposed: a single Magician demon
  carries the lantern in the periphery).
- P → X Wheel: nothing wired; the Wheel's PAINTER'S SPACE is
  Anna, but Frasier's workshop predates Anna's involvement —
  proposed: a wireframe on Frasier's drafting wall.
- P → XI Justice: Anna's wireframe inherits from Nicola's book,
  which inherits from Frasier's predictive model city.
- P → XII Hanged Man: Frasier modeled a "Simon's apartment"
  miniature (vol6 hook).
- P → XIII Death: Frasier modeled "Ward C" (chapter Dante was
  in at IV).
- P → XIV Temperance: Frasier's CRT shows Frank's heart rate
  remotely.
- P → XV Devil: Frasier modeled "Daigle's bar" (the middle
  barstool).
- P → XVI Tower: Frasier built the render farm (vol6 expansion:
  Evangeline was his apprentice).
- L → XVII Star: ankh constellation as Frasier's drafting compass.
- P → XVIII Moon: Natalie's sigils Frasier inscribed first.
- L → XIX Sun: the infinity Frasier draws becomes Frank's
  four-mote pattern (one curve, four cards).
- P → XX Judgement: gesture multiplied; the ensemble's "as above
  so below" is Frasier's posture replicated.
- L → XXI World: model city's missing center piece is
  the empty wreath.

---

### II — THE HIGH PRIESTESS

Elicia's outbound is the deck's archive vector. Every tape she
keeps, every journal entry she writes can wake content on the
card the tape/entry is about. Tape series: ANYA_03, HERMIT_01,
ENSEMBLE_01 are live; vol6 surfaces ANYA_07, ANYA_11, MAYA_FIRST_
COMMUNION (Maya/Y), and others.

**Live:** 0 (Polaroid archive), I (book spine glyph), IV (the
journal page on Dante's appointment book), V (lens reflected),
IX (HERMIT_01 tape in lantern base), X (23 Feb redaction
agreement), XIX (Sun entry bookmarked + read), XX (recording
the ensemble).

- L → 0 Fool: Polaroid pinned on archive wall.
- L → I Magician: shelf-book spine carries the infinity glyph.
- P → III Empress: a sealed Anya tape labelled "the cousin"
  has emerald data overlay rendered through the cassette window.
- L → IV Emperor: Dante's appointment book page in her archive.
- L → V Hierophant: camera lens reflected in rose window.
- P → VI Lovers: Anya&Elicia pair lattice entry wakes when she
  acknowledges (the journal entry of VI already names this).
- P → VII Chariot: a tape labelled "ANTONIO_FINAL" — recording
  of his last voicemail to Quent before the wreck.
- F → VIII Strength: she archives the un-named woman's single
  page in a folder labelled "FIGURE_R" (forward seed).
- L → IX Hermit: HERMIT_01 tape in lantern base.
- L → X Wheel: the 23 Feb redaction (paper sleeve replaced).
- P → XI Justice: an Anya tape contains Erica's voice
  inadvertently (forward seed).
- P → XII Hanged Man: a NATALIE_147AM tape next to ANYA_03.
- P → XIII Death: archive copy of e.s.'s 06:00 handover report.
- P → XIV Temperance: archive copy of Frank's Tuesday notebook.
- P → XV Devil: a tape DAIGLE_THURSDAY captures his morning note
  spoken aloud.
- P → XVI Tower: archive of Evangeline's apprentice records.
- P → XVII Star: archive of "what i poured" found page.
- F → XVIII Moon: ANYA tapes acquire transparent narwhal
  reflections under Natalie's broadcast.
- P → XIX Sun: bookmark added to her journal between the SUN
  pages (live reciprocal).
- L → XX Judgement: ENSEMBLE_01 recording.
- P → XXI World: her tarot journal closes with a "Frog Knows
  Best" margin notation.

---

### III — THE EMPRESS

Nicola's outbound is the deck's biometric vector. Aria's HUD
wakes content on cards that share the signal layer. Nicola's
breakfast presence (or absence) at D'Ambrosio's also seeds
several cards.

**Live:** I (CRT handshake), II (Polaroid reciprocal not yet),
IV (ram throne shared), VI (Frasier&Aria pair entry — reciprocal
to I), VII (breakfast witness), XI (dual-POV inheritance), XIII
(no wired; Nicola was not in Ward C), XVI (HUD bleed-through
when render farm fails — proposed), XVIII (Empress split
collapses into Natalie).

- P → 0 Fool: Nicola's POV of D'Ambrosio's breakfast (Antonio
  was at the next table; Aria flagged him).
- L → I Magician: Aria HUD ↔ CRT handshake.
- P → II Priestess: Nicola's journal becomes one of Elicia's
  archive items in vol6.
- L → IV Emperor: ram throne shared.
- P → V Hierophant: Nicola attended St. Jude's the Sunday
  before the painted dinner.
- L → VI Lovers: Frasier&Aria pair entry (when both signal
  ends fire).
- L → VII Chariot: breakfast witness via Antonio's SMS.
- F → VIII Strength: Aria's anxiety-spike baseline rhymes with
  the lion-tamer's heart rate (vol6 sensor reading).
- P → IX Hermit: nothing wired; Aria's silence pairs with the
  Hermit's silence.
- P → X Wheel: Erica was at the same breakfast.
- P → XI Justice: dual-POV inheritance reciprocal.
- L → XII Hanged Man: Aria's exit_node_search bathroom-as-
  fallback echoes Natalie's vigil.
- P → XIII Death: Aria's vitals reading on Mr. D (Dante) at
  Bed 6 — Aria knows because she's been reading Dante's
  signal remotely.
- L → XIV Temperance: Frank's chamber's pale-emerald light
  is the Empress's emerald POV.
- F → XV Devil: Aria's anxiety spike returns as Daigle's
  UNCOMFORTABLE INSIDE (same diagnostic, two vocabularies).
- P → XVI Tower: Aria stays running 0.4 sec off-chain when
  the engine crashes (canonized in render log).
- P → XVII Star: Aria's silence at the chapter's close.
- P → XVIII Moon: dual-POV split collapses; Empress's emerald
  becomes Natalie's emerald.
- P → XIX Sun: Aria's silence on Saturday is correct silence.
- L → XX Judgement: Aria does not speak at the ensemble (her
  silence is recorded).
- P → XXI World: Aria persists in the wreath.

---

### IV — THE EMPEROR

Dante's outbound is the deck's authority vector. The ankh
sceptre, the ram throne, the bourbon glass, the ASCII walls
each reach into specific cards. Dante's Bed 6 residency means
the throne room is being narrated from a hospital chapter.

**Live:** 0, I, II (appointment book), III (throne), V
(crozier), VII (calendar Wednesday slot), VIII (ankh-wielding
hand rhymes with lion-tamer's), X (audit window canonized),
XI (PetroTex case roots), XII (no wired), XIII (Bed 6 admit-
band), XIV (Dante's clock pattern), XVII (ankh constellation),
XX (gesture multiplied), XXI (OX corner figure).

- L → 0 Fool: ankh's tally-mark geometry rhymes with the BBS
  active-node count.
- L → I Magician: the model city contains a steamboat Dante
  hasn't bought yet — predictive succession.
- L → II Priestess: Dante's appointment book page in her
  archive.
- L → III Empress: ram throne shared.
- L → V Hierophant: bishop's crozier lineage.
- P → VI Lovers: Nicola&Dante pair entry — the throne passes
  by succession not romance, the painted card refuses to
  consummate the implicit.
- L → VII Chariot: Dante's Wednesday calendar slot at 09:00
  ("barge — manifest review with quentin") puts him with
  Quent and the boat the morning before the wreck.
- L → VIII Strength: ankh-wielding gesture matches the
  lion-tamer's bare hand.
- P → IX Hermit: Dante's "10:30 alma (private)" slot is the
  one event Quent doesn't know about — vol6 hook.
- L → X Wheel: 22-25 minute callback window.
- L → XI Justice: PetroTex case origin.
- L → XII Hanged Man: nothing yet wired; vol6 reveals he was
  Natalie's father.
- L → XIII Death: Bed 6 admit-band.
- P → XIV Temperance: Frank's clock subdial is Dante's
  appointment book's subdial (forward seed).
- P → XV Devil: Dante's calendar 21:30 "private — the boat,
  alone (90m)" lands at Daigle's pier.
- P → XVI Tower: the throne's render-engine watermark fails
  with the Tower's crash.
- L → XVII Star: ankh constellation.
- L → XVIII Moon: nothing wired; Dante is asleep at this hour.
- P → XIX Sun: Dante's daughter (the asheville dentist) reads
  Elicia's tarot journal page for Sun.
- P → XX Judgement: Dante names the dancer as not coming.
- P → XXI World: OX corner figure.

---

### V — THE HIEROPHANT

Maya/Father Quent's outbound is the deck's institutional vector.
The booth-call chain seeds three cards (VII Antonio, XII Natalie,
vol6 Carlie). AVDI ET TACE is inscribed on multiple cards as
they wake.

**Live:** 0 (bindle tag), I (model St. Jude's — proposed),
II (lens reflected in rose window), IV (crozier lineage), VI
(institutional witness inscription), VII (booth call origin),
IX (staff/crozier echo), X (Quent recorded himself),
XII (call 2 origin), XIII (Father Quent's instructions reach
the chaplain's room), XV (Daigle relay), XVI (crozier-shaped
fault line), XX (Maya quotes Quent), XXI (the rite acknowledges).

- L → 0 Fool: bindle tag AVDI ET TACE.
- L → I Magician: nothing yet wired; vol6 shows Frasier was
  baptised at St. Jude's.
- L → II Priestess: lens reflected.
- P → III Empress: Nicola attended St. Jude's (cross-listed).
- L → IV Emperor: bishop's crozier IS Dante's sceptre.
- L → VI Lovers: AVDI ET TACE inscribed across face-down back.
- L → VII Chariot: booth call origin (Call 1).
- L → VIII Strength: the riverbank dress unworn (Maya's biting
  dress is folded down).
- L → IX Hermit: staff/crozier lineage.
- P → X Wheel: Quent's hierarchy includes Erica's law firm as
  a Catholic firm (vol6 hook).
- P → XI Justice: nothing wired; Quent's recordings might
  surface in the case.
- L → XII Hanged Man: Call 2 origin (the 23:47 PT
  zone-shifted decline).
- L → XIII Death: the chaplain's room used for the brother in
  Bed 3's case.
- P → XIV Temperance: Frank's silence on Tuesday is Catholic
  silence.
- F → XV Devil: vol6 expansion — Quent and Daigle as priest
  and former parishioner.
- L → XV Devil: Daigle relay annotation already wired (the
  "Q — Thursday — undo" note).
- L → XVI Tower: crozier-shaped fault line.
- L → XVII Star: nothing wired; the open sky is Quent's mass
  cancelled.
- F → XVIII Moon: Quent's voicemails to Natalie (the call she
  didn't pick up) — vol6 hook.
- P → XIX Sun: Frank reads Elicia's journal, which has a
  Hierophant page.
- L → XX Judgement: Maya whispers Quent's permission to sit.
- P → XXI World: the chapter's silence joins the Frog's
  qualified verdicts.

---

### VI — THE LOVERS

The Lovers' outbound is the pair-lattice vector. Every cross-card
pair-confirmation wakes a row on the Lovers' lattice. The card's
refusal is also propagated (THREE REFUSED logic reaches XI Justice
and XX Judgement specifically).

**Live:** 0 (John&Faith pair confirmed via dog), I, II, IV
(throne with two seats), V (institutional witness),
VII (Quentin&Antonio confirmed via Chariot), X (lattice
state), XI (refused-card register reorders),
XV (welded furniture), XVII (smoke over the river),
XX (gesture refused by gathering — held),
XXI (lattice closed in footer).

- L → 0 Fool: lattice entry John&Faith.
- L → I Magician: implicit Frasier&Aria pair entry wakes
  when both signal ends fire.
- L → II Priestess: implicit Anya&Elicia entry.
- L → III Empress: implicit Nicola&Dante entry (succession).
- L → IV Emperor: throne with two seats.
- L → V Hierophant: AVDI ET TACE inscribed.
- L → VII Chariot: Quentin&Antonio confirmed.
- P → VIII Strength: the un-named woman & Faith — the only
  pair the deck does not refuse, because the deck does not
  name it as a pair.
- P → IX Hermit: the Hermit & his agreement-with-Elicia.
- P → X Wheel: Erica & Anna (friends before the case).
- L → XI Justice: refused → flipped anyway annotation.
- L → XII Hanged Man: Natalie & Simon implicit (the
  Hanged Man's vigil + the Death card's walkout).
- F → XIII Death: vol6 hook — death-pair implicit.
- F → XIV Temperance: Frank & Tuesday (the chapter as
  companion).
- F → XV Devil: Daigle & the middle barstool occupant.
- L → XV Devil: same furniture welded (already noted).
- F → XVI Tower: Evangeline & the render farm.
- F → XVII Star: the un-named figure & the river.
- F → XVIII Moon: Natalie & her own deck.
- F → XIX Sun: Frank & his own discipline.
- L → XX Judgement: refused company (XX joins VI).
- L → XXI World: lattice accounted for in footer.

---

### VII — THE CHARIOT

Antonio's outbound is the call-chain vector — the SMS thread
seeds 5 cards via specific messages. The wreck also leaves a
shadow on every card downstream of XV (Tower, Star, etc.).

**Live:** 0 (BBS sysop obit), I (steamboat in model), II
(ANTONIO_FINAL tape — proposed), III (breakfast witness),
IV (Wednesday calendar slot), V (booth call recipient),
VI (lattice entry), VIII (Faith witness), X (Erica
witnessed Antonio), XII (third call recipient annotated
from Antonio's end), XIII (Antonio's name in Quent's
chaplain-room instruction), XV (flame chain), XX (Antonio
is "the absent figure"), XXI (BBS count restored).

- L → 0 Fool: ACTIVE NODES dropped to 63.
- L → I Magician: model steamboat predictive.
- P → II Priestess: Antonio's last voicemail archived.
- L → III Empress: breakfast (Antonio noticed Nicola not eating).
- P → IV Emperor: Dante's 09:00 barge walkthrough includes
  Antonio (vol6 hook).
- L → V Hierophant: Call 1 recipient.
- L → VI Lovers: pair lattice second confirmation.
- L → VIII Strength: Faith was sentinel at the wreck.
- P → IX Hermit: nothing wired; vol6 hook.
- L → X Wheel: 19-call burst to Daigle by Alberto on the
  wreck night (Alberto knew because Antonio was missing).
- P → XI Justice: Antonio's death is referenced in the
  PetroTex case timeline.
- L → XII Hanged Man: third call recipient annotation.
- L → XIII Death: nothing wired; Antonio's death is offsite
  but the Ward C nurses know.
- P → XIV Temperance: the photograph on Frank's desk is
  the wreck site.
- L → XV Devil: flame chain (Chariot's Flame moved).
- L → XVI Tower: the wreck site is two miles from Evangeline's
  render farm (vol6 geography).
- P → XVII Star: the smoke at the clearing edge is partly
  the wreck's residual smoke.
- P → XVIII Moon: Antonio is one of the figures absent
  from Natalie's broadcast (she doesn't know).
- P → XIX Sun: nothing wired; Antonio is referenced in
  Elicia's journal Sun page (forward).
- L → XX Judgement: Antonio is "the absent figure" Frasier
  names.
- P → XXI World: the_charioteer's sysop status restored as
  ACTIVE in the World's BBS count.

---

(Cards VIII through XXI continue in the next commits — see
_UNLOCK_WEB_2.md and _UNLOCK_WEB_3.md.)
