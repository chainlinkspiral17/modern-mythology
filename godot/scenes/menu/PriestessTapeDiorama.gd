extends "res://scenes/menu/TapeDioramaBase.gd"
## PriestessTapeDiorama — ANYA_03 cassette, side B, 14:22 in.
## Anya speaks. The cousin thing is brought up twice.

func _init() -> void:
	_diorama_title = "ANYA_03  ·  II THE HIGH PRIESTESS  ·  cassette side B"
	_diorama_hint = "click an event to seek + reveal · play scrubs at 60× · esc to leave"
	_edge_wash_color = Color(0.65, 0.65, 0.65, 0.025)  # halftone monochrome
	_tape_id = "anya_03"
	_tape_header_label = "ANYA_03"
	_tape_side = "B"
	_tape_duration_sec = 280
	_tape_archivist_note = "anya brings up 'the cousin' for the second time. she has not used a name or pronoun for this person. possibly diegetic; possibly a placeholder. i have not pressed. (the no-pressing is the recording.)"
	_tape_tick_hz = 9.0   # the archivist's metronome
	_tape_fetch_banner = "[demon_listener.02 // priestess.bbs // 1 tape recovered // integrity 0.96]"
	_events = [
		{"ts": 0,   "label": "tape begins (mid-conversation)",
			"body": "ANYA: — but you know what I mean about the cousin thing.\nE: I don't.",
			"is_speech": true, "unlock": "vol5_anya_03_start"},
		{"ts": 12,  "label": "anya defines the cousin thing",
			"body": "ANYA: The cousin thing where everybody knows the cousin and nobody — like — nobody volunteers what they know about the cousin until you say the name first.\nE: That's not — Anya — that's not a tradition, that's gossip.\nANYA: It IS a tradition. It's gossip that has become a tradition by being everyone's at once.",
			"is_speech": true, "unlock": "vol5_anya_cousin_definition"},
		{"ts": 65,  "label": "anya: 'i was going to say i'm not catholic'",
			"body": "ANYA: I'm not Catholic.\nE: I know.\nANYA: I was going to say I'm not Catholic. I forgot you knew.\n\n[Anya's anxiety-tell: she repeats decisions about what she was going to say. The deck's cousin thread is partly Anya's own pattern of redacting in real time.]",
			"is_speech": true, "unlock": "vol5_anya_redaction_tell"},
		{"ts": 102, "label": "anya: 'are you recording this'",
			"body": "ANYA: Are you recording this.\nE: Yes.\nANYA: Why.\nE: Same reason I record the other ones.\nANYA: Which is.\nE: Which is that you don't get to choose what was important yet. The cousin thing might be important. I don't know.",
			"is_speech": true, "unlock": "vol5_anya_recording_acknowledgement"},
		{"ts": 178, "label": "anya: 'it's not a his'",
			"body": "ANYA: You think the cousin thing is important.\nE: I think you brought it up twice. Once in the kitchen, once now. You haven't said the cousin's name.\nANYA: Why would I say his name.\nE: See.\nANYA: It's not a HIS. Whatever you think — it's not a — okay. Okay. Tape this part too I guess. I'm leaving. Don't —\n\n[recording ends]",
			"is_speech": true, "unlock": "vol5_anya_cousin_pronoun"},
		{"ts": 280, "label": "tape ends · annotation",
			"body": "[notes, e.l.: 'cousin' referenced in tapes 03, 07, 11. Anya has never used a name or pronoun for this person. Possibly diegetic; possibly a placeholder she is using for someone she will not name to me. To investigate: who in graustark would not be safely nameable on tape in this room — i.e., who would she suspect this tape might reach.]\n\nForward seed for vol6.",
			"is_speech": false, "unlock": "vol5_anya_archive_question"}
	]
