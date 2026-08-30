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
