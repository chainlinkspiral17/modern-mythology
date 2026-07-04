# The Cabin's Personal Slowstock Library

Vol 7 · Land of Milk & Honey. Olaf and Eddvard built the cabin in
'79 and the west-wall shelf above the record player was Olaf's.
This directory holds:

- `unlock_graph.json` — the wave-by-wave unlock structure
- `shelf_layout.json` — the physical arrangement on the shelf
- `stubs/*.json` — per-slowstick manifests, one file per stick

Each stick's file is either a **full authored resource** (with
playable acts under `godot/resources/games/vol7/<stick_id>/`) or
an **authored stub** (manifest only, playable acts deferred to a
follow-up commit). The stub form still populates the shelf UI
and can be unlocked; booting a stub shows an acknowledgment
screen that names the deferral.

## Currently authored

| Stick                  | Wave | Status                    |
|------------------------|------|---------------------------|
| ESTUARY 3              | 1    | Full · acts 1–4 authored, Godot host pending |
| ESTUARY 2              | 2    | Stub                      |
| PIRATE SUMMER          | 2    | Stub                      |
| MRS. WU'S GARDEN       | 3    | Stub                      |
| KWIK STOP MANAGER      | 3    | Stub (RANCH; competitor)  |
| ESTUARY 1              | 3    | Stub                      |

## Not yet touched

The wave-4 and wave-5 sticks in `unlock_graph.json` — Estuary 4,
Sam's Summer Shifts, The Tideline, Tideline Survey — do not yet
have stubs. They're referenced in the graph so the shelf UI can
render locked placeholders, but no manifests exist yet. When the
player finishes 3 sticks and Wave 4 unlocks, these need at least
authored stubs.

## Adding a new stick

1. Add the id to `unlock_graph.json` in the appropriate wave (or
   create a new wave).
2. Add a physical position in `shelf_layout.json`.
3. Create `stubs/<id>.json` with the manifest schema (see
   `estuary_2.json` for the reference).
4. If the stick has playable acts, create
   `godot/resources/games/vol7/<id>/` with `manifest.json` plus
   act files, and reference them from the stub with `full_acts_at`.

## In-fiction guidance

The shelf is Olaf's shelf. Every stick on it should feel like a
thing Olaf plausibly bought. Olaf's habits:

- He gave to OPB every year at Level 3, so anything with an OPB
  pledge-drive premium is fair game.
- He bought used at Portland game stores (Rip Van Winkle's until
  2009; New Moon after that).
- He kept sticks in Betamax cases because he had a shelf of empty
  ones from the '80s.
- He read Slowstick Review Quarterly cover to cover.
- He gave sticks to Tem when he thought she was old enough.
- He never sold a stick, even ones he didn't like.

Sticks that would NOT be on Olaf's shelf: anything post-2044 that
Tem didn't add herself; anything with graphic violence (he was
against that); anything from before 2001 (that's the
pre-slowstick era in this world).
