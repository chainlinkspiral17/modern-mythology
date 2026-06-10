# THE TAROT GAUNTLET — data files

This directory holds the JSON data for the Tarot Gauntlet
arcana-as-playable-scenario framework. Spec lives at
`lore/_TAROT_GAUNTLET.md`.

## Layout

```
godot/resources/games/
  _README.md                          ← you are here
  framework/
    action_tableau_core.json          ← shared core verbs (Walk, Focus,
                                        Search, Sprint, Short Rest,
                                        Long Rest, Distraction, Guard,
                                        Close Call, Spend It, Improvise)
  fool/
    die.json                          ← Fool's 6-face arcana die
    setup_the_leap.json               ← THE LEAP setup (canonical
                                        Fool scenario at D'Ambrosio's)
    action_cards.json                 ← Fool-unique action cards
    gravity_deck.json                 ← 12 Gravity cards (the room
                                        being the room)
    finale.json                       ← three named reversal states
    items.json                        ← bindle components + content
                                        choices + item deck
    visitors.json                     ← six Visitors with arrival
                                        + connect rules
    achievements.json                 ← three-layer progression
                                        (coarse, fine, FG-style pages)
  locations/
    dambrosios.json                   ← location board + adjacency
                                        + event deck
  hands/
    john_frank.json                   ← Hand stats + ultimate ability
```

## Build status

| component | data file | engine code |
|---|---|---|
| Fool die | ✓ | pending |
| The Leap setup | ✓ | pending |
| Action cards (Fool) | ✓ | pending |
| Gravity deck | ✓ | pending |
| Finale | ✓ | pending |
| Visitors | ✓ | pending |
| Items | ✓ | pending |
| Location: D'Ambrosio's | ✓ | pending |
| Hand: John Frank | ✓ | pending |
| Achievements | ✓ | pending |
| Action tableau core | ✓ | pending |

## What's next

Engine code:
  * `godot/autoload/GauntletState.gd` — persistent meta-progression
    (cross-run unlocks, achievement progress, codex hotspot state)
  * `godot/scenes/games/TarotGauntletGame.gd` — main controller
    walking the 5-phase loop (Action → Planning → Shadow → Drift →
    Upkeep)
  * `godot/scenes/games/TarotGauntletGame.tscn` — root scene
  * supporting UI scripts/scenes (PlayerBoard, LocationBoard,
    ActionTableau, HandArea, ShadowBoard, Dice, CardCodex)

Gallery wire-in:
  * `godot/scenes/menu/GalleryOverlay.gd` adds a "▷ PLAY" affordance
    on the Fool card that launches TarotGauntletGame
