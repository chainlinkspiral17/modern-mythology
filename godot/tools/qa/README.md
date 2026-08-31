# Headless runtime QA (godot/tools/qa)

Born 2026-08 when "fix the games" needed more than linters. A real
Godot binary runs the project headless in the work container, so
game logic is verified by RUNNING it, not reading it.

## Setup (once per container)

```bash
cd <scratchpad>
curl -sSL -o g.zip https://github.com/godotengine/godot/releases/download/4.6-stable/Godot_v4.6-stable_linux.x86_64.zip
unzip g.zip && GODOT=$PWD/Godot_v4.6-stable_linux.x86_64
cd <repo>/godot && $GODOT --headless --import     # once, ~5 min
```

## The sweeps (run from `godot/`, output to a log; grep SCRIPT ERROR)

- `$GODOT --headless res://tools/qa/CompileSweep.tscn` — loads every
  .gd IN-PROJECT (autoloads live, unlike `--script` mode where
  autoload identifiers fail to resolve as false positives). Catches
  what gdparse/gdinfer can't.
- `$GODOT --headless res://tools/qa/HostBootSweep.tscn` — boots every
  game host scene for two frames. Catches _ready-time crashes.
- `$GODOT --headless res://tools/qa/CPSimSweep.tscn` — PLAYS a full
  Community Planned summer, day 1 → 100, hanging up each Sunday BBS
  and dismissing dialogs. First run caught 108 runtime errors (the
  "_globals" pseudo-region ticked as a real region from the first
  set_global effect onward — County-Seat-era bug invisible to every
  static check).

- `$GODOT --headless res://tools/qa/GauntletSimSweep.tscn` — PLAYS
  gauntlet scenarios with a pass-only player through all five
  phases to their endings (a pass-only player loses by stagnation,
  which exercises the loss finales). Covers the remapped boards.
- `$GODOT --headless res://tools/qa/MonkeySweep.tscn` — UI monkey:
  presses real visible buttons (skipping quit/erase words), ESC on
  buttonless screens. Its reach ends at keyboard-driven gameplay
  (salmonberry's town walkabout, where the crisis night locks ESC
  by design) — that is a monkey limitation, not a game bug.
- `SalmonberryProbe` — diagnostic variant that logs every press and
  dumps the UI tree at a dead screen. Copy the pattern when a
  monkey run needs explaining.

- `$GODOT --headless res://tools/qa/VnSweep.tscn` — PLAYS the whole
  visual novel: every indexed scene of every volume, BACK TO FRONT
  (per the 2026-08-30 direction: volume tails carry the least
  iteration). Advances lines, resolves choice option 0 via
  `_on_chosen`, dismisses CGs/interludes/chapter cards with an
  "advance" InputEventAction (the input map binds PHYSICAL
  keycodes — a bare InputEventKey never matches), treats
  game_ended as flow end. A scene that stops progressing is a
  STALL and stalls are real: the first honest run found three
  unwinnable choices (goto aimed at the choice's own index) and
  led to three malformed skill checks. Slow (~real playthrough
  speed); run in background. Static twin:
  `python3 godot/tools/audit/vn_story_audit.py` (suite gate).
- `$GODOT --headless res://tools/qa/SalmonberryYearSim.tscn` — PLAYS
  a full Salmonberry year through the real UI (errand-first, event
  next, rest when worn; March's realtime crisis skipped via the
  no-rescue path). Day-one driver for WAVE D's errand system; its
  first honest run found the JSON-float Array.has(int) class that
  had hidden every month-gated activity since v2 (see the
  authoring playbook). Asserts ≥3 errands, ≥1 event, bonds grew.
- `$GODOT --headless res://tools/qa/EstuaryFourSim.tscn` — PLAYS the
  full Estuary 4 campaign (all four chapters) with a rational-player
  season policy: repair damage, lash down when the glass drops, take
  the grant, rest a worn crew, else careful work. First run PASSED
  clean — the working season's first verification since it shipped.
- `$GODOT --headless res://tools/qa/ResumeIntSanity.tscn` — the
  regression net for the JSON-float resume class: writes a save the
  way a real round-trip leaves it (numbers → floats), boots the
  host, asserts the saved int arrays are ints again and .has(int)
  matches. Covers Fey Faire shows_attended + Riffrocker
  meetings_attended; add a block per new saved number array.
- `$GODOT --headless res://tools/qa/CPEndlessSim.tscn` — runs
  SEPTEMBER AND AFTER seeded from the campaign save CPSimSweep
  leaves in slot 3: ratcheting spawns, rhythm pools, milestones,
  tower brightness, and the run's ending. Its first three runs
  found three real bugs (see the commit log for 2026-08).
- `EndlessProbe` — the diagnostic twin with per-decade state
  prints. NOTE: deleting user:// files needs
  `ProjectSettings.globalize_path` first — the bare
  `DirAccess.remove_absolute(user://…)` fails SILENTLY and the
  probe once resumed a stale save because of it.

## Rules

1. Missing-GLB errors are expected here (GLBs build on the Deck).
2. A sim sweep must assert PROGRESS (day advanced), not just "no
   crash" — a stall is a failure even when nothing errors.
3. New game systems get a sim driver here the day they ship.
