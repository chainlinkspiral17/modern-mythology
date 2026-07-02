# Cameo Build Spec · Chapters I–VII

Cameos are guest-in-host scenarios: a non-host player walks into the
host arcana's room and plays the night through their own deck. Each
cameo is **not** a reskinned host scenario — it has to introduce
something the host's own three scenarios never see. The white-box
spec for every cameo:

| Pillar | Requirement |
|---|---|
| Hand | Guest's home deck (overrides host's default via `hand_override` on the picker tile). |
| Cards | **1–2 cameo-unique cards** declared inline under `scenario_action_cards` in the setup JSON. Same shape as `action_cards.json`. |
| Visitors | **At least one cameo-unique visitor** declared inline under `scenario_visitors`. May also draw from the host's pool. |
| Map | **At least one cameo-unique space** (node, threshold, or both) declared inline under `scenario_spaces_additions` / `scenario_adjacency_additions`. The new node should change a route the host doesn't have. |
| Mechanic | **One novel beat** — a timed unlock, a cross-arcana resource, a haunting that punishes a host verb, a courier who carries something through. Implementable in engine-supported terms (visitor schedules, threshold effects, card effects already in the framework). |
| Difficulty | One easy / one medium / one hard per host chapter. |
| Picker | Listed in the GalleryOverlay constants for the host arcana, with a colored difficulty chip. |

Engine support added to `TarotGauntletGame.gd`:
- `scenario_action_cards` array → merged into `_action_cards` after the arcana deck.
- `scenario_visitors` array → merged into `_visitors_def`.
- `scenario_spaces_additions` array → appended to `_location.spaces`.
- `scenario_adjacency_additions` array → appended to `_location.adjacency`.

UI:
- `GalleryOverlay._scenario_difficulty()` + `_difficulty_color()` render a colored chip on each tile.
- Cameos sit below the three core scenarios behind a `CAMEOS · OTHER PLAYERS IN THIS ROOM` divider.

---

## I · Magician · Cathedral (Frasier's warehouse)

### easy — `cameo_john_at_the_warehouse` · hand: fool

John walks the river path over from the diner with a folded napkin
and a question he can't write down yet.

- **Unique cards** (in `scenario_action_cards`)
  - `napkin_fold` — Time 1. Spend 1 sanity to draft a half-sentence onto the napkin. Records a lore_token `john_napkin_drafted`. After 3 plays, becomes free-cost.
  - `phone_call_to_elicia` — Time 2. Playable only at the `loading_dock` space (added below). Connects with Elicia at +1 hard-mood weight without needing to stand next to her.
- **Unique visitor** (`scenario_visitors`)
  - `daigle_courier` — Sammy's nephew arrives turn 3 with a paper bag of takeout John didn't order. He leaves before turn 5 if not greeted. Lore_token: `the_courier_remembered_you`.
- **Unique map** (`scenario_spaces_additions`)
  - `loading_dock` (river-side, threshold-adjacent to `warehouse_bay`). Pulls the cameo away from Frasier's workbench. From the dock you can `phone_call_to_elicia` and see the river horn.
- **Novel mechanic** — *the river horn at 10:00.* A steamboat horn at turn 5 opens the otherwise-hidden `loading_dock` threshold for the rest of the run, with ending_lore_token `leap_river_with_napkin`. Until the horn, John's only leaps are Frasier's defaults; after, John gets a private exit.

### medium — `cameo_elicia_films_a_scene` · hand: elicia

Elicia rigs lights in the south bay. The Demon refuses to be on
camera. Frasier won't stop welding.

- **Unique cards**
  - `frame_the_shot_with_iron` — Time 2. The Magician's iron sparks read as cinema; Elicia can frame a single shot here that earns Elicia 1 harvest *and* Frasier 1 fuel (cross-arcana cooperative gain). Once per run.
  - `unplug_the_radio` — Time 1. Silences the warehouse radio for one turn; ambient draws skip and Demon-on-the-phone visitor patience pauses. The Demon notices on turn 2 after.
