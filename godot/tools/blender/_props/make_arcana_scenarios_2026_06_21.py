"""One-shot driver: emits baseline scenario JSON for the 14 Major
Arcana that don't yet have data (Strength → World; existing
arcana fool/magician/priestess/empress/emperor/hierophant/chariot/
lovers are left alone).

Per-arcana files emitted:
  action_cards.json    — 4-6 arcana-themed action cards
  gravity_deck.json    — 12 destiny cards (pressure events)
  setup_<scenario>.json — scenario init state
  finale.json          — 3 finale endings keyed by tension-track
                          triggers
  die.json             — 6-face arcana die
  items.json           — 3 item piles per locale
  visitors.json        — 3 visitors w/ stepped conversation

These are SCAFFOLDS — minimal-but-valid content keyed to the
arcana's lore so each scenario loads cleanly and reads as itself.
Card text is intentionally terse so the user can write it up
later; the structural slot is what's being established here.
"""
import os, sys, json
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(_HERE, "../../../.."))
GAMES = os.path.join(REPO, "godot/resources/games")


# ── ARCANA CONFIGS ──────────────────────────────────────────────
ARCANA = [
    {
        "key": "strength",
        "title": "STRENGTH",
        "scenario": "lion_cage_open",
        "scenario_title": "THE LION CAGE OPEN",
        "scenario_subtitle": "Carnival Lot · evening",
        "location": "carnival_lot",
        "hand": "tbd_strength",
        "default_space": "merry_go_round",
        "spaces": ["merry_go_round", "big_top", "ticket_booth", "lion_cage",
                   "banner_posts", "front_gate"],
        "tension": {"key": "strain", "label": "STRAIN", "max": 10},
        "epigraph_up": "Quiet strength, courage, compassion, the gentleness "
                       "that doesn't need to prove itself.",
        "epigraph_down": "Strain, the strength that's actually exhaustion, "
                         "the cage door open and nothing inside it.",
        "scene_description": "The carnival's been closed for years. The "
                             "merry-go-round still spins if you push it. "
                             "The lion's gone but the cage is still here.",
        "direction_hint": "Hold what you can't hold. The hint is that you "
                          "don't actually have to.",
        "verbs": ["soothe", "carry", "stand_ground", "let_go", "harness"],
        "die_faces": [
            ("HOLD", "ss", "Success ★★. The weight settles."),
            ("CARRY", "s", "Success ★. You take it on."),
            ("STRAIN_PARTIAL_A", "partial", "Partial. Spend 2 Action cards to convert."),
            ("STRAIN_PARTIAL_B", "partial", "Partial. Spend 2 Action cards to convert."),
            ("DROP", "fail", "Failure. +1 STRAIN."),
            ("GENTLE", "wild", "Wild. ★ if the strain track is below 6, else failure."),
        ],
        "visitors": [
            ("the_strongman", "The Strongman", "left_alone"),
            ("the_child", "A Child Watching", "preoccupied"),
            ("the_animal", "Something Familiar in the Grass", "gruff"),
        ],
        "piles": {
            "ticket_booth": ["stub", "ledger_carbon", "owners_key"],
            "lion_cage": ["rope_coil", "feed_pail", "kept_collar"],
            "banner_posts": ["faded_banner", "tent_stake", "rusted_bell"],
        },
        "finales": [
            ("dropped_what_held", "DROPPED WHAT HELD"),
            ("held_until_empty", "HELD UNTIL EMPTY"),
            ("the_cage_was_always_open", "THE CAGE WAS ALWAYS OPEN"),
        ],
    },
    {
        "key": "hermit",
        "title": "THE HERMIT",
        "scenario": "watch_kept",
        "scenario_title": "WATCH KEPT",
        "scenario_subtitle": "Bayou Lighthouse · long after midnight",
        "location": "bayou_lighthouse",
        "hand": "tbd_hermit",
        "default_space": "writing_desk",
        "spaces": ["writing_desk", "bunk", "spiral_stair", "n_window",
                   "lens_hatch", "door"],
        "tension": {"key": "loneliness", "label": "LONELINESS", "max": 10},
        "epigraph_up": "Solitude, the inner light, the lamp held up for "
                       "the one who comes after.",
        "epigraph_down": "Loneliness, the room emptying of meaning around "
                         "the keeper.",
        "scene_description": "The lens turns. The light goes out into the "
                             "bayou. Nobody comes. Nobody has come for "
                             "three months. The logbook is up to date.",
        "direction_hint": "The light has to be lit. You don't have to be "
                          "the one who lights it tonight.",
        "verbs": ["log", "tend_lamp", "wait", "signal", "withdraw"],
        "die_faces": [
            ("KEEP_WATCH", "ss", "Success ★★. The lamp catches."),
            ("LOG_IT", "s", "Success ★. You write it down. Done."),
            ("LONG_NIGHT_A", "partial", "Partial. Spend 2 Action cards to convert."),
            ("LONG_NIGHT_B", "partial", "Partial. Spend 2 Action cards to convert."),
            ("DIM", "fail", "Failure. +1 LONELINESS."),
            ("FLAME", "wild", "Wild. ★ if you've logged anything this turn, else failure."),
        ],
        "visitors": [
            ("the_predecessor", "The Previous Keeper", "preoccupied"),
            ("a_boat_passing", "A Boat Passing", "gruff"),
            ("the_radio_voice", "A Voice on the Radio", "jovial"),
        ],
        "piles": {
            "writing_desk": ["logbook", "fountain_pen", "old_chart"],
            "bunk": ["spare_oil", "wool_blanket", "found_letter"],
            "spiral_stair": ["brass_polish_cloth", "lens_shim", "stair_step_count"],
        },
        "finales": [
            ("light_out", "THE LIGHT WENT OUT"),
            ("no_one_came", "NO ONE CAME"),
            ("watch_held_alone", "THE WATCH WAS KEPT ALONE"),
        ],
    },
    {
        "key": "wheel_of_fortune",
        "title": "THE WHEEL OF FORTUNE",
        "scenario": "the_house_edge",
        "scenario_title": "THE HOUSE EDGE",
        "scenario_subtitle": "Le Roulant Casino · 11:11 PM",
        "location": "le_roulant_casino",
        "hand": "tbd_wheel",
        "default_space": "roulette_table",
        "spaces": ["roulette_table", "slot_bank", "cashier_cage", "neon_sign",
                   "plaza_center", "front_door"],
        "tension": {"key": "tilt", "label": "TILT", "max": 10},
        "epigraph_up": "The turn, the cycle, providence, the wheel under "
                       "everybody and accountable to no one.",
        "epigraph_down": "Tilt, the wheel that's rigged, the cycle that's "
                         "not a cycle but a drain.",
        "scene_description": "The wheel spins. The ball lands wherever it "
                             "lands. The house always wins, eventually. "
                             "You've been here long enough to know this.",
        "direction_hint": "Walk away when the wheel's still spinning, "
                          "before it tells you anything.",
        "verbs": ["bet", "hedge", "double_down", "cash_out", "watch_wheel"],
        "die_faces": [
            ("HOUSE_FOLDS", "ss", "Success ★★. The wheel hits where you wanted."),
            ("EVEN_MONEY", "s", "Success ★. You break even on the spin."),
            ("EDGE_PARTIAL_A", "partial", "Partial. Spend 2 Action cards to convert."),
            ("EDGE_PARTIAL_B", "partial", "Partial. Spend 2 Action cards to convert."),
            ("BUST", "fail", "Failure. +1 TILT."),
            ("WILD_ZERO", "wild", "Wild. ★ if you cashed out last turn, else failure."),
        ],
        "visitors": [
            ("the_pit_boss", "The Pit Boss", "gruff"),
            ("the_regular", "A Regular at the Bar", "preoccupied"),
            ("someone_winning", "Someone Winning", "jovial"),
        ],
        "piles": {
            "roulette_table": ["last_chip", "casino_marker", "wheel_token"],
            "cashier_cage": ["receipt_stub", "house_pen", "loyalty_card"],
            "slot_bank": ["empty_cup", "lemon_pull", "jackpot_photo"],
        },
        "finales": [
            ("comp_room", "THE COMP ROOM"),
            ("walked_with_nothing", "WALKED WITH NOTHING"),
            ("one_more_spin", "ONE MORE SPIN FOREVER"),
        ],
    },
    {
        "key": "justice",
        "title": "JUSTICE",
        "scenario": "motion_to_dismiss",
        "scenario_title": "MOTION TO DISMISS",
        "scenario_subtitle": "Parish Courthouse · 9:00 AM",
        "location": "courthouse_chamber",
        "hand": "erica_anna",
        "default_space": "plaintiff_table",
        "spaces": ["judge_bench", "witness_stand", "jury_box",
                   "plaintiff_table", "defense_table", "pew_front",
                   "bar_rail", "rear_door"],
        "tension": {"key": "weight", "label": "WEIGHT OF EVIDENCE", "max": 10},
        "epigraph_up": "Truth, balance, accountability, cause and effect.",
        "epigraph_down": "The verdict that arrives too late, the evidence "
                         "that won't hold.",
        "scene_description": "The room is full. The case is on the docket. "
                             "Anna is at the plaintiff table. Erica is on "
                             "the bench.",
        "direction_hint": "Justice isn't who wins. It's what gets entered "
                          "into the record.",
        "verbs": ["enter_evidence", "object", "stipulate", "cross",
                  "recess"],
        "die_faces": [
            ("SUSTAINED", "ss", "Success ★★. The objection holds."),
            ("ON_RECORD", "s", "Success ★. The motion is recorded."),
            ("CONTINUED_A", "partial", "Partial. Spend 2 Action cards to convert."),
            ("CONTINUED_B", "partial", "Partial. Spend 2 Action cards to convert."),
            ("STRICKEN", "fail", "Failure. +1 WEIGHT."),
            ("GAVEL", "wild", "Wild. ★ if Erica is on the bench this turn, else failure."),
        ],
        "visitors": [
            ("anna_at_table", "Anna at the Plaintiff Table", "preoccupied"),
            ("the_witness", "The Witness", "gruff"),
            ("the_clerk", "The Court Clerk", "jovial"),
        ],
        "piles": {
            "plaintiff_table": ["exhibit_a", "client_brief", "highlighter"],
            "defense_table": ["motion_packet", "bar_card", "objections_list"],
            "judge_bench": ["gavel", "bench_book", "minute_order"],
        },
        "finales": [
            ("dismissed_without_prejudice", "DISMISSED WITHOUT PREJUDICE"),
            ("verdict_late", "THE VERDICT ARRIVED LATE"),
            ("on_the_record", "ON THE RECORD"),
        ],
    },
    {
        "key": "hanged_man",
        "title": "THE HANGED MAN",
        "scenario": "after_simon",
        "scenario_title": "AFTER SIMON",
        "scenario_subtitle": "Simon's Apartment · the third evening",
        "location": "simon_apartment",
        "hand": "natalie",
        "default_space": "armchair",
        "spaces": ["armchair", "bed", "kitchenette", "tv", "tipped_chair",
                   "hanging_boot", "front_window", "front_door"],
        "tension": {"key": "suspension", "label": "SUSPENSION", "max": 10},
        "epigraph_up": "Surrender, the pause that reveals, the upside-down "
                       "view that sees true.",
        "epigraph_down": "Suspended without surrender, the apartment "
                         "Simon left without leaving.",
        "scene_description": "Simon's not coming back. The chair's been "
                             "tipped over since Tuesday. The boot's been "
                             "hanging from the peg since you got here.",
        "direction_hint": "You don't have to put any of it right. You "
                          "have to be in the room.",
        "verbs": ["sit_still", "right_the_chair", "take_down_the_boot",
                  "answer_call", "open_window"],
        "die_faces": [
            ("STILL", "ss", "Success ★★. The room holds."),
            ("ACKNOWLEDGE", "s", "Success ★. You let it be true."),
            ("HUNG_PARTIAL_A", "partial", "Partial. Spend 2 Action cards to convert."),
            ("HUNG_PARTIAL_B", "partial", "Partial. Spend 2 Action cards to convert."),
            ("FLINCH", "fail", "Failure. +1 SUSPENSION."),
            ("TURNED", "wild", "Wild. ★ if you've sat down this turn, else failure."),
        ],
        "visitors": [
            ("simons_voicemail", "Simon's Voicemail", "gruff"),
            ("the_neighbor", "The Neighbor Downstairs", "jovial"),
            ("the_landlord", "The Landlord at the Door", "preoccupied"),
        ],
        "piles": {
            "kitchenette": ["instant_coffee", "spare_key", "rent_receipt"],
            "bed": ["folded_letter", "phone_charger", "wedding_band"],
            "tv": ["video_tape", "remote_no_batteries", "snow_static"],
        },
        "finales": [
            ("the_chair_still_tipped", "THE CHAIR STILL TIPPED"),
            ("the_boot_taken_down", "THE BOOT TAKEN DOWN"),
            ("you_sat_with_it", "YOU SAT WITH IT"),
        ],
    },
    {
        "key": "death",
        "title": "DEATH",
        "scenario": "walpurgisnacht",
        "scenario_title": "WALPURGISNACHT",
        "scenario_subtitle": "Asylum Ward C · the last shift",
        "location": "asylum_ward_c",
        "hand": "tbd_death",
        "default_space": "nurses_station",
        "spaces": ["nurses_station", "ward_1", "ward_2", "ward_3", "ward_4",
                   "ward_5", "gurney", "wheelchair", "cupola_below",
                   "corridor_s"],
        "tension": {"key": "vigil", "label": "VIGIL", "max": 10},
        "epigraph_up": "The end that makes a beginning, the threshold "
                       "honored, the page turned cleanly.",
        "epigraph_down": "The vigil that goes on too long, the ward that "
                         "won't close.",
        "scene_description": "The corridor is empty except for you. The "
                             "five rooms are quiet. The cupola has a "
                             "missing pane. Something's about to enter.",
        "direction_hint": "You walk the rounds. Each round is the last "
                          "one or it isn't.",
        "verbs": ["round", "check_chart", "close_eyes", "hold_hand",
                  "ring_bell"],
        "die_faces": [
            ("PEACEFUL", "ss", "Success ★★. The threshold is honored."),
            ("ROUNDED", "s", "Success ★. The room is checked."),
            ("VIGIL_PARTIAL_A", "partial", "Partial. Spend 2 Action cards to convert."),
            ("VIGIL_PARTIAL_B", "partial", "Partial. Spend 2 Action cards to convert."),
            ("MISSED", "fail", "Failure. +1 VIGIL."),
            ("HAND_HELD", "wild", "Wild. ★ if you've held a hand this turn, else failure."),
        ],
        "visitors": [
            ("the_attending", "The Attending Doctor", "gruff"),
            ("the_chaplain", "The Chaplain", "preoccupied"),
            ("the_family", "Someone's Family in the Hall", "jovial"),
        ],
        "piles": {
            "nurses_station": ["chart_binder", "saline_drip", "shift_log"],
            "gurney": ["folded_sheet", "id_band", "vial"],
            "wheelchair": ["lap_blanket", "wheel_brake", "found_dentures"],
        },
        "finales": [
            ("the_ward_closed", "THE WARD CLOSED"),
            ("vigil_unbroken", "THE VIGIL HELD"),
            ("missed_the_threshold", "MISSED THE THRESHOLD"),
        ],
    },
    {
        "key": "temperance",
        "title": "TEMPERANCE",
        "scenario": "tuesday_observation",
        "scenario_title": "TUESDAY OBSERVATION",
        "scenario_subtitle": "The Mixing Glass · 11:00 PM",
        "location": "mixing_glass",
        "hand": "frank",
        "default_space": "bar_stool_mid",
        "spaces": ["bar_stool_mid", "bar_stool_w", "backbar", "booth_1",
                   "booth_2", "booth_3", "booth_4", "neon_open",
                   "alley_door"],
        "tension": {"key": "off_pour", "label": "OFF POUR", "max": 10},
        "epigraph_up": "Mixing, moderation, the ratios that land — fire "
                       "and water held at exactly the right temperature.",
        "epigraph_down": "The off pour, the ratio that's wrong by a "
                         "splash, the night that tilts.",
        "scene_description": "Tuesday at the Mixing Glass. Frank takes a "
                             "stool at the end of the bar like he's "
                             "always there. The neon spells OPEN.",
        "direction_hint": "The measure has to be exact. Within a quarter "
                          "ounce or the drink is wrong.",
        "verbs": ["pour", "stir", "shake", "garnish", "comp"],
        "die_faces": [
            ("CLEAN_POUR", "ss", "Success ★★. The drink is right."),
            ("EVEN_RATIO", "s", "Success ★. You hit the mark."),
            ("SHORT_A", "partial", "Partial. Spend 2 Action cards to convert."),
            ("SHORT_B", "partial", "Partial. Spend 2 Action cards to convert."),
            ("HEAVY", "fail", "Failure. +1 OFF POUR."),
            ("LAST_CALL", "wild", "Wild. ★ if you've garnished this turn, else failure."),
        ],
        "visitors": [
            ("the_regular", "Frank's Regular Spot", "preoccupied"),
            ("the_first_date", "A First Date in Booth Two", "jovial"),
            ("the_owner", "The Owner Closing Out", "gruff"),
        ],
        "piles": {
            "backbar": ["jigger", "mixing_glass", "house_bitters"],
            "booth_1": ["matchbook", "cocktail_napkin", "olive_pick"],
            "alley_door": ["empty_keg", "shift_drink", "bar_apron"],
        },
        "finales": [
            ("the_off_pour", "THE OFF POUR"),
            ("perfect_round", "A PERFECT ROUND"),
            ("closed_clean", "CLOSED CLEAN"),
        ],
    },
    {
        "key": "devil",
        "title": "THE DEVIL",
        "scenario": "gumbo_limbo_night",
        "scenario_title": "GUMBO LIMBO NIGHT",
        "scenario_subtitle": "Daigle's Roadhouse · 1:00 AM",
        "location": "daigles_roadhouse",
        "hand": "tbd_devil",
        "default_space": "bar",
        "spaces": ["bar", "bar_stool", "pool_table", "jukebox", "gator_head",
                   "schlitz_neon", "front_door"],
        "tension": {"key": "chain", "label": "CHAIN", "max": 10},
        "epigraph_up": "The bond consciously chosen, the appetite known, "
                       "the contract a person can walk out of.",
        "epigraph_down": "The chain you didn't notice, the bar stool worn "
                         "into the shape of you.",
        "scene_description": "Daigle's at 1 AM. The juke knows your "
                             "songs. The bartender pours before you ask. "
                             "You've been here longer than you meant.",
        "direction_hint": "Leave. The door is right there. It's always "
                          "been right there.",
        "verbs": ["another_round", "rack_em", "feed_the_juke",
                  "settle_up", "walk_out"],
        "die_faces": [
            ("WALK_OUT", "ss", "Success ★★. You leave. You actually leave."),
            ("ONE_FOR_THE_ROAD", "s", "Success ★. The last one. Honest."),
            ("STAY_PARTIAL_A", "partial", "Partial. Spend 2 Action cards to convert."),
            ("STAY_PARTIAL_B", "partial", "Partial. Spend 2 Action cards to convert."),
            ("ANOTHER", "fail", "Failure. +1 CHAIN."),
            ("LAST_CALL", "wild", "Wild. ★ if you've paid your tab this turn, else failure."),
        ],
        "visitors": [
            ("the_bartender", "The Bartender", "gruff"),
            ("the_stranger", "Someone You Used to Be", "preoccupied"),
            ("the_one_who_left", "The One Who Got Out", "jovial"),
        ],
        "piles": {
            "bar": ["unopened_tab", "matchbook", "shot_glass"],
            "pool_table": ["broken_cue", "8_ball", "table_chalk"],
            "jukebox": ["coin_jar", "song_dedication", "old_setlist"],
        },
        "finales": [
            ("the_chain_loose", "THE CHAIN LOOSE"),
            ("stayed_till_close", "STAYED TILL CLOSE"),
            ("never_settled_up", "NEVER SETTLED UP"),
        ],
    },
    {
        "key": "tower",
        "title": "THE TOWER",
        "scenario": "render_queue",
        "scenario_title": "RENDER QUEUE",
        "scenario_subtitle": "WGUR Transmitter Shack · 2:00 AM",
        "location": "wgur_transmitter_shack",
        "hand": "evangeline",
        "default_space": "operator_desk",
        "spaces": ["operator_desk", "rack_a", "rack_b", "rack_c",
                   "patch_panel", "mic_stand", "n_window", "door"],
        "tension": {"key": "carrier", "label": "CARRIER OVERLOAD", "max": 10},
        "epigraph_up": "Sudden insight, the structure that breaks to let "
                       "the light in, the necessary collapse.",
        "epigraph_down": "Structure that won't break, the broadcast that "
                         "can't go off the air, the queue that keeps "
                         "rendering.",
        "scene_description": "The carrier is on. The tower's red lights "
                             "are pulsing. The queue is at 847 items and "
                             "you cannot kill the process.",
        "direction_hint": "Pull the plug. The tower won't let you. Pull "
                          "it anyway.",
        "verbs": ["push_render", "cue_break", "kill_signal", "patch_around",
                  "broadcast"],
        "die_faces": [
            ("BREAK_CLEAN", "ss", "Success ★★. The structure lets go."),
            ("CUE_BREAK", "s", "Success ★. A gap in the signal."),
            ("BUFFER_A", "partial", "Partial. Spend 2 Action cards to convert."),
            ("BUFFER_B", "partial", "Partial. Spend 2 Action cards to convert."),
            ("HOLD_SIGNAL", "fail", "Failure. +1 CARRIER OVERLOAD."),
            ("OBSTRUCTION", "wild", "Wild. ★ if you've killed a signal this turn, else failure."),
        ],
        "visitors": [
            ("the_engineer", "The Other Engineer", "gruff"),
            ("the_caller", "A Late-Night Caller", "preoccupied"),
            ("the_intern", "The Intern Who Stayed", "jovial"),
        ],
        "piles": {
            "operator_desk": ["log_binder", "bakelite_mic", "headphones"],
            "patch_panel": ["patch_cable_red", "patch_cable_yellow", "labels"],
            "rack_a": ["vu_meter_card", "tube_replacement", "fuse"],
        },
        "finales": [
            ("the_carrier_dropped", "THE CARRIER DROPPED"),
            ("the_queue_rendered_anyway", "THE QUEUE RENDERED ANYWAY"),
            ("you_pulled_the_plug", "YOU PULLED THE PLUG"),
        ],
    },
    {
        "key": "star",
        "title": "THE STAR",
        "scenario": "glass_skin",
        "scenario_title": "GLASS SKIN",
        "scenario_subtitle": "Christian Ice Co. · just before sunrise",
        "location": "christian_ice_co",
        "hand": "tbd_star",
        "default_space": "retail_counter",
        "spaces": ["retail_counter", "block_freezer", "chest_freezer_a",
                   "chest_freezer_b", "chest_freezer_c", "compressor_1",
                   "brine_tank", "dock_door", "storefront"],
        "tension": {"key": "fog", "label": "FOGGING", "max": 10},
        "epigraph_up": "Hope, the quiet luminous thing, the star you can "
                       "see only when you stop looking for it.",
        "epigraph_down": "The glass that fogs over, the hope that won't "
                         "stay clear long enough to read.",
        "scene_description": "The ice plant before sunrise. The ICE "
                             "letters are still lit. The freezer compressors "
                             "hum. Through the storefront glass, the sky "
                             "is starting.",
        "direction_hint": "Don't wipe the glass. Let it go clear on its "
                          "own.",
        "verbs": ["pull_block", "wipe_glass", "check_compressor", "bag_ice",
                  "open_doors"],
        "die_faces": [
            ("CLEAR_PANE", "ss", "Success ★★. The glass clears on its own."),
            ("STEADY", "s", "Success ★. The compressor holds the line."),
            ("FROST_A", "partial", "Partial. Spend 2 Action cards to convert."),
            ("FROST_B", "partial", "Partial. Spend 2 Action cards to convert."),
            ("FOGGED", "fail", "Failure. +1 FOGGING."),
            ("MORNING_LIGHT", "wild", "Wild. ★ if the dock door is open this turn, else failure."),
        ],
        "visitors": [
            ("the_first_customer", "The First Customer", "jovial"),
            ("the_other_shift", "The Other Shift Leaving", "gruff"),
            ("the_kid_at_glass", "A Kid at the Storefront Glass", "preoccupied"),
        ],
        "piles": {
            "retail_counter": ["punch_card", "ice_pick", "cash_drawer_key"],
            "block_freezer": ["ice_block", "block_tongs", "block_chip"],
            "brine_tank": ["pressure_gauge", "brine_sample", "service_log"],
        },
        "finales": [
            ("fog_never_cleared", "THE FOG NEVER CLEARED"),
            ("morning_light_landed", "THE MORNING LIGHT LANDED"),
            ("you_opened_the_doors", "YOU OPENED THE DOORS"),
        ],
    },
    {
        "key": "moon",
        "title": "THE MOON",
        "scenario": "sigils_in_static",
        "scenario_title": "SIGILS IN STATIC",
        "scenario_subtitle": "Static Drive-In · between features",
        "location": "static_drive_in",
        "hand": "natalie",
        "default_space": "counter",
        "spaces": ["counter", "popcorn", "soda_fountain", "candy_case",
                   "picture_window", "lot_porch"],
        "tension": {"key": "drift", "label": "MOONDRIFT", "max": 10},
        "epigraph_up": "The dreaming, the symbols that arrive at night, "
                       "the pattern in the static.",
        "epigraph_down": "The drift, the symbols that mean too much, the "
                         "static that reads like a sentence.",
        "scene_description": "The drive-in screen is blank between "
                             "features. The snack bar is open. The lot is "
                             "half-full. The moon is over the screen.",
        "direction_hint": "The patterns are real. They're just not for "
                          "you.",
        "verbs": ["pop_corn", "pour_soda", "watch_screen", "read_static",
                  "ring_bell"],
        "die_faces": [
            ("CLEAR_SIGNAL", "ss", "Success ★★. The pattern resolves."),
            ("READ_IT", "s", "Success ★. You see what it says."),
            ("FUZZY_A", "partial", "Partial. Spend 2 Action cards to convert."),
            ("FUZZY_B", "partial", "Partial. Spend 2 Action cards to convert."),
            ("NOISE", "fail", "Failure. +1 MOONDRIFT."),
            ("MOON_HIGH", "wild", "Wild. ★ if the marquee is lit this turn, else failure."),
        ],
        "visitors": [
            ("the_projectionist", "The Projectionist", "preoccupied"),
            ("a_family_in_a_truck", "A Family in a Truck", "jovial"),
            ("the_kid_alone", "A Kid Alone in Row Three", "gruff"),
        ],
        "piles": {
            "counter": ["ticket_stub", "register_drawer_key", "shift_log"],
            "popcorn": ["popcorn_scoop", "salt_shaker", "kernel_pile"],
            "candy_case": ["candy_box", "case_key", "expired_inventory"],
        },
        "finales": [
            ("read_too_much", "READ TOO MUCH INTO IT"),
            ("the_static_held", "THE STATIC HELD A SHAPE"),
            ("ring_at_close", "RANG THE BELL AT CLOSE"),
        ],
    },
    {
        "key": "sun",
        "title": "THE SUN",
        "scenario": "dust_motes",
        "scenario_title": "DUST MOTES",
        "scenario_subtitle": "Solenade Garden · early afternoon",
        "location": "solenade_garden",
        "hand": "frank",
        "default_space": "central_oak",
        "spaces": ["central_oak", "sundial", "bench_n", "bench_s", "bench_e",
                   "bench_w", "pergola_arch", "flowerbed_ne",
                   "flowerbed_nw", "gate"],
        "tension": {"key": "glare", "label": "GLARE", "max": 10},
        "epigraph_up": "Generosity of light, the warmth that doesn't ask "
                       "anything, the long afternoon that's enough.",
        "epigraph_down": "The light that doesn't relent, the warmth you "
                         "can't keep being grateful for.",
        "scene_description": "The garden is the most generous light in "
                             "the city. Frank's been sitting under the "
                             "oak for two hours. The sundial says so.",
        "direction_hint": "Stay until the shadow moves three hours. Stay "
                          "until you're done.",
        "verbs": ["sit_in_sun", "walk_path", "tend_bed", "read_sundial",
                  "give_seat"],
        "die_faces": [
            ("LONG_LIGHT", "ss", "Success ★★. The afternoon holds."),
            ("WARM_SEAT", "s", "Success ★. You take it easy."),
            ("SHADE_A", "partial", "Partial. Spend 2 Action cards to convert."),
            ("SHADE_B", "partial", "Partial. Spend 2 Action cards to convert."),
            ("GLARE", "fail", "Failure. +1 GLARE."),
            ("OAK_HIGH", "wild", "Wild. ★ if you're under the oak this turn, else failure."),
        ],
        "visitors": [
            ("a_grandfather", "A Grandfather with a Newspaper", "jovial"),
            ("a_dog_off_leash", "A Dog Off Its Leash", "preoccupied"),
            ("a_groundskeeper", "The Groundskeeper", "gruff"),
        ],
        "piles": {
            "sundial": ["bronze_gnomon", "shadow_reading", "noted_hour"],
            "bench_n": ["forgotten_book", "park_map", "lost_glove"],
            "flowerbed_ne": ["pruning_shears", "trowel", "rose_clipping"],
        },
        "finales": [
            ("the_garden_kept_you", "THE GARDEN KEPT YOU"),
            ("you_gave_the_seat", "YOU GAVE THE SEAT"),
            ("the_shadow_moved", "THE SHADOW MOVED"),
        ],
    },
    {
        "key": "judgement",
        "title": "JUDGEMENT",
        "scenario": "everyone_stays",
        "scenario_title": "EVERYONE STAYS",
        "scenario_subtitle": "Parish Cemetery · All Souls' eve",
        "location": "parish_cemetery",
        "hand": "ensemble",
        "default_space": "central_mausoleum",
        "spaces": ["central_mausoleum", "path_spine_n", "path_spine_s",
                   "vault_row_w", "vault_row_e", "vault_row_n",
                   "lamp_central", "oak_sw", "gate"],
        "tension": {"key": "call", "label": "THE CALL", "max": 10},
        "epigraph_up": "The call that's heard, the rising-to, the "
                       "ensemble that turns at the same beat.",
        "epigraph_down": "The call that won't stop, the ensemble that "
                         "won't come together.",
        "scene_description": "All Souls' eve at the parish cemetery. The "
                             "iron gate is half-open. The central "
                             "mausoleum's door is closed. The lamps are "
                             "lit.",
        "direction_hint": "Walk the vaults. Read the names. Say one of "
                          "them out loud.",
        "verbs": ["read_name", "light_candle", "leave_flower", "ring_lamp",
                  "walk_row"],
        "die_faces": [
            ("HEARD", "ss", "Success ★★. The name lands."),
            ("LIT", "s", "Success ★. The candle catches."),
            ("ECHO_A", "partial", "Partial. Spend 2 Action cards to convert."),
            ("ECHO_B", "partial", "Partial. Spend 2 Action cards to convert."),
            ("SILENT", "fail", "Failure. +1 THE CALL."),
            ("FULL_ROW", "wild", "Wild. ★ if you've read three names this turn, else failure."),
        ],
        "visitors": [
            ("the_caretaker", "The Caretaker with a Lantern", "preoccupied"),
            ("a_widow", "A Widow at the Mausoleum", "gruff"),
            ("a_child_with_a_rosary", "A Child with a Rosary", "jovial"),
        ],
        "piles": {
            "central_mausoleum": ["family_bible", "mausoleum_key",
                                   "inscription_brass"],
            "vault_row_w": ["candle_stub", "broken_brass_letter", "moss_patch"],
            "lamp_central": ["lamp_oil", "wick", "matches"],
        },
        "finales": [
            ("everyone_stayed", "EVERYONE STAYED"),
            ("you_said_a_name", "YOU SAID A NAME"),
            ("the_lamp_went_out", "THE LAMP WENT OUT"),
        ],
    },
    {
        "key": "world",
        "title": "THE WORLD",
        "scenario": "loop_completed",
        "scenario_title": "LOOP COMPLETED",
        "scenario_subtitle": "Frog Knows Best · the morning after",
        "location": "frog_knows_best",
        "hand": "tbd_world",
        "default_space": "retail_counter",
        "spaces": ["retail_counter", "minnow_tank", "catfish_tank",
                   "frog_tank", "nightcrawler", "pegboard_w", "pegboard_e",
                   "porch", "front_door"],
        "tension": {"key": "closure", "label": "CLOSURE", "max": 10},
        "epigraph_up": "The cycle completed, the loop closed with "
                       "everything inside it accounted for.",
        "epigraph_down": "Closure that won't take, the loop you can't "
                         "stop checking on.",
        "scene_description": "Frog Knows Best at 7 AM. The tanks are "
                             "running clean. The minnows are alive. The "
                             "frog is on the log. You're the morning "
                             "shift.",
        "direction_hint": "Feed everything. Lock up. Walk out without "
                          "looking back through the screen.",
        "verbs": ["feed_tank", "check_filter", "stock_tackle", "open_porch",
                  "lock_up"],
        "die_faces": [
            ("CLOSED_OK", "ss", "Success ★★. The loop ties off."),
            ("ROUNDS_DONE", "s", "Success ★. You can leave."),
            ("ONE_MORE_A", "partial", "Partial. Spend 2 Action cards to convert."),
            ("ONE_MORE_B", "partial", "Partial. Spend 2 Action cards to convert."),
            ("CHECK_AGAIN", "fail", "Failure. +1 CLOSURE."),
            ("FROG", "wild", "Wild. ★ if the frog is visible this turn, else failure."),
        ],
        "visitors": [
            ("the_morning_customer", "The Morning Customer", "jovial"),
            ("the_owner", "The Owner Phoning In", "gruff"),
            ("a_kid_with_a_jar", "A Kid with a Jar", "preoccupied"),
        ],
        "piles": {
            "retail_counter": ["fish_food_canister", "till_key", "shift_log"],
            "nightcrawler": ["worm_box", "label_tape", "cooler_lid"],
            "pegboard_w": ["lure_red", "lure_yellow", "hook_pack"],
        },
        "finales": [
            ("loop_closed", "THE LOOP CLOSED"),
            ("kept_checking", "YOU KEPT CHECKING"),
            ("walked_out", "WALKED OUT WITHOUT LOOKING BACK"),
        ],
    },
]


