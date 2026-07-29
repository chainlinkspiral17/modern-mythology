extends Control
## Sam's Summer Shifts · the twelve-week loop.
##
## One scripted shift-beat per week.  Choices move three meters:
##   TILL     · drawer accuracy / register craft
##   REGULARS · standing with the morning crowd
##   NERVE    · Sam's steadiness · hits 0, Sam walks off the job
##
## Week 6 is the armed-robbery anchor beat the whole game bends
## around.  Endings at week 12 (or early on nerve 0):
##   walked_off       · nerve reached 0 · early exit
##   kept_the_summer  · finished · the default, honest ending
##   made_manager     · till >= 6 and regulars >= 6 at week 12
##
## F4-compliant via add_to_group("ui").

signal quit
signal week_complete(state: Dictionary)
signal summer_over(state: Dictionary, ending_id: String)

# RANCH palette
const C_BG      := Color(0.055, 0.055, 0.055, 1.0)
const C_RED     := Color(0.910, 0.220, 0.282, 1.0)
const C_CREAM   := Color(0.957, 0.941, 0.910, 1.0)
const C_YELLOW  := Color(0.910, 0.784, 0.251, 1.0)
const C_GRAY    := Color(0.251, 0.251, 0.251, 1.0)
const C_DIM     := Color(0.60, 0.56, 0.50, 1.0)
const C_GREEN   := Color(0.42, 0.72, 0.42, 1.0)

