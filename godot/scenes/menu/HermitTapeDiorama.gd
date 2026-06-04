extends "res://scenes/menu/TapeDioramaBase.gd"
## HermitTapeDiorama — HERMIT_01 cassette, side A, 47:11.
## Mostly silence. The Hermit speaks twice and says one word.
## Elicia broke her no-tape agreement once and kept it after.

func _init() -> void:
    _diorama_title = "HERMIT_01  ·  IX THE HERMIT  ·  cassette side A"
    _diorama_hint = "click an event to seek + reveal · play scrubs at 60× · esc to leave"
    _edge_wash_color = Color(0.95, 0.65, 0.30, 0.025)  # lantern amber
    _tape_id = "hermit_01"
    _tape_header_label = "HERMIT_01"
    _tape_side = "A"
    _tape_duration_sec = 2831
    _tape_archivist_note = "no HERMIT_02 will exist. he heard me. he did not see me. i was sitting farther back than that. he knew the tape was running because he knew it would be. he asked me to stop. i did not. fine, he said. (recorded.) i have not made another."
    _tape_tick_hz = 1.0   # lantern fuel-tick
    _tape_fetch_banner = "[demon_listener.02 // priestess.bbs // 1 tape recovered // integrity 0.94 (events: 7)]"
    _events = [
        {"ts": 0,    "label": "tape begins",
            "body": "ambient. crickets, faint. very faint water — the river is far enough that this is residual in the air, not heard. no human sound.",
            "is_speech": false, "unlock": "vol5_hermit_tape_begin"},
        {"ts": 74,   "label": "lantern lit",
            "body": "a brief crackle of fuel going to flame. it is so quiet on this tape that the crackle is the loudest event recorded so far.",
            "is_speech": false, "unlock": ""},
        {"ts": 202,  "label": "he breathes",
            "body": "he breathes in. he breathes out. he sits down. cloth on grass. very small.",
            "is_speech": false, "unlock": ""},
        {"ts": 431,  "label": "first word — 'okay'",
            "body": "HERMIT: \"okay.\"\n\nOne word, very flat. He is silent for the next twelve minutes.",
            "is_speech": true, "unlock": "vol5_hermit_first_word"},
        {"ts": 1185, "label": "his ten-word line",
            "body": "HERMIT: \"i did not realize i was waiting for the lantern to gutter.\"\n\nThe lantern is not guttering. The lantern is fine. He did not realize. That is the report.",
            "is_speech": true, "unlock": "vol5_hermit_lantern_realization"},
        {"ts": 2531, "label": "he hears the tape",
            "body": "HERMIT: \"elicia, you can stop the tape.\"\n\nThree words. I did not stop the tape.\n\nHERMIT: \"fine.\"\n\nHe is silent for the rest of the tape.",
            "is_speech": true, "unlock": "vol5_hermit_caught_recording"},
        {"ts": 2831, "label": "tape ends",
            "body": "the recording ends. he has been silent for four minutes forty seconds. the lantern is still lit.\n\n[handwritten annotation, e.l.: HERMIT_01 because there will not be a HERMIT_02. that is the part i agreed to.]",
            "is_speech": false, "unlock": "vol5_hermit_tape_end"}
    ]
