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
| `voices` | `{ role: FORGE preset id or [ids] }` — roles: drums (`kit`), bass, chords, lead, pad, texture, fx |
| `textures` | `[ambience preset ids]` (≤ 2 play) or `"none"` |
| `fx` / `hit` | a transition / hit preset id, or `"none"` |
| `motif` | a character key (their leitmotif), or `null` |
| `shape` | track cues only: `[[section, bars, [roles]], …]` — sections `intro`, `A`, `A2`, `B`, `B2`, `C`, `brk`, `outro`; roles may include `texture` / `fx` to place the sound layer |
| `stems` | true → the take is layered by intensity in game |
| `feel` | prose: what this should feel like (shown in the director's BRIEF) |

`characters.<name>` adds: `instrument` (their signature lead), `motifSpec`
(`{ "rhythm": [16th-steps within 2 bars, 0–31], "degrees": [scale steps] }` — the motif itself),
`mode` (for their own theme), `feel`.