- **Unique visitor**
  - `the_dp_emory` — Elicia's DP (canonical from Whispers): a quiet visitor at `south_bay`. Hard mood "preoccupied"; only opens to `listen` if `frame_the_shot_with_iron` has been played.
- **Unique map**
  - `south_bay_set` — a partitioned corner of the warehouse with practical lighting Elicia rigged. New threshold from `south_bay_set` to `roof_hatch` (existing) with ending_lore_token `leap_with_the_footage`.
- **Novel mechanic** — *fuel↔harvest exchange.* The cooperative card creates the first place in the game where two distinct currencies (Frasier's fuel, Elicia's harvest) interact. Implemented purely through card effects.

### hard — `cameo_antonio_comes_home` · hand: antonio

Antonio at the door two months before the wreck. The smell is the
smell.

- **Unique cards**
  - `silt_of_voicemails` — Time 2. Reduces sanity by 1 to gain 2 insight; tags the run with `voicemails_at_eleven_today`. Each subsequent play is +1 doubt.
  - `ask_the_question` — Time 3. Playable only at the `model_city_platform` space. Closes the cameo with the highest hard-mood connection of the night becoming a `mood_burn` lore record (the ch7 wreck retroactively cites whichever connection he leaned on).
- **Unique visitor**
  - `the_demons_phone` — a *device* visitor on the workbench: the Demon's number lights up John's phone at random turns. Connect by ignoring three calls (verb: `let_it_ring`).
- **Unique map**
  - `model_city_platform` — the small empty platform on the west edge of the model city. Accessible from `workbench` only. Reveals an ending_lore_token `leap_back_toward_new_orleans_with_question`.
- **Novel mechanic** — *unanswered-call accumulator.* The Demon's phone visitor's `let_it_ring` step counts up across the run; reaching 3 unlocks `ask_the_question`. This is the first cameo where a verb is *suppressed-action* (ignoring) rather than reach-out.

---

## II · Priestess · Bungalow (Elicia's haunted house)

### easy — `cameo_mackenzie_at_the_bungalow` · hand: mackenzie

Mackenzie brings the casserole.

- **Unique cards**
  - `pour_two_glasses_of_iced_tea` — Time 1. Restores 1 sanity, gives the next visitor connection +1 patience. The Lovers' grounded warmth visibly stabilizing the haunted room.
  - `set_the_table` — Time 2. Requires the new `kitchen_table` space. Lays down a cooperative bonus: any visitor Mackenzie connects with from this turn onward records a `mackenzie_made_a_place_for_them` lore token.
- **Unique visitor**
  - `philip_phone_priestess` — Philip checks in by phone from the Roberts house (already in canon; introduced *here* as the first cross-arcana phone-call visitor a cameo player carries with them).
- **Unique map**
  - `kitchen_table` — between `living_room` and `the_kitchen`. New threshold `back_porch` with ending_lore_token `leap_back_to_the_roberts_house`.
- **Novel mechanic** — *patience-bank.* The iced-tea card stockpiles a +1 patience credit usable on the next visitor regardless of mood. First cameo to surface patience as a player-managed resource.

### medium — `cameo_john_before_montreal` · hand: john_frank

John on the porch with the printed email he's been carrying for
seven days.

- **Unique cards**
  - `unfold_the_email` — Time 1. Reveals the printed-email's text in a log block; +1 doubt; +2 insight. Cannot be played twice.
  - `step_inside` — Time 2. Playable only at `the_porch`; moves John from the porch threshold into `living_room` and triggers Elicia's interior visit (off-screen, she lets you).
- **Unique visitor**
  - `the_printed_email` — an *object visitor* in John's coat pocket. Verb labels: `unfold/read/refold/leave_it_on_the_table`. Sit-with completes only at `living_room`.
- **Unique map**
  - `the_porch` — already in the bungalow file, but cameo treats it as the *starting* threshold (set in `starting_state.player_pos`). New threshold `alley_to_the_diner` with `leap_through_the_alley_to_the_diner`.