# Twelve weeks · each: title, text, choices[{label, note, till, regulars, nerve}]
const WEEKS: Array = [
	{
		"title": "WEEK 1 · FIRST SHIFT",
		"text": "The Hi-Way 30 Stop-N-Go, four miles outside Clatskanie.  Ray hands you the register key on a lanyard that smells like his truck.  'Drawer starts at eighty even.  Count it however you count things.'\n\nThe morning crowd starts at 5:40 with Dot, who takes her coffee black and her silence seriously.",
		"choices": [
			{"label": "  Count the drawer twice before opening.  ", "note": "eight minutes late unlocking the door · but the count is right", "till": 2, "regulars": -1, "nerve": 0},
			{"label": "  Trust Ray's count and open on time.  ", "note": "the drawer is fine · you decide to believe things until they stop being true", "till": 0, "regulars": 1, "nerve": 1},
			{"label": "  Ask Dot how the last clerk did it.  ", "note": "Dot answers in nine words.  All nine are useful.  She refills her own coffee.", "till": 1, "regulars": 2, "nerve": 0}
		]
	},
	{
		"title": "WEEK 2 · THE REGULARS",
		"text": "You know them now.  Dot at 5:40.  Gus at 6:15 for lottery scratchers and exact change.  The log-truck drivers between 6:30 and 7:00, who buy more coffee than seems survivable.\n\nGus asks you to pick his scratcher for him.  'You look lucky,' he says.  He says this to every clerk.  Dot told you he says this to every clerk.",
		"choices": [
			{"label": "  Pick the third one down.  Ritual matters.  ", "note": "he wins four dollars · you are now permanently the lucky one · this will not stay simple", "till": 0, "regulars": 2, "nerve": 0},
			{"label": "  Tell him luck doesn't work by proxy.  ", "note": "Gus respects it · buys the same ticket he always buys · loses like always", "till": 0, "regulars": 1, "nerve": 1},
			{"label": "  Sell him the ticket and say nothing.  ", "note": "clean transaction · Dot notices you keeping the counter between you and everyone", "till": 1, "regulars": -1, "nerve": 0}
		]
	},
	{
		"title": "WEEK 3 · HEAT WAVE",
		"text": "Ninety-eight degrees.  The cooler compressor dies at noon with a sound like a dropped wrench.  Everything in it has maybe four hours.  Ray is at the coast and not answering.\n\nThe soda is warming.  The log-truck drivers will be here at 6:30 tomorrow expecting cold.",
		"choices": [
			{"label": "  Mark everything half price and sell it warm, honestly.  ", "note": "the drawer takes the hit · nobody pretends warm soda is fine · people remember honesty in a heat wave", "till": -1, "regulars": 2, "nerve": 0},
			{"label": "  Drive to Longview for ice on your own dime.  ", "note": "forty dollars of ice · the cooler becomes a legend for one day · Ray pays you back without being asked", "till": 1, "regulars": 1, "nerve": -1},
			{"label": "  Tape the cooler shut and sell what's on the shelf.  ", "note": "defensible · boring · Gus buys warm orange soda anyway out of loyalty and tells you it's fine, which it is not", "till": 1, "regulars": 0, "nerve": 0}
		]
	},
	{
		"title": "WEEK 4 · THE KID",
		"text": "A kid, maybe ten, puts a candy bar in his sock while pretending to read a comic.  He is bad at it in the way of someone doing it for the first time.  You know his bike.  It's outside every Tuesday.\n\nHe heads for the door.",
		"choices": [
			{"label": "  'Hey.  Sweeping.  Ten minutes, and it's yours.'  ", "note": "he sweeps · he keeps the candy bar · he comes back Tuesdays and sweeps without being asked · you have accidentally hired someone", "till": 0, "regulars": 2, "nerve": 1},
			{"label": "  Ring it up yourself from the tip jar.  ", "note": "the kid never knows · the drawer stays clean · something in you files this under 'things Ray doesn't need to hear about'", "till": 1, "regulars": 0, "nerve": 0},
			{"label": "  Stop him at the door and call his house.  ", "note": "by the book · his mother is mortified · Tuesday bike stops appearing · Dot looks at you for one second longer than usual", "till": 1, "regulars": -2, "nerve": 0}
		]
	},
	{
		"title": "WEEK 5 · THE MYSTERY SHOPPER",
		"text": "Corporate sends a mystery shopper every summer.  Ray warned you: 'They buy gas, a coffee, and one weird item.  Rate you on a clipboard in the car.'\n\nA man in a golf shirt buys gas, a coffee, and a single can of cat food.  He asks how your summer is going with the cadence of a man reading the question off a card.",
		"choices": [
			{"label": "  Give the corporate-perfect greeting, upsell the muffins.  ", "note": "textbook · he checks boxes · the muffins were two days old and you knew it", "till": 2, "regulars": 0, "nerve": -1},
			{"label": "  Answer him like a person.  'Long.  Good-long.'  ", "note": "he looks up from the card · writes something not on the form · the region manager later asks Ray who you are", "till": 0, "regulars": 1, "nerve": 1},
			{"label": "  'The cat food gives you away.  Nobody buys ONE can.'  ", "note": "a long pause · then the first real laugh you've heard from a golf shirt · the clipboard score is perfect and possibly fraudulent", "till": 1, "regulars": 1, "nerve": 0}
		]
	},
	{
		"title": "WEEK 6 · THE ROBBERY",
		"text": "Tuesday, 9:41 PM.  Nineteen minutes to close.  A man comes in with his hand inside his jacket and asks for the drawer in a voice that has practiced this sentence and nothing after it.\n\nHe is younger than you.  His hand is shaking inside the jacket.  The security camera has been broken since June and everyone in town knows it.",
		"choices": [
			{"label": "  Open the drawer.  Step back.  Say nothing.  ", "note": "he takes sixty-one dollars and runs · training says you did it right · your hands say otherwise for a week", "till": -1, "regulars": 0, "nerve": -2},
			{"label": "  'Okay.  It's yours.  You want the food too?  Take food.'  ", "note": "he freezes · takes the money and two sandwiches · at the door he says sorry · you believe him · this is somehow worse and better", "till": -1, "regulars": 1, "nerve": -1},
			{"label": "  Hit the silent alarm with your knee while you open the drawer.  ", "note": "he's gone before the county sheriff is close · sixty-one dollars · you spend the night giving statements and feeling like a movie extra", "till": 0, "regulars": 0, "nerve": -2}
		]
	},
	{
		"title": "WEEK 7 · THE WEEK AFTER",
		"text": "Ray offered you paid time off.  Corporate sent a laminated card about trauma with a 1-800 number.  Dot has switched, without comment, to arriving at opening and staying twenty minutes longer than her coffee takes.\n\nYour hands still do the thing when the door chime goes.",
		"choices": [
			{"label": "  Take your shifts.  All of them.  ", "note": "the only way you know how to do this · the chime gets quieter by Friday", "till": 1, "regulars": 0, "nerve": 1},
			{"label": "  Swap to day shifts for two weeks.  ", "note": "reasonable · the night crew covers · you feel the specific guilt of the sensible decision", "till": 0, "regulars": 0, "nerve": 2},
			{"label": "  Tell Dot about the hands and the chime.  ", "note": "she says 'I was robbed twice in '81 at the Arco.'  That's all.  It's enough.  It's exactly enough.", "till": 0, "regulars": 2, "nerve": 2}
		]
	},
	{
		"title": "WEEK 8 · THE RUMOR MILL",
		"text": "The county paper ran four sentences about the robbery.  The town has run four hundred.  In this week's version you fought him off with the coffee pot.\n\nGus repeats it to your face, delighted, buying his scratcher.  A woman you've never seen drives out from Rainier just to look at you.",
		"choices": [
			{"label": "  Correct the story every single time.  ", "note": "the truth is unglamorous and you insist on it · Dot approves · the story dies by Thursday · you kind of miss it", "till": 0, "regulars": 1, "nerve": 1},
			{"label": "  Let the story do what stories do.  ", "note": "by August you have fought off two men and possibly a bear · sales are up · you are a tourist attraction now", "till": 2, "regulars": 1, "nerve": -1},
			{"label": "  'The coffee pot was empty.  I'd never waste full coffee.'  ", "note": "a joke that feeds the legend AND signals you're okay · Gus tells everyone · the retelling now includes your line, verbatim", "till": 1, "regulars": 2, "nerve": 0}
		]
	},
	{
		"title": "WEEK 9 · FAIR WEEKEND",
		"text": "Clatskanie Heritage Days.  The highway becomes a parade route for three days and every car needs gas, ice, film, and directions.  You have never rung this fast in your life.  The drawer must be counted at every shift change or the weekend eats it.",
		"choices": [
			{"label": "  Systems.  Line discipline.  Call-outs.  You run the counter like a galley.  ", "note": "the drawer balances all three nights · Ray watches you for a while from the cooler door and says nothing, which from Ray is a medal", "till": 3, "regulars": 0, "nerve": -1},
			{"label": "  Loose and friendly.  The line moves slower and laughs more.  ", "note": "you lose maybe forty dollars of shrink and gain the whole fair crowd · three people from Portland ask if this place is always like this", "till": -1, "regulars": 3, "nerve": 0},
			{"label": "  Draft the Tuesday kid to bag and run ice.  ", "note": "he shows up in a clip-on tie · unstoppable · Dot pays him in quarters at closing like a casino boss", "till": 1, "regulars": 2, "nerve": 1}
		]
	},
	{
		"title": "WEEK 10 · THE OTHER SAM",
		"text": "A trucker you've never seen pays for diesel and squints at your name tag.\n\n'Huh.  There's a kid named Sam runs a Kwik Stop down the coast.  Estuary country.  Counts the drawer twice, same as you.'\n\nHe says it like it means something.  It doesn't.  It couldn't.  You think about it for the rest of the shift.",
		"choices": [
			{"label": "  'Common name.'  ", "note": "true · the shift goes on · at closing you count the drawer twice and stop halfway through the second count, amused at yourself", "till": 1, "regulars": 0, "nerve": 1},
			{"label": "  Ask what the other Sam is like.  ", "note": "'Quiet. Good with the regulars. The store's got a bird that lives in the rafters.' · you are strangely glad the other Sam is doing okay", "till": 0, "regulars": 1, "nerve": 1},
			{"label": "  'Tell him the Hi-Way 30 Sam says the drawer's always eighty even.'  ", "note": "a message in a bottle between two people who will never meet · the trucker promises · truckers keep these promises", "till": 0, "regulars": 2, "nerve": 0}
		]
	},
	{
		"title": "WEEK 11 · INVENTORY NIGHT",
		"text": "The whole store counted, shelf by shelf, after close, with Ray and a clipboard and the radio on the county station.  Around midnight Ray talks the way people only talk during inventory.\n\n'Twenty-two years I've had this store.  Kid, you're the first clerk who made it better instead of just keeping it open.'",
		"choices": [
			{"label": "  'It's a good store, Ray.'  ", "note": "the correct answer · the only answer · the radio plays something from 1978 and you both count in silence for a while", "till": 1, "regulars": 1, "nerve": 1},
			{"label": "  Ask him about the twenty-two years.  ", "note": "you learn the store's whole history including the '81 Arco robbery, which is how you learn Dot has been protecting clerks here for two decades", "till": 0, "regulars": 2, "nerve": 1},
			{"label": "  Ask what happens after summer.  ", "note": "Ray looks at the clipboard for a moment.  'That depends on you, doesn't it.'  He counts motor oil like he didn't just say that.", "till": 1, "regulars": 0, "nerve": 0}
		]
	},
	{
		"title": "WEEK 12 · LAST SHIFT",
		"text": "The last Saturday of summer.  Dot arrives at 5:40.  Gus wins eleven dollars and frames the ticket instead of cashing it.  The Tuesday kid sweeps without candy involved anymore, on principle.\n\nAt close, Ray leans on the counter with an envelope he keeps not handing you.",
		"choices": [
			{"label": "  Count the drawer one last time.  Twice.  ", "note": "eighty even, both counts · you set the key on the lanyard down flat · summers end the way drawers balance", "till": 1, "regulars": 0, "nerve": 1},
			{"label": "  Ask Ray what's in the envelope.  ", "note": "he slides it over · what happens next depends on the summer you had", "till": 0, "regulars": 1, "nerve": 0},
			{"label": "  Say the goodbyes first.  Dot.  Gus.  The kid.  ", "note": "Dot shakes your hand · nine words again · all nine land · you get the envelope either way", "till": 0, "regulars": 2, "nerve": 0}
		]
	}
]

