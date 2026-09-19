# THE VN CONSEQUENCE MAP — generated, do not edit

`python3 godot/tools/audit/consequence_map.py` draws this from the scene
JSON in `index.json` reading order. It is the design pillar's first
document (lore/_VISUAL_PROGRAM.md §6): what the reader can choose, what
the game remembers, and which skill checks can actually pass.

Skill rule: an option with `"skill": "<name>"` trains that skill by
one (or `"amount"`) when taken. A check passes when the skill is at or
above `diff`. **Earnable** is the most the reader can have before the
check's scene, taking the best option at every earlier choice.

| | |
|---|---|
| choices | 28 |
| skill checks | 5 |
| checks that cannot pass | 0 |
| flags set | 58 |
| flags set and never read | 38 |


## Volume 1 — 43 scenes · 12 choices · 2 checks

Skills earnable across the volume: empathy 4, logic 5, composure 7, rhetoric 7, signal 6


### Choices

**vol1_link_hub** #4
> 

- Look out the rain-glazed window. → scene `vol1_link_window` — trains **signal**
- Read the laminated menu. → scene `vol1_link_menu` — trains **logic**
- Stand by the jukebox. → scene `vol1_link_jukebox` — trains **signal**
- Examine the photographs above the booth. → scene `vol1_link_booth` — trains **logic**
- Take a stool at the counter. → scene `vol1_link_counter` — trains **rhetoric**
- Step outside to the bench. → scene `vol1_link_outside`
- Wait. The bus will come when it comes. → scene `vol1_link_shuttle` — trains **composure**

**vol1_link_outside_hub** #2
> 

- "Are you waiting for the Shillelagh?" → scene `vol1_link_q_shuttle` — trains **signal**
- "What's your name?" → scene `vol1_link_q_name` — trains **rhetoric**
- "Why does your coat glow at the seams?" → scene `vol1_link_q_coat` — trains **signal**
- "Where are you going?" → scene `vol1_link_q_where` — trains **logic**
- "Why aren't you cold?" → scene `vol1_link_q_cold` — trains **empathy**
- [Step back inside.] → scene `vol1_link_hub`

**vol1_link_shuttle** #13
> "We have a seat for you. We always do. You don't have to take it tonight."

- [Step up into the bus.] → #14 — trains **signal**
- [Stay on the apron. Watch it go.] → #17 — trains **composure**

**vol1_ch1_s2** #4
> The distinction, you're realizing, may not matter as much as you thought.

