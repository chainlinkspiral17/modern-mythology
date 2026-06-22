# CommunityPlannedBBS.gd
# ════════════════════════════════════════════════════════════════
# Phase 2 sprint 1 · The BBS shell, foundation pass.
#
# A CRT-styled dial-up overlay that opens when Sunday's ADVANCE
# DAY fires in CommunityPlannedGame. The player picks a BBS to
# dial, the dial-up tone synthesises (DialupToneSynth), the
# carrier locks, the board list renders, the player navigates by
# single-letter board keys, picks threads, reads, hangs up.
#
# Reads:
#   res://resources/games/community_planned/bbs/dial_directory.json
#   res://resources/games/community_planned/bbs/<bbs>/board_list.json
#   res://resources/games/community_planned/bbs/<bbs>/<board>.json
#
# Writes (back to the parent CommunityPlannedGame via signal):
#   bbs_session_state {
#     visited_bbs_ids: [...],
#     read_thread_ids: [...],
#     dialled_numbers: [...],   # for hidden-board clue tracking
#   }
#
# Sprint 1 ships: dial directory · board nav · thread render · the
# hang-up handoff. Sprint 2 ships DMs, the post composer, audio,
# Frasier's ban + W2 readmission, plus the full RUST_CODE content.
# Sprint 3 ships the 4 sysop boards + SNACKS + 3 named regulars +
# THE_BACKCHANNEL. Sprint 4 ships hidden boards + Aria glossary
# annotation + unlock shelf extension.
# ════════════════════════════════════════════════════════════════
extends Control

const BBS_ROOT := "res://resources/games/community_planned/bbs/"

signal hung_up(session_state: Dictionary)

# Phosphor green palette — picks up the CRT tile from the gallery.
const C_BG := Color(0.02, 0.05, 0.03, 1.0)
const C_FG := Color(0.62, 0.96, 0.62, 1.0)
const C_FG_DIM := Color(0.42, 0.78, 0.42, 1.0)
const C_FG_BRIGHT := Color(0.86, 1.0, 0.86, 1.0)
const C_HIGHLIGHT := Color(0.96, 0.86, 0.42, 1.0)
const C_WARN := Color(0.96, 0.62, 0.42, 1.0)
const C_BORDER := Color(0.32, 0.62, 0.32, 0.85)

var _dial_directory: Dictionary = {}      # full dial_directory.json
var _current_bbs_id: String = ""          # null while in dialer
var _current_board_id: String = ""        # null while in board-list
var _current_thread_id: String = ""       # null while in thread-list
var _current_board_data: Dictionary = {}  # cached threads for the current board
# Session state — handed back to the strategic engine on hang_up.
var _visited_bbs_ids: Array = []
var _read_thread_ids: Array = []
var _dialled_numbers: Array = []
# Player state from the strategic engine (passed in via open()).
var _current_week: int = 1
var _readmitted_to_snacks: bool = false

@onready var _status_bar: RichTextLabel = $VBox/StatusBar
@onready var _main_label: RichTextLabel = $VBox/MainScroll/MainLabel
@onready var _cmd_label: Label = $VBox/CmdLine


func _ready() -> void:
	_load_directory()
	_apply_crt_theme()
	_render_dial_directory()


