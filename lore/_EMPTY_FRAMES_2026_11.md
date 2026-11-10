# Empty frames, posters and screens — the work queue (2026-11-10)

The user: *"lots of frames still showing as empty, not sure if that's where art is going or not, seems like it should be."*

Written by `godot/tools/audit/empty_frame_audit.py` (re-run it to refresh): every thin slab a builder
named frame / poster / photo / painting / flyer / calendar / screen … that NO roster art row covers. Each stays a
flat rectangle of colour until a row is written for it (`meshy_roster.json`, kind `art`, with an `apply` row) and
the user generates the picture in Hero Studio.

**449 pictures in 95 sets.** Draft 2 of the list: a few entries are still not pictures (a shirt print, a
register's screen); read each set before writing its rows. Rows are written from the TEXT (what the scene says
hangs there); where the text says nothing the row is marked SPARSE and proposed.

Order of work (by how much the reader sees them): the model chapters' rooms first, then by count.

| set | empty | what they are |
|---|---:|---|
| `small_wood_high` | 28 | Lab_PC_Screen×24, Art_Easel_Canvas×4 |
| `dean_offices` | 26 | Desk_Faust_Sketch×5, Desk_Jacob_Sketch×5, Desk_Wagner_Sketch×5, Shirt_Art×3, Desk_Faust_Pinboard, Desk_Jacob_Pinboard … |
| `cedar_tower` | 24 | Poster_S×12, Poster_W×12 |
| `club_sharp` | 24 | Cabinet_Screen×24 |
| `honolulu_highrise` | 19 | Photo_Parlour_Print×8, Photo_Parlour_Lei×5, Travel_Agency_Desk_Screen×2, Photo_Parlour, Photo_Parlour_Floor, Photo_Parlour_Backdrop … |
| `chau_house` | 17 | Steven_Flyer×8, Mom_Photo, Art_N_W, Art_N_W_Canvas, Art_N_E, Art_N_E_Canvas … |
| `harmony_terrain` | 17 | KwikShop_Ldr_Flyer×6, CosmicComics_Bulletin_Flyer×6, KwikShop_Arc_Screen×3, OT_Tribute_Photo, KwikShop_KwikStop_ATM_Screen |
| `carrie_city` | 16 | Living_Sketch×6, Bedroom_Canvas×3, Easel_Canvas_Paint×2, Bedroom_Canvas_Mark, Bedroom, Easel_Canvas … |
| `nick_house` | 15 | Grandma_Photo×4, Shirt_Hang__nick_print_shop×3, Comic_Page__nick_print_shop×3, Family_Album__nick_print_shop×3, Poster_Hang×2 |
| `faust_apartment` | 13 | Painting_S_Canvas×2, Painting_S×2, Painting_Bed_Canvas, Painting_Bed, Painting_N_Canvas, Painting_N … |
| `roberts_kitchen` | 12 | Gallery×5, Calendar, Foyer_Photo_E, Shelf_Photo, Side_Photo, Hutch_Photo … |
| `lake_house` | 11 | Poster×9, Cot_Canvas, TV_Screen |
| `diner` | 9 | WestExt_Win_FrameSide×2, WestExt_Win_FrameT, WestExt_Win_FrameB, Chalkboard, Gauntlet_ArcanaFrame_Fool, Gauntlet_ArcanaFrame_Magician … |
| `graustark` | 8 | GasStation_Store_Frame_W_T, GasStation_Store_Frame_W_B, GasStation_Store_Frame_W_S, GasStation_Store_Frame_W_N, GasStation_Store_Frame_E_T, GasStation_Store_Frame_E_B … |
| `riverfront` | 8 | GasStation_Store_Frame_W_T, GasStation_Store_Frame_W_B, GasStation_Store_Frame_W_S, GasStation_Store_Frame_W_N, GasStation_Store_Frame_E_T, GasStation_Store_Frame_E_B … |
| `cosmic_comics_interior` | 7 | Poster_W×3, Poster_E×2, BO_Monitor_Screen, BO_Calendar |
| `frog_knows_best` | 7 | PorchScreen_W×2, PorchScreen_S, Calendar, FrogPoster, FrogPoster_Figure_Ball, BackOffice_License |
| `link_house` | 7 | Hall_Photo×4, Shower_Screen_S, Shower_Screen_E, Poster_Bed |
| `bianca_kitchen_morning` | 6 | Nook_Sideboard_Photo×3, Calendar, FR_TV_Screen, Nook_TV_Screen |
| `miller_kitchen` | 6 | Nook_Sideboard_Photo×3, Calendar, FR_TV_Screen, Nook_TV_Screen |
| `montreal_apartment` | 6 | Poster, Poster_Criterion_C_Sheet, Poster_Criterion_C, Poster_Criterion_D_Sheet, Poster_Criterion_D, Shelf_Photo |
| `pharmacy` | 6 | Register_Screen×2, Photo_Kiosk_Screen, RX_PickUp_Screen, Office_Calendar, BP_Kiosk_Screen |
| `elicia_apartment` | 5 | Print×3, Poster_N, Whiteboard |
| `foxhole_stage` | 5 | Poster_W×3, Monitor_Cone×2 |
| `graciela_bedroom` | 5 | Photo×4, Photo_Img |
| `kwik_stop` | 5 | Notice×5 |
| `le_roulant_casino` | 5 | Slot_Screen×5 |
| `sleep_lab` | 5 | Screen_S_Side__four_screens_show×2, Screen_S_Upper__four_screens_show, Screen_S_Figure__four_screens_show, Stalk_Lens__four_screens_beam |
| `small_wood_police` | 5 | Squad_Desk_CRT_Screen×5 |
| `christian_ice_co` | 4 | Calendar, Emile_Frame_Photo, Easel_PhotoFrame, Easel_PhotoInside |
| `cosmic_comics_back_office` | 4 | Monitor_Screen, Calendar, Corkboard, Map |
| `miller_back_porch` | 4 | Knee_W_Screen, Knee_E_Screen, Knee_S_W_Screen, Knee_S_E_Screen |
| `miller_office` | 4 | Commend×2, Sam_School_Photo, Bianca_Calendar_August |
| `vol4_story_rooms` | 4 | DeanHome_Photo×4 |
| `cosmic_comics` | 3 | Poster_W×3 |
| `desert_route` | 3 | Galaga_Screen, Room_TV_Screen, Room_Painting |
| `hospice_room` | 3 | PhotoFrame, Poster, Beach |
| `kai_apartment` | 3 | Poster_W×3 |
| `natalie_apartment` | 3 | Poster_W, Poster_E, Record_Sleeve |
| `parsonage_1945` | 3 | Print_Bed_Wire×2, Print_Bed |
| `roadside_chapel` | 3 | Facade_Lancet_Frame×2, Poster |
| `simon_apartment` | 3 | TV_Screen, Poster, TV_StaticScreen |
| `small_wood_backyard` | 3 | Poster_Rabbits, Poster_Horse, Poster_Everest |
| `vol3_rooms` | 3 | June_PC_Screen, Oregon, Studio_Pinned |
| `writers_desk` | 3 | Poster_W×2, Board |
| `airport_cabin` | 2 | Gate_Jetway, Gate_Screen |
| `asylum_ward_c` | 2 | Chart_Binder, ChartBinder_PagesEdge |
| `bayou_lighthouse` | 2 | Calendar_Backing, Calendar_Photo |
| `ben_bedroom` | 2 | Poster_S, Poster_S_Figure_Ball |
| `board_lords_interior` | 2 | Poster_E×2 |
| `cabin_interior` | 2 | Fern, NorthWall_Frame_Art |
| `darkroom` | 2 | Tray_Dev, Tray_Dev_Print_Img |
| `gallatin_water_tower` | 2 | Fence_Screen_W, Fence_Screen_E |
| `hans_bakery_back_kitchen` | 2 | Calendar, Poster_E |
| `lacombe_service_garage` | 2 | Calendar, Poster_Pinup |
| `lena_apartment` | 2 | Poster_W×2 |
| `mixing_glass` | 2 | Poster_S, LastCall_IceWell |
| `new_orleans_apartment` | 2 | PosterW, Sublet_Calendar |
| `new_orleans_bar` | 2 | Specials_Board, Hand_Truck |
| `pasadena_1945` | 2 | Cl_Eye_Chart, Cl_Calendar |
| `pit_stop_interior` | 2 | Calendar_Kitchen, Poster_E |
| `salty_tome_interior` | 2 | Calendar, Poster |
| `static_drive_in` | 2 | Screen_White, Poster_S |
| `wgur_transmitter_shack` | 2 | Calendar, WGUR_Terminal_Screen |
| `cabin_road` | 1 | FinnTruck_Map_Folded |
| `cafe_olimpico` | 1 | Poster_W |
| `caldwell_kitchen_night` | 1 | Calendar |
| `caldwell_radio_room_night` | 1 | Calendar |
| `centro_break_room` | 1 | Calendar |
| `courthouse_chamber` | 1 | Clerk_Screen_Doc |
| `daigles_roadhouse` | 1 | Poster_S |
| `dean_house_1994` | 1 | CRT_Screen_Off |
| `editing_suite` | 1 | Edit_Whiteboard |
| `ember_ash_office` | 1 | CrewPhoto |
| `finn_apartment` | 1 | Poster_W |
| `foxhole_bar` | 1 | DJ_Laptop_Screen |
| `grandmother_kitchen_morning` | 1 | Calendar |
| `harmony_commercial` | 1 | WatchDetail_Flyer |
| `henderson_kitchen` | 1 | Calendar |
| `hospital_room` | 1 | Nurse_Whiteboard |
| `houston_design_studio` | 1 | Monitor_Screen |
| `houston_office` | 1 | Hall_Art |
| `jesse_bedroom` | 1 | Poster |
| `kowalski_backyard` | 1 | Sketchbook |
| `kowalski_kitchen` | 1 | Calendar |
| `missing_link_interior` | 1 | Calendar |
| `new_orleans_office` | 1 | Lookout_Frame_M |
| `new_orleans_room` | 1 | Poster |
| `pit_stop_office` | 1 | Calendar |
| `ramos_kitchen_morning` | 1 | Calendar |
| `school_newspaper` | 1 | Board |
| `small_wood_farmhouse` | 1 | Kitchen_Calendar |
| `small_wood_ranch` | 1 | Poster_E |
| `vehicle_cab` | 1 | JD_Mural |
| `wagner_home` | 1 | Record_Sleeve |