- **Novel mechanic** — *object-as-visitor.* First cameo where the player carries a visitor in a pocket — must be sat-with by being placed on the table. Demonstrates the visitor-pattern generalizing beyond people.

### hard — `cameo_frasier_fixes_the_kettle` · hand: frasier

The back panel off the stove. The Demon on the phone.

- **Unique cards**
  - `tighten_the_compression_fitting` — Time 2. Repairs the burner. Reduces stagnation per turn by 1 for the remainder of the run.
  - `tell_the_demon_to_shut_up` — Time 1. Costs 1 sanity. The Demon visitor's patience freezes for 2 turns.
- **Unique visitor**
  - `the_demon_on_the_phone_at_elicias` — sibling of the warehouse demon; uniquely patient here (patience 5) and uniquely punishing (after turn 5, hard-mood connections cost +1 sanity until silenced).
- **Unique map**
  - `back_alcove` — behind the kitchen; only accessible after `tighten_the_compression_fitting`. Threshold `roof_via_back_alcove` with `leap_up_to_the_roof_with_the_demon`.
- **Novel mechanic** — *repair gates a route.* First cameo where a card-play physically opens a new space mid-run (the back alcove appears in the spaces list but is unreachable until the repair card flips a `back_alcove_unlocked` flag).

---

## III · Empress · Riverboat (Nicola's deck)

### easy — `cameo_dean_arrives` · hand: dean (NEW HAND)

Mr. D. Dean walks aboard at 6:14. He has not been seen on the boat
before. He carries no business card, no menu request, and the small
note in his breast pocket.

- **Unique cards**
  - `smooth_the_lapels` — Time 1. Dean's tell. Gains 1 insight; the bar's brass railing becomes a connect-anywhere conduit for the next turn.
  - `leave_the_note_under_the_bill` — Time 3. Requires `table_17`. Plants the canonical "when you're ready" + phone number. Lore token: `dean_left_the_note_himself`.
- **Unique visitor**
  - `the_water_glass` — an object-visitor at Table 17; verb labels `lift/sip/set_down/leave_full`. Connecting completes only when the glass is left full at the end of the run.
- **Unique map**
  - `dean_side_door` — staff-only door near the river; only Dean can walk through it (his arrival.kind is `side_door` per visitor lore). Threshold `leap_off_the_side_door_into_the_dark`.
- **Novel mechanic** — *new hand entirely.* Dean as cameo player introduces a one-night-only hand. Hand JSON `dean.json` to be authored: minimal deck of 4 starter cards + the 2 unique above. This is the first cameo whose hand doesn't exist in any host scenario.

### medium — `cameo_frasier_returns_to_the_kitchen` · hand: frasier (already authored, REWORK NEEDED)

Frasier on the gangway after five years.

