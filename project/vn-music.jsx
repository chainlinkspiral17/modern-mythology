// ── Music: catalog, heard-tracking, queue picker ──────────────────────────
// Single source of truth for the soundtrack. Loaded by:
//   • Modern Mythology.html (game) — feeds AudioMgr's heard-marking + queue
//   • Gallery.html (Music Room) — feeds the track list + unlock state
//
// Contract:
//   window.MM_MUSIC                  — curated catalog (array of tracks)
//   window.MM_MUSIC_HEARD            — heard set with .get/.has/.mark/.clear
//   window.MM_MUSIC_findEntry(src)   — catalog lookup by src
//   window.MM_MUSIC_buildTrackForSrc(src) — entry for any src (heard fallback)
//   window.MM_MUSIC_pickNext(currentSrc, opts) — next track id for the queue
//   window.MM_MUSIC_inferVol(src)    — extract vol number from filename
//   window.MM_MUSIC_humanizeTitle(s) — pretty title from filename
//
// Heard set is persisted to localStorage at key `mm_music_heard` and shared
// across the game + Music Room. It is *not* tied to a particular save slot:
// once you've heard a track, it stays unlocked.

// ── Curated catalog (mirrors godot/resources/music_catalog.json) ─────────
// Each entry: { id, vol, title, src, composer, desc, unlock, [chars], [chapters] }
//   chars:    character keys — showing one unlocks the track (AudioMgr.unlock_tracks_for_character)
//   chapters: scene ids whose bgm nodes play this src (GameEngine chapter context + unlock)
//   unlock: { type:'heard' }   → appears once played in-game (default)
//           { type:'always' }  → always visible, even before heard
//           { type:'key', key }  → gated on SaveSystem.is_unlocked(key)
//           { type:'flag', key } → legacy: unlocks via save flag
const MM_MUSIC = [
  // ── Title & credits ──────────────────────────────────────────────────
  { id:"credits_theme", vol:0, title:"Credits — Modern Mythology", src:"assets/audio/bgm/credits_theme.ogg",
    composer:"—", desc:"End-of-volume credits theme. The first pad of title_theme returning slower, lower, resolved.", unlock:{"type": "key", "key": "music:credits_theme"}, chapters:["credits"] },
  { id:"title_theme", vol:0, title:"Modern Mythology", src:"assets/audio/bgm/title_theme.ogg",
    composer:"—", desc:"The theme that plays at the beginning of everything.", unlock:{"type": "key", "key": "music:title_theme"} },

  // ── Vol 1 · Faust 3 ──────────────────────────────────────────────────
  { id:"vol1_ambient", vol:1, title:"The Diner at the Crossroads", src:"assets/audio/bgm/vol1_ambient.mp3",
    composer:"—", desc:"The diner. The stranger. The choice that starts everything.", unlock:{"type": "heard"}, chars:["stranger", "_narrator"], chapters:["vol1_ch16_four_am", "vol1_ch17_editing_suite", "vol1_ch2_act_one", "vol1_ch5_morning", "vol1_ch6_office", "vol1_ch7_joan", "meld_kaleidoscope_b", "vol4_curtain_call"] },
  { id:"vol1_club_thump", vol:1, title:"The Underworld", src:"assets/audio/bgm/vol1_club_thump.mp3",
    composer:"—", desc:"Intercut. Dancing. Loud music.", unlock:{"type": "heard"}, chapters:["vol1_ch13_deep_end", "vol1_ch3_club", "vol1_ch8_triumvirate", "vol1_ch9_street", "vol4_cc_3", "vol4_cc_5"] },
  { id:"vol1_diner_ambient", vol:1, title:"The Missing Link", src:"assets/audio/bgm/vol1_diner_ambient.mp3",
    composer:"—", desc:"Bus depot. Rain. No clock.", unlock:{"type": "heard"}, chapters:["vol1_ch11_aisles", "vol1_ch11_drugstore", "vol1_missing_link", "vol2_ch8_apple_peddler", "meld_kaleidoscope_c"] },
  { id:"vol1_dream_drone", vol:1, title:"Dream States", src:"assets/audio/bgm/vol1_dream_drone.mp3",
    composer:"—", desc:"Faust's bedroom. The room behind the room.", unlock:{"type": "heard"}, chapters:["vol1_ch12_history", "vol1_ch14_painting", "vol1_ch4_dream_states", "vol1_ch6_tutorial", "vol1_ch8_club", "meld_seam_1_2"] },
  { id:"vol1_drive_night", vol:1, title:"Driving Around · Night", src:"assets/audio/bgm/vol1_drive_night.mp3",
    composer:"—", desc:"EXT. Judgement Day. Headlights, then more headlights.", unlock:{"type": "heard"}, chapters:["vol1_ch10_longboat", "vol1_ch15_river_turn", "vol1_ch3_judgement_day"] },
  { id:"vol1_faust_theme", vol:1, title:"Faust III", src:"assets/audio/bgm/vol1_faust_theme.ogg",
    composer:"—", desc:"An echo of Sharp's bass but warmer — the same world from another mouth. Faust's signature.", unlock:{"type": "heard"}, chars:["faust3"] },
  { id:"vol1_milestone_choice", vol:1, title:"The Choice (resolved)", src:"assets/audio/bgm/vol1_milestone_choice.ogg",
    composer:"—", desc:"Released when Vol 1's central choice is committed. A held breath finally let out.", unlock:{"type": "key", "key": "milestone:vol1_choice"}, chapters:[] },
  { id:"vol1_painting", vol:1, title:"The Painting", src:"assets/audio/bgm/vol1_painting.ogg",
    composer:"—", desc:"A slow oil-tone pad. The painting that knows you saw it.", unlock:{"type": "heard"}, chapters:[] },
  { id:"vol1_pharmacy", vol:1, title:"The Pharmacy Mirror", src:"assets/audio/bgm/vol1_pharmacy.ogg",
    composer:"—", desc:"Pharmacy fluorescent buzz. The mirror that doesn't quite reflect right.", unlock:{"type": "heard"}, chapters:[] },
  { id:"vol1_sharp_theme", vol:1, title:"Sharp", src:"assets/audio/bgm/vol1_sharp_theme.ogg",
    composer:"—", desc:"Low bass swell, basement amp buzz. Sharp's signature, played whenever Sharp shows up.", unlock:{"type": "heard"}, chars:["sharp"] },
  { id:"vol1_stranger_theme", vol:1, title:"The Stranger", src:"assets/audio/bgm/vol1_stranger_theme.ogg",
    composer:"—", desc:"A single sustained tone in the upper register. The Stranger arrives at the booth.", unlock:{"type": "heard"}, chars:["stranger"] },
  { id:"vol1_title", vol:1, title:"Crossroads · Title", src:"assets/audio/bgm/vol1_title.mp3",
    composer:"—", desc:"Volume 1 title card. Warm pad + radio hush. The full deck has not yet been dealt.", unlock:{"type": "heard"}, chapters:[] },
  { id:"vol1_drive_day", vol:1, title:"Driving Around · Day", src:"assets/audio/bgm/vol1_drive_day.mp3",
    composer:"—", desc:"INT. Judgement Day · Day. Sun on the windshield, the radio stuck between stations.", unlock:{"type": "heard"}, chars:[], chapters:["vol1_ch6_judgement_day"] },

  // ── Vol 2 · Small Wood Volumes ───────────────────────────────────────
  { id:"vol2_ambient", vol:2, title:"Small Wood Variations", src:"assets/audio/bgm/vol2_ambient.mp3",
    composer:"—", desc:"The sound of trees that have been standing longer than the town.", unlock:{"type": "heard"}, chars:["lena"], chapters:["meld_seam_1_2", "vol2_ch10_salmon", "vol2_ch10_spawning_grounds", "vol2_ch11_dickens_dean", "vol2_ch12_drift_wood_intro", "vol2_ch1_history_one", "vol2_ch3_points_of_impact", "vol2_ch3_rewind", "vol2_ch4_lighthouse", "vol2_ch4_night_lights", "vol2_ch5_egretta", "vol2_ch5_lessons_in_leaves", "vol2_ch6_mayhune", "vol2_ch6_sacrificial_pair", "vol2_ch6_triptych", "vol2_ch7_scumm_d", "vol2_ch8_apple_peddler", "vol2_ch8_stories", "vol2_ch9_flotsam", "vol2_ch9_truck", "vol2_title", "meld_kaleidoscope_f"] },
  { id:"vol2_briar_falls_night", vol:2, title:"Briar Falls · After Dark", src:"assets/audio/bgm/vol2_briar_falls_night.ogg",
    composer:"—", desc:"Pine-wind drone, owl on a far ridge. Late at Briar Falls.", unlock:{"type": "heard"}, chapters:[] },
  { id:"vol2_graveyard_solo", vol:2, title:"The Graveyard", src:"assets/audio/bgm/vol2_graveyard_solo.ogg",
    composer:"—", desc:"A single low pad, no field-recording layer. The quietest track in Vol 2.", unlock:{"type": "heard"}, chapters:[] },
  { id:"vol2_lena_theme", vol:2, title:"Lena", src:"assets/audio/bgm/vol2_lena_theme.ogg",
    composer:"—", desc:"Acoustic guitar single-note phrase, repeated, mid-period Mark Hollis register. Lena's signature.", unlock:{"type": "heard"}, chars:["lena"] },
  { id:"vol2_milestone_seagash", vol:2, title:"Seagash, Closed", src:"assets/audio/bgm/vol2_milestone_seagash.ogg",
    composer:"—", desc:"Released when the Seagash mystery's last interlude resolves.", unlock:{"type": "key", "key": "milestone:vol2_seagash"}, chapters:[] },
  { id:"vol2_rest_stop_wind", vol:2, title:"Rest Stop · Wind", src:"assets/audio/bgm/vol2_rest_stop_wind.mp3",
    composer:"—", desc:"Briar Falls. Mid-nineties. Twelve hours from anywhere.", unlock:{"type": "heard"}, chapters:["vol2_briar_falls_interlude", "vol2_ch11_terminal_velocity", "vol2_ch6_watcher", "vol3_ch7_emulsion"] },
  { id:"vol2_seagash_drone", vol:2, title:"The Siren of Seagash", src:"assets/audio/bgm/vol2_seagash_drone.mp3",
    composer:"—", desc:"A history, with interludes.", unlock:{"type": "heard"}, chapters:["vol2_ch10_salmon", "vol2_ch2_seagash", "vol2_ch3_points_of_impact", "vol2_ch4_lighthouse", "vol2_ch6_ark", "vol2_ch6_watcher", "vol2_ch9_art_class", "vol2_ch9_truck", "meld_kaleidoscope_f"] },
  { id:"vol2_scumm_adlib", vol:2, title:"Sixteen Colors", src:"assets/audio/bgm/vol2_scumm_adlib.mp3",
    composer:"—", desc:"Dream journal, 1994. A point-and-click nightmare on a cheap FM sound card; the cursor never stops blinking.", unlock:{"type": "heard"}, chars:[], chapters:["vol2_ch7_scumm_a", "vol2_ch7_scumm_b", "vol2_ch7_scumm_c", "vol2_ch7_scumm_d", "meld_kaleidoscope_c", "meld_kaleidoscope_f"] },

  // ── Vol 3 · The Earthman Chronicles ──────────────────────────────────
  { id:"vol3_ambient", vol:3, title:"The Father's House", src:"assets/audio/bgm/vol3_ambient.mp3",
    composer:"—", desc:"Vol 3 bed · The Earthman Chronicles. Pulp static from 1945 over a 2003 Pasadena night; a Texas hospital at the edge of hearing.", unlock:{"type": "heard"}, chars:["andy"], chapters:[] },
  { id:"vol3_antonio_theme", vol:3, title:"Antonio", src:"assets/audio/bgm/vol3_antonio_theme.ogg",
    composer:"—", desc:"Single piano figure on the upbeat, returning each time the call doesn't connect.", unlock:{"type": "heard"}, chars:["antonio"] },
  { id:"vol3_call_drop", vol:3, title:"The Call Drops", src:"assets/audio/bgm/vol3_call_drop.ogg",
    composer:"—", desc:"Antonio mid-sentence, the line going hollow. A single note holding for too long.", unlock:{"type": "heard"}, chars:["antonio"], chapters:[] },
  { id:"vol3_milestone_choice", vol:3, title:"Decompression", src:"assets/audio/bgm/vol3_milestone_choice.ogg",
    composer:"—", desc:"Released when Vol 3's choice resolves. The pressure equalizes.", unlock:{"type": "key", "key": "milestone:vol3_choice"}, chapters:[] },
  { id:"vol3_tobor_theme", vol:3, title:"Tobor", src:"assets/audio/bgm/vol3_tobor_theme.ogg",
    composer:"—", desc:"Metallic resonator + held vacuum hum. The robot's signature.", unlock:{"type": "heard"}, chars:["tobor"] },
  { id:"vol3_radio_1945", vol:3, title:"Wireless, Pasadena 1945", src:"assets/audio/bgm/vol3_radio_1945.mp3",
    composer:"—", desc:"A tube set warming up in Ron's room. Dance-band ghosts under the static; the war just over.", unlock:{"type": "heard"}, chars:["ron"], chapters:["meld_seam_2_3", "vol3_ch10_notes_from_the_underground", "vol3_ch19_ron_takes_notes"] },
  { id:"vol3_signal_drone", vol:3, title:"The Transmission", src:"assets/audio/bgm/vol3_signal_drone.mp3",
    composer:"—", desc:"The ruined-future carrier wave. The time pod humming between 1945 and now.", unlock:{"type": "heard"}, chars:[], chapters:["meld_seam_2_3", "vol3_ch12_uncle_nick", "vol3_ch13_sins_of_our_fathers", "vol3_ch14_last_of_the_oil_men", "vol3_ch1_boy_from_pasadena", "vol3_ch2_dreams_in_the_key_of_godhead", "vol3_ch8_passengers", "vol3_ch8_passengers_b", "vol3_ch8_passengers_c", "vol3_ch8_pulp_the_catwalk", "vol3_ch9_backward_jaunt", "vol3_title"] },
  { id:"vol3_projector_hum", vol:3, title:"Slide Carousel", src:"assets/audio/bgm/vol3_projector_hum.mp3",
    composer:"—", desc:"Tulsa, mid-eighties. Projector fan, the clack of the next slide, a family safari on a bedsheet.", unlock:{"type": "heard"}, chars:[], chapters:["meld_seam_2_3", "vol3_ch3_safari"] },
  { id:"vol3_texas_summer", vol:3, title:"Last Weekend of Summer", src:"assets/audio/bgm/vol3_texas_summer.mp3",
    composer:"—", desc:"Texas after rain. Strip-mall sodium light, lake-house cicadas before dawn.", unlock:{"type": "heard"}, chars:[], chapters:["vol3_ch11_acceptable_losses", "vol3_ch11_acceptable_losses_b", "vol3_ch11_acceptable_losses_c"] },
  { id:"vol3_club_pulse", vol:3, title:"Friday, 1 A.M.", src:"assets/audio/bgm/vol3_club_pulse.mp3",
    composer:"—", desc:"Industrial downtown. A kick drum through two walls; the body keeping time the mind won't.", unlock:{"type": "heard"}, chars:[], chapters:["vol3_ch11_acceptable_losses_c", "vol3_ch13_sins_of_our_fathers", "vol3_ch8_passengers", "vol3_ch8_passengers_b"] },
  { id:"vol3_hospital_hum", vol:3, title:"Houston, After Hours", src:"assets/audio/bgm/vol3_hospital_hum.mp3",
    composer:"—", desc:"The ward at night. Monitor pips, air handlers, a father asleep. The pulp ward is the same room.", unlock:{"type": "heard"}, chars:[], chapters:["vol3_ch11_pulp_the_room_with_birds", "vol3_ch5_md_anderson", "vol3_ch5_pulp_the_ward", "meld_kaleidoscope_b", "meld_kaleidoscope_e", "meld_seam_3_4"] },
  { id:"vol3_ambient_home", vol:3, title:"Home, Now", src:"assets/audio/bgm/vol3_ambient_home.mp3",
    composer:"—", desc:"Uncle Nick at the house. Refrigerator, wall clock, a screen door that won't latch.", unlock:{"type": "heard"}, chars:[], chapters:["vol3_ch12_uncle_nick", "vol3_ch12_uncle_nick_b"] },
  { id:"vol3_pulp_theme", vol:3, title:"Earthman!", src:"assets/audio/bgm/vol3_pulp_theme.mp3",
    composer:"—", desc:"Forties serial fanfare worn to a whisper. Jack Perkins, the time pod, the boy from Pasadena.", unlock:{"type": "heard"}, chars:["betty", "jack_parsons"], chapters:["vol3_ch17_pulp_earthman", "vol3_ch2_dreams_in_the_key_of_godhead", "vol3_ch2_second_set_of_eyes"] },
  { id:"vol3_backyard_night", vol:3, title:"Backyard, Tulsa Night", src:"assets/audio/bgm/vol3_backyard_night.mp3",
    composer:"—", desc:"Crickets, a sprinkler ticking over, two boys out past the porch light.", unlock:{"type": "heard"}, chars:["niles", "marty"], chapters:["vol3_ch3_safari"] },
  { id:"vol3_eight_track_twang", vol:3, title:"Eight-Track Twang", src:"assets/audio/bgm/vol3_eight_track_twang.mp3",
    composer:"—", desc:"The back room, four screens. A country cartridge clunking over to the next program mid-song.", unlock:{"type": "heard"}, chars:[], chapters:["vol3_ch4_four_screens"] },
  { id:"vol3_neon_drift", vol:3, title:"Names in Neon", src:"assets/audio/bgm/vol3_neon_drift.mp3",
    composer:"—", desc:"Now. Invitations, a stranger's bathroom, the coast. A synth pad under buzzing tubes.", unlock:{"type": "heard"}, chars:["april"], chapters:["vol3_ch4_four_screens", "vol3_ch4_invitation_only", "vol3_ch4_names_in_neon", "vol3_ch4_the_coast"] },
  { id:"vol3_coast_radio", vol:3, title:"Coast Radio", src:"assets/audio/bgm/vol3_coast_radio.mp3",
    composer:"—", desc:"Weeks later, the Pacific. A car radio losing its station to the surf.", unlock:{"type": "heard"}, chars:[], chapters:["vol3_ch4_the_coast"] },
  { id:"vol3_signal_ambient", vol:3, title:"Non-Stop Flights", src:"assets/audio/bgm/vol3_signal_ambient.mp3",
    composer:"—", desc:"LAX to Oregon. Cabin pressure, engine drone, the stacks at altitude.", unlock:{"type": "heard"}, chars:[], chapters:["vol3_ch5_non_stop_flights", "vol3_ch6_stacks"] },
  { id:"vol3_suburban_hum", vol:3, title:"Saturday, Noon", src:"assets/audio/bgm/vol3_suburban_hum.mp3",
    composer:"—", desc:"Suburbia. Mowers three yards over, a TV through a screen door, four sleepers on one signal.", unlock:{"type": "heard"}, chars:[], chapters:["vol3_ch8_passengers_b", "vol3_ch8_passengers_c"] },

  // ── Vol 4 · Scraps (back-matter desk) ────────────────────────────────
  { id:"vol4_ambient", vol:4, title:"Five AM at the Desk", src:"assets/audio/bgm/vol4_ambient.mp3",
    composer:"—", desc:"Vol 4 bed · the back-matter desk at dawn. Copier cooling, red string on cork, the city not up yet.", unlock:{"type": "heard"}, chars:["_narrator"], chapters:[] },
  { id:"vol4_dante_theme", vol:4, title:"Dante D'Ambrosio", src:"assets/audio/bgm/vol4_dante_theme.ogg",
    composer:"—", desc:"A bowed double-bass note held until the bow leaves the string. The father.", unlock:{"type": "heard"}, chars:["dante"] },
  { id:"vol4_milestone_standoff", vol:4, title:"The Standoff (resolved)", src:"assets/audio/bgm/vol4_milestone_standoff.ogg",
    composer:"—", desc:"Released when the Vol 4 standoff resolves. The room finally lets you sit down.", unlock:{"type": "key", "key": "milestone:vol4_standoff"}, chapters:[] },
  { id:"vol4_nicola_theme", vol:4, title:"Nicola", src:"assets/audio/bgm/vol4_nicola_theme.ogg",
    composer:"—", desc:"A short three-note descending figure on a detuned upright piano. Nicola's signature.", unlock:{"type": "heard"}, chars:["nicola"] },
  { id:"vol4_standoff_strings", vol:4, title:"Five AM Strings", src:"assets/audio/bgm/vol4_standoff_strings.ogg",
    composer:"—", desc:"A single sustained note from a Lo-fi taped cello at the climax of the standoff.", unlock:{"type": "heard"}, chars:["nicola", "dante"], chapters:[] },
  { id:"vol4_radio_static", vol:4, title:"Between Stations", src:"assets/audio/bgm/vol4_radio_static.mp3",
    composer:"—", desc:"Scrapbook radio. An intersection under street lights, the dial never landing.", unlock:{"type": "heard"}, chars:[], chapters:["meld_kaleidoscope_a", "meld_kaleidoscope_d", "vol4_story_chimes", "vol4_story_cracked_and_broken"] },
  { id:"vol4_photocopier_drone", vol:4, title:"Generation Loss", src:"assets/audio/bgm/vol4_photocopier_drone.mp3",
    composer:"—", desc:"Copy shop, issue six. The platen light sweeping; every copy a little further from the first.", unlock:{"type": "heard"}, chars:[], chapters:["meld_kaleidoscope_d", "meld_seam_3_4", "vol4_story_agwat", "vol4_story_liquid_pour", "vol4_story_nothing_doing", "vol4_story_ps", "vol4_story_rescue_ranger", "vol4_story_wits_end"] },
  { id:"vol4_city_pulse", vol:4, title:"Map of the City", src:"assets/audio/bgm/vol4_city_pulse.mp3",
    composer:"—", desc:"Sun high, traffic as a pulse. The zine's city drawn from memory.", unlock:{"type": "heard"}, chars:[], chapters:["meld_kaleidoscope_d", "vol4_story_map_of_the_city"] },
  { id:"vol4_cabin_hum", vol:4, title:"Everyday in November", src:"assets/audio/bgm/vol4_cabin_hum.mp3",
    composer:"—", desc:"A blog post in transit. Airliner cabin hum, a reading light, nowhere yet.", unlock:{"type": "heard"}, chars:[], chapters:["meld_kaleidoscope_e", "vol4_story_everyday_in_november"] },
  { id:"vol4_beach_wind", vol:4, title:"Low Tide, Four A.M.", src:"assets/audio/bgm/vol4_beach_wind.mp3",
    composer:"—", desc:"A beach-house day care in the morning; one image at low tide. Wind across an open mic.", unlock:{"type": "heard"}, chars:[], chapters:["meld_kaleidoscope_g", "vol4_story_workinp"] },
  { id:"vol4_xerox_hum", vol:4, title:"Scraps", src:"assets/audio/bgm/vol4_xerox_hum.mp3",
    composer:"—", desc:"The desk after midnight. Copier idling, tube light buzzing, scissors and staples: the zine table Vol 4 is pinned to.", unlock:{"type": "heard"}, chars:[], chapters:["meld_seam_3_4", "vol4_board", "vol4_cc_6", "vol4_story_all_over_town", "vol4_story_angry_fog", "vol4_story_betterment_a", "vol4_story_betterment_b", "vol4_story_heavy_breathing", "vol4_story_jack_of_suede", "vol4_story_looking_forward_most", "vol4_story_ourobouros", "vol4_story_seem", "vol4_story_the_wasted_sentiment", "vol4_story_voices_in_a_crowded_room", "vol4_story_what_sort_of", "vol4_title"] },
  { id:"vol4_por_puesto_night", vol:4, title:"Por Puesto", src:"assets/audio/bgm/vol4_por_puesto_night.mp3",
    composer:"—", desc:"The corkboard's last pin. A Caracas jitney idling at night, two short and one long on the horn, a bolero leaking from the dash.", unlock:{"type": "heard"}, chars:[], chapters:["vol4_board"] },
  { id:"vol4_cc_ambient", vol:4, title:"Charlie & Caroline", src:"assets/audio/bgm/vol4_cc_ambient.mp3",
    composer:"—", desc:"The bus, the apartment, the sister's house, the couch. Two people in a screenplay that won't end.", unlock:{"type": "heard"}, chars:["charlie", "caroline"], chapters:["vol4_cc_1", "vol4_cc_2", "vol4_cc_4", "vol4_cc_5"] },
  { id:"vol4_glass_tower", vol:4, title:"Glass Tower on the Pacific", src:"assets/audio/bgm/vol4_glass_tower.mp3",
    composer:"—", desc:"Daddy. Monitors on in a tower over the water; the Dean house one late night.", unlock:{"type": "heard"}, chars:["esther"], chapters:["vol4_daddy_a", "vol4_daddy_b", "vol4_daddy_c"] },
  { id:"vol4_machine_hum", vol:4, title:"The Machine", src:"assets/audio/bgm/vol4_machine_hum.mp3",
    composer:"—", desc:"The office after hours. Fans, the star key, static electric. Always now.", unlock:{"type": "heard"}, chars:[], chapters:["vol4_story_209", "vol4_story_paper_cuts", "vol4_story_static_electric"] },
  { id:"vol4_chiptune_loop", vol:4, title:"Last Quarters", src:"assets/audio/bgm/vol4_chiptune_loop.mp3",
    composer:"—", desc:"Arcade, Caltech halls, the SCUMM addendum. A square-wave attract loop on a cabinet left on.", unlock:{"type": "heard"}, chars:[], chapters:["vol4_story_caltech", "vol4_story_scumm", "vol4_story_two_player"] },
  { id:"vol4_fridge_hum", vol:4, title:"Hit a Wall", src:"assets/audio/bgm/vol4_fridge_hum.mp3",
    composer:"—", desc:"Chess's kitchen, four p.m., waking hours. A refrigerator compressor and nothing else.", unlock:{"type": "heard"}, chars:[], chapters:["vol4_story_hit_a_wall"] },
  { id:"vol4_classroom_hum", vol:4, title:"In/Flux", src:"assets/audio/bgm/vol4_classroom_hum.mp3",
    composer:"—", desc:"A Texas middle school: before the bell, between periods, after lunch.", unlock:{"type": "heard"}, chars:[], chapters:["vol4_story_influx_a", "vol4_story_influx_b", "vol4_story_influx_c"] },

  // ── Vol 5 · Major Arcana (incl. prelude) ─────────────────────────────
  { id:"vol5_alberto_theme", vol:5, title:"Alberto · Sunglasses Indoors", src:"assets/audio/bgm/vol5_alberto_theme.ogg",
    composer:"—", desc:"Bowed cello single note, dampened. The grieving son.", unlock:{"type": "heard"}, chars:["alberto"] },
  { id:"vol5_ambient", vol:5, title:"D'Ambrosio's at Dawn", src:"assets/audio/bgm/vol5_ambient.ogg",
    composer:"—", desc:"Open 24 hours. Technically.", unlock:{"type": "heard"}, chars:["john", "_narrator"], chapters:["vol5_ch0_booth6", "vol5_ch0_frasier", "vol5_ch0_model_city", "vol5_ch0_closing"] },
  { id:"vol5_anya_theme", vol:5, title:"Anya · The Recording", src:"assets/audio/bgm/vol5_anya_theme.ogg",
    composer:"—", desc:"Found-tape hiss + an almost-melody just under the noise floor. Anya's signature.", unlock:{"type": "heard"}, chars:["anya_recording"] },
  { id:"vol5_bbs_caller_theme", vol:5, title:"Sysop · ember.ash.rest.bbs", src:"assets/audio/bgm/vol5_bbs_caller_theme.ogg",
    composer:"—", desc:"Modem handshake + low fluorescent buzz.", unlock:{"type": "heard"}, chars:["bbs_caller"] },
  { id:"vol5_bus_kid_theme", vol:5, title:"The Bus Kid", src:"assets/audio/bgm/vol5_bus_kid_theme.ogg",
    composer:"—", desc:"A bright wood-block tap + a smile of brass. The helper's signature.", unlock:{"type": "heard"}, chars:["bus_kid"] },
  { id:"vol5_cicadas_dusk", vol:5, title:"Cicadas at Dusk", src:"assets/audio/bgm/vol5_cicadas_dusk.ogg",
    composer:"—", desc:"Chapter II — The High Priestess.", unlock:{"type": "heard"}, chars:["elicia"], chapters:["vol5_ch2_priestess", "vol5_ch2_priestess_b", "vol5_ch5_hierophant", "vol5_prelude_arcana_liar_king"] },
  { id:"vol5_elicia_theme_solo", vol:5, title:"Elicia · Tape Reel", src:"assets/audio/bgm/vol5_elicia_theme_solo.ogg",
    composer:"—", desc:"Cassette-spool noise + a soft sustained voice-tone (no vocal). Elicia's signature.", unlock:{"type": "heard"}, chars:["elicia"] },
  { id:"vol5_frasier_theme_solo", vol:5, title:"Frasier · Notebook", src:"assets/audio/bgm/vol5_frasier_theme_solo.ogg",
    composer:"—", desc:"The pen scratch behind the warehouse drone — distinct from the chapter ambient.", unlock:{"type": "heard"}, chars:["frasier"] },
  { id:"vol5_gauntlet_loss", vol:5, title:"Twenty-Four Hours (reversed)", src:"assets/audio/bgm/vol5_gauntlet_loss.ogg",
    composer:"—", desc:"Released the first time you lose any Tarot Gauntlet scenario.", unlock:{"type": "key", "key": "milestone:gauntlet_loss"} },
  { id:"vol5_gauntlet_win", vol:5, title:"The Leap (won)", src:"assets/audio/bgm/vol5_gauntlet_win.ogg",
    composer:"—", desc:"Released the first time you win any Tarot Gauntlet scenario.", unlock:{"type": "key", "key": "milestone:gauntlet_win"} },
  { id:"vol5_john_theme", vol:5, title:"John Frank", src:"assets/audio/bgm/vol5_john_theme.ogg",
    composer:"—", desc:"An apron-tied phrase: a single mid-range pad, a slow heartbeat below. John's signature.", unlock:{"type": "heard"}, chars:["john"] },
  { id:"vol5_line_cook_theme", vol:5, title:"The Line Cook", src:"assets/audio/bgm/vol5_line_cook_theme.ogg",
    composer:"—", desc:"Heat-vent hum + a single brass bell strike at the start. The cook's signature.", unlock:{"type": "heard"}, chars:["line_cook"] },
  { id:"vol5_mackenzie_theme", vol:5, title:"Mackenzie · Receiver", src:"assets/audio/bgm/vol5_mackenzie_theme.ogg",
    composer:"—", desc:"Phone-line static + a single piano left-hand figure.", unlock:{"type": "heard"}, chars:["mackenzie"] },
  { id:"vol5_maya_theme", vol:5, title:"Maya · The Trick", src:"assets/audio/bgm/vol5_maya_theme.ogg",
    composer:"—", desc:"Music-box loop, ten seconds long, slightly varied each pass.", unlock:{"type": "heard"}, chars:["maya_kid"] },
  { id:"vol5_milestone_bindle", vol:5, title:"The Bindle", src:"assets/audio/bgm/vol5_milestone_bindle.ogg",
    composer:"—", desc:"Released the first time you successfully assemble the Bindle in THE LEAP.", unlock:{"type": "key", "key": "milestone:bindle_assembled"} },
  { id:"vol5_noon_room_room", vol:5, title:"Noon Room Room", src:"assets/audio/bgm/vol5_noon_room_room.ogg",
    composer:"—", desc:"Tarot Gauntlet · Lunch Service jukebox B-side. Lake Charles accordion, brass-mic'd dance-floor sound.", unlock:{"type": "heard"}, chars:[], chapters:[] },
  { id:"vol5_riverboat_drone", vol:5, title:"Static Bloom", src:"assets/audio/bgm/vol5_riverboat_drone.ogg",
    composer:"—", desc:"Chapter III — The Empress.", unlock:{"type": "heard"}, chars:["nicola", "dante"], chapters:["vol5_ch3_empress", "vol5_ch4_emperor"] },
  { id:"vol5_the_demon_theme", vol:5, title:"The Man at the Bar", src:"assets/audio/bgm/vol5_the_demon_theme.ogg",
    composer:"—", desc:"A cold sine pad about a half-step out of tune with everything around it.", unlock:{"type": "heard"}, chars:["the_demon"] },
  { id:"vol5_warehouse_drone", vol:5, title:"Cathedral of Rust and Code", src:"assets/audio/bgm/vol5_warehouse_drone.ogg",
    composer:"—", desc:"Chapter I — The Magician.", unlock:{"type": "heard"}, chars:["frasier", "the_demon"], chapters:["vol5_ch1_magician"] },
  { id:"vol5_where_the_bar_used_to_be", vol:5, title:"Where the Bar Used to Be", src:"assets/audio/bgm/vol5_where_the_bar_used_to_be.ogg",
    composer:"—", desc:"Tarot Gauntlet · Evening Service jukebox B-side. Solo after-hours piano recorded in the diner in 1979.", unlock:{"type": "heard"}, chars:[], chapters:[] },
  { id:"vol5_birdwatcher_theme", vol:5, title:"The Bird-Watcher", src:"assets/audio/bgm/vol5_birdwatcher_theme.ogg",
    composer:"—", desc:"Chair creak + binocular-strap rustle + a slow patient exhale. The watcher's signature.", unlock:{"type": "heard"}, chars:["the_birdwatcher"] },
  { id:"vol5_blow_out_the_candles", vol:5, title:"Blow Out the Candles", src:"assets/audio/bgm/vol5_blow_out_the_candles.ogg",
    composer:"—", desc:"Tarot Gauntlet · Magician · hard-mode B-side. Full moon over the river, the bank making a noise the bank should not be making, candle hiss, distant rager house-party low end. 11:47 PM.", unlock:{"type": "heard"}, chars:[], chapters:[] },
  { id:"vol5_college_friend_theme", vol:5, title:"The College Friend", src:"assets/audio/bgm/vol5_college_friend_theme.ogg",
    composer:"—", desc:"An old laugh, far in the back of the cathedral. The kind that remembers the year you stopped speaking.", unlock:{"type": "heard"}, chars:["the_college_friend"] },
  { id:"vol5_critic_theme", vol:5, title:"The Critic", src:"assets/audio/bgm/vol5_critic_theme.ogg",
    composer:"—", desc:"Pen-on-notebook scratch + a single sharp inhale through the nose. No music underneath.", unlock:{"type": "heard"}, chars:["the_critic"] },
  { id:"vol5_demon_filly", vol:5, title:"Filly (demon)", src:"assets/audio/bgm/vol5_demon_filly.ogg",
    composer:"—", desc:"A young horse's exhale. A hoof on wood, once. Then waiting. The Filly demon's room-tone.", unlock:{"type": "heard"} },
  { id:"vol5_demon_husk", vol:5, title:"Husk (demon)", src:"assets/audio/bgm/vol5_demon_husk.ogg",
    composer:"—", desc:"Hollow corn rasp. Dry rustle. The sound of nothing left inside the case.", unlock:{"type": "heard"} },
  { id:"vol5_demon_moth", vol:5, title:"Moth (demon)", src:"assets/audio/bgm/vol5_demon_moth.ogg",
    composer:"—", desc:"Paper-against-bulb flutter. A glass tap. One high whistling overtone that doesn't resolve.", unlock:{"type": "heard"} },
  { id:"vol5_demon_starling", vol:5, title:"Starling (demon)", src:"assets/audio/bgm/vol5_demon_starling.ogg",
    composer:"—", desc:"Many small wings. No melody. The whole flock turning the same instant.", unlock:{"type": "heard"} },
  { id:"vol5_demon_steamboat", vol:5, title:"Steamboat (demon)", src:"assets/audio/bgm/vol5_demon_steamboat.ogg",
    composer:"—", desc:"A small paddle-wheel micro-loop in the room — not the river version. This is the one Frasier is building on the workbench, and the texture is wrong.", unlock:{"type": "heard"} },
  { id:"vol5_demon_vagrant", vol:5, title:"Vagrant (demon)", src:"assets/audio/bgm/vol5_demon_vagrant.ogg",
    composer:"—", desc:"Low rumble + slow shuffle of bags + distant radio static. The Vagrant demon's drift through the room.", unlock:{"type": "heard"} },
  { id:"vol5_demon_weir", vol:5, title:"Weir (demon)", src:"assets/audio/bgm/vol5_demon_weir.ogg",
    composer:"—", desc:"Water under boards. Pressure building behind a thing about to spill.", unlock:{"type": "heard"} },
  { id:"vol5_drifter_theme", vol:5, title:"The Drifter", src:"assets/audio/bgm/vol5_drifter_theme.ogg",
    composer:"—", desc:"Gravel under boot. A far-away match-strike. The drifter doesn't stay long enough to leave a melody.", unlock:{"type": "heard"}, chars:["the_drifter"] },
  { id:"vol5_drunk_uncle_theme", vol:5, title:"Drunk Uncle", src:"assets/audio/bgm/vol5_drunk_uncle_theme.ogg",
    composer:"—", desc:"A baseline-room thump that refuses to sync to anything else playing. A glass on wood. The uncle who arrived and will not be greeted.", unlock:{"type": "heard"}, chars:["drunk_uncle"] },
  { id:"vol5_finale_inertia_fallback", vol:5, title:"The Room Sat on Him", src:"assets/audio/bgm/vol5_finale_inertia_fallback.ogg",
    composer:"—", desc:"Magician finale stinger — generic stagnation fallback. The room is exhausted and all motion has stopped.", unlock:{"type": "key", "key": "milestone:magician_finale:inertia_fallback"} },
  { id:"vol5_finale_maker_breaks", vol:5, title:"The Maker Breaks", src:"assets/audio/bgm/vol5_finale_maker_breaks.ogg",
    composer:"—", desc:"Magician finale stinger — Doubt at max. Silence under one pad falling a half-step. The last breath before the host closes his eyes for the last time.", unlock:{"type": "key", "key": "milestone:magician_finale:maker_breaks"} },
  { id:"vol5_finale_maker_forgets", vol:5, title:"The Maker Forgets the Make", src:"assets/audio/bgm/vol5_finale_maker_forgets.ogg",
    composer:"—", desc:"Magician finale stinger — Stagnation at max. Cassette-deck end-of-tape spool. Lights at full. The cathedral exhales without him.", unlock:{"type": "key", "key": "milestone:magician_finale:maker_forgets"} },
  { id:"vol5_finale_river_takes_bank", vol:5, title:"The River Takes the Bank", src:"assets/audio/bgm/vol5_finale_river_takes_bank.ogg",
    composer:"—", desc:"Magician finale stinger — the bank goes. A building giving up. Slow wood-and-metal collapse rendered as a half-degree sustained slide.", unlock:{"type": "key", "key": "milestone:magician_finale:river_takes_bank"} },
  { id:"vol5_finale_room_walked_out", vol:5, title:"The Room Walked Out", src:"assets/audio/bgm/vol5_finale_room_walked_out.ogg",
    composer:"—", desc:"Magician finale stinger — three visitors claimed. Everything has dropped out except the Demon's pad, held alone.", unlock:{"type": "key", "key": "milestone:magician_finale:room_walked_out"} },
  { id:"vol5_finale_shift_ends", vol:5, title:"Midnight, and Behind", src:"assets/audio/bgm/vol5_finale_shift_ends.ogg",
    composer:"—", desc:"Magician finale stinger — midnight overrun, the work undone. The workbench-lamp click off. Then nothing.", unlock:{"type": "key", "key": "milestone:magician_finale:shift_ends"} },
  { id:"vol5_finale_steamboat_sails", vol:5, title:"The Steamboat Sails", src:"assets/audio/bgm/vol5_finale_steamboat_sails.ogg",
    composer:"—", desc:"Magician finale stinger — the steamboat finished. Paddle wheel turning once though no one is touching it. Then the river bank slumps, far away. Then a held tone, resigned.", unlock:{"type": "key", "key": "milestone:magician_finale:steamboat_sails"} },
  { id:"vol5_milestone_candles_lit", vol:5, title:"The Candles Are Lit", src:"assets/audio/bgm/vol5_milestone_candles_lit.ogg",
    composer:"—", desc:"Released the first time you light the candles at the workbench in BLOW OUT THE CANDLES. A single sustained match-strike + held flame-hiss + a low pad. The cake is on the workbench.", unlock:{"type": "key", "key": "milestone:candles_lit"} },
  { id:"vol5_sinking_feeling", vol:5, title:"Sinking Feeling", src:"assets/audio/bgm/vol5_sinking_feeling.ogg",
    composer:"—", desc:"Tarot Gauntlet · Magician · easy-mode B-side. Afternoon sun on the cathedral skylights, low river lap outside, a distant freight horn. The riverside knowing what's coming and not saying.", unlock:{"type": "heard"}, chars:[], chapters:[] },
  { id:"vol5_steamboat_motif", vol:5, title:"The Paddle Wheel Builds Itself", src:"assets/audio/bgm/vol5_steamboat_motif.ogg",
    composer:"—", desc:"Magician's doom-clock. A slow paddle-wheel and far steam-whistle that thickens layer by layer across the run, one new element at each steamboat-ladder tier (0 → 6). Frasier hears it building whether he's working on it or not.", unlock:{"type": "heard"} },
  { id:"vol5_superfan_theme", vol:5, title:"The Superfan", src:"assets/audio/bgm/vol5_superfan_theme.ogg",
    composer:"—", desc:"Too-fast breath. Paper bag. Plastic-cup tap. A loyalty that hasn't read the room.", unlock:{"type": "heard"}, chars:["the_superfan"] },
  { id:"vol5_twins_theme", vol:5, title:"The Twins", src:"assets/audio/bgm/vol5_twins_theme.ogg",
    composer:"—", desc:"Two of the same tone, played milliseconds apart, panned hard left and hard right. Stereo phase. They share patience, they share a theme.", unlock:{"type": "heard"}, chars:["the_twins"] },
  { id:"vol5_watch_party", vol:5, title:"Watch Party", src:"assets/audio/bgm/vol5_watch_party.ogg",
    composer:"—", desc:"Tarot Gauntlet · Magician · medium-mode B-side. TV-room hum, the Pomegranate Hour theme bleeding through one wall, a far laugh from someone who isn't supposed to be in the room. 9:30 PM.", unlock:{"type": "heard"}, chars:[], chapters:[] },
  { id:"vol5_cicada_session", vol:5, title:"Cicada Session", src:"assets/audio/bgm/vol5_cicada_session.ogg",
    composer:"—", desc:"Tarot Gauntlet · Priestess · easy-mode B-side. The cicadas outside louder than they should be. The booth's red record-light. Reel turning, fresh. 9:18 PM.", unlock:{"type": "heard"}, chars:[], chapters:[] },
  { id:"vol5_long_quiet", vol:5, title:"The Long Quiet", src:"assets/audio/bgm/vol5_long_quiet.ogg",
    composer:"—", desc:"Tarot Gauntlet · Priestess · medium-mode B-side. Confessional hour. The booth's own noise floor instead of the cicadas now. 11:02 PM.", unlock:{"type": "heard"}, chars:[], chapters:[] },
  { id:"vol5_tape_witness", vol:5, title:"Tape Witness", src:"assets/audio/bgm/vol5_tape_witness.ogg",
    composer:"—", desc:"Tarot Gauntlet · Priestess · hard-mode B-side. 2:14 AM. Off-the-books. The truth-teller is already in the booth. The cathedral is dark on the other side.", unlock:{"type": "heard"}, chars:[], chapters:[] },
  { id:"vol5_priestess_finale_reel_ran_out", vol:5, title:"The Reel Ran Out", src:"assets/audio/bgm/vol5_priestess_finale_reel_ran_out.ogg",
    composer:"—", desc:"Priestess finale stinger — master_reel_full. Cassette-end-of-tape spool. The visitor mid-sentence. Elicia's hand goes up. The truth lives in the room but not on the tape.", unlock:{"type": "key", "key": "milestone:priestess_finale:reel_ran_out"} },
  { id:"vol5_priestess_finale_listener_breaks", vol:5, title:"The Listener Breaks", src:"assets/audio/bgm/vol5_priestess_finale_listener_breaks.ogg",
    composer:"—", desc:"Priestess finale stinger — Doubt at max. Elicia in the booth chair instead of the engineer's. The mic on, she silent. The reel turns. She is letting the room record her at last.", unlock:{"type": "key", "key": "milestone:priestess_finale:listener_breaks"} },
  { id:"vol5_priestess_finale_session_empty", vol:5, title:"The Session Ends Empty", src:"assets/audio/bgm/vol5_priestess_finale_session_empty.ogg",
    composer:"—", desc:"Priestess finale stinger — Stagnation at max. The end of the booked time. Lounge empty, booth empty, reel with nothing worth keeping. The BLANK · don't reuse label, again.", unlock:{"type": "key", "key": "milestone:priestess_finale:session_empty"} },
  { id:"vol5_priestess_finale_walked_out", vol:5, title:"Walked Out Mid-Sentence", src:"assets/audio/bgm/vol5_priestess_finale_walked_out.ogg",
    composer:"—", desc:"Priestess finale stinger — three visitors claimed. The silences they left behind, played back through the console headphones. Not nothing. The wrong thing.", unlock:{"type": "key", "key": "milestone:priestess_finale:walked_out"} },
  { id:"vol5_priestess_finale_cicadas_stopped", vol:5, title:"The Cicadas Stopped", src:"assets/audio/bgm/vol5_priestess_finale_cicadas_stopped.ogg",
    composer:"—", desc:"Priestess finale stinger — cross-arcana collapse. The cicadas have stopped all at once. The back door open onto the dark cathedral. Frasier on the other side, holding the steamboat. The red record-light still on.", unlock:{"type": "key", "key": "milestone:priestess_finale:cicadas_stopped"} },
  { id:"vol5_priestess_finale_shift_ends", vol:5, title:"The Session Is Over · Priestess", src:"assets/audio/bgm/vol5_priestess_finale_shift_ends.ogg",
    composer:"—", desc:"Priestess finale stinger — shift-over (priestess variant). The booth lamp shuts itself off on Elicia's timer. Visitors still in the lounge who didn't get their turn. She files what's done.", unlock:{"type": "key", "key": "milestone:priestess_finale:shift_ends"} },
  { id:"vol5_milestone_long_quiet", vol:5, title:"The Long Quiet (Elicia's Ability)", src:"assets/audio/bgm/vol5_milestone_long_quiet.ogg",
    composer:"—", desc:"Released the first time Elicia uses THE LONG QUIET in a session. A single sustained note holding a silence that wasn't supposed to be there.", unlock:{"type": "key", "key": "milestone:long_quiet_used"} },
  { id:"vol5_static_bloom", vol:5, title:"Static Bloom", src:"assets/audio/bgm/vol5_static_bloom.ogg",
    composer:"—", desc:"Tarot Gauntlet · Empress · easy-mode B-side. Friday dinner on Nicola's riverboat. First arrivals setting the long table; the garden deck still in season.", unlock:{"type": "heard"}, chars:[], chapters:[] },
  { id:"vol5_harvest_dinner", vol:5, title:"Harvest Dinner", src:"assets/audio/bgm/vol5_harvest_dinner.ogg",
    composer:"—", desc:"Tarot Gauntlet · Empress · medium-mode B-side. Late autumn. Frasier on the bank walking slow. The garden deck has cooled.", unlock:{"type": "heard"}, chars:[], chapters:[] },
  { id:"vol5_ice_in_the_river", vol:5, title:"Ice in the River", src:"assets/audio/bgm/vol5_ice_in_the_river.ogg",
    composer:"—", desc:"Tarot Gauntlet · Empress · hard-mode B-side. 11:14 PM, late February. The river has ice in it for the first time in a decade.", unlock:{"type": "heard"}, chars:[], chapters:[] },
  { id:"vol5_docket", vol:5, title:"Docket", src:"assets/audio/bgm/vol5_docket.ogg",
    composer:"—", desc:"Tarot Gauntlet · Emperor · easy-mode B-side. Tuesday morning. Brass clock. Radiator on too high. Stamp on the blotter.", unlock:{"type": "heard"}, chars:[], chapters:[] },
  { id:"vol5_first_session", vol:5, title:"First Session", src:"assets/audio/bgm/vol5_first_session.ogg",
    composer:"—", desc:"Tarot Gauntlet · Emperor · medium-mode B-side. Pre-clerk Monday. The petitioner slept in their car. The radiator is cold.", unlock:{"type": "heard"}, chars:[], chapters:[] },
  { id:"vol5_appeal", vol:5, title:"Appeal", src:"assets/audio/bgm/vol5_appeal.ogg",
    composer:"—", desc:"Tarot Gauntlet · Emperor · hard-mode B-side. Late Tuesday afternoon. Six-month appellate hearing. Volumes 9 and 10 of the river-code missing.", unlock:{"type": "heard"}, chars:[], chapters:[] },
  { id:"vol5_green_phosphor", vol:5, title:"Green Phosphor", src:"assets/audio/bgm/vol5_green_phosphor.ogg",
    composer:"—", desc:"Tarot Gauntlet · Hierophant · easy-mode B-side. Tuesday night BBS. Modem rack humming. Printer's banner paper rolling slowly.", unlock:{"type": "heard"}, chars:[], chapters:[] },
  { id:"vol5_long_signal", vol:5, title:"The Long Signal", src:"assets/audio/bgm/vol5_long_signal.ogg",
    composer:"—", desc:"Tarot Gauntlet · Hierophant · medium-mode B-side. Late Wednesday. Anya at the floppy wall. The ham band open. 14.301 MHz live.", unlock:{"type": "heard"}, chars:[], chapters:[] },
  { id:"vol5_broadcast_night", vol:5, title:"Broadcast Night", src:"assets/audio/bgm/vol5_broadcast_night.ogg",
    composer:"—", desc:"Tarot Gauntlet · Hierophant · hard-mode B-side. 3:14 AM. The lurker logged in. The ham band hisses then clears.", unlock:{"type": "heard"}, chars:[], chapters:[] },
  { id:"vol5_faucet_metronome", vol:5, title:"Faucet Metronome", src:"assets/audio/bgm/vol5_faucet_metronome.ogg",
    composer:"—", desc:"The Roberts kitchen before school. The faucet's drip keeping time; two people deciding, again, not to fix it.", unlock:{"type": "heard"}, chars:[], chapters:["vol5_ch6_lovers"] },
  { id:"vol5_two_speeds", vol:5, title:"Two Speeds", src:"assets/audio/bgm/vol5_two_speeds.ogg",
    composer:"—", desc:"Antonio's hot office above Ember & Ash. The window unit losing, the voicemail light blinking. Gone, and about to be gone.", unlock:{"type": "heard"}, chars:[], chapters:["vol5_ch7_chariot"] },
  { id:"vol5_the_score", vol:5, title:"The Score", src:"assets/audio/bgm/vol5_the_score.ogg",
    composer:"—", desc:"A New Orleans bar in refrains. Smoke curling back on itself in the ashtray; the beast not conquered, known.", unlock:{"type": "heard"}, chars:[], chapters:["vol5_ch8_strength"] },
  { id:"vol5_lantern_for_those_below", vol:5, title:"A Lantern for Those Below", src:"assets/audio/bgm/vol5_lantern_for_those_below.ogg",
    composer:"—", desc:"Joanna LeMoine in the ruin-scape of Graustark. Wind through scrawled walls; a lantern raised for whoever is still climbing.", unlock:{"type": "heard"}, chars:[], chapters:["vol5_ch9_hermit"] },
  { id:"vol5_closing_arguments", vol:5, title:"Closing Arguments", src:"assets/audio/bgm/vol5_closing_arguments.ogg",
    composer:"—", desc:"A Houston law office after the motion is denied. Fluorescent hum, files squared; the wheel turns either way.", unlock:{"type": "heard"}, chars:[], chapters:["vol5_ch10_wheel"] },
  { id:"vol5_the_weighing", vol:5, title:"The Weighing", src:"assets/audio/bgm/vol5_the_weighing.ogg",
    composer:"—", desc:"Erica Campbell's next morning, office to design studio. The scales don't lie about what the weighing costs.", unlock:{"type": "heard"}, chars:[], chapters:["vol5_ch11_justice"] },
  { id:"vol5_gravity_optional", vol:5, title:"Gravity Is Optional", src:"assets/audio/bgm/vol5_gravity_optional.ogg",
    composer:"—", desc:"Natalie's apartment after midnight. Incense and tape hiss; the world seen calmly upside down.", unlock:{"type": "heard"}, chars:[], chapters:["vol5_ch12_hanged"] },
  { id:"vol5_the_quiet_floor", vol:5, title:"The Quiet Floor", src:"assets/audio/bgm/vol5_the_quiet_floor.ogg",
    composer:"—", desc:"The second-floor hospice at St. Jude's Mercy, the last Tuesday in April. Machines breathing gently; nothing exempt, nothing cruel.", unlock:{"type": "heard"}, chars:[], chapters:["vol5_ch13_death"] },
  { id:"vol5_moderate_tuesday", vol:5, title:"The Moderate Temperature of Tuesday", src:"assets/audio/bgm/vol5_moderate_tuesday.ogg",
    composer:"—", desc:"A Montreal apartment, years on from the deck around it. Two cups in patient exchange; nothing spills.", unlock:{"type": "heard"}, chars:[], chapters:["vol5_ch14_temperance"] },
  { id:"vol5_gumbo_limbo", vol:5, title:"Gumbo Limbo", src:"assets/audio/bgm/vol5_gumbo_limbo.ogg",
    composer:"—", desc:"Jimmy Daigle under a wobbling ceiling fan in New Orleans. The chains are loose. The chains stay on.", unlock:{"type": "heard"}, chars:[], chapters:["vol5_ch15_devil"] },
  { id:"vol5_render_queue", vol:5, title:"Render Queue", src:"assets/audio/bgm/vol5_render_queue.ogg",
    composer:"—", desc:"Elicia's sleek Montreal command center gone to plaster ruins. Fans at full load; the crown already airborne.", unlock:{"type": "heard"}, chars:[], chapters:["vol5_ch16_tower"] },
  { id:"vol5_glass_skin", vol:5, title:"Glass Skin", src:"assets/audio/bgm/vol5_glass_skin.ogg",
    composer:"—", desc:"Graustark ruins under a shard-of-mirror moon. Water poured onto the earth and back; ink drying on glass skin.", unlock:{"type": "heard"}, chars:[], chapters:["vol5_ch17_star"] },
  { id:"vol5_five_am_reading", vol:5, title:"The Five A.M. Reading", src:"assets/audio/bgm/vol5_five_am_reading.ogg",
    composer:"—", desc:"After the cards, before the sun. Nicola asleep under the twilight quilt; Aria gone quiet, which is a different thing.", unlock:{"type": "heard"}, chars:[], chapters:["vol5_ch18_moon"] },
  { id:"vol5_saint_viateur", vol:5, title:"Tuesdays on Saint-Viateur", src:"assets/audio/bgm/vol5_saint_viateur.ogg",
    composer:"—", desc:"Café Olimpico, late May, morning espresso clatter. Six years of Tuesdays; by now the staff just nod.", unlock:{"type": "heard"}, chars:[], chapters:["vol5_ch19_sun"] },
  { id:"vol5_the_stillness_breaks", vol:5, title:"The Stillness Breaks", src:"assets/audio/bgm/vol5_the_stillness_breaks.ogg",
    composer:"—", desc:"One Tuesday morning across all of Graustark. The hush over the ruins shatters like flawed glass; the sound arrives.", unlock:{"type": "heard"}, chars:[], chapters:["vol5_ch20_judgement"] },
  { id:"vol5_minstrals_green", vol:5, title:"Minstral's Green", src:"assets/audio/bgm/vol5_minstrals_green.ogg",
    composer:"—", desc:"Down by the river where the steamship rusts. Old-honey sunlight through cypress; a child, a stick, a crawdad hole. The Frog says: mostly.", unlock:{"type": "heard"}, chars:[], chapters:["vol5_ch21_world"] },
  { id:"vol5_ember_ash_drone", vol:5, title:"Ember and Ash", src:"assets/audio/bgm/vol5_ember_ash_drone.ogg",
    composer:"—", desc:"Chapter VII — The Chariot. Antonio's warehouse. Low industrial hum + skylight wind + the slow creak of the cypress beam under load. The two cameos on this chapter's beats (Dante at Ember & Ash, Frasier at Ember & Ash, John at Ember & Ash) inherit this ambient.", unlock:{"type": "heard"}, chars:["antonio", "jimmy", "dante", "frasier", "john_frank"], chapters:["vol5_ch7_chariot", "vol5_cameo_dante_at_ember_and_ash", "vol5_cameo_frasier_at_ember_and_ash", "vol5_cameo_john_at_ember_and_ash"] },
  { id:"vol5_cameo_water_glass_left_full", vol:5, title:"The Water Glass, Left Full", src:"assets/audio/bgm/vol5_cameo_water_glass_left_full.ogg",
    composer:"—", desc:"Empress cameo · Dean Arrives finale stinger. The Dean-walks-out-with-the-note moment. Single brass note + the dining-room ambient cooling down + the small specific clink of a glass set back on the formica without being drunk from. 40s.", unlock:{"type": "heard"}, chars:["dean"], chapters:[] },
  { id:"vol5_cameo_bandstand_ringback", vol:5, title:"The Bandstand Calls Back", src:"assets/audio/bgm/vol5_cameo_bandstand_ringback.ogg",
    composer:"—", desc:"Empress cameo · Quentin at Table 17 mid-run cue. The bandstand payphone callback arriving on the boat's bar extension. A single distant ringing tone over the dining-room ambient + the slow muffled pickup. 30s.", unlock:{"type": "heard"}, chars:["quentin_paul"], chapters:[] },
  { id:"vol5_cameo_well_runs", vol:5, title:"The Well Runs", src:"assets/audio/bgm/vol5_cameo_well_runs.ogg",
    composer:"—", desc:"Emperor cameo · Sammy at the Well sustaining ambient. Ice scoop on stainless + the lemons being cut + the speed-pourer's small mechanical pulse + the pitcher refill. A working bartender's signature texture, never melodic. Loops under the run.", unlock:{"type": "heard"}, chars:["sammy"], chapters:[] },
  { id:"vol5_cameo_iron_stair_landing", vol:5, title:"The Iron Stair Landing", src:"assets/audio/bgm/vol5_cameo_iron_stair_landing.ogg",
    composer:"—", desc:"Emperor cameo · Antonio's Friday Visit finale stinger. The held quiet of the small dark helm cabin + the leaded window light landing + Marta's voice on the phone audible only as a register. 45s.", unlock:{"type": "heard"}, chars:["antonio", "dante"], chapters:[] },
  { id:"vol5_cameo_circuit_tuesday", vol:5, title:"The Same Circuit on a Tuesday", src:"assets/audio/bgm/vol5_cameo_circuit_tuesday.ogg",
    composer:"—", desc:"Hierophant cameo · Dante Walks the Same Circuit ambient. Tuesday-afternoon St Jude's interior + parking-lot asphalt heat-shimmer + the rectory window open. A Sunday space heard at a Tuesday hour. Loops under the run.", unlock:{"type": "heard"}, chars:["dante", "father_amato"], chapters:[] },
  { id:"vol5_cameo_pauls_flinch", vol:5, title:"Paul's Flinch", src:"assets/audio/bgm/vol5_cameo_pauls_flinch.ogg",
    composer:"—", desc:"Hierophant cameo · Antonio Confronts Paul stinger. The moment of the recorded no. Candle hiss + the small intake of breath caught on the recording + the corner-booth silence folding inward. 30s.", unlock:{"type": "heard"}, chars:["antonio", "quentin_paul"], chapters:[] },
  { id:"vol5_cameo_anya_on_mackenzie_tv", vol:5, title:"Anya on Mackenzie's TV", src:"assets/audio/bgm/vol5_cameo_anya_on_mackenzie_tv.ogg",
    composer:"—", desc:"Lovers cameo · Elicia at the Roberts stinger. The first frame of the Anya tape on the Roberts' CRT — Elicia's bungalow source ambient bleeding through the cooler living-room speakers. The cassette warm and the room cold around it. 50s.", unlock:{"type": "heard"}, chars:["elicia", "mackenzie"], chapters:[] },
  { id:"vol5_cameo_polaroid_morning", vol:5, title:"The Morning of the Polaroid", src:"assets/audio/bgm/vol5_cameo_polaroid_morning.ogg",
    composer:"—", desc:"Lovers cameo · John at the Roberts deferred-reveal stinger. Fires at doubt 5 when the Polaroid-about-to-arrive registers. The street is the street + the cicadas at morning-frequency + a small Polaroid-camera shutter sound from two streets over. 40s.", unlock:{"type": "heard"}, chars:["john_frank", "mackenzie"], chapters:[] },
  { id:"vol5_cameo_mailbox_post", vol:5, title:"Setting the Post", src:"assets/audio/bgm/vol5_cameo_mailbox_post.ogg",
    composer:"—", desc:"Lovers cameo · Frasier at the Roberts ambient. The four-verb manual labor as a sustained piece: post-hole digger biting soil + the cypress 4x4 sliding in + the level's bubble settling + the tamper packing down. The work is the cue. Loops.", unlock:{"type": "heard"}, chars:["frasier"], chapters:[] },
  { id:"vol5_cameo_dont_say_what_youre_thinking", vol:5, title:"Don't Say What You're Thinking", src:"assets/audio/bgm/vol5_cameo_dont_say_what_youre_thinking.ogg",
    composer:"—", desc:"Chariot cameo · Dante at Ember & Ash silent-presence stinger. The Time-0 verb of restraint. A held breath + the office leaded-window light settling + the ledger closing one beat too soon. No melody. 25s.", unlock:{"type": "heard"}, chars:["dante", "antonio"], chapters:[] },
  { id:"vol5_cameo_cypress_beam_choice", vol:5, title:"The Beam Holds For Now", src:"assets/audio/bgm/vol5_cameo_cypress_beam_choice.ogg",
    composer:"—", desc:"Chariot cameo · Frasier at Ember & Ash binary-choice stinger. Plays the moment TELL HIM FINE / TELL HIM NOT resolves. Slow upward groan of structural wood + the skylight wind + the cardinal-direction air shifting around the catwalk. 50s. The same stinger fires for either answer; the saga flag decides which voice the BBM hears in vol7's read.", unlock:{"type": "heard"}, chars:["frasier", "antonio"], chapters:[] },
  { id:"vol5_cameo_warehouse_phone", vol:5, title:"The Warehouse Phone", src:"assets/audio/bgm/vol5_cameo_warehouse_phone.ogg",
    composer:"—", desc:"Chariot cameo · John at Ember & Ash sustaining ambient. The host-as-visitor scenario. The warehouse interior empty of crew + the cicadas on the phone at afternoon-frequency + the wrong-quiet of a building by 5 PM. Loops.", unlock:{"type": "heard"}, chars:["antonio", "john_frank"], chapters:[] },
  { id:"vol5_whispers_theme", vol:5, title:"Whispers from the Liminal", src:"assets/audio/bgm/vol5_whispers_theme.mp3",
    composer:"—", desc:"Prelude · a channel page past midnight. Late-night broadcast theme for the episode hub; every episode already up.", unlock:{"type": "heard"}, chars:[], chapters:["vol5_prelude_arcana_channel", "vol5_prelude_arcana_whispers"] },
  { id:"vol5_prelude_low_bar", vol:5, title:"Shadiest Bar, Best Zip Code", src:"assets/audio/bgm/vol5_prelude_low_bar.mp3",
    composer:"—", desc:"Prelude · after work with the tribe called best friends. Smoke that clings, a jukebox two decades behind.", unlock:{"type": "heard"}, chars:[], chapters:["vol5_prelude_arcana_john_bar"] },
  { id:"vol5_prelude_dinner_rush", vol:5, title:"The Dinner Rush", src:"assets/audio/bgm/vol5_prelude_dinner_rush.mp3",
    composer:"—", desc:"Prelude · John's shift at the future restaurant. Ticket printer, plates on the pass, a portrait lighting up in the gallery.", unlock:{"type": "heard"}, chars:[], chapters:["vol5_prelude_arcana_john_shift"] },

  // ── Vol 6 · Planned Community ────────────────────────────────────────
  { id:"vol6_sam_theme", vol:6, title:"Sam · Eleven Forty-Seven", src:"assets/audio/bgm/vol6_sam_theme.ogg",
    composer:"—", desc:"Register clerk's steady. Low sine + a paper-thin chime on the entry bell, half a beat behind where you'd expect.", unlock:{"type": "heard"}, chars:["sam"] },
  { id:"vol6_diego_theme", vol:6, title:"Diego · Two-A-Days", src:"assets/audio/bgm/vol6_diego_theme.ogg",
    composer:"—", desc:"Sneaker squeak on gym lacquer + a held breath at the line of scrimmage. Diego's signature.", unlock:{"type": "heard"}, chars:["diego"] },
  { id:"vol6_maya_theme", vol:6, title:"Maya · Bedroom Recording", src:"assets/audio/bgm/vol6_maya_theme.ogg",
    composer:"—", desc:"Cassette-deck hiss + a half-strummed guitar through the wall. Maya's signature.", unlock:{"type": "heard"}, chars:["maya"] },
  { id:"vol6_rick_theme", vol:6, title:"Rick · Back-Issue Reverence", src:"assets/audio/bgm/vol6_rick_theme.ogg",
    composer:"—", desc:"Bagged-and-boarded mylar shuffle + a vintage-store CRT hum at 60 Hz. Rick Cosmic's signature.", unlock:{"type": "heard"}, chars:["rick"] },
  { id:"vol6_skip_theme", vol:6, title:"Skip · Pump Four", src:"assets/audio/bgm/vol6_skip_theme.ogg",
    composer:"—", desc:"Pump-bell ding + a fluorescent ballast click + the canopy fans. Skip Donnelly's signature.", unlock:{"type": "heard"}, chars:["skip"] },
  { id:"vol6_tanya_theme", vol:6, title:"Tanya · The HCE Take", src:"assets/audio/bgm/vol6_tanya_theme.ogg",
    composer:"—", desc:"Talk-radio bleed under a wood-panel dash + the click of a long-press lighter. Tanya Horne's signature.", unlock:{"type": "heard"}, chars:["tanya"] },
  { id:"vol6_carl_theme", vol:6, title:"Carl · Lunch Pail", src:"assets/audio/bgm/vol6_carl_theme.ogg",
    composer:"—", desc:"Tin-clasp pop + a thermos pour + the unhurried exhale of a man who has done this thirty thousand times. Carl Reno's signature.", unlock:{"type": "heard"}, chars:["carl"] },
  { id:"vol6_lena_theme", vol:6, title:"Lena · Apartment Window", src:"assets/audio/bgm/vol6_lena_theme.ogg",
    composer:"—", desc:"A single Spanish-guitar string left open + window-glass condensation drip. Lena's vol6 signature (carries to vol7).", unlock:{"type": "heard"}, chars:["lena"] },
  { id:"vol6_kwik_stop_interior", vol:6, title:"The Kwik Stop · Night Shift", src:"assets/audio/bgm/vol6_kwik_stop_interior.ogg",
    composer:"—", desc:"Sodium-buzz fluorescents, beer-cooler compressor cycle, taquito roller squeak, occasional door chime. The store at 11:47 PM.", unlock:{"type": "heard"}, chapters:["vol6_ch1_stranger", "vol6_ch10_night_shift", "vol6_ch15_kwik_stop", "vol6_ch18_stockroom", "vol6_ch2_kwik_stop", "vol6_ch6_kwik_stop_open", "vol6_ch6_kwik_stop_slushie", "vol6_ch6_kwik_stop_text"] },
  { id:"vol6_cosmic_comics_interior", vol:6, title:"Cosmic Comics · Saturday Pull", src:"assets/audio/bgm/vol6_cosmic_comics_interior.ogg",
    composer:"—", desc:"Bagged-and-boarded shuffle + a vintage Casio demo loop from a hand-me-down keyboard in the back room.", unlock:{"type": "heard"}, chapters:["vol6_ch1_cosmic_comics", "vol6_ch12_cosmic", "vol6_ch2_cosmic", "vol6_ch3_back_room", "vol6_ch3_coda", "vol6_ch21_cosmic"] },
  { id:"vol6_gas_and_go_interior", vol:6, title:"NexCorp Gas & Go · Locker Four", src:"assets/audio/bgm/vol6_gas_and_go_interior.ogg",
    composer:"—", desc:"Pump-canopy fans + cooler ice-maker + the manager-office printer ginning out a daily report.", unlock:{"type": "heard"}, chapters:["vol6_ch1_gas_and_go"] },
  { id:"vol6_el_rancho_interior", vol:6, title:"El Rancho · Late Plate", src:"assets/audio/bgm/vol6_el_rancho_interior.ogg",
    composer:"—", desc:"A norteño guitar held one chord too long + the dishwasher's last cycle of the night.", unlock:{"type": "heard"}, chapters:["vol6_ch16_el_rancho"] },
  { id:"vol6_live_oak_field", vol:6, title:"Live Oak Field · Two-A-Days", src:"assets/audio/bgm/vol6_live_oak_field.ogg",
    composer:"—", desc:"Cleat on Bermuda grass + cicadas at 6:15 AM + a far whistle's three short bursts.", unlock:{"type": "heard"}, chapters:["vol6_ch13_two_a_days", "vol6_ch14_live_oak"] },
  { id:"vol6_substation_nine", vol:6, title:"Substation Nine · The Hum", src:"assets/audio/bgm/vol6_substation_nine.ogg",
    composer:"—", desc:"Chain-link buzz + transformer 60 Hz drone + a single grackle that won't leave.", unlock:{"type": "heard"}, chapters:["vol6_ch14_substation_nine"] },
  { id:"vol6_alma_theme", vol:6, title:"Alma · Pleasant Beige", src:"assets/audio/bgm/vol6_alma_theme.ogg",
    composer:"—", desc:"Saccharine corporate-jingle-adjacent two-note motif. Alma's signature.", unlock:{"type": "heard"}, chars:["alma"] },
  { id:"vol6_ambient", vol:6, title:"Harmony Creek Estates", src:"assets/audio/bgm/vol6_ambient.mp3",
    composer:"—", desc:"Sixty-eight degrees, year-round, by corporate decree.", unlock:{"type": "heard"}, chapters:["vol6_ch0_prelude"] },
  { id:"vol6_corporate_hum", vol:6, title:"Sixty-Eight, Year-Round", src:"assets/audio/bgm/vol6_corporate_hum.ogg",
    composer:"—", desc:"HVAC system + a single sine pad at 68 Hz. Clean. Inhuman. The planned community at rest.", unlock:{"type": "heard"}, chapters:[] },
  { id:"vol6_milestone_phc", vol:6, title:"The Community (acknowledged)", src:"assets/audio/bgm/vol6_milestone_phc.ogg",
    composer:"—", desc:"Released at the Vol 6 turning point.", unlock:{"type": "key", "key": "milestone:vol6_phc"} },
  { id:"vol6_planning_office", vol:6, title:"The Planning Office", src:"assets/audio/bgm/vol6_planning_office.ogg",
    composer:"—", desc:"Office-air recirc + a single fluorescent buzz, no human movement.", unlock:{"type": "heard"}, chapters:["vol6_planning_office"] },
  { id:"vol6_slushie_futures", vol:6, title:"Slushie Futures · Monday", src:"assets/audio/bgm/vol6_slushie_futures.ogg",
    composer:"—", desc:"Monday, dressed up as itself — the lawns permitted to thirst by HOA decree, the Pit Stop's lunch-shuffle grill, a white sedan keeping an unassigned vigil at the curb after dark.", unlock:{"type": "heard"}, chars:[], chapters:["vol6_ch2_gas_oracles", "vol6_ch2_bindery", "vol6_ch2_dumpster", "vol6_ch2_gas_go_lot", "vol6_ch2_pit_stop_kitchen", "vol6_ch2_maya_bedroom", "vol6_ch2_coda"] },
  { id:"vol6_tuesday_notebooks", vol:6, title:"Tuesday · Notebooks", src:"assets/audio/bgm/vol6_tuesday_notebooks.ogg",
    composer:"—", desc:"Tuesday in Harmony Creek — Sam down to the kitchen before her father for the first time in six months, a white sedan in the strip-mall lot, lists and chat windows glowing after dark.", unlock:{"type": "heard"}, chars:[], chapters:["vol6_ch3_circle_k", "vol6_ch3_parking_lot", "vol6_ch3_pit_stop_office", "vol6_ch3_jesse_bedroom", "vol6_ch3_sam_bedroom"] },
  { id:"vol6_gulf_storm", vol:6, title:"The Storm off the Gulf", src:"assets/audio/bgm/vol6_gulf_storm.ogg",
    composer:"—", desc:"The Wednesday storm, in off the Gulf since midnight — thunder rolling from six-oh-four, parking lots turning to shallow lakes, a Speak & Spell glowing darkroom red on Rick's shelf.", unlock:{"type": "heard"}, chars:[], chapters:["vol6_ch4_storm", "vol6_ch4_sam_list", "vol6_ch4_kwik_stop", "vol6_ch4_pit_stop", "vol6_ch4_maya_floor", "vol6_ch4_speak_spell", "vol6_ch4_miller_office", "vol6_ch4_kitchen"] },
  { id:"vol6_garage_band", vol:6, title:"Garage Band Catharsis", src:"assets/audio/bgm/vol6_garage_band.ogg",
    composer:"—", desc:"Thursday evening — three distorted Telecaster chords leaking through the garage-door vent, Ben's truck parked dark, 1776 kHz coming in under the static.", unlock:{"type": "heard"}, chars:[], chapters:["vol6_ch5_garage", "vol6_ch5_truck", "vol6_ch5_radio", "vol6_ch5_miller_drive", "vol6_ch5_meadowlark"] },
  { id:"vol6_service_roads", vol:6, title:"Service Roads · Friday", src:"assets/audio/bgm/vol6_service_roads.ogg",
    composer:"—", desc:"Friday along I-10 — an unmarked van at pump six, a white sedan on the gravel shoulder three miles east of the FM-3411 exit, a small frame house on a county road thirty-two miles southeast.", unlock:{"type": "heard"}, chars:[], chapters:["vol6_ch6_miller_truck", "vol6_ch6_fueling_station", "vol6_ch6_boyd", "vol6_ch6_interstate", "vol6_ch6_tome", "vol6_ch6_pit_stop", "vol6_ch6_jesse_bedroom", "vol6_ch6_maya_bedroom", "vol6_ch6_safehouse", "vol6_ch6_miller_kitchen", "vol6_ch6_sam_bedroom"] },
  { id:"vol6_waiting_rooms", vol:6, title:"The Day After · Waiting Rooms", src:"assets/audio/bgm/vol6_waiting_rooms.ogg",
    composer:"—", desc:"The day after — vending-machine coffee going cold in the hospital waiting room, pot roast in the oven since two-thirty, Daisy hiding from a butterfly behind a lawn chair.", unlock:{"type": "heard"}, chars:[], chapters:["vol6_ch7_hospital", "vol6_ch7_pit_stop", "vol6_ch7_ben_room", "vol6_ch7_henderson_kitchen", "vol6_ch7_henderson_driveway", "vol6_ch7_safehouse"] },
  { id:"vol6_pre_dawn_blue", vol:6, title:"Pre-Dawn Blue · Late May", src:"assets/audio/bgm/vol6_pre_dawn_blue.ogg",
    composer:"—", desc:"The eight minutes of pre-dawn blue Texas does in late May — a truck on the highway at first light, Courtroom 4 waiting on the judge's lunch, Room 318 with the IV in the Morse hand.", unlock:{"type": "heard"}, chars:[], chapters:["vol6_ch8_miller_truck", "vol6_ch8_lake_palestine", "vol6_ch8_kowalski_kitchen", "vol6_ch8_hospital_318", "vol6_ch8_courthouse"] },
  { id:"vol6_the_long_sleep", vol:6, title:"The Long Sleep · Safehouse", src:"assets/audio/bgm/vol6_the_long_sleep.ogg",
    composer:"—", desc:"Diego at the safehouse — eighteen hours of sleep in every twenty-four, and the caged fluorescent room that follows him under.", unlock:{"type": "heard"}, chars:[], chapters:["vol6_ch9_room", "vol6_ch9_safehouse"] },
  { id:"vol6_four_thirty_kitchen", vol:6, title:"Bianca's Kitchen · Four Thirty", src:"assets/audio/bgm/vol6_four_thirty_kitchen.ogg",
    composer:"—", desc:"The kitchen before the subdivision stirs — awake at four eleven again, coffee made in the dark, the doorbell at eight oh-three on a Monday nobody was expecting.", unlock:{"type": "heard"}, chars:[], chapters:["vol6_ch11_kitchen", "vol6_ch11_eileen"] },
  { id:"vol6_porch_light_watch", vol:6, title:"Porch Lights · Mid-August", src:"assets/audio/bgm/vol6_porch_light_watch.ogg",
    composer:"—", desc:"Mid-August at the cul-de-sac windows — Don Geller's porch light eight minutes early at four forty-three, the shaded back-porch hour before the ninety-five settles in.", unlock:{"type": "heard"}, chars:[], chapters:["vol6_ch17_table", "vol6_ch17_porch"] },
  { id:"vol6_depth_chart", vol:6, title:"The Depth Chart · Friday", src:"assets/audio/bgm/vol6_depth_chart.ogg",
    composer:"—", desc:"Friday of the depth chart — three easy miles at six oh-eight with no stopwatch, then the drive home with two new things riding along in the Civic.", unlock:{"type": "heard"}, chars:[], chapters:["vol6_ch19_depthchart", "vol6_ch19_chains"] },
  { id:"vol6_fourth_chord", vol:6, title:"The Fourth Chord", src:"assets/audio/bgm/vol6_fourth_chord.ogg",
    composer:"—", desc:"Substation Nine gets its bridge — a suspended fourth chord found at four-twelve in Jesse's bedroom, the kitchen light still on at ten thirty-eight.", unlock:{"type": "heard"}, chars:[], chapters:["vol6_ch20_bridge", "vol6_ch20_prints"] },
  { id:"vol6_iced_tea_porch", vol:6, title:"Linda's Porch · Iced Tea", src:"assets/audio/bgm/vol6_iced_tea_porch.ogg",
    composer:"—", desc:"Evening on Linda's porch — the light on, the wicker chair, two glasses of iced tea with Maya's poured in advance.", unlock:{"type": "heard"}, chars:[], chapters:["vol6_ch21_porch"] },
  { id:"vol6_saturday_town", vol:6, title:"The Long Saturday", src:"assets/audio/bgm/vol6_saturday_town.ogg",
    composer:"—", desc:"The long Saturday — coffee made in the dark at four eleven, the Vinton bus in the lot at four oh-three, the Foxhole on the back side of the strip mall, inventory codes read in half-voice.", unlock:{"type": "heard"}, chars:[], chapters:["vol6_ch22_bianca", "vol6_ch22_vinton", "vol6_ch22_foxhole", "vol6_ch22_inventory", "vol6_ch22_sunday"] },
  { id:"vol6_sunday_dinner", vol:6, title:"Sunday · Lights Out", src:"assets/audio/bgm/vol6_sunday_dinner.ogg",
    composer:"—", desc:"Sunday closing out — Diego waking at four-oh-eight PM behind blackout curtains, enchiladas kept warm, three Hendersons at the table.", unlock:{"type": "heard"}, chars:[], chapters:["vol6_ch23_sunday", "vol6_ch23_sleep"] },

  // ── Vol 7 · Land of Milk & Honey ─────────────────────────────────────
  { id:"vol7_ambient", vol:7, title:"Smolvud Ambient", src:"assets/audio/bgm/vol7_ambient.mp3",
    composer:"—", desc:"The kind of town that knows when you have arrived before you do.", unlock:{"type": "heard"} },
  { id:"vol7_apartment_rain", vol:7, title:"Lena's Apartment · Rain", src:"assets/audio/bgm/vol7_apartment_rain.mp3",
    composer:"—", desc:"Six o'clock. Four coats on four hooks.", unlock:{"type": "heard"}, chars:["lena"], chapters:["vol7_ch3_apartment", "vol7_ch7_bridge", "vol7_ch7_six_oclock", "vol7_ch7_night", "vol7_ch8_six_oclock", "vol7_ch8_the_table", "vol7_ch8_kitchen", "vol7_ch8_roy", "vol7_ch8_finn_speaks", "vol7_ch8_the_apology", "vol7_ch8_the_daughter", "vol7_ch8_the_vessel", "vol7_ch8_goodnight", "vol7_ch8_dark"] },
  { id:"vol7_aria_theme", vol:7, title:"Aria", src:"assets/audio/bgm/vol7_aria_theme.ogg",
    composer:"—", desc:"A single hand-bell strike, then a held silence of three seconds, then again. Aria's signature.", unlock:{"type": "heard"}, chars:["aria"] },
  { id:"vol7_bread_table", vol:7, title:"Bread, Table, Family", src:"assets/audio/bgm/vol7_bread_table.ogg",
    composer:"—", desc:"Kitchen fire crackle, distant German hymn fragment, table set for nine.", unlock:{"type": "heard"}, chapters:["vol7_ch15_bread"] },
  { id:"vol7_hymn_fragment", vol:7, title:"Hymn Fragment · From Another Room", src:"assets/audio/bgm/vol7_hymn_fragment.ogg",
    composer:"—", desc:"A German hymn played on a far piano in another room of the house. Recurs across the family scenes.", unlock:{"type": "heard"}, chapters:["vol7_ch15_bread", "vol7_ch16_aud", "vol7_ch17_aria"] },
  { id:"vol7_marit_theme", vol:7, title:"Marit", src:"assets/audio/bgm/vol7_marit_theme.ogg",
    composer:"—", desc:"An older voice humming a hymn fragment, very close to the mic. (No legible vocal.)", unlock:{"type": "heard"}, chars:["marit"] },
  { id:"vol7_milestone_bell", vol:7, title:"Aria Rings the Bell", src:"assets/audio/bgm/vol7_milestone_bell.ogg",
    composer:"—", desc:"Released at Vol 7's title moment.", unlock:{"type": "key", "key": "milestone:aria_rings_bell"}, chapters:["vol7_ch17_aria"] },
  { id:"vol7_rain_on_roof", vol:7, title:"Rain on Roof", src:"assets/audio/bgm/vol7_rain_on_roof.mp3",
    composer:"—", desc:"With two of them left in it the apartment was hers again.", unlock:{"type": "heard"}, chapters:["vol7_ch15_bread", "vol7_ch16_aud", "vol7_ch17_aria"] },
  { id:"vol7_wren_theme", vol:7, title:"Wren", src:"assets/audio/bgm/vol7_wren_theme.ogg",
    composer:"—", desc:"Two notes of a wooden whistle, the first held, the second never quite arriving. Wren's signature.", unlock:{"type": "heard"}, chars:["wren"] },
  { id:"vol7_tem_theme", vol:7, title:"Tem", src:"assets/audio/bgm/vol7_tem_theme.ogg",
    composer:"—", desc:"Wool-mitten brush across a kitchen-window pane + a kettle two rooms over. Tem's signature.", unlock:{"type": "heard"}, chars:["tem"] },
  { id:"vol7_petra_theme", vol:7, title:"Petra", src:"assets/audio/bgm/vol7_petra_theme.ogg",
    composer:"—", desc:"A child's six-note recorder run, played twice, the second time a half-step lower. Petra's signature.", unlock:{"type": "heard"}, chars:["petra"] },
  { id:"vol7_kai_theme", vol:7, title:"Kai", src:"assets/audio/bgm/vol7_kai_theme.ogg",
    composer:"—", desc:"Boot-heel on plank pier + a single hand-line clicking. Kai's signature.", unlock:{"type": "heard"}, chars:["kai"] },
  { id:"vol7_per_theme", vol:7, title:"Per", src:"assets/audio/bgm/vol7_per_theme.ogg",
    composer:"—", desc:"Tarred rope laid down, a pipe-knife strop, an exhale through close-trimmed beard. Per's signature.", unlock:{"type": "heard"}, chars:["per"] },
  { id:"vol7_sal_theme", vol:7, title:"Sal Carratura", src:"assets/audio/bgm/vol7_sal_theme.ogg",
    composer:"—", desc:"Espresso-machine steam wand + a tin sign tap + half a Sicilian phrase under the breath. Sal's signature.", unlock:{"type": "heard"}, chars:["sal"] },
  { id:"vol7_finn_theme", vol:7, title:"Finn", src:"assets/audio/bgm/vol7_finn_theme.ogg",
    composer:"—", desc:"A short bow across a single fiddle string + the snow-shovel scrape outside the door. Finn's signature.", unlock:{"type": "heard"}, chars:["finn"] },
  { id:"vol7_gable_theme", vol:7, title:"Mrs Gable", src:"assets/audio/bgm/vol7_gable_theme.ogg",
    composer:"—", desc:"Tea-cup against saucer + the long-case clock at the end of the hall. Marian Gable's signature.", unlock:{"type": "heard"}, chars:["gable"] },
  { id:"vol7_cabin_woodstove", vol:7, title:"Cabin · Woodstove", src:"assets/audio/bgm/vol7_cabin_woodstove.ogg",
    composer:"—", desc:"Damper-pull tick + a log settling at the back of the firebox + plank floor cooling.", unlock:{"type": "heard"}, chapters:["vol7_ch10_cabin", "vol7_ch10_morning", "vol7_ch1_morning", "vol7_ch1_finn", "vol7_ch4_alone", "vol7_ch4_finn"] },
  { id:"vol7_kestrel_circle", vol:7, title:"Kestrel · Wind Above", src:"assets/audio/bgm/vol7_kestrel_circle.ogg",
    composer:"—", desc:"Slow-cycling thermal hiss + the small, very-far cry of a bird on patrol.", unlock:{"type": "heard"}, chapters:["vol7_ch11_kestrel"] },
  { id:"vol7_marina_morning", vol:7, title:"Marina · Halyards", src:"assets/audio/bgm/vol7_marina_morning.ogg",
    composer:"—", desc:"Halyard tap on aluminum mast + dock-line creak + a single gull a long way off.", unlock:{"type": "heard"}, chapters:["vol7_ch13_marina"] },
  { id:"vol7_painting_room", vol:7, title:"The Painting Room", src:"assets/audio/bgm/vol7_painting_room.ogg",
    composer:"—", desc:"Turpentine bottle uncorked + brush tap on canvas + the close attentive breath of someone looking.", unlock:{"type": "heard"}, chapters:["vol7_ch14_painting", "vol7_ch14_figure", "vol7_ch3_studio"] },
  { id:"vol7_loft_dust", vol:7, title:"Loft · Dust at Four", src:"assets/audio/bgm/vol7_loft_dust.ogg",
    composer:"—", desc:"Hayloft settle + a sparrow in the eaves + the four-o'clock sun on warm wood.", unlock:{"type": "heard"}, chapters:["vol7_ch15_loft"] },
  { id:"vol7_shop_signal_bell", vol:7, title:"The Shop · Signal Bell", src:"assets/audio/bgm/vol7_shop_signal_bell.ogg",
    composer:"—", desc:"Door-spring chime + the till's small mechanical click + the floorboard that always pops under the second step.", unlock:{"type": "heard"}, chapters:["vol7_ch16_shop"] },
  { id:"vol7_werner_theme", vol:7, title:"Werner", src:"assets/audio/bgm/vol7_werner_theme.ogg",
    composer:"—", desc:"A slow upright piano with the una corda pedal in. The bread-maker's signature.", unlock:{"type": "heard"}, chars:["werner"] },
  { id:"vol7_bluff_drones", vol:7, title:"Drones off the Bluff · Before Dawn", src:"assets/audio/bgm/vol7_bluff_drones.ogg",
    composer:"—", desc:"Friday before dawn — cargo drones coming up the cliff face in fours and fives, then the grandfather's wagon down through Sitka and alder in the rain.", unlock:{"type": "heard"}, chars:[], chapters:["vol7_ch2_morning", "vol7_ch2_afternoon"] },
  { id:"vol7_across_main", vol:7, title:"Board Lords · Across Main", src:"assets/audio/bgm/vol7_across_main.ogg",
    composer:"—", desc:"Kai's stretch of Main — the shop opened at ten like every Sunday since '48, Finn's rooms above the closed kayak shop, and the patch on the laundromat wall bigger each morning.", unlock:{"type": "heard"}, chars:[], chapters:["vol7_ch5_roy", "vol7_ch5_cabin", "vol7_ch9_tuesday", "vol7_ch9_evening"] },
  { id:"vol7_chillwave_back_room", vol:7, title:"ChillWave · The Back Room", src:"assets/audio/bgm/vol7_chillwave_back_room.ogg",
    composer:"—", desc:"The back of ChillWave — cedar shelves alphabetized by designer, a soldering iron cooling on the workbench, the wall transformer humming faintly with the iron unplugged.", unlock:{"type": "heard"}, chars:[], chapters:["vol7_ch6_sunday", "vol7_ch6_cale_opening", "vol7_ch6_cale", "vol7_ch6_chillwave", "vol7_ch6_why_lena", "vol7_ch6_nate", "vol7_ch6_brandon", "vol7_ch6_pattern_persistence", "vol7_ch6_the_stick", "vol7_ch6_tem_call", "vol7_ch6_get_going"] },
  { id:"vol7_daily_grind", vol:7, title:"The Daily Grind · Gray Monday", src:"assets/audio/bgm/vol7_daily_grind.ogg",
    composer:"—", desc:"The Daily Grind on a gray Monday — the bell at eleven fifty-eight, rain-light at the counter, the count of thirty after Roy walks out.", unlock:{"type": "heard"}, chars:[], chapters:["vol7_ch8_monday", "vol7_ch8_aria"] },
  { id:"vol7_thursday_rounds", vol:7, title:"Thursday Rounds · The Hexagon", src:"assets/audio/bgm/vol7_thursday_rounds.ogg",
    composer:"—", desc:"Thursday in late August, the town awake an hour — the completed hexagon riding in a canvas bag, short drives between Lena's window, Board Lords, and the alley behind the bakery.", unlock:{"type": "heard"}, chars:[], chapters:["vol7_ch12_morning", "vol7_ch12_lena", "vol7_ch12_kai"] },
  { id:"vol7_tide_pool", vol:7, title:"Tide Pool · Inside the Stick", src:"assets/audio/bgm/vol7_tide_pool.ogg",
    composer:"—", desc:"Inside the stick — a tide pool on a basalt headland, rendered by someone who had been to the coast: one open anemone, two purple stars, and the end-of-stick beep waiting back in the bedroom.", unlock:{"type": "heard"}, chars:[], chapters:["vol7_ch18_stick", "vol7_ch18_pool", "vol7_ch18_home"] },
  { id:"vol7_four_bowls", vol:7, title:"The Cabin · Four Bowls", src:"assets/audio/bgm/vol7_four_bowls.ogg",
    composer:"—", desc:"Sunday evening at the cabin — the stove banked higher than she banks it in the mornings, kerosene light, four bowls warm on the table, mint tea for seven.", unlock:{"type": "heard"}, chars:[], chapters:["vol7_ch19_per", "vol7_ch19_roy", "vol7_ch19_cedar", "vol7_ch19_ring"] },
  { id:"vol7_three_oh_two", vol:7, title:"3:02 AM · The Knock", src:"assets/audio/bgm/vol7_three_oh_two.ogg",
    composer:"—", desc:"A knock at 3:02 AM coming through the cedar wall — seven at the table holding still, then the alley at six forty-three with the painted face at its far end.", unlock:{"type": "heard"}, chars:[], chapters:["vol7_ch20_door", "vol7_ch20_each", "vol7_ch20_calls", "vol7_ch20_wall"] },
  { id:"vol7_the_leaving", vol:7, title:"The Wall · The Leaving", src:"assets/audio/bgm/vol7_the_leaving.ogg",
    composer:"—", desc:"Monday morning at the wall — the face closed-eyed since seven thirty-eight, brioche and rye going around from Hans's van, the leaving beginning without anyone calling for it.", unlock:{"type": "heard"}, chars:[], chapters:["vol7_ch21_leaving", "vol7_ch21_cabin", "vol7_ch21_tower"] },
  { id:"vol7_the_tower", vol:7, title:"The Tower · Old-Yachats", src:"assets/audio/bgm/vol7_the_tower.ogg",
    composer:"—", desc:"Forty-three miles up 101 to old-Yachats — the tower's polished-cedar lobby, an empty reception desk, a six-inch window set into a fourth-floor door.", unlock:{"type": "heard"}, chars:[], chapters:["vol7_ch22_drive", "vol7_ch22_floors", "vol7_ch22_portal"] },
];