## Rows written so far

- `caltech_dabney` — Spencer's three small frames (2026-11-09): `caltech_dabney_spencer_photo_two_girls` (the
  picture the text names), `caltech_dabney_spencer_sprite_sheet`, `caltech_dabney_spencer_world_map` (SPARSE, proposed).
- **The Miller house** (`miller_kitchen`, `bianca_kitchen_morning` — one build, two sets; 2026-11-10): seven
  photos, `miller_kitchen_photo_sam_one / _six / _ten / _fourteen` over the family-room TV (the album holds Sam
  "from one through fourteen", ch5) and `miller_kitchen_hall_photo_family / _chief / _sam_school` in the hall.
  No photograph of the father as a young man: ch3 has Sam dream of one "she has never seen".
- **Graciela's house** (`grandmother_kitchen_morning`, `ramos_kitchen_morning`, and the two prints again in
  `graciela_bedroom`): `ramos_kitchen_guadalupe`, `ramos_kitchen_sacred_heart`, `ramos_kitchen_wedding_photo`,
  `ramos_kitchen_hutch_photo`, `ramos_kitchen_hall_photo_communion / _beach / _drumline`, and Diego's eleven
  school pictures `ramos_kitchen_school_photo_00 … _10` (K to tenth). All SPARSE — proposed from the household
  the text gives.
- **The Foxhole** (`foxhole_bar`): three flyers over the nine wall spots — `foxhole_bar_flyer_aug22` (the
  flyer ch14 quotes word for word, posted four times), `foxhole_bar_flyer_open_mic`, `foxhole_bar_flyer_dj_saturdays`
  (SPARSE, in the house style the text describes).

## Found while writing rows

- `graciela_bedroom`: the five photo frames on the dresser have their pictures on the WALL side of the
  frames (`Photo_k_Img` at `fx - 0.012`; the dresser's drawers face +x) — they read as blank frames whatever
  art is assigned. Builder fix first, then rows.
- The Miller kitchen's three sideboard photos are tilted boxes (`make_rot_box`, pitch 0.12): HeroArt lays
  axis-aligned quads, so they need either an upright frame or a tilted-quad option.
- Calendars (19 sets) are left: a month on a wall is a DATE — each needs `_MASTER_TIMELINE.md` read first.