# Endings
const ENDINGS: Dictionary = {
	"walked_off": {
		"title": "· WALKED OFF THE JOB ·",
		"text": "There's a version of this summer where you finish it.  This isn't that one.\n\nYou set the lanyard on the counter mid-shift and walk out into the parking lot heat, and the door chime rings behind you one last time, and it doesn't make your hands do anything at all, and that's how you know it was the right call and the wrong one at the same time.\n\nRay mails your last check with a note: 'Door's open next June.'  He means it."
	},
	"kept_the_summer": {
		"title": "· KEPT THE SUMMER ·",
		"text": "The envelope is a bonus check and a Polaroid Ray took of the storefront in June, before you started, when the window still had last year's poster in it.\n\nOn the back, in pencil: 'BEFORE.'\n\nThat's the whole review.  You worked a register in a town off Highway 30 for twelve weeks, and the place is better, and the drawer is eighty even, and the summer is over, and you kept it.  Every week of it.  Even the one nobody wants."
	},
	"made_manager": {
		"title": "· MADE MANAGER ·",
		"text": "The envelope is a key.  Not the register key · the door key.\n\n'Winters I go to my sister's in Yuma,' Ray says, at the counter, not looking at you.  'Store needs somebody October through March.  Somebody the regulars already trained.'\n\nDot, from her stool, without turning around: 'He'll do it.'\n\nAnd that's that.  You came for a summer job.  You leave with a store, a town's worth of 5:40 AM regulars, and the specific feeling of a drawer that balances because you're the one who counts it."
	}
}

