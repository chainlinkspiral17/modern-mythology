extends Control
## Fey Faire · midway navigation · text-forward booth graph.
##
## A hand-authored subset of the 48-cell midway map from
## _FEY_FAIRE_ROUTES.md · ~18 booth cells with adjacency edges.
## The player is always AT a specific cell.  Interact with the
## cell's booth-fey (opens the negotiation scene), OR move to an
## adjacent cell.
##
## First-person grid rendering is a follow-up commit; this is the
## text-forward version that surfaces the same content and adjacency
## structure so we can validate the map and playtest the content.
##
## Signals:
##   negotiate_with_fey(fey_id) · host opens negotiation scene
##   quit · returns to Gate
##
## F4-compliant via add_to_group("ui").

signal negotiate_with_fey(fey_id: String)
signal enter_big_top
signal rest_at_booth(fey_id: String)
signal read_fortune
signal request_save
signal quit

const FEYS_PATH := "res://resources/games/vol7/fey_faire/feys.json"
const QUOTES_PATH := "res://resources/games/vol7/fey_faire/quotes.json"
const OFF_SEASON_PATH := "res://resources/games/vol7/fey_faire/off_season.json"

# Rocha palette
const C_BG        := Color(0.157, 0.094, 0.173, 1.0)
const C_PANEL     := Color(0.455, 0.157, 0.282, 1.0)
const C_PANEL_DIM := Color(0.28, 0.10, 0.18, 1.0)
const C_CREAM     := Color(0.957, 0.878, 0.816, 1.0)
const C_ROSE      := Color(0.878, 0.722, 0.753, 1.0)
const C_MAUVE     := Color(0.87, 0.68, 0.76, 1.0)
const C_GOLD      := Color(0.973, 0.784, 0.282, 1.0)
const C_GOLD_DIM  := Color(0.72, 0.52, 0.26, 1.0)
const C_RECRUITED := Color(0.62, 0.82, 0.55, 1.0)