// Default every entry to heard-based unlock unless explicitly overridden.
MM_MUSIC.forEach(t => { if (!t.unlock) t.unlock = { type: 'heard' }; });

// ── Heard set ────────────────────────────────────────────────────────────
const MM_MUSIC_HEARD_KEY = 'mm_music_heard';
const MM_MUSIC_HEARD = {
  _cache: null,
  _load() {
    try { this._cache = new Set(JSON.parse(localStorage.getItem(MM_MUSIC_HEARD_KEY) || '[]')); }
    catch { this._cache = new Set(); }
    return this._cache;
  },
  get() { return this._cache || this._load(); },
  has(src) { return this.get().has(src); },
  mark(src) {
    if (!src) return false;
    const set = this.get();
    if (set.has(src)) return false;
    set.add(src);
    try { localStorage.setItem(MM_MUSIC_HEARD_KEY, JSON.stringify([...set])); } catch {}
    try { window.dispatchEvent(new CustomEvent('mm-music-heard', { detail: src })); } catch {}
    return true;
  },
  clear() {
    this._cache = new Set();
    try { localStorage.removeItem(MM_MUSIC_HEARD_KEY); } catch {}
    try { window.dispatchEvent(new CustomEvent('mm-music-heard', { detail: null })); } catch {}
  },
};