# ── EMITTERS ────────────────────────────────────────────────────

def emit_setup(cfg):
    space0 = cfg["default_space"]
    return {
        "id": cfg["scenario"],
        "arcana": cfg["key"],
        "location": cfg["location"],
        "hand": cfg["hand"],
        "title": cfg["scenario_title"],
        "subtitle": cfg["scenario_subtitle"],
        "epigraph_upright": cfg["epigraph_up"],
        "epigraph_reversed": cfg["epigraph_down"],
        "scene_description": cfg["scene_description"],
        "direction_hint": cfg["direction_hint"],
        "opening_log_lines": [
            f"You arrive at {cfg['scenario_subtitle']}.",
            "The pressure starts low. It does not stay low.",
            "Click [b]PHASE: ACTION[/b] anytime for the rules. "
            "Try [b]MOVE ↪[/b] to walk."
        ],
        "starting_state": {
            "player_pos": space0,
            "time": 6,
            "time_per_turn": 6,
            "inertia": 0,
            "inertia_per_turn": 1,
            "sanity": 6,
            "sanity_max": 7,
            # The arcana's "tension" colors the room — but mechanically
            # the engine's universal pressure stat is INERTIA. The
            # tension_* fields below are flavor labels that the UI may
            # surface in place of the word "Inertia"; the engine still
            # ticks inertia under the hood.
            "tension_stat": cfg["tension"]["key"],
            "tension_label": cfg["tension"]["label"],
            "tension_max": cfg["tension"]["max"],
            "starting_hand": ["walk", "focus", "search", "short_rest"]
                + cfg["verbs"][:4]
        },
        "visitors_present_at_start": [],
        "visitor_schedule": [
            {"visitor": cfg["visitors"][0][0], "arrival_turn": 1,
             "arrival_space": cfg["default_space"]},
            {"visitor": cfg["visitors"][1][0], "arrival_turn": 4,
             "arrival_space": cfg["default_space"]},
            {"visitor": cfg["visitors"][2][0], "arrival_turn": 7,
             "arrival_space": cfg["default_space"]},
        ],
        # Win condition is the standard four-corner reach: assemble
        # the bindle, connect ≥3 visitors, stay below inertia cap,
        # land on a threshold space. Per-arcana refinement TODO.
        "win_conditions": {
            "require_bindle_assembled": True,
            "require_visitors_connected_min": 3,
            "require_inertia_below": 7,
            "require_threshold_space": True
        },
        "loss_conditions": {
            "inertia_max": 12,
            "visitors_claimed_max": 3
        },
        # Per-tier inertia track. Numbers + effects mirror the Fool's
        # shape; arcana-flavored labels can be re-written later.
        "inertia_thresholds": [
            {"level": 0,  "label": cfg["tension"]["label"].lower() + " latent",
             "tick_per_turn": 1, "effects": []},
            {"level": 4,  "label": "the room registers you",
             "tick_per_turn": 1, "effects": []},
            {"level": 7,  "label": "the pressure tips",
             "tick_per_turn": 1, "effects": ["gravity_deck_plus_1"]},
            {"level": 8,  "label": "the room presses back",
             "tick_per_turn": 1, "effects": ["claim_closest_unconnected_visitor"]},
            {"level": 10, "label": "the exits look farther",
             "tick_per_turn": 1, "effects": ["claim_next_closest_visitor",
                                               "exit_movement_cost_plus_1"]},
            {"level": 11, "label": "every action costs more",
             "tick_per_turn": 1, "effects": ["action_card_cost_plus_1"]},
            {"level": 12, "label": cfg["finales"][0][1],
             "tick_per_turn": 1, "effects": ["reveal_inertia_finale"]},
        ],
        "claim_turns_to_consume": 2,
        # Three threshold spaces — exit points that satisfy
        # win_conditions.require_threshold_space. Generator picks the
        # last three space ids from the host's SPACE_MAP as defaults;
        # per-locale refinement (which spaces are actually thresholds
        # vs stations) is TODO.
        "thresholds": [
            {"id": cfg["spaces"][-1], "label": cfg["spaces"][-1].upper().replace("_", " "),
             "ending_lore_token": f"leap_from_{cfg['key']}_a",
             "visible_from_start": True},
            {"id": cfg["spaces"][-2], "label": cfg["spaces"][-2].upper().replace("_", " "),
             "ending_lore_token": f"leap_from_{cfg['key']}_b",
             "visible_from_start": True},
            {"id": cfg["spaces"][-3], "label": cfg["spaces"][-3].upper().replace("_", " "),
             "ending_lore_token": f"leap_from_{cfg['key']}_c",
             "visible_from_start": False,
             "appears_when": "visitors_on_board_min:3"},
        ],
        "max_turns": 14,
        "notes": (f"SCAFFOLD setup for {cfg['title']} / {cfg['scenario_title']}. "
                  "Mechanical fields match the Fool's the_leap shape so "
                  "the engine loads cleanly. Per-arcana refinement of "
                  "thresholds / win conditions / tier effects is TODO."),
    }