var _run_state: Dictionary = {}
var _phase: String = "week"        # shift | week | ending

# ── THE SHIFT (2026-07-27 depth pass) ────────────────────────────
# Every week now OPENS at the register: a seeded queue of customers
# you actually ring — pick the right total (register craft · TILL)
# and handle the counter moments (REGULARS · NERVE) — before the
# week's beat. Week 6's third customer is the robbery. Heritage
# Days rings a longer line with tighter totals.
const CUSTOMERS := [
	{"id": "gus", "line": "Gus, first through the door, exact same order since Nixon.",
	 "items": [["scratcher", 1.00], ["coffee, small", 0.65]],
	 "moment": {"prompt": "He's a dime short. He knows it. You know it. He's looking at you.",
		"choices": [
			{"label": "  Wave it off. It's Gus.  ", "regulars": 1, "till": 0, "note": "the drawer is a dime light and the morning is right"},
			{"label": "  'Dime, Gus.'  ", "till": 1, "regulars": -1, "note": "he pays it and calls you Ray Junior for a week"}]}},
	{"id": "dot", "line": "Dot from the diner, buying the register's whole roll of quarters.",
	 "items": [["roll of quarters", 10.00], ["iced tea", 0.89]]},
	{"id": "hay_crew", "line": "Two guys off a hay truck, sunburned past argument.",
	 "items": [["gas", 14.50], ["ice", 1.85], ["pop, two", 1.30]]},
	{"id": "film_lady", "line": "A woman with a station wagon full of kids wants film before the light goes.",
	 "items": [["film, 24 exp", 4.99], ["candy, assorted", 2.15]],
	 "moment": {"prompt": "The kids are eyeing the candy rack like a jury.",
		"choices": [
			{"label": "  Slip each kid a tootsie roll on the house.  ", "regulars": 1, "till": -1, "note": "four future customers, one nickel each"},
			{"label": "  Keep the line moving.  ", "till": 1, "note": "the drawer stays honest and the wagon rolls on"}]}},
	{"id": "trucker", "line": "A long-hauler wants the works and wants it counted back out loud.",
	 "items": [["diesel", 22.75], ["coffee, large", 0.95], ["jerky", 3.49]]},
	{"id": "check_guy", "line": "A man you've never seen wants to pay with an out-of-county check.",
	 "items": [["gas", 11.20], ["oil, quart", 2.29]],
	 "moment": {"prompt": "Ray's rule is county checks only. The man is polite and in a hurry, which is either nothing or something.",
		"choices": [
			{"label": "  Take the check.  ", "till": -1, "nerve": 0, "note": "it clears, or it doesn't · you'll know friday"},
			{"label": "  'Cash or county, sorry.'  ", "till": 1, "nerve": 1, "regulars": -1, "note": "he pays cash, unhappily · the rule holds because somebody holds it"}]}},
	{"id": "teens", "line": "Three teenagers, one of them auditioning to buy beer with a mustache that isn't finished.",
	 "items": [["pop, three", 1.95], ["chips", 1.59]],
	 "moment": {"prompt": "The tall one sets a six-pack on the counter and dares you with his eyebrows.",
		"choices": [
			{"label": "  Card him.  ", "nerve": 1, "regulars": 0, "note": "he's sixteen · the pack goes back · his friends are delighted"},
			{"label": "  Pretend not to see the six-pack until he puts it back himself.  ", "regulars": 1, "note": "the town's oldest de-escalation"}]}},
	{"id": "rainier_lady", "line": "A woman from Rainier who talks to you like the store is a museum of itself.",
	 "items": [["postcard", 0.35], ["pop", 0.65], ["film, 12 exp", 3.49]]},
	{"id": "night_guy", "line": "The quiet man who buys the same two things and never says which shift he's coming off.",
	 "items": [["coffee, large", 0.95], ["sandwich, egg", 2.25]]},
	{"id": "mrs_alvarez", "line": "Mrs. Alvarez, fourteen items, coupons for six of them, patience for all of it.",
	 "items": [["groceries", 18.40], ["ice cream, pints", 4.50]],
	 "moment": {"prompt": "Her coupon for the ice cream expired Tuesday.",
		"choices": [
			{"label": "  Take it anyway.  ", "regulars": 1, "till": -1, "note": "forty cents of neighborliness"},
			{"label": "  'This one's expired, sorry.'  ", "till": 1, "note": "she pays it and respects you slightly more and likes you slightly less"}]}},
	{"id": "fisherman", "line": "A fisherman off the Columbia with a cooler and a theory about the weather.",
	 "items": [["ice, two bags", 3.70], ["bait", 2.95], ["beer", 4.25]]},
	{"id": "bus_kids", "line": "The church bus stops and eleven kids want eleven different things simultaneously.",
	 "items": [["slushies, eleven", 8.25], ["napkins", 0.00]]},
	{"id": "salesman", "line": "A rack-jobber wants to sell Ray a display of sunglasses nobody in this county will buy.",
	 "items": [["coffee, small", 0.65]],
	 "moment": {"prompt": "He wants you to 'just sign for the trial rack, kid.'",
		"choices": [
			{"label": "  'Ray signs. Ray's at the coast.'  ", "till": 1, "nerve": 1, "note": "the oldest counter-move · he respects it"},
			{"label": "  Sign it. How bad can it be.  ", "till": -2, "note": "the rack arrives thursday · Ray's face on friday is a whole education"}]}},
	{"id": "dot_late", "line": "Dot again, off-shift now, buying one pack of the cigarettes she quit.",
	 "items": [["cigarettes", 1.85], ["matches", 0.10]]},
	{"id": "old_ray_friend", "line": "An old man who knew Ray's father, narrating the store as it was in 1958.",
	 "items": [["pop", 0.65], ["pretzels", 1.19]]},
	{"id": "heritage_family", "line": "A family in matching festival shirts needs gas, ice, film, and directions.",
	 "items": [["gas", 13.60], ["ice", 1.85], ["film, 24 exp", 4.99]]},
]