# Midway map · grown from the 48-cell layout · ~42 cells, 40 booths.
# Each cell: id, name, description, fey (or null if no booth),
# neighbors (adjacency).
const MIDWAY: Dictionary = {
	"gate": {
		"name": "THE GATE",
		"description": "Cricket's ticket-counter · cream and mauve striped canvas · Edison bulbs on strings overhead.",
		"fey": "cricket_the_cricket",
		"neighbors": ["midway_south", "parking_lot"]
	},
	"parking_lot": {
		"name": "THE PARKING LOT",
		"description": "Gravel · rows of parked cars · past the last row, past the generator shack, a specific Airstream trailer.",
		"fey": null,
		"neighbors": ["gate", "trailer_area", "lot_edge"]
	},
	"trailer_area": {
		"name": "TRAILER GROUNDS",
		"description": "Prospero's Airstream sits on cinderblocks.  A specific cat watches you from the window.",
		"fey": null,
		"neighbors": ["parking_lot"],
		"leads_to_trailer": true
	},
	"midway_south": {
		"name": "MIDWAY · SOUTH END",
		"description": "The main promenade begins here.  Booths line either side.  A specific Boggart-run lost-and-found is at your right.  A pond edge is visible past a specific chain-link fence to the east.",
		"fey": "boggart",
		"neighbors": ["gate", "midway_center", "ring_toss", "pond_edge"]
	},
	"ring_toss": {
		"name": "RING TOSS BOOTH",
		"description": "The FIRST booth you noticed on your first night.  Cream and mauve stripes.  Behind the counter · Ondine.  Plush prizes hanging in a row that nobody has won in living memory.",
		"fey": "ondine",
		"neighbors": ["midway_south", "fountain_jump"]
	},
	"fountain_jump": {
		"name": "FOUNTAIN-JUMP BOOTH",
		"description": "A shallow pool of pennies · a wooden frog cutout painted green · nixies swimming in it.  Every third jump the water speaks your name back.",
		"fey": "nixie",
		"neighbors": ["ring_toss", "midway_center"]
	},
	"midway_center": {
		"name": "MIDWAY · CENTER",
		"description": "The heart of the promenade.  A specific Edison-bulb archway.  A carousel to the north, a coin-in-glass booth to the east, the cotton-candy wagon to the west.  An east games alley opens off the center; a west fortune-tent row opens the other direction.",
		"fey": null,
		"neighbors": ["midway_south", "carousel", "coin_glass", "cotton_candy", "midway_north", "dart_gallery", "fortune_tellers_tent", "flower_cart", "wandering_bulb", "fountain_jump"]
	},
	"carousel": {
		"name": "THE CAROUSEL",
		"description": "A specific hand-crank music-box tune plays as the wooden horses go round.  You do not know where you have heard the tune before.",
		"fey": null,
		"neighbors": ["midway_center", "funhouse"]
	},
	"coin_glass": {
		"name": "COIN-IN-A-GLASS BOOTH",
		"description": "An old man behind the counter demonstrates that if you slide the quarter down the ramp JUST SO it lands in the shot glass.  Two dollars for three tries.  Nobody wins.  He asks your name twice.",
		"fey": "puck",
		"neighbors": ["midway_center", "bookstall"]
	},
	"cotton_candy": {
		"name": "COTTON CANDY WAGON",
		"description": "A wagoneer in a paper hat.  Green overalls.  The wagon is not hooked to any truck.  Cotton candy stays with you longer than cotton candy should.",
		"fey": "green_man",
		"neighbors": ["midway_center", "popcorn", "moss_grove"]
	},
	"popcorn": {
		"name": "POPCORN WAGON",
		"description": "A small hairy fellow in overalls pops corn in a tall glass box.  A dollar a bag.  Every bag has one popped kernel that's the color of blood.  It is not blood.",
		"fey": "hob_of_the_hedgerow",
		"neighbors": ["cotton_candy", "funnel_cake_vent"]
	},
	"funhouse": {
		"name": "FUNHOUSE MIRROR MAZE",
		"description": "Nine mirrors that don't show what they should.  The attendant is in a rabbit costume.  You suspect the rabbit costume is not a costume.  A dim alley behind the funhouse smells of woodsmoke.",
		"fey": "pooka",
		"neighbors": ["carousel", "sleep_tent", "kitsune_alley"]
	},
	"sleep_tent": {
		"name": "MOTH'S QUIET · SLEEP TENT",
		"description": "Two adjacent tents.  MOTH'S QUIET is candlelit · Moth is inside, silent · she puts a moth on your palm.  The SLEEP TENT next door is darker · a specific fine linen bed · someone else is in it, in a dream.",
		"fey": "moth",
		"neighbors": ["funhouse", "midway_north", "dream_tent"]
	},
	"bookstall": {
		"name": "THE BOOKSTALL",
		"description": "Used paperbacks stacked on wooden crates.  Two gold each.  A specific slim volume on the top shelf has your name on the cover.  It is not your name yet.",
		"fey": null,
		"neighbors": ["coin_glass", "midway_north"],
		"special_action": "bookstall"
	},
	"midway_north": {
		"name": "MIDWAY · NORTH END",
		"description": "The Big Top rises here · striped in mauve and cream.  Nightly Shakespeare shows.  Backstage is locked (Night 4+).  To the east: the kissing booth and the wheel of fortune.  To the west: a corn maze; further west, a specific overgrown grave.",
		"fey": null,
		"neighbors": ["midway_center", "bookstall", "sleep_tent", "kissing_booth", "wheel_fortune", "big_top", "corn_maze", "hamlets_grave", "shakespeare_theatre", "horse_fountain", "weird_sisters_cauldron"]
	},
	"kissing_booth": {
		"name": "KISSING BOOTH",
		"description": "Deliberately old-fashioned.  Deliberately gothic.  She is in a long dark dress that touches the floor.  Sign: ONE DOLLAR · ONE KISS · ONE QUESTION.",
		"fey": "baobhan_sith",
		"neighbors": ["midway_north", "wheel_fortune"]
	},
	"wheel_fortune": {
		"name": "WHEEL OF FORTUNE",
		"description": "A tall painted wheel with sixteen sectors.  A gaunt man in a long grey coat spins it.  His crown is antler.  Sector 16 says CHILD.  Nobody has landed on Sector 16 in living memory.",
		"fey": "erlking",
		"neighbors": ["midway_north", "kissing_booth"]
	},
	"big_top": {
		"name": "THE BIG TOP · MAIN TENT",
		"description": "The nightly show is starting.  Cast varies · tonight's playbill reads A MIDSUMMER NIGHT'S DREAM.  Titania is playing herself.  Backstage locked.",
		"fey": null,
		"neighbors": ["midway_north", "backstage"],
		"needs_night_4_for_backstage": true
	},

	# ─── East wing · games ───────────────────────────────────────
	"dart_gallery": {
		"name": "DART GALLERY",
		"description": "Three feet tall, standing on a wooden stool, a small man in a green vest is running a dart gallery.  He is called Cluricaune.  He is not sober.  The prizes are stuffed rabbits · every rabbit has a specific missing button-eye that is the same rabbit's other button-eye if you look closely.",
		"fey": "cluricaune",
		"neighbors": ["midway_center", "shooting_gallery", "strongman_booth"]
	},
	"shooting_gallery": {
		"name": "SHOOTING GALLERY",
		"description": "Tin ducks on a rail.  Behind the counter · a specific small dog with green fur watches you.  His name is Cu Sìth.  He does not blink.  The rifle-sight has been pre-adjusted to your specific eye.",
		"fey": "cu_sith",
		"neighbors": ["dart_gallery", "corn_maze", "fishbowl_booth"]
	},
	"corn_maze": {
		"name": "CORN MAZE",
		"description": "Twelve-foot corn.  An hour before you enter the maze you will see a specific stag in the row-ends.  Once inside, the stag becomes a man in an antler crown.  His name is HERNE.  He does not offer to help you find the exit.",
		"fey": "herne_the_hunter",
		"neighbors": ["shooting_gallery", "midway_north"]
	},

	# ─── West wing · fortune-tents ───────────────────────────────
	"fortune_tellers_tent": {
		"name": "FORTUNE-TELLER'S TENT",
		"description": "Velvet drapes.  A woman in her seventies with hair still black at the roots.  She calls herself Morgan.  She knows your name.  She knows the answer to question seven.  She is not showing off · she is warning you.",
		"fey": "morgan_le_fey",
		"neighbors": ["midway_center", "musicians_tent", "chicken_leg_hut"],
		"special_action": "fortune"
	},
	"musicians_tent": {
		"name": "MUSICIANS' TENT",
		"description": "A small stage lit by two candle-footlights.  A woman with a lute is tuning it.  She stops when you walk in.  She was expecting you specifically.  Her name is Leanan.  She knows the song you have not told anyone you love.",
		"fey": "leanan_sidhe",
		"neighbors": ["fortune_tellers_tent", "tattoo_stall", "buskers_corner"]
	},
	"tattoo_stall": {
		"name": "TATTOO STALL",
		"description": "A hand-painted sign · SYCORAX · TATTOOS · CASH ONLY.  Inside: a woman older than any three grandmothers, tattooing a specific mark on her own forearm.  She has been drawing that mark for thirty-seven years.  She could give you a copy of it.  It would mark you Unseelie.",
		"fey": "sycorax",
		"neighbors": ["musicians_tent", "freak_show_tent", "palm_readers_tent"]
	},
	"freak_show_tent": {
		"name": "FREAK SHOW TENT",
		"description": "The sign outside is politely worded.  Inside is a man in a specific cage.  His name is CALIBAN.  Do not gawk.  You should feel bad that you paid a dollar.  Talk to him instead.  He will tell you what he actually is if you sit for the length of time he needs.",
		"fey": "caliban",
		"neighbors": ["tattoo_stall"]
	},

	# ─── South spur · pond edge ──────────────────────────────────
	"pond_edge": {
		"name": "POND EDGE",
		"description": "Past a specific chain-link fence · a green pond that isn't on the Faire's map.  A girl with algae-green teeth waves at you.  Her name is JENNY.  She is standing waist-deep.  She is asking politely for you to come in.",
		"fey": "jenny_greenteeth",
		"neighbors": ["midway_south", "sea_pavilion"]
	},

	# ─── Deep map · Night 3+ only ────────────────────────────────
	"sea_pavilion": {
		"name": "SEA PAVILION",
		"description": "A canvas pavilion that smells of seawater despite the town being three hundred miles inland.  Inside · a woman-figure with the tail of a fish, half-submerged in a specific glass tank.  Her name is MERROW.  Nobody has explained where the tank came from.",
		"fey": "merrow",
		"neighbors": ["pond_edge"],
		"needs_night_3": true
	},
	"moss_grove": {
		"name": "MOSS GROVE",
		"description": "A small stand of trees Fey-planted specifically to be here.  Moss on every surface.  A specific tree in the center is a woman · you can see her wooden fingers in the bark.  Her name is DRYAD.  She is old.  She is thinking.",
		"fey": "dryad",
		"neighbors": ["cotton_candy", "green_border"],
		"needs_night_3": true
	},

	# ─── Grave & theatre corner ──────────────────────────────────
	"hamlets_grave": {
		"name": "HAMLET'S GRAVE",
		"description": "A specific carnival-prop tombstone reads · HAMLET, PRINCE OF DENMARK · 1601 - 1601.  Sitting on it is a young man in specific black rehearsal blacks.  He is playing Hamlet at the Big Top on Night 3.  He is also, specifically, the Ghost.  He would like to tell you what Hamlet actually meant.",
		"fey": "hamlets_ghost",
		"neighbors": ["midway_north"]
	},
	"shakespeare_theatre": {
		"name": "SHAKESPEARE THEATRE · STUDIO",
		"description": "A smaller theatre behind the Big Top.  For rehearsals only.  Oberon holds court here from Night 5.  Before Night 5 the door is a specific closed door.  On Night 5+ · a specific tall man in a long black coat gestures you in.",
		"fey": "oberon",
		"neighbors": ["midway_north"],
		"needs_night_5": true
	},
	"backstage": {
		"name": "BIG TOP · BACKSTAGE",
		"description": "A specific narrow passage behind the main stage.  Titania holds court here from Night 4 onwards.  Costume racks · faded velvet · a specific rose still fresh in a specific paper cup of water.",
		"fey": "titania",
		"neighbors": ["big_top"],
		"needs_night_4": true
	},

	# ─── Weird sisters & foxes ───────────────────────────────────
	"weird_sisters_cauldron": {
		"name": "WEIRD SISTERS' CAULDRON",
		"description": "A specific pit off the main promenade · three women around a copper cauldron · the youngest is nine years old, the middle is thirty-nine, the eldest is somewhere past ninety.  All three glance up.  They speak all three at once.  This works better than it should.",
		"fey": "weird_sister_first",
		"neighbors": ["midway_north"],
		"needs_night_4": true
	},
	"kitsune_alley": {
		"name": "KITSUNE ALLEY",
		"description": "A dim alley behind the funhouse.  A specific fox-woman stands at the end of it.  Nine tails today · they were three tails on Night 1.  She has been counting your specific nights.  She has been in this alley since Night 1.  She has been waiting.",
		"fey": "kitsune",
		"neighbors": ["funhouse"]
	},

	# ─── Orphan wiring 2026-07 · booths placed per each fey's own
	# authored manifestation in feys.json ─────────────────────────
	"strongman_booth": {
		"name": "TEST-YOUR-STRENGTH",
		"description": "A wooden tower with a bell at the top.  Cobweb runs it · she's ninety-three or she's thirteen, depending on the light.  She hands you the mallet and says 'do not swing hard; swing TRUE.'  The mallet is heavier than it looks.  Nobody has rung the bell by swinging hard.",
		"fey": "cobweb",
		"neighbors": ["dart_gallery", "milk_bottles"]
	},
	"milk_bottles": {
		"name": "MILK BOTTLES BOOTH",
		"description": "Knock three plastic bottles off a table with a baseball.  The operator wears a red knitted cap and a broad polite smile.  His teeth are yellow.  The bottles are real.  The bat is heavier than baseballs are.  You can win.  You should think about whether you want to.",
		"fey": "redcap",
		"neighbors": ["strongman_booth", "fishbowl_booth"]
	},
	"fishbowl_booth": {
		"name": "FISHBOWL BOOTH",
		"description": "Win a goldfish · real, live, in a plastic bag with too little water · by tossing a ping-pong ball into the right jar.  The operator is a woman in her forties with long dark hair kept damp deliberately.  Every fish she gives away, she watches leave like a coat she lent out.",
		"fey": "selkie",
		"neighbors": ["milk_bottles", "shooting_gallery"]
	},
	"flower_cart": {
		"name": "FLOWER STALL",
		"description": "Glass vases of impossibly-blue lupines · roses that smell like something other than roses.  Two dollars a stem, one dollar if you smile.  The girl behind the counter is seven years old and speaking in complete sonnets when she thinks nobody official is listening.",
		"fey": "peaseblossom",
		"neighbors": ["midway_center"]
	},
	"wandering_bulb": {
		"name": "THE UNWIRED BULB",
		"description": "One light on the Edison string isn't wired to anything.  You noticed it because it moved.  It is moving now, bulb to bulb, patient, in the direction of a part of the Faire that isn't on the map and is nonetheless real.  Do NOT follow it past the Gate at night.",
		"fey": "will_o_wisp",
		"neighbors": ["midway_center"],
		"needs_night_3": true
	},
	"horse_fountain": {
		"name": "THE DRINKING FOUNTAIN",
		"description": "At the far end of the midway · a fountain shaped like a horse's head, water pouring from its mouth.  It is not connected to any pipe.  The water is very cold and very clean and tastes vaguely of iron.  There is a horse-hair at the bottom of the basin.  Do not pick it up.",
		"fey": "kelpie",
		"neighbors": ["midway_north"],
		"needs_night_3": true
	},
	"funnel_cake_vent": {
		"name": "FUNNEL CAKE WAGON · BACK VENT",
		"description": "You smell fresh grease.  Under the fry-sizzle, specific and unmistakable once heard, somebody is weeping.  The wagon staff work around the sound the way you'd work around a load-bearing pillar.  Whatever she is grieving has not happened yet.",
		"fey": "banshee",
		"neighbors": ["popcorn"],
		"needs_night_4": true
	},
	"buskers_corner": {
		"name": "BUSKER'S CORNER",
		"description": "A young man playing a fiddle beside an actual small waterfall, which should not exist here, three hundred miles inland and forty feet from a corn dog stand.  He plays better when you stand in the spray.  He will teach the tune to anyone who asks correctly.",
		"fey": "fossegrim",
		"neighbors": ["musicians_tent"]
	},
	"chicken_leg_hut": {
		"name": "THE REPLACEMENT HUT",
		"description": "Behind the Fortune-Teller's tent, where no structure stood on Night 1 · a hut, standing on two enormous chicken legs, turning slowly to keep its porch toward you.  An old woman on the porch watches you decide whether to believe the legs.  Take your time.  She has hers.",
		"fey": "baba_yaga",
		"neighbors": ["fortune_tellers_tent"],
		"needs_night_3": true
	},
	"palm_readers_tent": {
		"name": "PALM-READER'S TENT",
		"description": "A stone-shelved table · three burning candles that never dwindle · a woman who reads your palm with three fingers, not five.  She does not tell fortunes.  She tells FORKS · here is where it splits, here, and here.  Which way is your own business, she says.",
		"fey": "hecate",
		"neighbors": ["tattoo_stall", "velvet_booth"],
		"needs_night_5": true
	},
	"velvet_booth": {
		"name": "THE BLACK VELVET BOOTH",
		"description": "A small tent draped in black velvet · a cracked crystal ball · an old woman shuffling cards nobody is dealt.  She is not the Sluagh.  She works for the Sluagh.  Overhead, on the tent-ropes, birds have settled that are not birds, facing all one way, which is yours.",
		"fey": "sluagh",
		"neighbors": ["palm_readers_tent"],
		"needs_night_5": true
	},
	"dream_tent": {
		"name": "THE SLEEP TENT · INSIDE",
		"description": "Darker mauve, almost black.  Sign reads DREAM FOR TWO DOLLARS · WAKE UP OR DON'T.  Mab is not visible; a bed is.  Fine linens, turned down.  She does not meet anyone on the midway.  She meets you in a dream, and the bed is the door, and the door is open.",
		"fey": "queen_mab",
		"neighbors": ["sleep_tent"],
		"needs_night_5": true
	},
	"green_border": {
		"name": "THE TREE LINE",
		"description": "Where the moss grove thins into actual trees that were not planted by anybody.  A tall figure stands at the edge, back turned, always back turned however you circle.  His shadow does not match his body.  The trees arrange themselves to be walked through, or not.",
		"fey": "leshy",
		"neighbors": ["moss_grove"],
		"needs_night_4": true
	},
	"lot_edge": {
		"name": "PARKING LOT · FAR EDGE",
		"description": "The last row of cars, then gravel, then dark.  When headlights sweep in you see it for exactly the length of the sweep · black shape, red eyes, loping without hurry along the fence.  It has walked drunks to their cars all summer.  Nobody it walked has come to harm.  Yet.",
		"fey": "black_dog",
		"neighbors": ["parking_lot"],
		"needs_night_4": true
	}
}