def emit_action_cards(cfg):
    cards = []
    for vi, v in enumerate(cfg["verbs"]):
        cards.append({
            "id": v,
            "title": v.replace("_", " ").upper(),
            "time_cost": 1 if vi else 0,  # first verb is a 0-cost starter
            "starter": (vi < 2),
            "available_in_locations": [cfg["location"]],
            "flavor": f"({cfg['title']} action — refine later.) "
                      f"Spend 1 Time. Affects the {cfg['tension']['label']} "
                      f"track.",
            "requires": [],
            "effects": [
                {"kind": "gain_time", "amount": 1},
                {"kind": "log",
                 "text": f"{v.replace('_', ' ').upper()} — placeholder beat."},
            ],
        })
    return {
        "scope": cfg["key"],
        "notes": (f"{cfg['title']}-unique action cards. SCAFFOLD — "
                  "card text + effects are placeholder. Author final "
                  "text per the arcana's lore."),
        "cards": cards,
    }


def emit_gravity_deck(cfg):
    cards = []
    tension_key = cfg["tension"]["key"]
    base_titles = [
        "PRESSURE BUILDS",
        "THE ROOM TIGHTENS",
        "SOMETHING SLIPS",
        "THE HOUR HOLDS",
        "AN OLD HABIT RETURNS",
        "THE LIGHT CHANGES",
        "SOMEONE WAS WAITING",
        "TIME LEAKS",
        "A PHONE RINGS UNANSWERED",
        "THE FLOOR REMEMBERS YOU",
        "YOU NOTICE YOU'RE NOTICING",
        f"THE {cfg['tension']['label']} SHIFTS",
    ]
    for ti, t in enumerate(base_titles):
        cards.append({
            "id": f"{cfg['key']}_grav_{ti+1:02d}",
            "title": t,
            "flavor": (f"({cfg['title']} pressure — refine later.) "
                       f"The {cfg['tension']['label'].lower()} ticks."),
            "effects": [
                {"kind": "gain_inertia", "amount": 1},
            ] + ([{"kind": "drain_sanity", "amount": 1}] if ti == 11 else []),
        })
    return {
        "scope": cfg["key"],
        "notes": (f"{cfg['title']} 12-card gravity deck. SCAFFOLD — "
                  "card flavor + per-card effects are placeholder. "
                  "Author final pressure beats per lore."),
        "cards": cards,
    }