- "What are you?" → #5 — trains **signal**
- "Why are you telling me this?" → #8 — trains **logic**
- [LOGIC] The coffee appeared without anyone taking an order. The booth was empty when you w → next — CHECK logic ≥ 1 (pass #11 / fail #8)

**vol1_ch2_pharmacy** #9
> The latest model. Think I'll try three. Going down a stringent chalky burn — can't sell what isn't personal.

- Swallow them with coffee. → #10
- [COMPOSURE] Set the bottle down. Two will do. → next — CHECK composure ≥ 1 (pass #13 / fail #10)

**vol1_ch2_park** #21
> I know of Monsieur Xenu — but not of this Parsons dude.

- "Long story short, let me sum it up." → #22 — trains **logic**
- "Buckle up. This one earns its bourbon." → #22 — trains **rhetoric**

**vol1_ch2_painting** #38
> I just want to paint you. Not hash out some magical deal. So apologies if I get the details wrong — next time I'll take a reference photo.

- [Listen to Fire. Lean in.] → #39 — trains **rhetoric**
- [Listen to Water. Stay steady.] → #41 — trains **composure**
- [Listen to Air. Take the warning.] → #43 — trains **signal**

**vol1_ch3_bar** #23
> Already drawing up some wacky shit. Still hot for teacher or star pupil — move, but quick, else some one will. There's timing, and then there's timing.

- "Time and place for everything — you know this." → #24 — trains **rhetoric**
- "From where you look, sure. From where I sit, no." → #26 — trains **logic**
- [Say nothing. Let him finish.] → #28 — trains **empathy**

**vol1_ch3_outside** #10
> What sort of superpower would you have?

- "To be myself, only better." → #11 — trains **composure**
- "Flight. The earthbound thing tires me." → #13
- "I'd hear what people aren't saying." → #15 — trains **signal**

**vol1_ch4_dream_states** #16
> Want me to leave you be — or hold you close?

- "If you're already in my head — hold me close." → #17 — trains **empathy**
- "Leave me. Let me sleep this off." → #21 — trains **composure**

**vol1_ch4_club_sharp** #21
> No joke. Mania creeps inside. So you either have to want it in you — or not.

- "What if insanity was a large part of me to begin with?" → #22 — trains **rhetoric**
- "Then I'll fortify. I have things to make." → #25 — trains **composure**
- [Say nothing. Watch the dance floors.] → #28 — trains **empathy**

**vol1_ch4_club_sharp_b** #13
> Faust straightens up.

- "Can I see you again tomorrow?" → #14 — trains **rhetoric**
- "I have to go. The friends I came with." → #18 — trains **composure**

### Checks

| scene | skill | diff | earnable before | pass ≠ fail | verdict |
|---|---|---|---|---|---|
| vol1_ch1_s2 #4 | logic | 1 | 2 | yes | passable |
| vol1_ch2_pharmacy #9 | composure | 1 | 2 | yes | passable |

### Flags

| flag | set at | read at |
|---|---|---|
| `faust_asked_for_joan` | vol1_ch4_club_sharp_b#16, vol1_ch4_club_sharp_b#20 | vol1_ch4_waking#5 (when_flag), vol1_ch4_waking#6 (when_not_flag) |
| `faust_black_lodge` | vol1_ch3_outside_b#17 | **never — loose** |
| `faust_dose` | vol1_ch2_pharmacy#11, vol1_ch2_pharmacy#14 | vol1_ch2_pharmacy_mirror#3 (when_flag), vol1_ch2_pharmacy_mirror#4 (when_flag) |
| `faust_dream_woman_held` | vol1_ch4_dream_states#19, vol1_ch4_dream_states#23 | vol1_ch4_lullaby#5 (when_flag), vol1_ch4_lullaby#6 (when_not_flag) |
| `faust_elem_favored` | vol1_ch2_painting#39, vol1_ch2_painting#41, vol1_ch2_painting#43 | vol1_ch2_painting_b#2 (when_flag), vol1_ch2_painting_b#3 (when_flag), vol1_ch2_painting_b#4 (when_flag) |
| `faust_met_dickens` | vol1_ch4_dream_bar#22 | **never — loose** |
| `handsome_triumvirate` | vol1_ch3_judgement_day#17 | **never — loose** |
| `vol1_ch1_complete` | vol1_end#0 | **never — loose** |
| `vol1_ch2_complete` | vol1_ch2_skatepark#38 | **never — loose** |
| `vol1_ch3_complete` | vol1_ch3_club#22 | **never — loose** |
| `vol1_ch4_complete` | vol1_ch4_waking#17 | **never — loose** |
| `vol1_missing_link_complete` | vol1_link_end#1 | **never — loose** |
| `vol1_shuttle_boarded` | vol1_link_shuttle#14, vol1_link_shuttle#17 | **never — loose** |


## Volume 2 — 20 scenes · 2 choices · 0 checks

Skills earnable across the volume: empathy 2, logic 2, composure 2, signal 1


### Choices

**vol2_bf_hub** #4
> 

- The low brick building. → scene `vol2_bf_building` — trains **logic**
- The picnic shelter. → scene `vol2_bf_picnic` — trains **empathy**
- The wooden box at the trailhead. → scene `vol2_bf_trail` — trains **signal**
- Down to the railing. The falls. → scene `vol2_bf_overlook` — trains **composure**
- The family. From a distance. → scene `vol2_bf_lot` — trains **empathy**
- The dog. It has not moved. → scene `vol2_bf_dog` — trains **signal**
- Get back on the road. → scene `vol2_bf_end`

**vol2_graveyard** #6
> Of course she did. Of course.

- "I'll sell it." → #5 — trains **logic**
- "I hadn't thought about it yet." → #8 — trains **composure**
- "What do you think I should do?" → #11 — trains **empathy**

### Flags

| flag | set at | read at |
|---|---|---|
| `vol2_briar_falls_visited` | vol2_bf_end#8 | **never — loose** |
| `vol2_ch2_complete` | vol2_ch2_disappearance#26 | **never — loose** |
| `vol2_cliffside_circus_seen` | vol2_ch1_history_one#56 | **never — loose** |
| `vol2_delores_ghost` | vol2_ch2_ghost#31 | **never — loose** |
| `vol2_delores_lost` | vol2_ch2_cliffside#27 | **never — loose** |
| `vol2_found_jiggles` | vol2_ch1_history_one#55 | **never — loose** |
| `vol2_funeral_attended` | vol2_graveyard#1 | **never — loose** |
| `vol2_preface_read` | vol2_title#28 | **never — loose** |


## Volume 3 — 2 scenes · 1 choices · 0 checks

Skills earnable across the volume: none


### Choices

**vol3_the_choice** #4
> This is the part where I ask if that's a warning or a recommendation.

- "Is that a warning?" → #5
- "Is that a recommendation?" → #8
- "I'm going to open it." → #11

### Flags

| flag | set at | read at |
|---|---|---|
| `vol3_oracle_trusted` | vol3_end#0 | **never — loose** |


## Volume 4 — 2 scenes · 1 choices · 0 checks

Skills earnable across the volume: none


### Choices

**vol4_standoff** #2
> That's a lot of work for a wall nobody was using.

- "The city was going to buff it anyway." → #3
- "I wanted it to mean something." → #6
- "I can go over it. If that's what you want." → #9

### Flags

| flag | set at | read at |
|---|---|---|
| `vol4_casper_met` | vol4_end#0 | **never — loose** |


## Volume 5 — 27 scenes · 1 choices · 0 checks

Skills earnable across the volume: logic 1, composure 1, signal 1


### Choices

**vol5_ch2_priestess** #45
> Option C — Realize free will is an illusion and embrace the comforting void.

- [A — the slaughterhouse] → #46 — trains **logic**
- [B — the mannequins] → #48 — trains **signal**
- [C — the comforting void] → #50 — trains **composure**

### Flags

| flag | set at | read at |
|---|---|---|
| `aria_active` | vol5_ch3_empress#34 | **never — loose** |
| `aria_named_by_nicola` | vol5_ch3_empress#63 | vol5_ch18_moon#149 (when_flag), vol5_ch18_moon#150 (when_flag), vol5_ch18_moon#151 (when_flag) |
| `elicia_pick` | vol5_ch2_priestess#46, vol5_ch2_priestess#48, vol5_ch2_priestess#50 | vol5_ch19_sun#53 (when_flag), vol5_ch19_sun#54 (when_flag), vol5_ch19_sun#55 (when_flag), vol5_ch19_sun#56 (when_flag), vol5_ch19_sun#57 (when_flag), vol5_ch19_sun#58 (when_flag) |
| `nicola_has_dean_note` | vol5_ch3_empress#108 | vol5_ch20_judgement#217 (when_flag), vol5_ch20_judgement#218 (when_flag) |
| `nicola_pregnant_known` | vol5_ch3_empress#62 | **never — loose** |
| `vol5_ch0_complete` | vol5_ch0_closing#19 | **never — loose** |
| `vol5_ch1_complete` | vol5_ch1_magician#105 | **never — loose** |
| `vol5_ch2_complete` | vol5_ch2_priestess_b#68 | **never — loose** |
| `vol5_ch3_complete` | vol5_ch3_empress#124 | **never — loose** |


## Volume 6 — 118 scenes · 3 choices · 0 checks

Skills earnable across the volume: empathy 2, logic 2, composure 2, signal 1


### Choices

**vol6_ch1_shift_change** #16
> "Sammy. Call his grandma. Tonight. Before you talk to anyone else. Including your dad."

- "Why." → #17 — trains **logic**; sets `shift_change_answer` = asked_why
- [Listen. Wait for the rest of it.] → #17 — trains **empathy**; sets `shift_change_answer` = waited

**vol6_ch1_graciela** #26
> "I know what I am asking. I will not be offended if you refuse. Whatever you decide, I am on your side. You are a good girl. Diego loves you. I love you too, mi

- "I'll do it." → #27 — trains **composure**; sets `graciela_answer` = said_yes
- [She has been sitting here since four forty-nine this morning. Alone with this for eleven  → #27 — trains **empathy**; sets `graciela_answer` = sat_with_it

**vol6_ch2_kwik_stop** #11 · verb coin on **the back cooler**
> The back cooler hums against the far wall. In its glass, the aisle; in the aisle, him — not looking at it.

- look at → #12 — trains **logic**; sets `ch2_cooler_looked`; hidden once `ch2_cooler_looked`
- watch him → #14 — trains **signal**; sets `ch2_cooler_watched`; hidden once `ch2_cooler_watched`
- say nothing → #16 — trains **composure**

### Flags

| flag | set at | read at |
|---|---|---|
| `ben_has_list` | vol6_ch3_pit_stop_office#26 | **never — loose** |
| `ben_has_prints` | vol6_ch2_dumpster#104 | **never — loose** |
| `ch2_cooler_looked` | vol6_ch2_kwik_stop#11 | vol6_ch2_kwik_stop#11 (hide_if) |
| `ch2_cooler_watched` | vol6_ch2_kwik_stop#11 | vol6_ch2_kwik_stop#11 (hide_if) |
| `graciela_answer` | vol6_ch1_graciela#26, vol6_ch1_graciela#26 | vol6_ch7_safehouse#22 (when_flag), vol6_ch7_safehouse#23 (when_flag) |
| `maya_has_envelope` | vol6_ch2_bindery#19 | vol6_ch4_maya_floor#19 (when_flag), vol6_ch4_maya_floor#20 (when_flag) |
| `maya_knows_ft` | vol6_ch2_cosmic#78 | **never — loose** |
| `maya_knows_grandfather` | vol6_ch2_maya_bedroom#55 | **never — loose** |
| `pc_group_of_five` | vol6_ch3_back_room#94 | **never — loose** |
| `sam_dream_charcoal_suit` | vol6_ch3_sam_bedroom#26 | vol6_ch8_courthouse#101 (when_flag), vol6_ch8_courthouse#102 (when_flag), vol6_ch8_courthouse#103 (when_flag) |
| `shift_change_answer` | vol6_ch1_shift_change#16, vol6_ch1_shift_change#16 | vol6_ch6_kwik_stop_open#12 (when_flag), vol6_ch6_kwik_stop_open#13 (when_flag) |
| `vol6_ch1_complete` | vol6_ch1_bedroom#15 | **never — loose** |
| `vol6_ch1_graciela_meeting` | vol6_ch1_graciela#36 | **never — loose** |
| `vol6_ch2_complete` | vol6_ch2_coda#19 | **never — loose** |
| `vol6_ch3_complete` | vol6_ch3_coda#31 | **never — loose** |


## Volume 7 — 100 scenes · 8 choices · 3 checks

Skills earnable across the volume: empathy 5, logic 4, composure 5, rhetoric 2, signal 3


### Choices

**vol7_ch6_tem_call** #15
> She stood on Main with her phone in her hand and the rain not quite raining and the patch on the sanderling about three feet square now.

- Go home. Sit. Eat. → #16 — trains **composure**
- Walk to ChillWave. → #16 — trains **signal**
- [Stay on the corner a moment longer.] → #16 — trains **empathy**

**vol7_ch6_nate** #15
> Either he was at work in Newport or he was upstairs with the door shut. Nate had the run of the house. He had the run of the basement. He had built things in th

- "What kind of things." → #17 — trains **logic**
- [Listen. Let him find the order.] → #17 — trains **empathy**
- [EMPATHY] His thumb. The held breath. He has been carrying this a long time. → next — CHECK empathy ≥ 1 (pass #16 / fail #17)

**vol7_ch6_why_lena** #2
> She sat with her hands in her lap. The chair under her was a folding metal one Cale had probably grabbed out of the closet when his mother visited at Christmas.

- "Why me and not her, Cale." → #3 — trains **rhetoric**
- [Say nothing. Wait for him to continue.] → #4 — trains **empathy**

**vol7_ch8_the_apology** #21
> Tem looked at him.

- Listen. Say nothing. → #23 — trains **empathy**; sets `vol7_ch7_apology_heard`
- "All right." → #22 — trains **composure**
- [EMPATHY] She already knew. She's been waiting for someone to say it. → next — CHECK empathy ≥ 2 (pass #24 / fail #22); sets `vol7_ch7_apology_heard`

**vol7_ch8_goodnight** #22
> She said it to Lena.

- "Yeah. Stay." → #24 — trains **empathy**
- [EMPATHY] You feel the ask in it — not just for a place to sleep. → next — CHECK empathy ≥ 3 (pass #23 / fail #24)

**vol7_ch10_cabin** #98 · verb coin on **Per's box**
> Per set the wooden box on the table, between the bowls, and did not open it. Nobody asked him to. The kettle ticked toward its whistle.

- look at → #99 — trains **logic**; sets `ch10_box_looked`; hidden once `ch10_box_looked`
- ask Per → #101 — trains **rhetoric**; sets `ch10_box_asked`; hidden once `ch10_box_asked`
- leave it → #104 — trains **composure**

**vol7_ch14_painting** #17 · verb coin on **the three bowls**
> The man on Marina's grandfather's bowl had his eyes now slightly above the rim of the bowl he was carved into, looking — by what Lena could read in the pre-dawn

- look at → #18 — trains **logic**; sets `ch14_bowls_looked`; hidden once `ch14_bowls_looked`
- turn a bowl → #21 — trains **signal**; sets `ch14_bowls_turned`; hidden once `ch14_bowls_turned`
- leave them → #24 — trains **composure**

**vol7_ch20_wall** #14 · verb coin on **the four bowls on the crate**
> She took the four bowls out one at a time and arranged them on the crate in the order they had been at the bakery — Roy's at the right end, then Marit's, then t

- look at → #15 — trains **logic**; sets `ch20_bowls_looked`; hidden once `ch20_bowls_looked`
- touch Roy's → #18 — trains **signal**; sets `ch20_bowls_touched`; hidden once `ch20_bowls_touched`
- step back → #21 — trains **composure**

### Checks

| scene | skill | diff | earnable before | pass ≠ fail | verdict |
|---|---|---|---|---|---|
| vol7_ch6_nate #15 | empathy | 1 | 1 | yes | passable |
| vol7_ch8_the_apology #21 | empathy | 2 | 3 | yes | passable |
| vol7_ch8_goodnight #22 | empathy | 3 | 4 | yes | passable |

### Flags

| flag | set at | read at |
|---|---|---|
| `ch10_box_asked` | vol7_ch10_cabin#98 | vol7_ch10_cabin#98 (hide_if) |
| `ch10_box_looked` | vol7_ch10_cabin#98 | vol7_ch10_cabin#98 (hide_if) |
| `ch14_bowls_looked` | vol7_ch14_painting#17 | vol7_ch14_painting#17 (hide_if) |
| `ch14_bowls_turned` | vol7_ch14_painting#17 | vol7_ch14_painting#17 (hide_if) |
| `ch20_bowls_looked` | vol7_ch20_wall#14 | vol7_ch20_wall#14 (hide_if) |
| `ch20_bowls_touched` | vol7_ch20_wall#14 | vol7_ch20_wall#14 (hide_if) |
| `vol7_ch6_complete` | vol7_ch6_get_going#9 | **never — loose** |
| `vol7_ch7_apology_heard` | vol7_ch8_the_apology#21, vol7_ch8_the_apology#21 | vol7_ch8_roy#2 (when_flag), vol7_ch8_roy#3 (when_not_flag) |
| `vol7_ch7_complete` | vol7_ch8_dark#22 | **never — loose** |
| `vol7_ch7_tem_stays` | vol7_ch8_goodnight#29 | **never — loose** |
| `vol7_ch7_vessel_understood` | vol7_ch8_the_vessel#27 | **never — loose** |

