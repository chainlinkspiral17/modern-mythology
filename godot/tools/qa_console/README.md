# QA Console

A two-piece QA workflow: capture in-game state with one hotkey,
organize feedback in a local HTML tool, export a markdown report
to paste back to Claude as direction.

## How the loop works

```
  In-game             user://qa/                  Browser
  ─────────           ──────────                  ───────
  Shift+F1   ──→  qa_snapshots.jsonl    ──→  load via picker
  (capture)       qa_NNNN.png                 → annotate
                                              → export markdown
                                              → paste to Claude
```

## Capture side · `Shift + F1`

A `QASnapshot` autoload (`godot/autoload/QASnapshot.gd`,
registered in `project.godot`) listens globally. Press
**Shift + F1** anywhere in the game.

What gets captured:
- **Scene** — name + .tscn path
- **Player** — position in BOTH Godot and Blender frames (so
  you can cross-reference build scripts directly), yaw/pitch
  in deg + rad, camera FOV, camera basis-Z (look direction)
- **MoodCycler** — current stratum name + index, blend % (the
  tens/ones tuner), lighting index, style-pack index
- **Shaders** — `strength` parameter from every ColorRect in
  PostProcess (neon, dir_ascii, ascii, starscape, motion,
  blur, demoscene_post, old_film, liminal_proximity)
- **Liminal** — current proximity-shader strength + the active
  station type
- **Gauntlet** — nearest space in the host's `SPACE_MAP` (and
  whether you're exactly on it or between)
- **HUD** — visible-state (handy: if you press F4 and forget,
  the snapshot tells you the toggle was off)
- **Session ID** — a Unix timestamp from autoload start; every
  snapshot from one game-run shares it so the console can
  auto-group sessions

