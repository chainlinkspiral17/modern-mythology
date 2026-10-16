# The score bible

Written musical direction for every catalog track. The composer (`godot/tools/seqgen.js`
`applyScore`) layers these files: **soundtrack → volume → chapter → character → track cue**,
then the AUDIO DIRECTOR's typed direction wins over all of them. Every `*.json` here is merged
(one file per volume group plus `soundtrack.json`). Validate with
`node godot/tools/tests/data.test.js` (the "score bible" test runs `SeqGen.checkScore`).

Any layer may set (all optional; a list or `[lo, hi]` is picked per take seed):

| field | value |
|---|---|
| `style` | a `SeqGen.STYLES` id (or a list) |
| `form` | `song` · `short` · `loop` · `bed` |
| `mode` | major · minor · dorian · phrygian · mixolydian · lydian · harmonic |
| `key` | `"D"`, `"Eb"`, `"F#"` or 0–11 (or a list) |
| `bpm` | a number, or `[lo, hi]` |
| `density` | 0–1, or `[lo, hi]` (how busy the parts are) |
| `voices` | `{ role: FORGE preset id or [ids] }` — roles: drums (`kit`), bass, chords, lead, pad, counter, arp, double, perc (`kit`), texture, fx |
| `textures` | `[ambience preset ids]` (≤ 2 play) or `"none"` |
| `fx` / `hit` | a transition / hit preset id, or `"none"` |
| `motif` | a character key (their leitmotif), or `null` |
| `shape` | track cues only: `[[section, bars, [roles]], …]` — sections `intro`, `A`, `A2`, `B`, `B2`, `C`, `brk`, `outro`; roles: drums, bass, chords, lead, pad, the arrangement parts `counter` / `arp` / `perc` / `double` (see below), and `texture` / `fx` to place the sound layer. A section that lists its roles gets exactly those; a section without a list gets the style's own choice (arrangement parts included) |
| `stems` | true → the take is layered by intensity in game |
| `feel` | prose: what this should feel like (shown in the director's BRIEF) |

`characters.<name>` adds: `instrument` (their signature lead), `motifSpec`
(`{ "rhythm": [16th-steps within 2 bars, 0–31], "degrees": [scale steps] }` — the motif itself),
`mode` (for their own theme), `feel`.

**Arrangement parts** (`SeqGen.ARR_ROLES`, per style in `SeqGen.ARRANGE`). Without a cue they come in by the
style's odds, with intent: an arp entering in A2 (or opening the intro in synthwave / motorik / minimal), the counter
answering the lead in A2 / B, hand percussion lifting B, the doubling in B / C.

| role | what it plays | game layer |
|---|---|---|
| `counter` | a countermelody under the lead: answers in its rests (`answer`), a muted horn (`horn`), a second voice (`second`), jazz guide tones (`guide`), a harmony a third / sixth below (`harmony`), a high ringing line (`ring`), an interlocking cell (`interlock`) | 0.75 |
| `arp` | an ostinato over the chord: up, down, updown, broken thirds, alberti, pedal, a 16th sequencer with a gate, triplets, a walk | 0.5 |
| `perc` | hand percussion on a KIT (congas, bongos, shaker, cabasa, tambourine, cowbell, clave, wood blocks, frame drum, nyabinghi, washboard) — never a voice the drums already play | 0.4 |
| `double` | the lead an octave down / up, or the bass an octave up, on another instrument | 0.9 |

`checkScore` rejects an unknown role in a `shape` or a `voices` key.
