extends "res://scenes/menu/TapeDioramaBase.gd"
## JudgementTapeDiorama — ENSEMBLE_01, full 50:00.
## The cast holds the gesture for fifty minutes; speaks five
## sentences. Faith thumps her tail twice. The Frog croaks three
## times. The chapter is the gathering held.

func _init() -> void:
    _diorama_title = "ENSEMBLE_01  ·  XX JUDGEMENT  ·  cassette side A (full)"
    _diorama_hint = "click an event to seek + reveal · play scrubs at 60× · esc to leave"
    _edge_wash_color = Color(0.50, 0.80, 0.95, 0.025)  # cyan neon
    _tape_id = "ensemble_01"
    _tape_header_label = "ENSEMBLE_01"
    _tape_side = "A"
    _tape_duration_sec = 3000
    _tape_archivist_note = "recorded from the back, third row, behind the curtain. the cast held the gesture for fifty minutes. five lines were spoken in that time. the chapter is the holding, not the speaking. the recording was for me, not for them."
    _tape_tick_hz = 0.0   # the gesture is silent; no substrate tick
    _tape_fetch_banner = "[demon_listener.02 // ensemble.bbs // 1 recording recovered // integrity 0.97 (refusal noted)]"
    _events = [
        {"ts": 18,  "label": "john shifts his weight",
            "body": "john (the fool) shifts his weight. small step forward, small step back. nobody else moves.",
            "is_speech": false, "unlock": ""},
        {"ts": 33,  "label": "FRASIER speaks first",
            "body": "FRASIER: \"we are doing this without him.\"\n\n(quietly, not to the others, on mic.)\n\nFRASIER: \"the chapter is the gathering. the chapter is not the verdict. the gathering is enough for sunday.\"\n\nThe absent figure is plural — Antonio, Simon, maybe more. The deck's first refusal to consummate the verdict is voiced.",
            "is_speech": true, "unlock": "vol5_judgement_frasier_opening"},
        {"ts": 74,  "label": "natalie tests the gesture",
            "body": "natalie (the moon, also the hanged man) lowers her arm a few centimeters and raises it again. she is not breaking the gesture; she is making sure she can break the gesture if she needs to.",
            "is_speech": false, "unlock": ""},
        {"ts": 88,  "label": "erica stares at the empty center",
            "body": "erica (the wheel, also justice) does not move. she is looking at the empty center. she is not looking at anyone else. she has been looking at the empty center since the chapter began.",
            "is_speech": false, "unlock": "vol5_judgement_erica_center_stare"},
        {"ts": 104, "label": "FRANK: the trumpet line",
            "body": "FRANK: \"we are not waiting for a trumpet. we are waiting for sunday to end.\"\n\nThe chapter's working method made diegetic. The deck refuses the trumpet and substitutes patience.",
            "is_speech": true, "unlock": "vol5_judgement_frank_trumpet"},
        {"ts": 121, "label": "maya sits — quent's recorded permission",
            "body": "maya (the hierophant kneeler) lowers her arm. she lowers it for the right reason: she is too young to hold the gesture all chapter and the deck is letting her sit down.\n\nMAYA: [whispers, on mic clearly:] \"father quent says we don't have to hold it the whole chapter. he says holding it is the beginning. he says the rest is just sitting in the room with it held.\"\n\nThe hierophant's institution reaches into XX through a child's whispered remembrance of an instruction the priest is not in this room to give.",
            "is_speech": true, "unlock": "vol5_judgement_maya_sits"},
        {"ts": 168, "label": "DANTE: 'the dancer is not coming'",
            "body": "DANTE: \"the dancer is not coming. the dancer was always not coming. the wreath closes around the absence. let it.\"\n\nFlat, low, audible. The World's dancer — the painted card's central absence at XXI — named in advance at XX by the Emperor who has been Bed 6 all week.",
            "is_speech": true, "unlock": "vol5_judgement_dante_dancer"},
        {"ts": 208, "label": "FIGURE: 'i poured the water already'",
            "body": "FIGURE (un-named, signed in the deck with a dash): \"i poured the water already. the chapter is whatever happens after the water is in the river.\"\n\nThe Strength/Star figure speaks. Her one sentence on the recording closes the deck's water-pour register.",
            "is_speech": true, "unlock": "vol5_judgement_figure_river"},
        {"ts": 228, "label": "faith's tail thump",
            "body": "faith (the dog, not the lion, the dog, at the feet of the figure) — sound: tail thump, twice, on the stage. audible on mic. attributed to faith.\n\nThe deck's most enduring presence is also the only audible participant who isn't speaking words.",
            "is_speech": false, "unlock": "vol5_judgement_faith_thump"},
        {"ts": 252, "label": "frog croaks (1 of 3)",
            "body": "the frog (XXI, oracle, somewhere offstage near the river) — sound: one single low croak, audible because the chapter is quiet. attributed to the frog.\n\nFROG: [croak.]",
            "is_speech": false, "unlock": "vol5_judgement_frog_1"},
        {"ts": 1108, "label": "frank smiles (annotation only)",
            "body": "(e.l. annotation, no audio: frank smiled once, briefly, at minute 22. i was the only one positioned to see it. i did not call attention to it. the smile was for me. the smile is part of this archive but not part of this recording.)",
            "is_speech": false, "unlock": "vol5_judgement_frank_smile"},
        {"ts": 1580, "label": "frog croaks (2 of 3)",
            "body": "FROG: [croak.] (audible.)",
            "is_speech": false, "unlock": ""},
        {"ts": 2210, "label": "natalie closes her eyes",
            "body": "(annotation: natalie eventually closed her eyes. she did not break the gesture; she stopped looking. that is its own decision.)",
            "is_speech": false, "unlock": ""},
        {"ts": 2680, "label": "frog croaks (3 of 3)",
            "body": "FROG: [croak.] (the last sound on the recording besides ambient.)",
            "is_speech": false, "unlock": "vol5_judgement_frog_3"},
        {"ts": 3000, "label": "tape ends (gathering continues)",
            "body": "tape ends. the cast continued holding the gesture for an unmeasured interval after the recording stopped. the gathering ended when the world began. when the world began is not in this recording.\n\n[annotation, e.l.: the chapter is the gathering held for fifty minutes. the verdict was not rendered. the rendering of the gathering is the chapter. it is enough.]",
            "is_speech": false, "unlock": "vol5_judgement_tape_end"}
    ]