var _shift_queue: Array = []
var _shift_idx: int = 0
var _rings_right: int = 0
var _rings_total: int = 0
var _shift_week_done: int = -1


func _shift_rng(week: int, salt: int) -> RandomNumberGenerator:
	var rng := RandomNumberGenerator.new()
	if not _run_state.has("seed"):
		_run_state["seed"] = randi() % 100000
	rng.seed = int(_run_state["seed"]) * 41 + week * 17 + salt
	return rng


func _start_shift(week: int) -> void:
	_phase = "shift"
	var rng := _shift_rng(week, 0)
	var pool: Array = CUSTOMERS.duplicate()
	var count: int = 8 if week == 8 else 6
	if week == 6:
		count = 3   # the third customer is not a customer
	_shift_queue = []
	for _i in range(count):
		if pool.is_empty():
			break
		_shift_queue.append(pool.pop_at(rng.randi_range(0, pool.size() - 1)))
	_shift_idx = 0
	_rings_right = 0
	_rings_total = 0
	_render_customer()


func _render_customer() -> void:
	var week: int = int(_run_state.get("week", 1))
	if _shift_idx >= _shift_queue.size():
		_end_shift()
		return
	_clear_content()
	var cust: Dictionary = _shift_queue[_shift_idx]
	_content_root = Control.new()
	_content_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_content_root)
	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -400
	v.offset_right = 400
	v.offset_top = -230
	v.offset_bottom = 250
	v.add_theme_constant_override("separation", 10)
	_content_root.add_child(v)
	var hdr := Label.new()
	hdr.text = "· WEEK %d · THE SHIFT · customer %d of %d ·      %s" % [week, _shift_idx + 1, _shift_queue.size(), _meters_string()]
	hdr.add_theme_font_size_override("font_size", 13)
	hdr.add_theme_color_override("font_color", C_DIM)
	v.add_child(hdr)
	var line := Label.new()
	line.text = String(cust.get("line", ""))
	line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	line.add_theme_font_size_override("font_size", 16)
	line.add_theme_color_override("font_color", C_CREAM)
	v.add_child(line)
	var total: float = 0.0
	for it_v in cust.get("items", []):
		var it: Array = it_v
		total += float(it[1])
		var il := Label.new()
		il.text = "    %s · $%.2f" % [String(it[0]), float(it[1])]
		il.add_theme_font_size_override("font_size", 14)
		il.add_theme_color_override("font_color", C_YELLOW)
		v.add_child(il)
	var prompt := Label.new()
	prompt.text = "RING IT:"
	prompt.add_theme_font_size_override("font_size", 14)
	prompt.add_theme_color_override("font_color", C_RED)
	v.add_child(prompt)
	# three totals · one true · Heritage week cuts the spread tight
	var rng := _shift_rng(week, 100 + _shift_idx)
	var spread_lo: float = 0.10 if week == 8 else 0.30
	var spread_hi: float = 0.35 if week == 8 else 0.95
	var opts: Array = [total]
	while opts.size() < 3:
		var d: float = rng.randf_range(spread_lo, spread_hi) * (1.0 if rng.randi_range(0, 1) == 0 else -1.0)
		var cand: float = snappedf(total + d, 0.05)
		if cand > 0.0 and not opts.has(cand):
			opts.append(cand)
	# seeded shuffle
	for i in range(opts.size() - 1, 0, -1):
		var j: int = rng.randi_range(0, i)
		var tmp: Variant = opts[i]
		opts[i] = opts[j]
		opts[j] = tmp
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 16)
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	v.add_child(row)
	for o_v in opts:
		var amount: float = float(o_v)
		var b := Button.new()
		b.text = "  $%.2f  " % amount
		b.add_theme_font_size_override("font_size", 16)
		b.pressed.connect(_on_ring.bind(cust, absf(amount - total) < 0.01))
		row.add_child(b)
	GamepadMgr.focus_first.call_deferred(row)