- **Unique cards**
  - `step_into_the_pass_for_one_plate` — Time 2. Once per run. Frasier helps Hector through one ticket; gains 2 harvest, +2 doubt (he wasn't supposed to).
  - `tell_hector_about_the_third` — Time 1. Cooperative connect: Hector + Frasier both record a lore token together (`pass_carried_the_news`).
- **Unique visitor**
  - `the_apron_on_the_hook` — object-visitor at `the_pass`. Verb: `look_at/touch/put_on/leave_it`. Putting it on triggers the stagnation-10 condition early (the spectacular exit reversed).
- **Unique map**
  - `the_old_locker` — behind the pass. New threshold `leap_off_the_back_walkway_with_the_apron`.
- **Novel mechanic** — *temptation flag.* The apron is a visitor you *can* connect with, but doing so spikes stagnation. First cameo where a connection is a loss vector if pursued — choose to ignore the visitor to win.

### hard — `cameo_quentin_at_table_17` · hand: quentin_paul

Q. Paul holds court at Table 17 on a Friday Nicola is also working
(off-canon — this is Paul's POV of a regular Friday Sunday-brunch
prep dinner).

- **Unique cards**
  - `make_a_phone_call` — Time 2. Outbound. Selects an off-board visitor from the cameo's NPC list (Dante, Antonio, the bandstand) and writes a doctrine entry. First cameo where a card spawns a *scheduled visitor arrival*.
  - `the_envelope_under_the_napkin` — Time 3. Plants a doctrine token on whichever staff visitor served the table last. Punishes Nicola's apron the next time the world cycles.
- **Unique visitor**
  - `the_bandstand_payphone` — phone visitor at `table_17` (rings if Paul has not made a call by turn 4). Connection unlocks the back room threshold.
- **Unique map**
  - `paul_back_room_path` — direct edge from `table_17` to `back_room` (skipping the catering office). Threshold `leap_from_the_back_room_with_the_envelope`.
- **Novel mechanic** — *card-spawns-visitor.* `make_a_phone_call` is the first card to add an entry to the visitor schedule live (engine work: card effect type `schedule_visitor` — TODO).

---

## IV · Emperor · Dante's office / helm

### easy — `cameo_sammy_at_the_well` · hand: sammy (NEW HAND)

Sammy works the bar through Friday dinner. Dante is at the helm.

- **Unique cards**
  - `pour_a_short_one_for_yourself` — Time 1. Restores 1 sanity. Trackable across the run (Dante notices on the third).
  - `route_the_phone_call` — Time 1. Reroutes any phone-call visitor that arrives this turn to the bar's intercom; Sammy connects with the caller without leaving the well.
- **Unique visitor**
  - `the_well_itself` — object-visitor at `sammys_bar`. Refilling is the work; the well is a passive presence Sammy can `sit_with` for the closer.
- **Unique map**
  - `the_back_bar_passthrough` — connects `sammys_bar` to `the_pass` without going through the dining room. Threshold `leap_off_the_back_bar_at_close`.
- **Novel mechanic** — *passive-completion visitor.* The well completes by Sammy doing his job; no explicit verb sequence. First cameo where staying-in-place satisfies a connection.

### medium — `cameo_antonios_friday_visit` · hand: antonio

Antonio's rare Friday visit home from Houston (canonically rare —
he flew in for Dante's birthday next week, came tonight because he
couldn't wait).

- **Unique cards**
  - `sit_with_dad_at_the_helm` — Time 3. Once per run. Climbs the iron stair; locks Dante's attention for one turn (Dante visitor steps advance regardless of his patience clock).
  - `borrow_a_white_jacket` — Time 2. Lets Antonio briefly help on the floor; +1 fuel, +1 doubt (he isn't supposed to).
- **Unique visitor**
  - `mom_on_the_phone` — Marta calls from Houston at turn 3. Phone-call visitor at `maitre_d_stand`. Sit-with completes only if Antonio has been to the helm first.
- **Unique map**
  - `iron_stair_landing` — between `main_dining_room` and `helm`. Threshold `leap_from_the_landing_with_the_question`.
- **Novel mechanic** — *visitor-gates-visitor.* Marta's sit-with is gated by Antonio having connected with Dante first. First cameo with a directional visitor dependency.

### hard — `cameo_paul_at_table_17_sunday` · hand: quentin_paul

The canonical Sunday brunch from Dante's POV, replayed from Paul's.

- **Unique cards**
  - `request_a_better_table` — Time 1. Forces Hector to swap two plates' timing. Stagnation +1 for Dante, but Paul gains 2 doctrine.
  - `whisper_to_the_mayor_aide` — Time 2. Cooperative connect with `the_aide_visitor` (new). On a hit, doctrine +2 and a `paul_filed_a_favor` lore token.
- **Unique visitor**
  - `the_aide_visitor` — Paul's seat-mate, a city aide. Patience 4. Connect quickly or he leaves.
- **Unique map**
  - `the_back_room_through_the_kitchen` — Paul's known route. Adds an edge `table_17 → back_room` skipping catering. Threshold `leap_from_the_back_room_brunch`.
- **Novel mechanic** — *doctrine punishes the host's apron.* Every doctrine point Paul banks raises Nicola's start-of-next-run doubt by 1 (lore-only flag; surfaces in cross-run scoring). First cameo with cross-run consequence.

---

## V · Hierophant · Sunday circuit (Paul's car, the bandstand, Table 17)

### easy — `cameo_dante_walks_the_same_circuit` · hand: dante (NEW HAND OR reuses emperor)

Dante walks Paul's Sunday route alone on a Tuesday afternoon to see
what Paul sees.

- **Unique cards**
  - `stand_in_the_back_pew` — Time 1. At `st_judes_parking_lot`. +1 insight, no doubt cost.
  - `pay_for_the_aide_lunch` — Time 2. At `dambrosios_table_17`. Banks a `dante_pre-empted_paul` lore token.
- **Unique visitor**
  - `father_amato` — the parish priest. New visitor at `st_judes_parking_lot`. Hard mood, talkative; only Dante and Paul can connect with him.
- **Unique map**
  - `the_pew_in_the_back` — interior space inside `st_judes_parking_lot`. Threshold `leap_back_to_the_helm`.
- **Novel mechanic** — *out-of-character traversal.* Dante on Paul's route. The route's visitors react to the wrong host showing up — Father Amato's first response is `who_is_this` instead of `greet`. Establishes that hand-on-host-route can shift visitor opening lines.

### medium — `cameo_john_at_the_bandstand` · hand: john_frank

John writes about a campaign rally at the bandstand he didn't
expect to attend.

- **Unique cards**
  - `take_the_notebook_out` — Time 1. +1 insight per turn while at `the_bandstand`. Pricey: +1 doubt per turn (he is being seen).
  - `ask_the_aide_a_question` — Time 2. Connect with Paul's aide without going through Paul. Bypasses the Hierophant's gatekeeping.
- **Unique visitor**
  - `the_aide_visitor` (shared with hard Emperor cameo).
- **Unique map**
  - `the_press_riser` — back of the bandstand. Threshold `leap_off_the_riser_into_the_alley`.
- **Novel mechanic** — *bypass-the-host.* John can connect with the host's gated visitor (the aide) without first connecting with the host (Paul). First cameo to demonstrate the gatekeeping pattern being broken by a guest's verbs.

### hard — `cameo_antonio_confronts_paul` · hand: antonio

Antonio flies in to confront Paul about a business dispute (one
month before the wreck).

- **Unique cards**
  - `tell_paul_no` — Time 3. Once per run. +2 insight, +2 doubt. Locks Paul's patience at 0 for the rest of the run.
  - `walk_out_mid_sentence` — Time 1. Free leap to any visible threshold. Costs 1 sanity.
- **Unique visitor**
  - `the_recording_phone` — Antonio's phone (recording silently). Sit-with requires no verb; just having it on the table during a Paul-connection counts.
- **Unique map**
  - `the_corner_booth_of_table_17` — a partition within `dambrosios_table_17`. Threshold `leap_with_the_recording_out_the_side_door`.
- **Novel mechanic** — *recording-as-passive-connection.* The phone-visitor satisfies a connection just by being present during another connection. First cameo where a visitor's connection is parasitic on another's.

---

## VI · Lovers · Roberts' house

### easy — `cameo_elicia_at_the_roberts` · hand: elicia

Elicia brings a tape of her Anya footage over for Mackenzie to
watch.

- **Unique cards**
  - `cue_the_tape` — Time 2. At `roberts_living_room`. Plays the Anya footage; Mackenzie connects at +2.
  - `take_the_tape_back` — Time 1. Mid-watch retrieval; Elicia gains 1 harvest, leaves Mackenzie at the verge of connection. Risk/reward.
- **Unique visitor**
  - `anya_on_the_tv` — Anya from Elicia's archive appears on Mackenzie's TV. Off-platform visitor.
- **Unique map**
  - `the_couch` — a focal interior space inside `roberts_living_room`. Threshold `leap_with_the_tape_back_to_the_bungalow`.
- **Novel mechanic** — *visitor-on-another's-screen.* Anya appears on Mackenzie's TV; the visitor exists at a node Mackenzie owns but only Elicia can connect with her. First cross-arcana visitor presence.

### medium — `cameo_john_at_the_roberts` · hand: john_frank

John drops by the day before the boy with the Polaroid arrives.

- **Unique cards**
  - `sit_on_the_back_porch_with_philip` — Time 2. Connect with Philip at `back_porch`; insight +2, but a `john_was_warned_first` token sets.
  - `leave_the_napkin_on_the_kitchen_counter` — Time 1. Plants the half-written email-draft for Mackenzie to find post-run.
- **Unique visitor**
  - `the_polaroid_about_to_arrive` — a *forthcoming* visitor. Not on the board; revealed by a doubt-threshold milestone (level 5). First cameo with a deferred-reveal visitor.
- **Unique map**
  - `the_back_porch` — already in the location file; treated as a *starting* threshold from John's POV.
- **Novel mechanic** — *deferred-reveal visitor.* The Polaroid isn't on the board at start; doubt 5 triggers its arrival the next turn. First cameo to surface a doubt-driven visitor entry.

### hard — `cameo_frasier_at_the_roberts` · hand: frasier

Frasier visits the Roberts to install a new mailbox post for them
(canonical small favor; sets up the day-after-the-Polaroid grief).

- **Unique cards**
  - `replace_the_mailbox_post` — Time 3. Outdoor work at `front_walk`. Restores 1 sanity per turn while at `front_walk`. Banks a `frasier_set_the_post` lore token.
  - `say_what_dante_would_say` — Time 2. Connect with Philip using Dante's phrasing. +1 hard-mood. Risk: +1 doubt.
- **Unique visitor**
  - `the_mailbox_post_itself` — object-visitor. Verb labels: `set_the_post / fill_the_hole / level_it / step_back`. The four-verb sequence is the whole connection.
- **Unique map**
  - `the_front_walk` — outdoors. Threshold `leap_back_toward_the_warehouse_with_the_mail_key`.
- **Novel mechanic** — *manual-labor as the entire connection arc.* The post is a passive structure; connecting is the doing. First cameo where physical labor is the verb sequence.

---

## VII · Chariot · Ember & Ash (Antonio's warehouse)

### easy — `cameo_dante_at_ember_and_ash` · hand: dante

Dante visits Antonio's warehouse for the first time since the
business expanded. Two months before the wreck.

- **Unique cards**
  - `look_at_the_books` — Time 2. At `warehouse_office`. Reads Antonio's ledger silently; +2 insight, +1 doubt. Banks `dante_saw_the_numbers`.
  - `dont_say_what_youre_thinking` — Time 1. Free for Dante; suppresses his next sit-with's verbalization. Conveys exactly the kindness of the not-mentioning.
- **Unique visitor**
  - `jimmy_with_two_coffees` — Antonio's crew chief Jimmy, here on a Tuesday at 11:14. Connects with Dante at high warmth.
- **Unique map**
  - `the_book_shelf_in_the_office` — interior at `warehouse_office`. Threshold `leap_back_to_the_helm_with_the_numbers`.
- **Novel mechanic** — *witness-without-speaking.* Dante's silent-presence card. Verbalization-suppression as a positive resource. First cameo where holding-back is a played verb.

### medium — `cameo_frasier_at_ember_and_ash` · hand: frasier

Frasier inspects a load-bearing beam Antonio asked him about a week
ago.

- **Unique cards**
  - `take_the_level_to_it` — Time 2. At `warehouse_floor`. Confirms or corrects Antonio's professional read. +1 fuel.
  - `tell_him_the_beam_is_fine` (or `tell_him_the_beam_is_not`) — Time 3, one or the other. Locks a doctrinal record either way; Antonio will believe Frasier on the wreck day.
- **Unique visitor**
  - `the_cypress_beam` — object-visitor at the warehouse's central span. Verb labels: `look_at / touch / press / leave_alone`. The wreck-day will, in vol5, hinge on whichever verb Frasier ended on.
- **Unique map**
  - `the_beam_under_the_skylight` — interior space within `warehouse_floor`. Threshold `leap_under_the_skylight_with_the_truth`.
- **Novel mechanic** — *binary verbalization choice.* One of two `tell_him` cards must be played; the choice writes a cross-run flag that vol5 ch20 reads. First cameo with a hard binary doctrinal outcome.

### hard — `cameo_john_at_ember_and_ash` · hand: john_frank

John visits Antonio the afternoon of (Antonio called him at noon).

- **Unique cards**
  - `let_it_ring_three_times` — Time 1. Free. Costs Antonio +1 doubt (he is on the other end). Three plays of this card and Antonio's patience hits 0 for the rest of the run.
  - `pick_up_the_phone` — Time 2. The opposite move. Connects John with Antonio at any node, +2 hard-mood, +1 doubt.
- **Unique visitor**
  - `antonio_on_the_phone` — Antonio is the visitor here, not the host. Phone-call visitor at any node John occupies.
- **Unique map**
  - `the_back_stair_at_ember_and_ash` — outdoor stair on the west wall. Threshold `leap_into_the_wreck_aftermath` (early access to the canonical post-wreck scene).
- **Novel mechanic** — *the host as visitor.* In John's cameo at Antonio's warehouse, *Antonio is the visitor*. First cameo where the room's owner is the connection target rather than a host-NPC.

---

## Implementation queue

Status — at the close of this session:

| Cameo | Status | Notes |
|---|---|---|
| magician · john_at_the_warehouse | JSON exists, needs rework to new spec | base prose pass done |
| magician · elicia_films_a_scene | JSON exists, needs rework | base done |
| magician · antonio_comes_home | JSON exists, needs rework | base done |
| priestess · mackenzie_at_the_bungalow | JSON exists, needs rework | base done |
| priestess · john_before_montreal | JSON exists, needs rework | base done |
| priestess · frasier_fixes_the_kettle | JSON exists, needs rework | base done |
| empress · frasier_returns_to_the_kitchen | JSON exists, needs rework | base done |
| empress · dean_arrives | not started | hand JSON for `dean.json` required |
| empress · quentin_at_table_17 | not started | depends on `quentin_paul.json` hand (already exists) |
| emperor · sammy_at_the_well | not started | hand JSON for `sammy.json` required |
| emperor · antonios_friday_visit | not started | reuses `antonio.json` |
| emperor · paul_at_table_17_sunday | not started | reuses `quentin_paul.json` |
| hierophant · dante_walks_the_same_circuit | not started | hand JSON for `dante.json` (or reuse `emperor.json`) |
| hierophant · john_at_the_bandstand | not started | reuses `fool.json` |
| hierophant · antonio_confronts_paul | not started | reuses `antonio.json` |
| lovers · elicia_at_the_roberts | not started | reuses `elicia.json` |
| lovers · john_at_the_roberts | not started | reuses `fool.json` |
| lovers · frasier_at_the_roberts | not started | reuses `frasier.json` |
| chariot · dante_at_ember_and_ash | not started | hand JSON or reuse emperor |
| chariot · frasier_at_ember_and_ash | not started | reuses `frasier.json` |
| chariot · john_at_ember_and_ash | not started | reuses `fool.json` |

Next session work order:
1. Author new hands: `dean.json`, `sammy.json`, optionally `dante.json` (or alias to emperor).
2. Rework the existing 7 to embed `scenario_action_cards`, `scenario_visitors`, `scenario_spaces_additions`.
3. Author the 14 not-started cameos following the design above.
4. Add picker tiles for all 14 to `GalleryOverlay.gd` (constants are pre-stubbed).
5. Engine TODO: card effect type `schedule_visitor` for the Empress hard cameo's `make_a_phone_call`.