func _load_directory() -> void:
	var path := BBS_ROOT + "dial_directory.json"
	if not FileAccess.file_exists(path):
		push_error("[BBS] missing dial_directory.json")
		return
	var f := FileAccess.open(path, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	if typeof(parsed) == TYPE_DICTIONARY:
		_dial_directory = parsed


func _apply_crt_theme() -> void:
	var bg: ColorRect = $Background as ColorRect
	bg.color = C_BG


# Called by the strategic engine when Sunday's ADVANCE DAY hits.
# Hands in the current week + the SNACKS readmission flag so the
# directory render can hide / show entries correctly.
func open(week: int, readmitted_to_snacks: bool) -> void:
	_current_week = week
	_readmitted_to_snacks = readmitted_to_snacks
	visible = true
	_current_bbs_id = ""
	_current_board_id = ""
	_current_thread_id = ""
	_render_dial_directory()


# ── Top-level rendering: dial directory ─────────────────────────
func _render_dial_directory() -> void:
	_status_bar.clear()
	_status_bar.append_text("[color=#a8e0a8][b]DIAL-UP DIRECTORY[/b][/color]  ·  ")
	_status_bar.append_text("[color=#62c862]week %d  ·  Sunday night[/color]" % _current_week)
	_main_label.clear()
	_main_label.append_text("[color=#a8e0a8]Pick a board to dial. Press the letter key in brackets.[/color]\n\n")
	var letter_codes := "123456789"
	var i := 0
	for entry in _dial_directory.get("bbses", []):
		if not _is_directory_entry_visible(entry):
			continue
		var letter: String = letter_codes.substr(i, 1)
		i += 1
		var color: String = "#86d0a8"
		if not _is_bbs_dialable(entry):
			color = "#62a862"
		var sysop: String = String(entry.get("sysop_handle", ""))
		var where: String = String(entry.get("where", ""))
		var name: String = String(entry.get("name", ""))
		_main_label.append_text("[color=%s]  [%s]  %s[/color]" % [color, letter, name])
		_main_label.append_text("  [color=#42a042]· sysop %s · %s[/color]\n" % [sysop, where])
		# Special render for SNACKS pre-readmission
		if String(entry["id"]) == "SNACKS" and not _is_bbs_dialable(entry):
			_main_label.append_text("       [color=#866642]your tombstone is still pinned. (banned until W%d)[/color]\n" %
				int(entry.get("frasiers_ban", {}).get("in_effect_until_week", 2)))
	_main_label.append_text("\n[color=#62a862]  [Q]  hang up.  return to the board.[/color]\n")
	_cmd_label.text = "press a number to dial · Q to hang up"


func _is_directory_entry_visible(entry: Dictionary) -> bool:
	if not bool(entry.get("in_public_directory", true)):
		# SNACKS only appears in the dialer once Frasier's been
		# readmitted (W2+).
		if String(entry["id"]) == "SNACKS":
			return _readmitted_to_snacks
		return false
	return true


func _is_bbs_dialable(entry: Dictionary) -> bool:
	var from_week: int = int(entry.get("available_from_week", 1))
	if _current_week < from_week:
		return false
	if String(entry["id"]) == "SNACKS" and not _readmitted_to_snacks:
		return false
	return true


# ── Per-BBS: board list ─────────────────────────────────────────
func _render_board_list() -> void:
	var bbs_entry: Dictionary = _find_bbs(_current_bbs_id)
	if bbs_entry.is_empty():
		_render_dial_directory()
		return
	_status_bar.clear()
	_status_bar.append_text("[color=#a8e0a8][b]%s[/b][/color]" % String(bbs_entry["name"]))
	_status_bar.append_text("  ·  [color=#62c862]@%s  ·  %s baud  ·  CONNECTED[/color]" % [
		String(bbs_entry.get("dial_number", "?")),
		String(bbs_entry.get("baud", "?"))])
	_main_label.clear()
	# Masthead
	var ascii: String = String(bbs_entry.get("masthead_ascii", ""))
	if ascii != "":
		_main_label.append_text("[color=#62c862]%s[/color]\n\n" % ascii)
	# Board list
	var path: String = String(bbs_entry.get("board_list_path", ""))
	if path == "":
		_main_label.append_text("[color=#a8a86a]No boards listed yet.[/color]\n")
		_cmd_label.text = "press D to redial, Q to hang up"
		return
	var board_list: Dictionary = _load_json_strict(path)
	for b in board_list.get("boards", []):
		var vis: String = String(b.get("visibility", "public_from_start"))
		if vis == "hidden":
			continue
		_main_label.append_text("[color=#a8e0a8]  [%s]  %s[/color]" % [
			String(b["letter"]), String(b["name"])])
		_main_label.append_text("  [color=#42a042]· %s[/color]\n" %
			String(b.get("subtitle", "")))
	_main_label.append_text("\n[color=#62a862]  [D]  redial.  back to directory.[/color]\n")
	_main_label.append_text("[color=#62a862]  [Q]  hang up.  return to the board.[/color]\n")
	_cmd_label.text = "press a board letter to enter · D to redial · Q to hang up"


# ── Per-board: thread list ──────────────────────────────────────
func _render_thread_list() -> void:
	var bbs_entry: Dictionary = _find_bbs(_current_bbs_id)
	var board_list: Dictionary = _load_json_strict(String(bbs_entry.get("board_list_path", "")))
	var board: Dictionary = _find_in_array(board_list.get("boards", []), "id", _current_board_id)
	if board.is_empty():
		_render_board_list()
		return
	_status_bar.clear()
	_status_bar.append_text("[color=#a8e0a8]%s · [b]%s[/b][/color]" % [
		String(bbs_entry["name"]), String(board["name"])])
	_main_label.clear()
	_main_label.append_text("[color=#62a862]%s[/color]\n\n" % String(board.get("flavor", "")))
	# Load threads
	var threads_path: String = String(board.get("threads_path", ""))
	if threads_path == "" or not FileAccess.file_exists(threads_path):
		_main_label.append_text("[color=#a8a86a]No threads here yet.[/color]\n\n")
	else:
		_current_board_data = _load_json_strict(threads_path)
		var idx := 1
		for t in _current_board_data.get("threads", []):
			var avail: int = int(t.get("available_from_week", 1))
			if avail > _current_week:
				continue
			var read_marker: String = "  "
			if _read_thread_ids.has(String(t["id"])):
				read_marker = "· "
			_main_label.append_text("[color=#a8e0a8]  %s[%d]  %s[/color]\n" % [
				read_marker, idx, String(t["subject"])])
			_main_label.append_text("       [color=#42a042]%s · %s[/color]\n" % [
				String(t["op"].get("handle", "?")),
				String(t["op"].get("date", ""))])
			idx += 1
	_main_label.append_text("\n[color=#62a862]  [B]  back to board list.[/color]\n")
	_main_label.append_text("[color=#62a862]  [Q]  hang up.[/color]\n")
	_cmd_label.text = "press a thread number to read · B to back · Q to hang up"


# ── Per-thread: full post body ──────────────────────────────────
func _render_thread(thread_id: String) -> void:
	var bbs_entry: Dictionary = _find_bbs(_current_bbs_id)
	var thread: Dictionary = _find_in_array(_current_board_data.get("threads", []), "id", thread_id)
	if thread.is_empty():
		_render_thread_list()
		return
	_status_bar.clear()
	_status_bar.append_text("[color=#a8e0a8]%s · %s · [b]%s[/b][/color]" % [
		String(bbs_entry["name"]), _current_board_id, String(thread["subject"])])
	_main_label.clear()
	_main_label.append_text("[color=#a8e0a8][b]%s[/b][/color]\n" % String(thread["subject"]))
	_render_post(thread["op"], true)
	for r in thread.get("replies", []):
		_main_label.append_text("\n[color=#42a042]      ↳[/color]\n")
		_render_post(r, false)
	# Mark as read.
	var tid: String = String(thread["id"])
	if not _read_thread_ids.has(tid):
		_read_thread_ids.append(tid)
	_main_label.append_text("\n[color=#62a862]  [B]  back to thread list.[/color]\n")
	_main_label.append_text("[color=#62a862]  [Q]  hang up.[/color]\n")
	_cmd_label.text = "B to back · Q to hang up"


func _render_post(post: Dictionary, is_op: bool) -> void:
	var handle: String = String(post.get("handle", "?"))
	var date: String = String(post.get("date", ""))
	var body: String = String(post.get("body", ""))
	var prefix: String = "[b]" if is_op else ""
	var suffix: String = "[/b]" if is_op else ""
	_main_label.append_text("[color=#86d0a8]%s%s%s[/color]" % [prefix, handle, suffix])
	_main_label.append_text("  [color=#42a042]%s[/color]\n" % date)
	_main_label.append_text("[color=#a8e0a8]%s[/color]\n" % body)


# ── Input handling ──────────────────────────────────────────────
func _unhandled_key_input(event: InputEvent) -> void:
	if not visible: return
	if not (event is InputEventKey): return
	var k := event as InputEventKey
	if not k.pressed or k.echo: return
	var keystr: String = OS.get_keycode_string(k.keycode).to_lower()
	# Q always hangs up.
	if k.keycode == KEY_Q:
		_hang_up()
		get_viewport().set_input_as_handled()
		return
	# Where are we?
	if _current_thread_id != "":
		# In a thread — B goes back.
		if k.keycode == KEY_B:
			_current_thread_id = ""
			_render_thread_list()
			get_viewport().set_input_as_handled()
		return
	if _current_board_id != "":
		# In a thread list — B goes back, digit picks thread.
		if k.keycode == KEY_B:
			_current_board_id = ""
			_render_board_list()
			get_viewport().set_input_as_handled()
			return
		if k.keycode >= KEY_1 and k.keycode <= KEY_9:
			var n: int = k.keycode - KEY_0
			_pick_thread_by_index(n)
			get_viewport().set_input_as_handled()
		return
	if _current_bbs_id != "":
		# In a board list — D redials, letter picks board.
		if k.keycode == KEY_D:
			_current_bbs_id = ""
			_render_dial_directory()
			get_viewport().set_input_as_handled()
			return
		_pick_board_by_letter(keystr.to_upper())
		get_viewport().set_input_as_handled()
		return
	# Dialer — digit picks bbs.
	if k.keycode >= KEY_1 and k.keycode <= KEY_9:
		var d: int = k.keycode - KEY_0
		_pick_bbs_by_index(d)
		get_viewport().set_input_as_handled()


func _pick_bbs_by_index(idx: int) -> void:
	var visible_entries: Array = []
	for e in _dial_directory.get("bbses", []):
		if _is_directory_entry_visible(e):
			visible_entries.append(e)
	if idx < 1 or idx > visible_entries.size():
		return
	var entry: Dictionary = visible_entries[idx - 1]
	if not _is_bbs_dialable(entry):
		return
	_current_bbs_id = String(entry["id"])
	var num: String = String(entry.get("dial_number", entry.get("dial_number_after_ban_rotation", entry.get("dial_number_initial", ""))))
	if num != "" and not _dialled_numbers.has(num):
		_dialled_numbers.append(num)
	if not _visited_bbs_ids.has(_current_bbs_id):
		_visited_bbs_ids.append(_current_bbs_id)
	_render_board_list()


func _pick_board_by_letter(letter: String) -> void:
	var bbs_entry: Dictionary = _find_bbs(_current_bbs_id)
	var board_list: Dictionary = _load_json_strict(String(bbs_entry.get("board_list_path", "")))
	for b in board_list.get("boards", []):
		if String(b.get("visibility", "")) == "hidden":
			continue
		if String(b.get("letter", "")).to_upper() == letter:
			_current_board_id = String(b["id"])
			_render_thread_list()
			return


func _pick_thread_by_index(n: int) -> void:
	# n is 1-indexed against the *visible* threads in this board.
	var idx := 0
	for t in _current_board_data.get("threads", []):
		var avail: int = int(t.get("available_from_week", 1))
		if avail > _current_week:
			continue
		idx += 1
		if idx == n:
			_current_thread_id = String(t["id"])
			_render_thread(_current_thread_id)
			return


# ── Hang up ─────────────────────────────────────────────────────
func _hang_up() -> void:
	var session: Dictionary = {
		"visited_bbs_ids": _visited_bbs_ids.duplicate(),
		"read_thread_ids": _read_thread_ids.duplicate(),
		"dialled_numbers": _dialled_numbers.duplicate(),
	}
	visible = false
	hung_up.emit(session)


# ── Helpers ─────────────────────────────────────────────────────
func _find_bbs(id: String) -> Dictionary:
	for e in _dial_directory.get("bbses", []):
		if String(e.get("id", "")) == id:
			return e
	return {}


func _find_in_array(arr: Array, key: String, value: String) -> Dictionary:
	for entry in arr:
		if String(entry.get(key, "")) == value:
			return entry
	return {}


func _load_json_strict(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	if typeof(parsed) != TYPE_DICTIONARY:
		return {}
	return parsed