func _on_ring(cust: Dictionary, right: bool) -> void:
	_rings_total += 1
	var sfx := get_node_or_null("/root/SFXBank")
	if right:
		_rings_right += 1
		if sfx: sfx.play("register_ding", 0.4)
	else:
		if sfx: sfx.play("loss_thud", 0.3)
	var moment: Dictionary = cust.get("moment", {})
	if not moment.is_empty():
		_render_moment(cust, moment, right)
	else:
		_shift_idx += 1
		_render_customer()


func _render_moment(cust: Dictionary, moment: Dictionary, rang_right: bool) -> void:
	_clear_content()
	_content_root = Control.new()
	_content_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_content_root)
	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -400
	v.offset_right = 400
	v.offset_top = -170
	v.offset_bottom = 210
	v.add_theme_constant_override("separation", 10)
	_content_root.add_child(v)
	var ring_note := Label.new()
	ring_note.text = "· rung true ·" if rang_right else "· rung wrong · you'll find it at count-out ·"
	ring_note.add_theme_font_size_override("font_size", 13)
	ring_note.add_theme_color_override("font_color", C_GREEN if rang_right else C_RED)
	v.add_child(ring_note)
	var prompt := Label.new()
	prompt.text = String(moment.get("prompt", ""))
	prompt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	prompt.add_theme_font_size_override("font_size", 16)
	prompt.add_theme_color_override("font_color", C_CREAM)
	v.add_child(prompt)
	for c_v in moment.get("choices", []):
		var choice: Dictionary = c_v
		var b := Button.new()
		b.text = String(choice.get("label", ""))
		b.add_theme_font_size_override("font_size", 15)
		b.pressed.connect(func() -> void:
			_apply_deltas(choice)
			_shift_idx += 1
			_render_customer())
		v.add_child(b)
		var note := Label.new()
		note.text = "     " + String(choice.get("note", ""))
		note.add_theme_font_size_override("font_size", 12)
		note.add_theme_color_override("font_color", C_DIM)
		note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		v.add_child(note)
	GamepadMgr.focus_first.call_deferred(v)


func _apply_deltas(choice: Dictionary) -> void:
	var till_mult: int = 2 if int(_run_state.get("week", 1)) == int(_run_state.get("solo_week", -1)) else 1
	_run_state["till"] = clampi(int(_run_state.get("till", 3)) + int(choice.get("till", 0)) * till_mult, 0, 10)
	_run_state["regulars"] = clampi(int(_run_state.get("regulars", 3)) + int(choice.get("regulars", 0)), 0, 10)
	_run_state["nerve"] = clampi(int(_run_state.get("nerve", 3)) + int(choice.get("nerve", 0)), 0, 10)