var _run_state: Dictionary = {}
var _feys_by_id: Dictionary = {}
var _current_cell: String = "midway_south"
var _ambient_timer: SceneTreeTimer = null
var _ambient_alive: bool = true

# Which ambient one-shot drifts through each part of the map ·
# played on a loose interval like Pirate Summer's zone ambients.
const AMBIENT_FOR_CELL := {
	"big_top":        {"preset": "calliope_drift", "interval": 14.0, "vol": 0.8},
	"backstage":      {"preset": "calliope_drift", "interval": 18.0, "vol": 0.5},
	"midway_north":   {"preset": "calliope_drift", "interval": 22.0, "vol": 0.4},
	"carousel":       {"preset": "calliope_drift", "interval": 12.0, "vol": 0.9},
	"pond_edge":      {"preset": "canvas_flap",    "interval": 16.0, "vol": 0.6},
	"sea_pavilion":   {"preset": "canvas_flap",    "interval": 14.0, "vol": 0.7},
	"moss_grove":     {"preset": "canvas_flap",    "interval": 20.0, "vol": 0.5},
	"trailer_area":   {"preset": "canvas_flap",    "interval": 18.0, "vol": 0.6},
	"kitsune_alley":  {"preset": "canvas_flap",    "interval": 15.0, "vol": 0.5}
}
const AMBIENT_DEFAULT := {"preset": "night_crowd", "interval": 17.0, "vol": 0.5}


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	_schedule_ambient()