def emit_finale(cfg):
    # Engine's finale.triggered_by is "inertia_<N>" matching
    # loss_conditions.inertia_max in the setup file. All 3 finales
    # share the same trigger and are picked by weight.
    finales = []
    for fi, (fid, ftitle) in enumerate(cfg["finales"]):
        finales.append({
            "id": fid,
            "title": ftitle,
            "triggered_by": "inertia_12",
            "weight": 1.0 / len(cfg["finales"]),
            "flavor": f"({cfg['title']} finale — refine later.)",
            "effects": [
                {"kind": "end_game",
                 "outcome": f"reversed_{cfg['key']}"},
            ],
        })
    return {
        "scope": cfg["key"],
        "notes": (f"{cfg['title']} finales. SCAFFOLD — flavor is "
                  "placeholder, but the trigger / outcome wiring is real."),
        "finales": finales,
    }


def emit_die(cfg):
    faces = []
    for fi, (sym, result, desc) in enumerate(cfg["die_faces"]):
        faces.append({
            "face": fi + 1,
            "symbol": sym,
            "result": result,
            "description": desc,
        })
    return {
        "scope": cfg["key"],
        "notes": (f"{cfg['title']}'s six-face arcana die. Replaces the "
                  "default d6 during a Strength/Hermit/etc. run."),
        "die": {
            "id": f"{cfg['key']}_die",
            "title": f"{cfg['title']} Die",
            "faces": faces,
        },
    }