func _end_shift() -> void:
	var week: int = int(_run_state.get("week", 1))
	_shift_week_done = week
	# Persisted so a quit/resume mid-week doesn't replay the shift and
	# re-apply its meter deltas.
	_run_state["shift_done_week"] = week
	# register craft converts to the drawer
	var frac: float = float(_rings_right) / maxf(1.0, float(_rings_total))
	var till_mult: int = 2 if week == int(_run_state.get("solo_week", -1)) else 1
	if frac >= 0.8:
		_run_state["till"] = clampi(int(_run_state.get("till", 3)) + 1 * till_mult, 0, 10)
	elif frac < 0.5:
		_run_state["till"] = clampi(int(_run_state.get("till", 3)) - 1 * till_mult, 0, 10)
	if int(_run_state.get("nerve", 3)) <= 0:
		_render_ending("walked_off")
		return
	_phase = "week"
	_render_week_beat()
var _ending_id: String = ""
var _content_root: Control = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(state: Dictionary) -> void:
	_run_state = state
	# One solo week per summer · Ray's at the coast and Sam runs the
	# store alone, so register craft counts double.  Rolled once and
	# saved; never lands on the intro, the robbery, or the last shift.
	if not _run_state.has("solo_week"):
		var pool: Array = [2, 3, 4, 5, 7, 10, 11]
		_run_state["solo_week"] = int(pool[randi() % pool.size()])
	# Restore the shift-done marker · transient before, which replayed
	# a finished shift (and its meter deltas) on quit/resume.
	_shift_week_done = int(_run_state.get("shift_done_week", -1))
	_build_frame()
	_render_week()


func _build_frame() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	var band_top := ColorRect.new()
	band_top.color = C_RED
	band_top.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	band_top.offset_top = 0
	band_top.offset_bottom = 32
	add_child(band_top)

	var hdr := Label.new()
	hdr.text = "SAM'S SUMMER SHIFTS · HI-WAY 30 STOP-N-GO"
	hdr.set_anchors_preset(Control.PRESET_TOP_LEFT)
	hdr.position = Vector2(14, 8)
	hdr.add_theme_font_size_override("font_size", 15)
	hdr.add_theme_color_override("font_color", C_BG)
	add_child(hdr)

	var stripe := ColorRect.new()
	stripe.color = C_YELLOW
	stripe.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	stripe.offset_top = 32
	stripe.offset_bottom = 37
	add_child(stripe)


func _meters_string() -> String:
	return "TILL %d/10  ·  REGULARS %d/10  ·  NERVE %d/10" % [
		int(_run_state.get("till", 3)),
		int(_run_state.get("regulars", 3)),
		int(_run_state.get("nerve", 3))
	]


func _clear_content() -> void:
	if _content_root != null and is_instance_valid(_content_root):
		_content_root.queue_free()
	_content_root = null


func _render_week() -> void:
	var wknum: int = clampi(int(_run_state.get("week", 1)), 1, 12)
	if _shift_week_done != wknum:
		_start_shift(wknum)
		return
	_render_week_beat()


func _render_week_beat() -> void:
	_clear_content()
	var week: int = clampi(int(_run_state.get("week", 1)), 1, 12)
	var wk: Dictionary = WEEKS[week - 1]
	if week == 6:
		# (the shift's third customer was not a customer)
		# The robbery week opens in the hands before it opens on
		# screen · a slow strong-motor swell, no sound.
		var bank := get_node_or_null("/root/SFXBank")
		if bank != null and bank.has_method("rumble"):
			bank.call("rumble", 0.08, 0.35, 0.9)

	_content_root = Control.new()
	_content_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_content_root)

	var panel := ColorRect.new()
	panel.color = C_GRAY
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.offset_left = -420
	panel.offset_right = 420
	panel.offset_top = -230
	panel.offset_bottom = 250
	_content_root.add_child(panel)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -400
	v.offset_right = 400
	v.offset_top = -210
	v.offset_bottom = 230
	v.add_theme_constant_override("separation", 10)
	_content_root.add_child(v)

	var title := Label.new()
	title.text = String(wk.get("title", ""))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 20)
	title.add_theme_color_override("font_color", C_YELLOW)
	v.add_child(title)

	var meters := Label.new()
	meters.text = "· " + _meters_string() + " ·"
	meters.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	meters.add_theme_font_size_override("font_size", 14)
	meters.add_theme_color_override("font_color", C_GREEN)
	v.add_child(meters)

	if week == int(_run_state.get("solo_week", -1)):
		var mod_lbl := Label.new()
		mod_lbl.text = "· RAY'S AT THE COAST · you run it solo this week · till swings count double ·"
		mod_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		mod_lbl.add_theme_font_size_override("font_size", 13)
		mod_lbl.add_theme_color_override("font_color", C_YELLOW)
		v.add_child(mod_lbl)

	var week_text := String(wk.get("text", ""))
	# Crossover guest · Fair Weekend only, and only if the shelf has
	# a finished PIRATE SUMMER save somewhere in the token store.
	if week == 9 and OneironauticsTokens.has("pirate_summer_finished"):
		week_text += "\n\nSaturday of the fair, a guy buys a blue slushie and a rock-shaped postcard.  His t-shirt says CAMP SWEETGUM STAFF.  He drums two fingers on the counter · some song you almost know · and says the canteen slushies at camp were never this good, and that a friend of his would want the postcard because it looks like a rock she'd respect.  He leaves humming it.  You hum it for the rest of the shift and can't say where it came from."

	var body := RichTextLabel.new()
	body.bbcode_enabled = false
	body.fit_content = true
	body.text = week_text
	body.add_theme_font_size_override("normal_font_size", 16)
	body.add_theme_color_override("default_color", C_CREAM)
	body.custom_minimum_size = Vector2(760, 130)
	v.add_child(body)

	for c_v in wk.get("choices", []):
		var choice: Dictionary = c_v
		var vh := VBoxContainer.new()
		vh.add_theme_constant_override("separation", 1)
		v.add_child(vh)

		var btn := Button.new()
		btn.text = String(choice.get("label", ""))
		btn.add_theme_font_size_override("font_size", 15)
		btn.pressed.connect(func() -> void: _on_choice(choice))
		vh.add_child(btn)

		var note := Label.new()
		note.text = "     " + String(choice.get("note", ""))
		note.add_theme_font_size_override("font_size", 12)
		note.add_theme_color_override("font_color", C_DIM)
		note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		vh.add_child(note)

	var back := Button.new()
	back.text = "  ← clock out (save + title)  "
	back.add_theme_font_size_override("font_size", 14)
	back.pressed.connect(func() -> void: quit.emit())
	v.add_child(back)