func _exit_tree() -> void:
	_ambient_alive = false


func _schedule_ambient() -> void:
	if not _ambient_alive or not is_inside_tree():
		return
	var amb: Dictionary = AMBIENT_FOR_CELL.get(_current_cell, AMBIENT_DEFAULT)
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play(String(amb.get("preset", "night_crowd")), float(amb.get("vol", 0.5)))
	_ambient_timer = get_tree().create_timer(float(amb.get("interval", 17.0)))
	_ambient_timer.timeout.connect(_schedule_ambient)


var _off_season_def: Dictionary = {}


func _off_season() -> bool:
	return bool(_run_state.get("off_season", false))


func _load_off_season() -> void:
	if not FileAccess.file_exists(OFF_SEASON_PATH): return
	var f := FileAccess.open(OFF_SEASON_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_off_season_def = parsed


func boot(state: Dictionary) -> void:
	_run_state = state
	# Restore last cell if saved
	var saved_cell := String(_run_state.get("midway_cell", "midway_south"))
	if MIDWAY.has(saved_cell):
		_current_cell = saved_cell
	_load_feys()
	_load_quotes()
	_load_off_season()
	# The off season starts at the gate, from the outside.
	if _off_season() and not bool(_run_state.get("_off_season_entered", false)):
		_run_state["_off_season_entered"] = true
		_current_cell = "gate"
	_render_current_cell()


var _quotes: Array = []

func _load_quotes() -> void:
	if not FileAccess.file_exists(QUOTES_PATH): return
	var f := FileAccess.open(QUOTES_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_quotes = (parsed as Dictionary).get("quotes", [])


func _load_feys() -> void:
	if not FileAccess.file_exists(FEYS_PATH): return
	var f := FileAccess.open(FEYS_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		for entry_v in (parsed as Dictionary).get("feys", []):
			var entry: Dictionary = entry_v
			_feys_by_id[String(entry.get("id", ""))] = entry


func _clear_children() -> void:
	for c in get_children():
		c.queue_free()


func _render_current_cell() -> void:
	_clear_children()
	_run_state["midway_cell"] = _current_cell

	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# The midway itself behind the booth graph — big top, string
	# lights, the wheel. Dimmed so the cells stay readable; missing
	# JSON falls back to the flat fill.
	var backdrop := HeroImage.new()
	if backdrop.load_from("res://resources/games/vol7/fey_faire/hero_images/midway_backdrop.json"):
		var bd := TextureRect.new()
		bd.texture = backdrop.texture(Vector2i(1280, 720))
		bd.stretch_mode = TextureRect.STRETCH_SCALE
		bd.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		bd.mouse_filter = Control.MOUSE_FILTER_IGNORE
		bd.modulate = Color(0.52, 0.58, 0.68, 1.0) if _off_season() else Color(0.72, 0.72, 0.72, 1.0)
		add_child(bd)

	# Mauve tent-stripe hint · top
	for x in range(60, 1280, 90):
		var stripe := ColorRect.new()
		stripe.color = C_MAUVE
		stripe.set_anchors_preset(Control.PRESET_TOP_LEFT)
		stripe.position = Vector2(x, 0)
		stripe.size = Vector2(6, 30)
		add_child(stripe)

	var cell: Dictionary = MIDWAY[_current_cell]

	# Top: cell name
	var header := Label.new()
	if _off_season():
		header.text = "· THE OFF SEASON · " + String(cell.get("name", "?")) + " ·"
	else:
		header.text = "· " + String(cell.get("name", "?")) + " ·"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 20)
	header.add_theme_color_override("font_color", Color(0.72, 0.82, 0.88, 1.0) if _off_season() else C_GOLD)
	header.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header.offset_top = 46
	header.offset_bottom = 74
	add_child(header)

	# Purse · night · top-right
	var purse := Label.new()
	if _off_season():
		purse.text = "winter · the gate is open"
	else:
		purse.text = "night " + str(int(_run_state.get("night", 1))) + "/6 · " + str(int(_run_state.get("gold", 0))) + " gold"
	purse.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	purse.position = Vector2(-170, 50)
	purse.add_theme_font_size_override("font_size", 14)
	purse.add_theme_color_override("font_color", C_GOLD)
	add_child(purse)

	# Central panel
	var panel := ColorRect.new()
	panel.color = C_PANEL
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.offset_left = -420
	panel.offset_right = 420
	panel.offset_top = -240
	panel.offset_bottom = 240
	add_child(panel)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -400
	v.offset_right = 400
	v.offset_top = -220
	v.offset_bottom = 220
	v.add_theme_constant_override("separation", 10)
	add_child(v)

	# Description
	var desc := RichTextLabel.new()
	desc.bbcode_enabled = false
	desc.fit_content = true
	desc.text = String(cell.get("description", ""))
	desc.add_theme_font_size_override("normal_font_size", 16)
	desc.add_theme_color_override("default_color", C_CREAM)
	desc.custom_minimum_size = Vector2(0, 80)
	v.add_child(desc)

	# THE OFF SEASON · winter overlay + booths without commerce.
	if _off_season():
		_render_off_season_cell(v, cell)

	# Booth-fey (if any)
	var fey_id: Variant = cell.get("fey", null)
	if fey_id != null and fey_id != "" and not _off_season():
		var fey: Dictionary = _feys_by_id.get(String(fey_id), {})
		if not fey.is_empty():
			var recruited: Array = _run_state.get("recruited_feys", [])
			var is_recruited: bool = recruited.has(String(fey_id))
			var booth_row := HBoxContainer.new()
			booth_row.add_theme_constant_override("separation", 12)
			v.add_child(booth_row)

			var booth_lbl := Label.new()
			if is_recruited:
				booth_lbl.text = "✓ " + String(fey.get("name", fey_id)) + " · recruited · their booth is unattended"
				booth_lbl.add_theme_color_override("font_color", C_RECRUITED)
			else:
				booth_lbl.text = "· " + String(fey.get("name", fey_id)) + " · " + String(fey.get("court", "?")) + " · tier " + str(int(fey.get("tier", 1))) + " ·"
				booth_lbl.add_theme_color_override("font_color", C_ROSE)
			booth_lbl.add_theme_font_size_override("font_size", 15)
			booth_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			booth_row.add_child(booth_lbl)

			if not is_recruited:
				# A failed negotiation closes the flap until the night
				# advances · time is the currency.
				var locks: Dictionary = _run_state.get("booth_locks", {})
				var locked_tonight: bool = locks.has(String(fey_id)) \
						and int(locks[String(fey_id)]) == int(_run_state.get("night", 1))
				var special: String = String(cell.get("special_action", ""))
				if locked_tonight and special != "fortune":
					var closed_lbl := Label.new()
					closed_lbl.text = "· the flap is closed tonight ·"
					closed_lbl.add_theme_font_size_override("font_size", 14)
					closed_lbl.add_theme_color_override("font_color", C_GOLD_DIM)
					booth_row.add_child(closed_lbl)
				else:
					var interact_btn := Button.new()
					if special == "fortune" and not bool(_run_state.get("fortune_read", false)):
						interact_btn.text = "  sit for a reading  "
						interact_btn.pressed.connect(func() -> void: read_fortune.emit())
					else:
						interact_btn.text = "  approach the booth  "
						interact_btn.pressed.connect(func() -> void: negotiate_with_fey.emit(String(fey_id)))
					interact_btn.add_theme_font_size_override("font_size", 15)
					interact_btn.add_theme_color_override("font_color", C_GOLD)
					booth_row.add_child(interact_btn)
			else:
				# REST at a recruited booth · advances the night
				var night_now: int = int(_run_state.get("night", 1))
				var rest_btn := Button.new()
				if night_now >= 6:
					rest_btn.text = "  · rest here · (night 6 · the last night · nothing more to advance to)  "
					rest_btn.disabled = true
				else:
					var attended: Array = _run_state.get("shows_attended", [])
					if not attended.has(night_now):
						rest_btn.text = "  · rest here · (see tonight's show at the Big Top first)  "
						rest_btn.disabled = true
					else:
						rest_btn.text = "  · rest at " + String(fey.get("name", fey_id)) + "'s booth · advance to night " + str(night_now + 1) + " ·  "
						rest_btn.add_theme_color_override("font_color", C_GOLD)
						rest_btn.pressed.connect(func() -> void: rest_at_booth.emit(String(fey_id)))
				rest_btn.add_theme_font_size_override("font_size", 15)
				booth_row.add_child(rest_btn)

	# Special-case: trailer link
	if bool(cell.get("leads_to_trailer", false)) and not _off_season():
		var trailer_btn := Button.new()
		trailer_btn.text = "  ⌂  walk up to the trailer door  "
		trailer_btn.add_theme_font_size_override("font_size", 15)
		trailer_btn.add_theme_color_override("font_color", C_GOLD)
		trailer_btn.pressed.connect(_on_visit_trailer_pressed)
		v.add_child(trailer_btn)

	# Big Top backstage lock message + attend-show action
	if bool(cell.get("needs_night_4_for_backstage", false)) and not _off_season():
		var night: int = int(_run_state.get("night", 1))
		var attended: Array = _run_state.get("shows_attended", [])
		var attend_btn := Button.new()
		if attended.has(night):
			attend_btn.text = "  · you have already seen tonight's show ·  "
			attend_btn.disabled = true
		else:
			attend_btn.text = "  · take a seat · watch tonight's show ·  "
			attend_btn.add_theme_color_override("font_color", C_GOLD)
			attend_btn.pressed.connect(func() -> void: enter_big_top.emit())
		attend_btn.add_theme_font_size_override("font_size", 16)
		v.add_child(attend_btn)

		var lock_lbl := Label.new()
		if night < 4:
			lock_lbl.text = "· backstage is locked · night " + str(night) + "/6 · Oberon holds court there from night 4 ·"
			lock_lbl.add_theme_color_override("font_color", C_GOLD_DIM)
		else:
			lock_lbl.text = "· backstage is open · Oberon is here ·"
			lock_lbl.add_theme_color_override("font_color", C_GOLD)
		lock_lbl.add_theme_font_size_override("font_size", 14)
		v.add_child(lock_lbl)

	# Bookstall shop · paperbacks at 2 gold · each teaches a RECITE line
	if String(cell.get("special_action", "")) == "bookstall" and not _off_season():
		_render_bookstall_shop(v)

	var sep := Control.new()
	sep.custom_minimum_size = Vector2(0, 12)
	v.add_child(sep)

	# Directions
	var dir_header := Label.new()
	dir_header.text = "· FROM HERE ·"
	dir_header.add_theme_font_size_override("font_size", 14)
	dir_header.add_theme_color_override("font_color", C_GOLD_DIM)
	v.add_child(dir_header)

	var neighbors: Array = cell.get("neighbors", [])
	var night_now: int = int(_run_state.get("night", 1))
	for n_id_v in neighbors:
		var n_id: String = String(n_id_v)
		if not MIDWAY.has(n_id): continue
		var n: Dictionary = MIDWAY[n_id]
		var btn := Button.new()
		var fey_hint: String = ""
		var n_fey: Variant = n.get("fey", null)
		if n_fey != null and n_fey != "":
			var f: Dictionary = _feys_by_id.get(String(n_fey), {})
			var r: Array = _run_state.get("recruited_feys", [])
			var checked: String = "✓" if r.has(String(n_fey)) else "·"
			fey_hint = "  (" + checked + " " + String(f.get("name", "?")) + ")"
		# Night gates · disable the button until the appropriate night
		var gate_note: String = ""
		var locked: bool = false
		if bool(n.get("needs_night_3", false)) and night_now < 3:
			locked = true
			gate_note = "  · locked · Night 3+  "
		elif bool(n.get("needs_night_4", false)) and night_now < 4:
			locked = true
			gate_note = "  · locked · Night 4+  "
		elif bool(n.get("needs_night_5", false)) and night_now < 5:
			locked = true
			gate_note = "  · locked · Night 5+  "
		btn.text = "  →  " + String(n.get("name", n_id)) + fey_hint + gate_note + "  "
		btn.add_theme_font_size_override("font_size", 15)
		if locked:
			btn.disabled = true
			btn.add_theme_color_override("font_color_disabled", C_GOLD_DIM)
		else:
			btn.pressed.connect(func() -> void: _on_move_to(n_id))
		v.add_child(btn)

	var sep2 := Control.new()
	sep2.custom_minimum_size = Vector2(0, 12)
	v.add_child(sep2)

	# Back to gate
	var back_btn := Button.new()
	back_btn.text = "  ← return to the Gate  "
	back_btn.add_theme_font_size_override("font_size", 15)
	back_btn.pressed.connect(_on_back)
	v.add_child(back_btn)


# ─── THE OFF SEASON · the park after close ───────────────────────
# Winter overlay + booths without commerce. The recruited party is
# the only crowd; everything else is laced shut. Exit by the gate.

func _render_off_season_cell(v: VBoxContainer, cell: Dictionary) -> void:
	var cid := String(cell.get("name", _current_cell))
	# One winter line per cell, stable per cell id.
	var winters: Array = _off_season_def.get("winter_lines", [])
	if not winters.is_empty():
		var w_lbl := Label.new()
		w_lbl.text = String(winters[posmod(_current_cell.hash(), winters.size())])
		w_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		w_lbl.add_theme_font_size_override("font_size", 13)
		w_lbl.add_theme_color_override("font_color", Color(0.70, 0.78, 0.86, 1.0))
		v.add_child(w_lbl)
	# The Big Top, dark.
	if bool(cell.get("needs_night_4_for_backstage", false)):
		var bt_lbl := Label.new()
		bt_lbl.text = String(_off_season_def.get("big_top_dark", ""))
		bt_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		bt_lbl.add_theme_font_size_override("font_size", 14)
		bt_lbl.add_theme_color_override("font_color", C_CREAM)
		v.add_child(bt_lbl)
	# The booth, off season.
	var fey_id_v: Variant = cell.get("fey", null)
	if fey_id_v != null and fey_id_v != "":
		var f_id := String(fey_id_v)
		var fey: Dictionary = _feys_by_id.get(f_id, {})
		var recruited: Array = _run_state.get("recruited_feys", [])
		var line := ""
		var color := C_ROSE
		if recruited.has(f_id):
			var specials: Dictionary = _off_season_def.get("special_lines", {})
			if specials.has(f_id):
				line = String(specials[f_id])
			else:
				var court := String(fey.get("court", "wildfey"))
				var pool: Array = (_off_season_def.get("court_lines", {}) as Dictionary).get(court, [])
				if not pool.is_empty():
					line = String(pool[posmod(f_id.hash(), pool.size())]) % String(fey.get("name", f_id))
			color = C_RECRUITED
		elif String(cell.get("special_action", "")) == "fortune":
			line = String(_off_season_def.get("fortune_empty", ""))
			color = C_MAUVE
		else:
			var shut: Array = _off_season_def.get("shuttered_lines", [])
			if not shut.is_empty():
				line = String(shut[posmod(f_id.hash(), shut.size())])
			color = C_GOLD_DIM
		if line != "":
			var b_lbl := Label.new()
			b_lbl.text = line
			b_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			b_lbl.add_theme_font_size_override("font_size", 14)
			b_lbl.add_theme_color_override("font_color", color)
			v.add_child(b_lbl)
	# The way out.
	if _current_cell == "gate":
		var leave := Button.new()
		leave.text = "  · %s ·  " % String(_off_season_def.get("gate_leave_label", "leave by the gate"))
		leave.add_theme_font_size_override("font_size", 15)
		leave.add_theme_color_override("font_color", C_GOLD)
		leave.pressed.connect(_on_off_season_leave)
		v.add_child(leave)
	if cid == "":
		pass


func _on_off_season_leave() -> void:
	var tok := String(_off_season_def.get("token", "fey_faire_off_season_walked"))
	OneironauticsTokens.add(tok)
	_run_state["_off_season_left"] = true
	quit.emit()


func _render_bookstall_shop(v: VBoxContainer) -> void:
	var gold: int = int(_run_state.get("gold", 0))
	var unlocked: Array = _run_state.get("unlocked_quotes", [])
	var night: int = int(_run_state.get("night", 1))

	var shop_hdr := Label.new()
	shop_hdr.text = "· THE STALL · two gold a paperback · your purse: " + str(gold) + " gold ·"
	shop_hdr.add_theme_font_size_override("font_size", 15)
	shop_hdr.add_theme_color_override("font_color", C_GOLD)
	v.add_child(shop_hdr)

	# Tonight's shelf · three deterministic picks per night from the
	# not-yet-unlocked catalog (starters excluded · you own those).
	var candidates: Array = []
	for q_v in _quotes:
		var q: Dictionary = q_v
		if bool(q.get("starter", false)): continue
		if unlocked.has(String(q.get("id", ""))): continue
		candidates.append(q)
	var shown := 0
	var offset: int = (night * 7) % max(1, candidates.size())
	for i in range(candidates.size()):
		if shown >= 3: break
		var q: Dictionary = candidates[(offset + i * 5) % candidates.size()]
		var qid: String = String(q.get("id", ""))
		if unlocked.has(qid): continue
		var vh := VBoxContainer.new()
		vh.add_theme_constant_override("separation", 1)
		v.add_child(vh)
		var btn := Button.new()
		if gold >= 2:
			btn.text = "  buy · \"" + String(q.get("text", "")).left(58) + "\" · 2 gold  "
			btn.pressed.connect(func() -> void: _buy_quote(qid))
		else:
			btn.text = "  \"" + String(q.get("text", "")).left(58) + "\" · 2 gold · not enough  "
			btn.disabled = true
		btn.add_theme_font_size_override("font_size", 14)
		vh.add_child(btn)
		var meta := Label.new()
		meta.text = "     " + String(q.get("play", "")) + " · " + String(q.get("speaker", "")) + " speaks it"
		meta.add_theme_font_size_override("font_size", 12)
		meta.add_theme_color_override("font_color", C_GOLD_DIM)
		vh.add_child(meta)
		shown += 1

	# The slim volume with your name on the cover · Night 5+
	var slim_btn := Button.new()
	var kp: Array = _run_state.get("keepsakes", [])
	if kp.has("the_slim_volume"):
		slim_btn.text = "  · the slim volume is yours · the cover has settled ·  "
		slim_btn.disabled = true
	elif night < 5:
		slim_btn.text = "  · the slim volume with your name on the cover · not for sale yet · Night 5+ ·  "
		slim_btn.disabled = true
	elif gold < 5:
		slim_btn.text = "  · the slim volume · 5 gold · not enough ·  "
		slim_btn.disabled = true
	else:
		slim_btn.text = "  buy · the slim volume with your name on the cover · 5 gold  "
		slim_btn.pressed.connect(_buy_slim_volume)
	slim_btn.add_theme_font_size_override("font_size", 14)
	slim_btn.add_theme_color_override("font_color", C_ROSE)
	v.add_child(slim_btn)


func _buy_quote(quote_id: String) -> void:
	var gold: int = int(_run_state.get("gold", 0))
	if gold < 2: return
	_run_state["gold"] = gold - 2
	var unlocked: Array = _run_state.get("unlocked_quotes", [])
	if not unlocked.has(quote_id):
		unlocked.append(quote_id)
	_run_state["unlocked_quotes"] = unlocked
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("coin", 0.6)
	request_save.emit()
	_render_current_cell()


func _buy_slim_volume() -> void:
	var gold: int = int(_run_state.get("gold", 0))
	if gold < 5: return
	_run_state["gold"] = gold - 5
	var kp: Array = _run_state.get("keepsakes", [])
	if not kp.has("the_slim_volume"):
		kp.append("the_slim_volume")
	_run_state["keepsakes"] = kp
	_run_state["court_seelie"] = int(_run_state.get("court_seelie", 0)) + 1
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("lore_token_reveal", 0.7)
	request_save.emit()
	_render_current_cell()


func _on_move_to(cell_id: String) -> void:
	if not MIDWAY.has(cell_id): return
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("tile_enter", 0.4)
	_current_cell = cell_id
	_render_current_cell()


func _on_visit_trailer_pressed() -> void:
	# Emit a specific quit + set flag so host routes to trailer
	_run_state["_route_to_trailer"] = true
	quit.emit()


func _on_back() -> void:
	quit.emit()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			_on_back()
			get_viewport().set_input_as_handled()