// Cross-tab sync (Music Room open while game plays in another tab)
try {
  window.addEventListener('storage', (e) => {
    if (e.key === MM_MUSIC_HEARD_KEY) {
      MM_MUSIC_HEARD._cache = null;
      try { window.dispatchEvent(new CustomEvent('mm-music-heard', { detail: '*' })); } catch {}
    }
  });
} catch {}

// ── Helpers ──────────────────────────────────────────────────────────────
function MM_MUSIC_inferVol(src) {
  const m = (src || '').match(/vol(\d+)_/);
  return m ? parseInt(m[1], 10) : null;
}

function MM_MUSIC_humanizeTitle(src) {
  const name = (src || '').split('/').pop().replace(/\.[^.]+$/, '');
  const noVol = name.replace(/^vol\d+_/, '');
  return noVol.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function MM_MUSIC_findEntry(src) {
  if (!src) return null;
  return MM_MUSIC.find(t => t.src === src) || null;
}

// Returns an entry for any src — falls back to a synthesized "discovered"
// entry when the track was heard in-game but isn't in the curated catalog.
function MM_MUSIC_buildTrackForSrc(src) {
  const known = MM_MUSIC_findEntry(src);
  if (known) return known;
  return {
    id: 'heard_' + (src || '').split('/').pop().replace(/\W+/g, '_'),
    vol: MM_MUSIC_inferVol(src) || 1,
    title: MM_MUSIC_humanizeTitle(src),
    src,
    composer: '—',
    unlock: { type: 'heard' },
    __discovered: true, // not in curated catalog
  };
}

// Pick the next track to queue when the currently playing one ends.
// Order of preference:
//   1. A heard catalog track in the same vol as the current one, in catalog
//      order rotating from the current position (so the user hears variety,
//      not the same two tracks ping-ponging).
//   2. Any other heard catalog track.
//   3. null — caller should fall back to looping.
function MM_MUSIC_pickNext(currentSrc, opts = {}) {
  const heard = MM_MUSIC_HEARD.get();
  const currentEntry = MM_MUSIC_findEntry(currentSrc);
  const preferVol = opts.preferVol ?? currentEntry?.vol ?? MM_MUSIC_inferVol(currentSrc);
  const heardOthers = MM_MUSIC.filter(t => t.src !== currentSrc && heard.has(t.src));
  if (!heardOthers.length) return null;

  // 1. Same-vol rotation
  if (preferVol != null) {
    const sameVolHeard = heardOthers.filter(t => t.vol === preferVol);
    if (sameVolHeard.length) {
      const baseIdx = MM_MUSIC.findIndex(t => t.src === currentSrc);
      const start = baseIdx >= 0 ? baseIdx : 0;
      for (let i = 1; i <= MM_MUSIC.length; i++) {
        const cand = MM_MUSIC[(start + i) % MM_MUSIC.length];
        if (!cand) continue;
        if (cand.vol === preferVol && cand.src !== currentSrc && heard.has(cand.src)) {
          return cand.src;
        }
      }
    }
  }

  // 2. Any heard
  return heardOthers[0].src;
}

Object.assign(window, {
  MM_MUSIC,
  MM_MUSIC_HEARD,
  MM_MUSIC_findEntry,
  MM_MUSIC_buildTrackForSrc,
  MM_MUSIC_humanizeTitle,
  MM_MUSIC_inferVol,
  MM_MUSIC_pickNext,
});