func _on_choice(choice: Dictionary) -> void:
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("register_ding", 0.5)
	var till_mult: int = 2 if int(_run_state.get("week", 1)) == int(_run_state.get("solo_week", -1)) else 1
	_run_state["till"] = clampi(int(_run_state.get("till", 3)) + int(choice.get("till", 0)) * till_mult, 0, 10)
	_run_state["regulars"] = clampi(int(_run_state.get("regulars", 3)) + int(choice.get("regulars", 0)), 0, 10)
	_run_state["nerve"] = clampi(int(_run_state.get("nerve", 3)) + int(choice.get("nerve", 0)), 0, 10)
	var log: Array = _run_state.get("choices_log", [])
	log.append({"week": int(_run_state.get("week", 1)), "label": String(choice.get("label", "")).strip_edges()})
	_run_state["choices_log"] = log

	# Nerve 0 · Sam walks off · early ending
	if int(_run_state.get("nerve", 3)) <= 0:
		_render_ending("walked_off")
		return

	var week: int = int(_run_state.get("week", 1))
	if week >= 12:
		# Final ending selection
		if int(_run_state.get("till", 0)) >= 6 and int(_run_state.get("regulars", 0)) >= 6:
			_render_ending("made_manager")
		else:
			_render_ending("kept_the_summer")
		return

	_run_state["week"] = week + 1
	week_complete.emit(_run_state)
	_shift_week_done = -1
	_render_week()


func _render_ending(ending_id: String) -> void:
	_ending_id = ending_id
	_phase = "ending"
	_clear_content()
	var e: Dictionary = ENDINGS.get(ending_id, ENDINGS["kept_the_summer"])

	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("win_chord" if ending_id != "walked_off" else "loss_thud", 0.7)

	_content_root = Control.new()
	_content_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_content_root)

	var panel := ColorRect.new()
	panel.color = C_GRAY
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.offset_left = -420
	panel.offset_right = 420
	panel.offset_top = -200
	panel.offset_bottom = 220
	_content_root.add_child(panel)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -400
	v.offset_right = 400
	v.offset_top = -180
	v.offset_bottom = 200
	v.add_theme_constant_override("separation", 14)
	_content_root.add_child(v)

	var title := Label.new()
	title.text = String(e.get("title", ""))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 20)
	title.add_theme_color_override("font_color", C_YELLOW)
	v.add_child(title)

	var meters := Label.new()
	meters.text = "· final · " + _meters_string() + " ·"
	meters.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	meters.add_theme_font_size_override("font_size", 14)
	meters.add_theme_color_override("font_color", C_GREEN)
	v.add_child(meters)

	var body := RichTextLabel.new()
	body.bbcode_enabled = false
	body.fit_content = true
	body.text = String(e.get("text", ""))
	body.add_theme_font_size_override("normal_font_size", 16)
	body.add_theme_color_override("default_color", C_CREAM)
	body.custom_minimum_size = Vector2(760, 180)
	v.add_child(body)

	var done := Button.new()
	done.text = "  · turn off the slowstick ·  "
	done.add_theme_font_size_override("font_size", 16)
	done.add_theme_color_override("font_color", C_YELLOW)
	done.pressed.connect(func() -> void: summer_over.emit(_run_state, _ending_id))
	v.add_child(done)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			quit.emit()
			get_viewport().set_input_as_handled()