def emit_items(cfg):
    piles = {}
    for pile_id, items in cfg["piles"].items():
        piles[pile_id] = {
            "label": pile_id.replace("_", " ").title(),
            "items": items,
        }
    return {
        "scope": cfg["key"],
        "notes": (f"{cfg['title']} item piles. Each pile lives at the "
                  "named board space. SCAFFOLD — item ids exist; "
                  "per-item effects belong in a future items table."),
        "piles": piles,
    }


def emit_visitors(cfg):
    visitors = []
    for vi, (vid, name, mood) in enumerate(cfg["visitors"]):
        visitors.append({
            "id": vid,
            "name": name,
            "as_hand_id": vid,
            "arrival": {
                "kind": "scheduled",
                "turn": 1 + vi * 3,
                "from": cfg["spaces"][min(vi, len(cfg["spaces"]) - 1)],
                "to": cfg["default_space"],
            },
            "lore_token": f"{vid}_seen",
            "lore_text": f"You see {name}. ({cfg['title']} beat — refine.)",
            "accent": ["#ffa860", "#88c0ff", "#a8e0a8"][vi % 3],
            "placeholder_name": "someone approaching",
            "pre_arrival_hints": [
                f"You sense {name.lower()} is near.",
                "Steps. Or breath. Or the room shifting.",
            ],
            "mood": mood,
            "order_item": None,
            "steps": {
                "greet":   f"You meet eyes with {name}. The room "
                           "registers it.",
                "listen":  f"{name} tells you what they came to tell you.",
                "deliver": f"You give {name} what they were after.",
                "sit_with": f"{name} stays for a beat. You stay back.",
            },
        })
    return {
        "scope": cfg["key"],
        "notes": (f"{cfg['title']} visitors. SCAFFOLD — three visitors "
                  "with the canonical waiter sequence; per-visitor "
                  "step flavor is placeholder."),
        "visitors": visitors,
    }


