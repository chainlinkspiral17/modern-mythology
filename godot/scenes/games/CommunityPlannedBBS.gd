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
const DM_ROOT := "res://resources/games/community_planned/bbs/dms/"
const DIALUP_SYNTH_SCRIPT := preload("res://scripts/DialupToneSynth.gd")

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
var _hidden_boards_def: Dictionary = {}   # full hidden_boards.json
var _aria_glossary: Dictionary = {}       # full aria_glossary.json
var _current_bbs_id: String = ""          # null while in dialer
var _current_board_id: String = ""        # null while in board-list
var _current_thread_id: String = ""       # null while in thread-list
var _current_board_data: Dictionary = {}  # cached threads for the current board
# DM panel state — orthogonal to board nav. Accessed via `M` (mail).
var _in_dm_view: bool = false             # true when DM panel is rendering
var _current_dm_canonical: String = ""    # canonical_character_id of open DM
# Dial-input mode — orthogonal to nav. Activated by `N` from dialer.
var _in_dial_input: bool = false
var _dial_input_buffer: String = ""
# Glossary annotation overlay — orthogonal to nav. Activated by `G`
# once unlocked (snacks_bleached_counter_entries_read_min_6 + W11).
var _in_glossary_view: bool = false
var _glossary_unlocked: bool = false
# Session state — handed back to the strategic engine on hang_up.
var _visited_bbs_ids: Array = []
var _read_thread_ids: Array = []
var _dialled_numbers: Array = []
var _dm_replies_this_session: Array = []    # [{canonical, week, option_idx, effects}]
var _artifact_unlocks_this_session: Array = []  # [{artifact_id, kind, source_thread_id}]
var _hidden_boards_discovered_this_session: Array = []  # ids unlocked this session
# Strategic effects collected during the BBS session and applied by
# the engine on hang_up. Each entry is a {kind, ...} dict; the engine
# routes them through _exec_effect or handles them inline.
var _strategic_effects_this_session: Array = []
# Per-session entry tracking for hidden boards that have once-per-night
# strategic effects (THE_RIVER_HOUSE cover cost, THE_BASEMENT burn -1).
var _hidden_board_entries_this_session: Dictionary = {}
# Player state from the strategic engine (passed in via open()).
var _current_week: int = 1
var _readmitted_to_snacks: bool = false
# DM read-state passed in from the strategic engine (which beat
# index each character's DM was last read up to). On hang_up the
# engine updates from the session.
var _dm_read_to_week: Dictionary = {}       # canonical_character_id → last week read
# Hidden-board discovery state from the strategic engine. Map of
# hidden_board_id → true once unlocked.
var _discovered_hidden_boards: Dictionary = {}
var _unlocked_artifacts: Array = []         # artifact_ids already on the shelf
# Canon vars snapshot from the engine. Used to drive branch-filtered
# DM beats — a beat tagged {if_branch: "rebind", branch_key: "aria_w11_choice"}
# only renders if _canon_vars[branch_key] matches the branch tag.
var _canon_vars: Dictionary = {}

@onready var _status_bar: RichTextLabel = $VBox/StatusBar
@onready var _main_label: RichTextLabel = $VBox/MainScroll/MainLabel
@onready var _cmd_label: Label = $VBox/CmdLine


func _ready() -> void:
	add_to_group("ui")   # F4 master-toggle sweep (CLAUDE.md hard rule)
	_load_directory()
	_load_hidden_boards()
	_load_glossary()
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


