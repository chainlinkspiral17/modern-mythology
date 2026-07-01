# Gauntlet Design Playbook

Lessons for authoring TAROT GAUNTLET scenarios · the setup JSON,
the visitor casts, the win/loss conditions, the inertia curves.

Companion playbook to `_3D_MODELING_PLAYBOOK.md` (locale build) and
`_LIMINAL_PLAYBOOK.md` (station/threshold tagging). This playbook is
about **the scenario-level design work** · what happens inside one
`setup_<scenario_name>.json` and its visitors.

Read this before authoring any new gauntlet scenario. The Wave-2
28-scenario batch (2026-07-01) was the crucible for these rules.

## Core rules

### The three-scenario floor per arcana

Every arcana MUST ship with at least three scenarios: the canonical
(medium difficulty) + one easier bookend + one harder bookend. The
easier bookend gives new players a way in; the harder one gives
returning players a reason to come back. Wave-1 shipped this from the
start; Wave-2 shipped with 1 each and got expanded to 3 in the
2026-07-01 arc.

### scenario_visitors live inline on the setup file, not on visitors.json

The engine loader reads `_setup.get("scenario_visitors", [])` as an
inline array on the setup JSON. Do NOT try to put a scenario-scoped
visitor pool in `visitors.json` under a `scenario_visitors` key ·
that key exists nowhere the engine reads. Two authoring reasons this
is right:

1. **Colocation**: the visitor's role in the scenario (schedule,
   arrival space, tutorial note) is meaningful only in context of
   that specific setup. Splitting it forces cross-file lookup during
   authoring and playtest.
2. **canonical visitors.json stays small**: the visitors that appear
   across scenarios (the_dog_in_the_field, the_auctioneer, Pearl,
   Erica, Lou, Maddox, etc.) live in visitors.json; the one-off
   scenario cast lives inline.

Structure: `scenario_visitors` is an array of visitor objects with
the same schema as `visitors` entries in visitors.json. Fields:
`id`, `name`, `as_hand_id` (or null), `arrival` (`{kind, turn/pos,
from, to}`), `lore_token`, `lore_text`, `accent` (hex color),
`placeholder_name` (optional), `pre_arrival_hints` (optional array),
`mood`, `tutorial_note`, `steps` (`{greet, listen, deliver,
sit_with}`).

### The one-easy + one-hard bookend pattern

The two new scenarios per arcana in the Wave-2 expansion followed
this shape:

- **Easier**: earlier or later in the timeline than the canonical.
  Same location, same hand. Smaller cast (3-4 scenario_visitors).
  Lower `inertia_per_turn`, lower `tension_max`, shorter
  `max_turns` (8-10). Win condition is a couple of gentle-yet-real
  gestures; loss condition is one obvious mistake.
- **Harder**: adjacent to the canonical but under more pressure ·
  emergency, deadline, unexpected arrival, or (most powerfully) a
  reversal that forces the character to sit in a role they're not
  ready for. Larger cast (5-6 scenario_visitors). Higher starting
  inertia. Tighter `tension_max`. Longer `max_turns` (12-16). Three
  or four specific loss conditions instead of two.

**Difficulty in gauntlet is not health-bar difficulty · it's
role-difficulty.** The hard scenario is hard because the character
is being asked to do something harder emotionally or professionally,
not because the enemies are stronger.

### Time-of-day is the primary difficulty axis

Every gauntlet scenario is anchored to a specific hour and minute
(e.g. "6:14 AM early November" · "11:48 PM mid-August squall"). The
time-of-day IS the difficulty:

- **Dawn**: gentler. The world hasn't woken up. Fewer witnesses.
- **Mid-morning**: setup/handoff work. Public but forgiving.
- **Afternoon**: canonical for reflection/ceremony scenarios.
- **Dusk/early evening**: liminal · the canonical hour for the
  canonical scenario.
- **Late night**: hardest. Crisis, decompression, or vigil.
- **Post-midnight into pre-dawn**: hardest of all · the vigil that
  has become the room.

When picking a time for a new scenario, pick the hour first · the
rest of the scenario shape follows.

### Loss conditions should be specific and named, not vague pins

Bad: `loss: sanity_max: 12` alone. That's fine as a fallback but it
doesn't teach the player anything about the scenario's actual
question.

Good: `loss_conditions: {sanity_max: 12, chair_righted_first_night:
true, mother_call_missed: true, stayed_past_three_am: true}`. Each
of the three named losses corresponds to a specific choice the
scenario is testing. When the player triggers it, they know exactly
what they did wrong and why. The scenario TEACHES through its loss
conditions.

Every hardest-tier scenario should have 3-4 named loss conditions.
Every easy-tier scenario should have 1-2.

### The win-condition trio: mechanical + relational + restraint

Well-shaped gauntlet win conditions consistently have three parts:

1. **Mechanical**: a specific action taken (feed all tanks, sign
   the closing sheet, plant the sapling, pull the block).
2. **Relational**: a specific visitor connected via a specific
   action verb (SHORT REST with X, STAND GROUND with Y).
3. **Restraint**: a specific thing NOT done (didn't right the chair,
   didn't answer the age question, didn't apologize for closing,
   didn't double-check).

The restraint condition is usually where the arcana's actual lesson
lives. Wave-1 sometimes forgot the restraint condition; Wave-2 leans
on it hard.

### The scenario_visitor "connection through" pattern

Every scenario_visitor needs a `tutorial_note` that specifies THE
ONE ACTION VERB that connects them plus WHY. Example patterns:

- "Marisol connects through SHORT REST at back_room_door · the
  gesture is greeting her with the standard AA welcome as she
  arrives, giving her a Big Book and a meeting card, letting her sit
  closest to the door."

- "Cordelia connects through GARNISH at the bar_stool_w · the
  gesture is having her Negroni ready before she sits down."

- "Wilfred connects through STAND GROUND at the graveside · the
  gesture is walking the perimeter of the open grave at the right
  pace, which signals to him that you're doing the rite right."

The verb + location + gesture triple is the entire tutorial note.
Don't add more. Players learn what to do by reading it once at
scenario start; long tutorial notes get skipped.

### Named characters are more powerful than abstract archetypes

Wave-1 sometimes used "the auctioneer" or "the widow" · placeholder
naming that could be filled in at scenario time. Wave-2 gave every
visitor a specific first-name-plus-last-name plus an age. The named
characters land harder because the player carries them across
scenarios · Marcelle Bernard (Simon's mother) shows up in three
different Hanged Man scenarios and her personhood carries across.

Rule: every scenario_visitor gets a name. Every name has to sound
like it belongs to the parish (French-Louisianian, some Spanish,
some Anglo, some German-Alsatian, some Vietnamese for the
second-generation immigrants, some Zydeco-family names).

### The "hand" field can be a placeholder · use it

Wave-2 setup files use hand IDs like `tbd_devil` or `the_ensemble`
that don't have JSON files behind them · the engine falls back to
a placeholder character. This is fine and productive · it lets the
scenario ship before its hand's specific mechanical language is
finalized. Do NOT block a scenario on the hand being fully authored;
ship the scenario, note the hand as tbd, and finalize the hand later
when three scenarios have been played and the hand's role is clear.

### One arrival-space per visitor · reuse the location's canonical spaces

Every `arrival.pos` (or `arrival.to`) MUST be a space that exists in
the location JSON. Don't invent new spaces per scenario. If your
scenario needs a new space, add it to the location's json first,
then reference it. This is the same invariant as CommunityPlanned
BBS thread IDs: schema before content.

## Recent lessons

### 2026-07-01 · 28 new Wave-2 scenarios in one arc · every arcana at 3

The long weekend of gauntlet-scenario authoring. Went from Wave-2 at
1 scenario per arcana (14 arcana) to 3 per arcana. Twenty-eight new
scenario files, ~130 named visitors, ~$8,500 words of scene
description across the batch. Most durable lessons:

- **The bookend pattern is the pattern.** One easier scenario in
  earlier time-of-day + one harder scenario in later time-of-day +
  the canonical in the middle. Every one of the 14 arcana absorbed
  this shape cleanly. Trying to write a "medium harder" scenario
  next to a "medium canonical" made both worse; the easy/hard
  bookends give the canonical air.
- **Time-of-day IS the difficulty knob.** The single most reliable
  authoring lever · pick 6 AM for easy, 11 PM for hard. The rest
  of the scenario's shape (pressure, visitor count, loss conditions)
  follows the hour.
- **Named loss conditions teach.** The most successful scenarios in
  the batch have three or four SPECIFICALLY-NAMED loss conditions
  (e.g. `stumbled_on_louis`, `chair_righted_first_night`,
  `answered_theroux_age_question`). Vague `inertia_max` losses are
  fallbacks; named losses are the pedagogy.
- **The restraint condition is where the arcana lives.** Every
  arcana has a specific "thing not to do" that is the actual test.
  Devil: don't sit on the stool. Hanged Man first-night: don't right
  the chair. Star: don't apologize for closing. World: don't
  double-check. The restraint condition IS the win condition; the
  mechanical action is just the vehicle.
- **Named characters are cheap and load-bearing.** Adding a
  first-name-last-name-age triple to every visitor took ~10 seconds
  per visitor · Marcelle Bernard, sixty-four, alone in Metairie · and
  paid for itself in every scene. The parish feels like a parish
  because the characters have names. Placeholder-abstract characters
  ("the widow", "the neighbor") read as generic in the moment.
- **The scenario is the day, not the concept.** Every Wave-2
  scenario got anchored to a concrete date/time/weather condition
  (Wednesday morning after the Picayune notice ran · Sunday
  afternoon of the last day · Thursday night after the storm). The
  concrete date IS the setup. Abstract framings ("some Wednesday
  afternoon") land soft; specific framings ("2:38 AM · the count
  room · doors are locked · Denise going home first at 3:04") land.
- **The scenario_visitors inline pattern is the correct one.** The
  engine loader reads them from the setup file directly. Do not put
  scenario-scoped visitors in visitors.json · that got attempted mid-
  batch, wasted 20 minutes, corrected. Colocation is the discipline.
- **Steps under each visitor form a four-beat arc.** greet → listen
  → deliver → sit_with. The four beats map to the four phases of
  the gauntlet turn (approach, information exchange, transaction,
  closure). Writing all four beats per visitor forces the author to
  actually work through the connection · not just gesture at it.
- **Don't rush the last scenario.** The World arcana's third
  scenario (`the_year_ago_first_open`) was written last in the batch
  after 27 others. It could have been phoned in. It got the
  hardest-in-the-batch scenario shape instead · the 90-second window
  where Ezra does NOT double-check as the year's template. This is
  the scenario that closes the whole deck's cycle · it earned its
  weight. Rule: the last scenario in a batch gets the most care, not
  the least.

## Templates

### Easy-bookend scenario template

```
{
  "id": "<scenario_id>",
  "arcana": "<roman>_<arcana>",
  "location": "<canonical_location>",
  "hand": "<hand_id>",
  "title": "<ALL CAPS>",
  "subtitle": "<Location · Time · Date/Context>",
  "difficulty": "easy",
  "epigraph_upright": "<one sentence about what upright means in this scene>",
  "epigraph_reversed": "<one sentence about what reversed means · often the failure mode>",
  "scene_description": "<opening paragraph · concrete date/time/weather/named-characters-present>",
  "direction_hint": "<second-person direction to player · plain>",
  "opening_log_lines": ["<time/context>", "<second sensory line>", "<HUD hint>"],
  "starting_state": {
    "player_pos": "<canonical space>",
    "time": 4-5, "time_per_turn": 4-5,
    "inertia": 0-1, "inertia_per_turn": 1,
    "sanity": 6-7, "sanity_max": 6-7,
    "tension_stat": "<lower-case tension>",
    "tension_label": "<UPPER-CASE tension name>",
    "tension_max": 6-8,
    "starting_hand": [<action_cards>]
  },
  "visitors_present_at_start": [<0-2 visitor_ids>],
  "visitor_schedule": [<2-3 scheduled arrivals>],
  "win_conditions": {
    "require_<mechanical>": true,
    "require_<relational>": true,
    "require_<restraint>_not_done": true,
    "require_visitors_connected_min": 2,
    "require_inertia_below": 5-6
  },
  "loss_conditions": {
    "inertia_max": 7-8,
    "<one_specific_loss>": true,
    "<second_specific_loss>": true
  },
  "inertia_thresholds": [<4-5 thresholds>],
  "claim_turns_to_consume": 2,
  "thresholds": [<1-2 gate spaces>],
  "max_turns": 8-10,
  "notes": "<one paragraph · win path + loss conditions + visitor list>",
  "scenario_visitors": [<3-4 inline visitor definitions>]
}
```

### Hardest-bookend scenario template

Same shape, but:
- `difficulty: hard`
- `time: 6-7, time_per_turn: 6-7`
- `inertia: 2-4` (starting)
- `sanity: 3-5, sanity_max: 6-7`
- `tension_max: 10-12`
- 3-4 named loss conditions
- 4-6 scenario_visitors
- `max_turns: 12-16`
- Two threshold gates (the standard exit + one revealed-by-flag
  secondary exit for the alternate-ending path)

## When to spin up a new gauntlet playbook file

The Wave-2 batch generated enough lessons about scenario-level
authoring specifically to fill this file. When the following domains
accumulate ≥ 5 distinct lessons each, spin them up:

- **Hand-authoring**: the JSON files for a specific hand character
  (dice profile, action-card variants, cameo appearances)
- **Location-scenario coupling**: which locales support which kinds
  of scenarios, when to build a new locale vs. reuse
- **Visitor-across-scenarios continuity**: named characters who
  appear in multiple scenarios (Marcelle Bernard, Lou Daigle, etc.)
  and how their arcs stay coherent
- **Ending-lore-token collection UX**: the finale-per-arcana card
  browser + the collected tokens display

Each of these is not yet 5 lessons deep. Watch them.

## TEMPLATE for new "Recent lessons" entry

```
### YYYY-MM-DD · <one-line title>

<one-paragraph situation>

- **<Bolded principle>.** <two-to-three-sentence explanation.>
- **<Bolded principle>.** <two-to-three-sentence explanation.>
- **<Bolded principle>.** <two-to-three-sentence explanation.>
```