# ── DRIVER ──────────────────────────────────────────────────────

def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


def main():
    # Marker file the generator drops in each emitted dir. Lets us
    # tell scaffolded-by-this-script dirs apart from hand-authored
    # ones (fool / magician / priestess / etc.) so subsequent re-runs
    # don't trample real content.
    MARKER = ".scaffolded_by_make_arcana_scenarios"
    n_dirs = 0
    n_files = 0
    for cfg in ARCANA:
        out_dir = os.path.join(GAMES, cfg["key"])
        if os.path.exists(out_dir) and not os.path.exists(
                os.path.join(out_dir, MARKER)):
            print(f"  ⚠ {cfg['key']}/ exists and was NOT scaffolded by this "
                  "tool — skipping (refusing to overwrite hand-authored data)")
            continue
        n_dirs += 1
        write(os.path.join(out_dir, "action_cards.json"),
              emit_action_cards(cfg))
        write(os.path.join(out_dir, "gravity_deck.json"),
              emit_gravity_deck(cfg))
        write(os.path.join(out_dir, f"setup_{cfg['scenario']}.json"),
              emit_setup(cfg))
        write(os.path.join(out_dir, "finale.json"), emit_finale(cfg))
        write(os.path.join(out_dir, "die.json"), emit_die(cfg))
        write(os.path.join(out_dir, "items.json"), emit_items(cfg))
        write(os.path.join(out_dir, "visitors.json"), emit_visitors(cfg))
        # Drop the marker so we can safely re-run later.
        with open(os.path.join(out_dir, MARKER), "w") as f:
            f.write("This arcana dir was scaffolded by "
                    "make_arcana_scenarios_2026_06_21.py.\n"
                    "Re-running the script WILL overwrite the seven JSON "
                    "files in this directory.\n"
                    "Once you start writing real content, delete this "
                    "marker file to lock the dir against re-emission.\n")
        n_files += 7
        print(f"  ✓ {cfg['key']}/  (7 files)")
    print(f"\nemitted {n_dirs} arcana dirs, {n_files} JSON files")


if __name__ == "__main__":
    main()