func _load_hidden_boards() -> void:
	var path := BBS_ROOT + "hidden_boards.json"
	if not FileAccess.file_exists(path):
		return
	var f := FileAccess.open(path, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	if typeof(parsed) == TYPE_DICTIONARY:
		_hidden_boards_def = parsed


func _load_glossary() -> void:
	var path := BBS_ROOT + "aria_glossary.json"
	if not FileAccess.file_exists(path):
		return
	var f := FileAccess.open(path, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	if typeof(parsed) == TYPE_DICTIONARY:
		_aria_glossary = parsed


func _apply_crt_theme() -> void:
	var bg: ColorRect = $Background as ColorRect
	bg.color = C_BG


# Called by the strategic engine when Sunday's ADVANCE DAY hits.
# Hands in the current week + the SNACKS readmission flag so the
# directory render can hide / show entries correctly.
func open(week: int, readmitted_to_snacks: bool, dm_read_to_week: Dictionary = {},
		discovered_hidden_boards: Dictionary = {}, unlocked_artifacts: Array = [],
		glossary_unlocked: bool = false, canon_vars: Dictionary = {}) -> void:
	_canon_vars = canon_vars.duplicate()
	_current_week = week
	_readmitted_to_snacks = readmitted_to_snacks
	_dm_read_to_week = dm_read_to_week
	_discovered_hidden_boards = discovered_hidden_boards.duplicate()
	_unlocked_artifacts = unlocked_artifacts.duplicate()
	_glossary_unlocked = glossary_unlocked
	visible = true
	_current_bbs_id = ""
	_current_board_id = ""
	_current_thread_id = ""
	_in_dm_view = false
	_current_dm_canonical = ""
	_in_dial_input = false
	_dial_input_buffer = ""
	_in_glossary_view = false
	_dm_replies_this_session.clear()
	_artifact_unlocks_this_session.clear()
	_hidden_boards_discovered_this_session.clear()
	_strategic_effects_this_session.clear()
	_hidden_board_entries_this_session.clear()
	# Auto-check the BACKCHANNEL breadth condition on open so the
	# unlock surfaces immediately if the player crossed the threshold
	# during the previous BBS night.
	_check_backchannel_breadth()
	# Glossary self-unlock: if engine didn't pass true but the
	# cumulative SNACKS reads satisfy the threshold and the week is
	# reached, flip it on. Lets the unlock fire mid-summer without a
	# round-trip through the engine.
	if not _glossary_unlocked and _current_week >= int(_aria_glossary.get("unlock_week", 11)):
		if _count_snacks_threads_read() >= 6:
			_glossary_unlocked = true
	_render_dial_directory()


func _count_snacks_threads_read() -> int:
	var n := 0
	for tid in _read_thread_ids:
		if String(tid).begins_with("SN_"):
			n += 1
	return n


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
	_main_label.append_text("\n[color=#62a862]  [N]  dial a number you've heard about.[/color]\n")
	_main_label.append_text("[color=#62a862]  [Q]  hang up.  return to the board.[/color]\n")
	if _glossary_unlocked:
		_main_label.append_text("[color=#c8a842]  [G]  glossary · the substitutions are now legible.[/color]\n")
	_cmd_label.text = "press a digit to dial · N to type a number · Q to hang up"


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
			if not bool(_discovered_hidden_boards.get(String(b["id"]), false)):
				continue
			# Discovered hidden board — render with a quiet marker.
			_main_label.append_text("[color=#e0c862]  [%s]  %s[/color]" % [
				String(b["letter"]), String(b["name"])])
			_main_label.append_text("  [color=#c8a842]· %s[/color]\n" %
				String(b.get("subtitle", "")))
			continue
		_main_label.append_text("[color=#a8e0a8]  [%s]  %s[/color]" % [
			String(b["letter"]), String(b["name"])])
		_main_label.append_text("  [color=#42a042]· %s[/color]\n" %
			String(b.get("subtitle", "")))
	_main_label.append_text("\n[color=#62a862]  [D]  redial.  back to directory.[/color]\n")
	_main_label.append_text("[color=#62a862]  [Q]  hang up.  return to the board.[/color]\n")
	if _glossary_unlocked:
		_main_label.append_text("[color=#c8a842]  [G]  glossary · register for this board.[/color]\n")
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
	# If the thread carries a file_unlock and we haven't surfaced it
	# yet (this session OR in the persistent shelf), push it.
	var unlock: Dictionary = thread.get("file_unlock", {})
	if not unlock.is_empty() and bool(unlock.get("unlocks_after_read", false)):
		var aid: String = String(unlock.get("artifact_id", ""))
		if aid != "" and not _unlocked_artifacts.has(aid):
			var already_this_session := false
			for u in _artifact_unlocks_this_session:
				if String((u as Dictionary).get("artifact_id", "")) == aid:
					already_this_session = true
					break
			if not already_this_session:
				_artifact_unlocks_this_session.append({
					"artifact_id": aid,
					"kind": String(unlock.get("kind", "")),
					"source_thread_id": tid,
					"notes": String(unlock.get("notes", "")),
				})
				_main_label.append_text("\n[color=#e0c862][b]artifact unlocked:[/b] %s[/color]" % aid)
				_main_label.append_text("  [color=#c8a842](%s)[/color]\n" % String(unlock.get("kind", "")))
	# Glossary footnote: if the glossary is unlocked and the thread's
	# body contains any of this register's terms, surface them
	# below the thread as a small key.
	if _glossary_unlocked and _current_bbs_id != "":
		var combined_body: String = String(thread.get("op", {}).get("body", ""))
		for r in thread.get("replies", []):
			combined_body += " " + String((r as Dictionary).get("body", ""))
		var found_terms: Array = _glossary_terms_in_body(combined_body, _current_bbs_id)
		if not found_terms.is_empty():
			_main_label.append_text("\n[color=#42a042]── glossary footnote ──[/color]\n")
			for entry in found_terms:
				_main_label.append_text("[color=#e0c862]  %s[/color]  [color=#42a042]= %s[/color]\n" % [
					String((entry as Dictionary)["term"]),
					String((entry as Dictionary)["canonical"])])
	# Re-check breadth — reading the right thread can flip the
	# BACKCHANNEL unlock state mid-session.
	_check_backchannel_breadth()
	# THE_GROVE intel: once the player has read 2+ threads on
	# THE_GROVE in a single session, queue the prebuffered-anomaly
	# hint for the engine.
	if _current_board_id == "THE_GROVE":
		var grove_reads := 0
		for r_tid in _read_thread_ids:
			if String(r_tid).begins_with("TG_"):
				grove_reads += 1
		var already_queued := false
		for ef in _strategic_effects_this_session:
			if String((ef as Dictionary).get("kind", "")) == "the_grove_intel":
				already_queued = true
				break
		if grove_reads >= 2 and not already_queued:
			_strategic_effects_this_session.append({
				"kind": "the_grove_intel",
				"reason": "the_grove_two_or_more_threads_read",
			})
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
	if _glossary_unlocked and _current_bbs_id != "":
		var annotated_body: String = _annotate_body_with_glossary(body, _current_bbs_id)
		_main_label.append_text("[color=#a8e0a8]%s[/color]\n" % annotated_body)
	else:
		_main_label.append_text("[color=#a8e0a8]%s[/color]\n" % body)


# Inline glossary annotation. Once unlocked, scan the post body for
# this board's register-specific terms and render them in amber.
# We do a longest-first match so multi-word terms ("the third bell",
# "the lyric") highlight before shorter contained terms. Cheap O(n*m)
# scan — board posts are short, term list is 20.
func _annotate_body_with_glossary(body: String, bbs_id: String) -> String:
	var terms: Array = []
	for concept in _aria_glossary.get("concepts", []):
		var per_sysop: Dictionary = concept.get("per_sysop", {})
		var term: String = String(per_sysop.get(bbs_id, ""))
		if term == "":
			continue
		terms.append(term)
	terms.sort_custom(func(a, b): return String(a).length() > String(b).length())
	var annotated: String = body
	for term in terms:
		var lower_term: String = String(term).to_lower()
		# Case-insensitive replacement: walk through the body finding
		# every case-variant occurrence and wrap it in amber. Skip
		# wraps that would land inside an existing BBCode tag.
		var idx := 0
		while true:
			var found: int = annotated.to_lower().find(lower_term, idx)
			if found < 0:
				break
			# Guard against double-wrapping: check the 8 chars before
			# for our own color tag.
			var lookback: String = annotated.substr(max(0, found - 10), 10)
			if lookback.find("[color=#e0c862]") >= 0:
				idx = found + lower_term.length()
				continue
			var original: String = annotated.substr(found, lower_term.length())
			var wrapped: String = "[color=#e0c862]" + original + "[/color]"
			annotated = annotated.substr(0, found) + wrapped + annotated.substr(found + lower_term.length())
			idx = found + wrapped.length()
	return annotated


func _glossary_terms_in_body(body: String, bbs_id: String) -> Array:
	var out: Array = []
	var seen: Dictionary = {}
	var body_lower: String = body.to_lower()
	for concept in _aria_glossary.get("concepts", []):
		var per_sysop: Dictionary = concept.get("per_sysop", {})
		var term: String = String(per_sysop.get(bbs_id, ""))
		if term == "" or seen.has(term):
			continue
		if body_lower.find(term.to_lower()) < 0:
			continue
		seen[term] = true
		out.append({
			"term": term,
			"canonical": String(concept.get("canonical", "")),
		})
	return out


# ── Input handling ──────────────────────────────────────────────
func _unhandled_key_input(event: InputEvent) -> void:
	if not visible: return
	if not (event is InputEventKey): return
	var k := event as InputEventKey
	if not k.pressed or k.echo: return
	var keystr: String = OS.get_keycode_string(k.keycode).to_lower()
	# Dial-input mode consumes all keys until ENTER or ESC.
	if _in_dial_input:
		_handle_dial_input_key(k)
		get_viewport().set_input_as_handled()
		return
	# Q always hangs up.
	if k.keycode == KEY_Q:
		_hang_up()
		get_viewport().set_input_as_handled()
		return
	# M from anywhere opens the DM panel. M from inside the DM
	# panel goes back to wherever you were before.
	if k.keycode == KEY_M:
		if _in_dm_view:
			_in_dm_view = false
			_current_dm_canonical = ""
			_render_current_view()
		else:
			_in_dm_view = true
			_render_dm_list()
		get_viewport().set_input_as_handled()
		return
	if _in_dm_view:
		_handle_dm_input(k)
		get_viewport().set_input_as_handled()
		return
	# G opens the glossary annotation overlay once unlocked. G
	# again (or B) closes back to the previous view.
	if k.keycode == KEY_G and _glossary_unlocked:
		if _in_glossary_view:
			_in_glossary_view = false
			_render_current_view()
		else:
			_in_glossary_view = true
			_render_glossary_view()
		get_viewport().set_input_as_handled()
		return
	if _in_glossary_view:
		if k.keycode == KEY_B:
			_in_glossary_view = false
			_render_current_view()
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
	# Dialer — digit picks bbs; N opens free dial.
	if k.keycode == KEY_N:
		_enter_dial_input()
		get_viewport().set_input_as_handled()
		return
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
	# Play the 8-second dial-up handshake on first dial-in to this
	# BBS. Subsequent dials in the same session skip the audio so the
	# board reads fast on a re-visit.
	if num != "":
		_play_dialup(num)
	_render_board_list()


# Audio hookup. DialupToneSynth is a child Node created on demand;
# the audio plays asynchronously while the board list renders in
# the foreground, which is the period-correct experience (the
# noise was the wait; the board appearing was when the noise
# stopped). Re-dials within a session skip the audio.
var _dialup_played_this_session: Dictionary = {}  # bbs_id → bool

func _play_dialup(dial_number: String) -> void:
	if _dialup_played_this_session.get(_current_bbs_id, false):
		return
	_dialup_played_this_session[_current_bbs_id] = true
	var synth = DIALUP_SYNTH_SCRIPT.new()
	add_child(synth)
	synth.play_full_sequence(dial_number)
	# Cleanup is deferred — the synth queue_frees itself after the
	# sequence completes via a connected timer.
	synth.create_tween().tween_callback(synth.queue_free).set_delay(9.0)


func _pick_board_by_letter(letter: String) -> void:
	var bbs_entry: Dictionary = _find_bbs(_current_bbs_id)
	var board_list: Dictionary = _load_json_strict(String(bbs_entry.get("board_list_path", "")))
	for b in board_list.get("boards", []):
		# Hidden boards are pickable only if discovered.
		if String(b.get("visibility", "")) == "hidden":
			if not bool(_discovered_hidden_boards.get(String(b["id"]), false)):
				continue
		if String(b.get("letter", "")).to_upper() == letter:
			_current_board_id = String(b["id"])
			_on_board_entered(String(b["id"]))
			_render_thread_list()
			return


func _on_board_entered(board_id: String) -> void:
	# Once-per-session strategic effects when the player enters a
	# hidden board with a documented cost / benefit. The actual
	# effect is queued for the engine to apply on hang_up.
	if _hidden_board_entries_this_session.get(board_id, false):
		return
	_hidden_board_entries_this_session[board_id] = true
	match board_id:
		"THE_RIVER_HOUSE":
			_strategic_effects_this_session.append({
				"kind": "spend_cover",
				"region": "graustark",
				"amount": 1,
				"reason": "the_river_house_visit",
			})
		"THE_BASEMENT":
			_strategic_effects_this_session.append({
				"kind": "demon_burn_reduction",
				"amount": 1,
				"reason": "the_basement_visit",
			})


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


# ── DM panel ────────────────────────────────────────────────────
# The DM panel is orthogonal to board nav. M from anywhere opens it;
# M again closes it back to whatever view you were at. Files live in
# res://resources/games/community_planned/bbs/dms/<canonical>.json
# and are listed in dms/index.json so we don't depend on directory
# scanning at runtime (works inside exported PCKs).

# Cached list of DM threads available this session, populated lazily.
var _dm_threads_cache: Array = []           # [{canonical, display_name, file}]
var _dm_pending_choices: Array = []         # current choice options shown
var _dm_pending_choice_week: int = -1       # week index of the beat awaiting reply


func _render_current_view() -> void:
	# Dispatches to whichever nav level the player was at when they
	# opened the DM panel. Mirrors the dispatch in _unhandled_key_input.
	if _current_thread_id != "":
		_render_thread(_current_thread_id)
	elif _current_board_id != "":
		_render_thread_list()
	elif _current_bbs_id != "":
		_render_board_list()
	else:
		_render_dial_directory()


func _load_dm_index() -> void:
	_dm_threads_cache.clear()
	var index_path := DM_ROOT + "index.json"
	if not FileAccess.file_exists(index_path):
		return
	var idx: Dictionary = _load_json_strict(index_path)
	for entry in idx.get("threads", []):
		var canonical: String = String(entry.get("canonical_character_id", ""))
		if canonical == "":
			continue
		var available_from: int = int(entry.get("available_from_week", 1))
		if _current_week < available_from:
			continue
		_dm_threads_cache.append(entry)


func _render_dm_list() -> void:
	_dm_pending_choices.clear()
	_dm_pending_choice_week = -1
	_current_dm_canonical = ""
	_load_dm_index()
	_status_bar.clear()
	_status_bar.append_text("[color=#a8e0a8][b]DM · DIRECT MESSAGES[/b][/color]")
	_status_bar.append_text("  ·  [color=#62c862]week %d[/color]" % _current_week)
	_main_label.clear()
	if _dm_threads_cache.is_empty():
		_main_label.append_text("[color=#a8a86a]No direct messages yet. Sundays will fill this up.[/color]\n\n")
	else:
		_main_label.append_text("[color=#a8e0a8]Press a number to open a thread.[/color]\n\n")
		var i := 1
		for entry in _dm_threads_cache:
			var canonical: String = String(entry["canonical_character_id"])
			var name: String = String(entry.get("display_name", canonical))
			var beats_path: String = DM_ROOT + String(entry.get("file", canonical + ".json"))
			var unread: int = _dm_unread_count(canonical, beats_path)
			var marker: String = "  "
			if unread > 0:
				marker = "* "
			_main_label.append_text("[color=#a8e0a8]  %s[%d]  %s[/color]" % [marker, i, name])
			if unread > 0:
				_main_label.append_text("  [color=#e0c862]· %d new[/color]\n" % unread)
			else:
				_main_label.append_text("  [color=#42a042]· read[/color]\n")
			i += 1
	_main_label.append_text("\n[color=#62a862]  [M]  close DM panel.[/color]\n")
	_main_label.append_text("[color=#62a862]  [Q]  hang up.[/color]\n")
	_cmd_label.text = "press a number to open · M to close panel · Q to hang up"


func _dm_unread_count(canonical: String, beats_path: String) -> int:
	if not FileAccess.file_exists(beats_path):
		return 0
	var data: Dictionary = _load_json_strict(beats_path)
	var read_to: int = int(_dm_read_to_week.get(canonical, 0))
	var count := 0
	for beat in data.get("beats", []):
		var week: int = int(beat.get("week", 1))
		if week > _current_week or week <= read_to:
			continue
		var if_branch: String = String(beat.get("if_branch", ""))
		if if_branch != "":
			var branch_key: String = String(beat.get("branch_key", "aria_w11_choice"))
			if String(_canon_vars.get(branch_key, "")) != if_branch:
				continue
		count += 1
	return count


func _render_dm_view(canonical: String) -> void:
	_current_dm_canonical = canonical
	_dm_pending_choices.clear()
	_dm_pending_choice_week = -1
	var entry: Dictionary = _find_in_array(_dm_threads_cache, "canonical_character_id", canonical)
	if entry.is_empty():
		_render_dm_list()
		return
	var name: String = String(entry.get("display_name", canonical))
	var beats_path: String = DM_ROOT + String(entry.get("file", canonical + ".json"))
	var data: Dictionary = _load_json_strict(beats_path)
	_status_bar.clear()
	_status_bar.append_text("[color=#a8e0a8][b]DM · %s[/b][/color]" % name)
	_status_bar.append_text("  ·  [color=#62c862]week %d[/color]" % _current_week)
	_main_label.clear()
	var read_to: int = int(_dm_read_to_week.get(canonical, 0))
	var advanced_read_to: int = read_to
	var awaiting_choice_at_week: int = -1
	for beat in data.get("beats", []):
		var week: int = int(beat.get("week", 1))
		if week > _current_week:
			break
		if awaiting_choice_at_week >= 0:
			# The previous beat had a choice still unanswered; don't
			# render past it until the player replies.
			break
		# Branch filter: beats tagged with if_branch only render when
		# the player's recorded choice matches. Allows a single DM
		# file to ship branch-specific post-decision beats.
		var if_branch: String = String(beat.get("if_branch", ""))
		if if_branch != "":
			var branch_key: String = String(beat.get("branch_key", "aria_w11_choice"))
			var current_branch: String = String(_canon_vars.get(branch_key, ""))
			if current_branch != if_branch:
				continue
		var from: String = String(beat.get("from", "them"))
		var body: String = String(beat.get("body", ""))
		var date_label: String = String(beat.get("date", "W%d" % week))
		var is_unread: bool = (week > read_to)
		var who_color: String = "#86d0a8" if from == "them" else "#e0c862"
		var who_label: String = name if from == "them" else "you"
		var body_color: String = "#a8e0a8" if is_unread else "#62a862"
		_main_label.append_text("[color=%s][b]%s[/b][/color]  [color=#42a042]%s[/color]\n" % [
			who_color, who_label, date_label])
		_main_label.append_text("[color=%s]%s[/color]\n\n" % [body_color, body])
		var choices: Array = beat.get("choices", [])
		# If this is a "them" beat with choices for the player and the
		# player hasn't replied yet, surface the picker.
		if choices.size() > 0 and from == "them" and is_unread:
			_dm_pending_choices = choices
			_dm_pending_choice_week = week
			awaiting_choice_at_week = week
			_main_label.append_text("[color=#e0c862]  reply:[/color]\n")
			var idx := 1
			for choice in choices:
				_main_label.append_text("[color=#e0c862]   [%d]  %s[/color]\n" % [
					idx, String(choice.get("label", ""))])
				idx += 1
			_main_label.append_text("\n")
		else:
			if is_unread:
				advanced_read_to = max(advanced_read_to, week)
	# Advance the read pointer for beats that didn't gate on a choice.
	if advanced_read_to > read_to:
		_dm_read_to_week[canonical] = advanced_read_to
	_main_label.append_text("\n[color=#62a862]  [B]  back to DM list.[/color]\n")
	_main_label.append_text("[color=#62a862]  [M]  close DM panel.[/color]\n")
	if _dm_pending_choices.size() > 0:
		_cmd_label.text = "press a number to reply · B to back · M to close"
	else:
		_cmd_label.text = "B to back · M to close · Q to hang up"


func _handle_dm_input(k: InputEventKey) -> void:
	if _current_dm_canonical == "":
		# On the DM list — digit picks a thread.
		if k.keycode >= KEY_1 and k.keycode <= KEY_9:
			var n: int = k.keycode - KEY_0
			if n >= 1 and n <= _dm_threads_cache.size():
				var entry: Dictionary = _dm_threads_cache[n - 1]
				_render_dm_view(String(entry["canonical_character_id"]))
		return
	# In a DM view.
	if k.keycode == KEY_B:
		_render_dm_list()
		return
	if _dm_pending_choices.size() > 0:
		if k.keycode >= KEY_1 and k.keycode <= KEY_9:
			var n: int = k.keycode - KEY_0
			if n >= 1 and n <= _dm_pending_choices.size():
				_handle_dm_reply(_current_dm_canonical, _dm_pending_choice_week, n - 1, _dm_pending_choices[n - 1])


func _handle_dm_reply(canonical: String, week: int, option_idx: int, choice: Dictionary) -> void:
	var effects: Array = choice.get("effects", [])
	_dm_replies_this_session.append({
		"canonical": canonical,
		"week": week,
		"option_idx": option_idx,
		"label": String(choice.get("label", "")),
		"effects": effects,
	})
	# Picking a reply advances the read pointer past this beat.
	var read_to: int = int(_dm_read_to_week.get(canonical, 0))
	if week > read_to:
		_dm_read_to_week[canonical] = week
	# Re-render — the next beat will now be visible (or another
	# choice will gate the view).
	_render_dm_view(canonical)


# ── Glossary annotation overlay ─────────────────────────────────
# Once unlocked, G surfaces the sysop circle's coded vocabulary.
# Per aria_glossary.json: 20 concepts × 6 registers. The overlay
# shows the register-correct substitution for the BBS the player
# is currently inside (or all six if they're at the dialer).
func _render_glossary_view() -> void:
	_status_bar.clear()
	_status_bar.append_text("[color=#a8e0a8][b]GLOSSARY · the substitutions[/b][/color]")
	if _current_bbs_id != "":
		_status_bar.append_text("  ·  [color=#62c862]%s register[/color]" % _current_bbs_id)
	_main_label.clear()
	var preamble: String = "Once you knew the rule, the posts read different.\nThe sysops have been coding for a girl on this network for years."
	_main_label.append_text("[color=#86c8a8]%s[/color]\n\n" % preamble)
	var bbs_for_render: String = _current_bbs_id
	if bbs_for_render == "":
		bbs_for_render = "RUST_CODE"
	for concept in _aria_glossary.get("concepts", []):
		var per_sysop: Dictionary = concept.get("per_sysop", {})
		var term: String = String(per_sysop.get(bbs_for_render, ""))
		var canonical: String = String(concept.get("canonical", ""))
		if term == "":
			continue
		_main_label.append_text("[color=#e0c862]  %s[/color]" % term)
		_main_label.append_text("  [color=#42a042]= %s[/color]\n" % canonical)
	_main_label.append_text("\n[color=#62a862]  [G]/[B]  close glossary.[/color]\n")
	_cmd_label.text = "G or B to close · glossary unlocked"


# ── Hidden board discovery ──────────────────────────────────────
# Dial-input mode: the player presses N from the dialer, types a
# 7-digit number, presses ENTER. If the number matches one of the
# hidden boards' dial_number AND the board's discoverable_from_week
# is reached, the board unlocks on its parent BBS. Otherwise we get
# the period-correct NO CARRIER tombstone.
func _enter_dial_input() -> void:
	_in_dial_input = true
	_dial_input_buffer = ""
	_status_bar.clear()
	_status_bar.append_text("[color=#a8e0a8][b]DIAL-UP[/b][/color]  ·  ")
	_status_bar.append_text("[color=#62c862]type a number you've seen in a post[/color]")
	_main_label.clear()
	_main_label.append_text("\n[color=#a8e0a8]> _[/color]\n\n")
	_main_label.append_text("[color=#62a862]  type 7 digits · ENTER to dial · ESC to cancel[/color]\n")
	_cmd_label.text = "> _"


func _handle_dial_input_key(k: InputEventKey) -> void:
	# NO CARRIER state — any key dismisses.
	if _dial_input_buffer == "__nocarrier__":
		_in_dial_input = false
		_dial_input_buffer = ""
		_render_dial_directory()
		return
	if k.keycode == KEY_ESCAPE:
		_in_dial_input = false
		_dial_input_buffer = ""
		_render_dial_directory()
		return
	if k.keycode == KEY_ENTER or k.keycode == KEY_KP_ENTER:
		_try_dial_typed_number(_dial_input_buffer)
		_in_dial_input = false
		_dial_input_buffer = ""
		return
	if k.keycode == KEY_BACKSPACE:
		if _dial_input_buffer.length() > 0:
			_dial_input_buffer = _dial_input_buffer.substr(0, _dial_input_buffer.length() - 1)
			_update_dial_input_render()
		return
	if k.keycode >= KEY_0 and k.keycode <= KEY_9 and _dial_input_buffer.length() < 7:
		_dial_input_buffer += str(k.keycode - KEY_0)
		_update_dial_input_render()


func _update_dial_input_render() -> void:
	_main_label.clear()
	_main_label.append_text("\n[color=#a8e0a8]> %s_[/color]\n\n" % _dial_input_buffer)
	_main_label.append_text("[color=#62a862]  type 7 digits · ENTER to dial · ESC to cancel[/color]\n")
	_cmd_label.text = "> %s_" % _dial_input_buffer


func _try_dial_typed_number(num: String) -> void:
	# Track for hidden-clue accounting.
	if num != "" and not _dialled_numbers.has(num):
		_dialled_numbers.append(num)
	# Try matching against the hidden boards.
	for hb in _hidden_boards_def.get("hidden_boards", []):
		var hb_dial: String = String(hb.get("dial_number", ""))
		if hb_dial == "" or hb_dial != num:
			continue
		var from_week: int = int(hb.get("discoverable_from_week", 1))
		if _current_week < from_week:
			_render_no_carrier("the number rings. no one picks up.\n(this number isn't live yet.)")
			return
		var hb_id: String = String(hb["id"])
		if not bool(_discovered_hidden_boards.get(hb_id, false)):
			_discovered_hidden_boards[hb_id] = true
			if not _hidden_boards_discovered_this_session.has(hb_id):
				_hidden_boards_discovered_this_session.append(hb_id)
		# Drop the player into the parent BBS's board list with the
		# hidden board now visible.
		_current_bbs_id = _find_bbs_id_from_label(String(hb.get("bbs", "RUST_CODE.BBS")))
		_play_dialup(num)
		_render_board_list()
		return
	# Also try the public directory — a player might type a known
	# number rather than picking by digit. Useful for SNACKS once
	# rotated, etc.
	for entry in _dial_directory.get("bbses", []):
		var entry_dial: String = String(entry.get("dial_number",
			entry.get("dial_number_after_ban_rotation",
			entry.get("dial_number_initial", ""))))
		if entry_dial == "" or entry_dial != num:
			continue
		if not _is_bbs_dialable(entry):
			_render_no_carrier("the number rings. no one picks up.")
			return
		_current_bbs_id = String(entry["id"])
		if not _visited_bbs_ids.has(_current_bbs_id):
			_visited_bbs_ids.append(_current_bbs_id)
		_play_dialup(num)
		_render_board_list()
		return
	_render_no_carrier("NO CARRIER.\n(dial did not connect.)")


func _render_no_carrier(message: String) -> void:
	_main_label.clear()
	_main_label.append_text("\n[color=#c89a42]%s[/color]\n\n" % message)
	_main_label.append_text("[color=#62a862]  press any key to return to the directory[/color]\n")
	_cmd_label.text = "press any key"
	# Single-shot listener — next key returns to directory.
	_in_dial_input = true
	_dial_input_buffer = "__nocarrier__"


func _find_bbs_id_from_label(label: String) -> String:
	# hidden_boards.json uses "RUST_CODE.BBS" while dial_directory
	# uses "RUST_CODE" as the id; strip the .BBS suffix for matching.
	var stripped: String = label.replace(".BBS", "")
	for e in _dial_directory.get("bbses", []):
		if String(e.get("id", "")) == stripped:
			return stripped
	return "RUST_CODE"


# THE_BACKCHANNEL breadth condition: read at least one thread on
# each of the four external sysop BBSes (OVERPASS / CALICHE /
# DRY_BLOOM / BEDROCK) AND at least one SNACKS thread. When the
# condition flips, mark THE_BACKCHANNEL discovered.
func _check_backchannel_breadth() -> void:
	if bool(_discovered_hidden_boards.get("THE_BACKCHANNEL", false)):
		return
	if _current_week < 9:
		return
	const REQUIRED_BBSES := ["OVERPASS", "CALICHE", "DRY_BLOOM", "BEDROCK", "SNACKS"]
	for bbs_id in REQUIRED_BBSES:
		if not _has_read_thread_on_bbs(bbs_id):
			return
	_discovered_hidden_boards["THE_BACKCHANNEL"] = true
	if not _hidden_boards_discovered_this_session.has("THE_BACKCHANNEL"):
		_hidden_boards_discovered_this_session.append("THE_BACKCHANNEL")


func _has_read_thread_on_bbs(bbs_id: String) -> bool:
	# A thread id like "OH_001" or "TB_004" doesn't carry the BBS,
	# so we infer by checking which board_list_path/threads_paths the
	# read ids could appear in. Cheap version: each BBS's threads
	# carry id-prefixes by convention. Map here.
	var prefixes: Dictionary = {
		"OVERPASS": ["OH_", "OT_", "OOB_"],
		"CALICHE": ["CP_", "CB_", "CK_"],
		"DRY_BLOOM": ["DA_", "DK_"],
		"BEDROCK": ["BP_", "BL_"],
		"SNACKS": ["SN_"],
	}
	var pfxs: Array = prefixes.get(bbs_id, [])
	for tid in _read_thread_ids:
		var t: String = String(tid)
		for p in pfxs:
			if t.begins_with(String(p)):
				return true
	return false


# ── Hang up ─────────────────────────────────────────────────────
func _hang_up() -> void:
	var session: Dictionary = {
		"visited_bbs_ids": _visited_bbs_ids.duplicate(),
		"read_thread_ids": _read_thread_ids.duplicate(),
		"dialled_numbers": _dialled_numbers.duplicate(),
		"dm_replies": _dm_replies_this_session.duplicate(),
		"dm_read_to_week": _dm_read_to_week.duplicate(),
		"discovered_hidden_boards": _discovered_hidden_boards.duplicate(),
		"new_artifact_unlocks": _artifact_unlocks_this_session.duplicate(),
		"newly_discovered_hidden_boards": _hidden_boards_discovered_this_session.duplicate(),
		"strategic_effects": _strategic_effects_this_session.duplicate(),
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