The snapshot also:
- Saves a PNG screenshot of the current viewport to
  `user://qa/qa_NNNN.png` (HUD flash NOT in the screenshot —
  it's drawn the frame after capture)
- Copies the JSON to clipboard for immediate paste anywhere
- Echoes one line to the Godot console with the index + path
- Shows a small "QA #NNNN" HUD flash for ~1 second so you know
  it landed

The snapshot index is persistent — if you restart Godot, the
next snapshot continues from where the JSONL left off (no
overwrites).

### Where the files live

On Linux / Steam Deck:
```
~/.local/share/godot/app_userdata/<project-name>/qa/
  qa_snapshots.jsonl
  qa_0001.png
  qa_0002.png
  ...
```

On macOS:
```
~/Library/Application Support/Godot/app_userdata/<project>/qa/
```

On Windows:
```
%APPDATA%\Godot\app_userdata\<project>\qa\
```

Easiest workflow on the Deck: open the file manager, navigate
to the `qa/` directory, and from there drag-drop the `.jsonl`
and the `qa_*.png` files into the QA console's file pickers.

## Organize side · `index.html`

Open `godot/tools/qa_console/index.html` in any modern browser
(Firefox / Chrome / Safari). Everything is local; no network
calls; state lives in browser localStorage with manual
JSON-file export/import for cross-machine backup.

### Tabs

**Snapshots** — Loads `qa_snapshots.jsonl` from the disk
picker. Each capture renders as a card showing the scene,
gauntlet space (if any), and timestamp. Click the collapsible
to see the full state JSON + screenshot. Per card you set:

- `[ ] I've seen updates` — after Claude reports back, check
  this so the card visually moves to the "seen" colour and
  you can filter it out
- `[ ] satisfied for now` — when the issue is parked, check
  this so the card moves to the "satisfied" colour and gets
  filtered from the default markdown export
- Verdict pills — ✓ great / ⚠ rough / ✗ broken (click to
  toggle; recolours the card border)
- Severity — low / med / high (sorts the export)
- Category — locale_geometry, lighting, shader, portrait_3d,
  gauntlet_balance, gauntlet_content, audio, vn, other
- Comment — your direction. Markdown OK; multi-line OK.

Auto-grouped by date, then by session within each date.

**Content** — For feedback that isn't tied to a captured
moment. Add an item by picking a type (visitor / action_card /
gravity_card / scenario / asset / scene / shader / portrait /
other) and a ref ID (e.g. `ft_veil_comment`, `packing`,
`john_frank.glb`, `bungalow.tscn`). Same annotation set.
Grouped by type.

**Notes** — Free-form. Title + body (markdown) + tag
(inspiration / instruction / idea / concern / thought). Use
for general direction that doesn't have a specific anchor.

**Export** — Filter toggles (hide satisfied / hide seen /
since-date), one button to regenerate the markdown report
into the big textarea, one button to copy it to clipboard.

### Toolbar (top of every tab)

- **Load qa_snapshots.jsonl** — file picker. Re-loading the
  same file is safe; existing annotations are preserved.
  New snapshots get added; old ones get their captured state
  refreshed (in case you re-captured with the same index by
  accident, which you shouldn't, but).
- **Load qa_*.png folder** — multi-file picker for all the
  PNG screenshots. Loads them into browser memory so the
  cards show thumbnails. (These don't save to localStorage —
  re-pick after a browser reload.)
- **Save state.json** — downloads the full annotation state
  to a file. Use for backup or for moving between machines.
- **Restore state.json** — replace current state with a file
  you previously saved.
- **Clear all state** — nuke localStorage. Confirms first.

### Per-item state colours

- Default (no annotation): grey left-border
- `seen` only: blue left-border
- `satisfied`: green left-border + dimmed
- verdict `great`: green left-border
- verdict `rough`: amber left-border
- verdict `broken`: red left-border

Satisfied overrides verdict in colour so parked items read
calmly even if they were once flagged broken.

## Markdown export shape

The exported markdown is structured for Claude to act on:

```markdown
# QA report · 2026-06-17

## Snapshots (4)

### lighting

- **⚠ [high] #0042** — Bungalow @ the_editing_desk
    The screen-glow practical is too cool; warm it to the kettle's amber.
    > blender=[3.70, -1.80, 0.00] · yaw=-90° · mood=raw · blend=100% · 📷qa_0042.png

### shader

- **✓ [low] #0044** — Cathedral @ devil
    Demon static at 1.0 strength is dialed exactly right for the empty stool.

## Content (2)

### visitor

- **✗ [med] ft_veil_comment**
    The 'THE INDEX IS UNBROKEN' line is wrong tone — Frasier is more
    architectural; rewrite as 'the lattice is intact' or similar.

## Notes (1)

### inspiration

- **Lynch's editing rhythm in PH** · 2026-06-17
    Watch the cut in episode III of Twin Peaks Returns — the way the
    breath holds. The Anya footage should land like that.
```

## Tips

- One snapshot per moment that needs feedback. Don't capture
  every walking step — capture the moments that need
  attention. Each capture lives forever in the JSONL, so
  density matters.
- The "seen updates" checkbox is the way you confirm Claude
  responded to your direction. The next time you play the
  fixed version, tick it before re-capturing — then if
  there's still something off, do a new snapshot rather than
  amending the old comment.
- The session_id auto-grouping means you can play, look at
  the file, see what changed, play again, look at the file,
  and snapshots stay grouped sanely even if you forget to
  restart Godot between play sessions.
- Use the **Notes** tab for inspiration / external
  references (a film clip, a piece of music, a passage of
  text). These flow into the markdown report under their
  own section.

## Future hooks (deferred)

- Cross-link content items to the JSONs in the repo (so
  picking `visitor / ft_veil_comment` would show the file
  contents and current state)
- Filter snapshots by gauntlet space / mood stratum / shader
  preset
- "Re-capture-after-fix" workflow — link a new snapshot to
  the old one and auto-mark the old one seen when the new
  arrives
- Direct file-system access for the JSONL via File System
  Access API (currently file-picker per session, which is
  one extra step but works on every browser)
