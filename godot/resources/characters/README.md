# Canonical Character Registry

`_index.json` is the single source of truth for any character that
appears across more than one game system in Modern Mythology.

## Consumer systems

| System | Lookup key | Local file |
|---|---|---|
| Tarot Gauntlet | `lore_links.gauntlet_hand` | `resources/games/hands/<id>.json` |
| Community Planned | `lore_links.community_planned_agent` | `resources/games/community_planned/agents.json` (record's `id`) |
| Locales (Graustark / arcana) | `primary_locale` | `resources/games/locations/<id>.json` (informational) |

## Convention

When adding a character that already exists in another system,
add their canonical entry here **first**, then add the
system-local record with a `canonical_character_id` field that
points back to this index.

When editing canon-affecting biography (relationships, primary
locale, arcana associations, name), edit the registry. The
system-local files should treat the registry as authoritative
on identity and treat their local fields as the *mechanical
shape* of the character within their system.

## What stays local

System-specific mechanical fields stay in the system-local file:

- Gauntlet hands: stats, ultimate_ability, starting_hand
- Community Planned agents: class, home_region, specialty_problem_
  types, competence_modifier, burn/obligation costs, evolution_paths,
  signature_failure

Don't promote those to the registry — they're definitional to
the system, not to the character.

## When a character is system-local only

Extras, placeholders, and TBD characters stay in their system's
file without a registry entry. The registry is for the cross-
system cast.

## Validation

The expected pattern is for both consumer systems to do a soft
cross-check on load. (Not yet implemented in either; the registry
is the data step that lets us implement it later.)
