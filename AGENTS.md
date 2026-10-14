# Flycast Reader: a guide for contributors and their coding agents

Flycast Reader is a fork of the Flycast Dreamcast emulator that is to show a game's text as
real text: tap or click a word in the game's own picture to look it up, make Anki cards, keep
a backlog and reading statistics, and (in a build of one's own) sync saves between devices.
It is the Dreamcast sibling of
Eden Reader (Switch), Azahar Reader (3DS), PPSSPP Reader (PSP) and the two PS2 readers, and
shares their reading layer. Its main screen is made in the manner of the Dreamcast's own menu.

**It reads a game only when it has a text profile for it**: a Lua script that knows where
that game keeps the text it shows. Seven games have one so far (the list is under "State",
each with a note in `docs/reader/games/`). The work most worth doing here is another game's
profile.

If a file `MAINTAINER.md` exists (the maintainer's own checkout), read it after this one: it
has their machines, devices and requests. It is not needed for contributing.

## State (2026-10-10): the app on three systems, seven games read

**What is there**

- **The text engine in Flycast** (`reader/core`): it hears of a started game, a changed
  disc, each frame and a loaded savestate, reads the console's main, video and sound memory,
  and keeps what the console plays for a card's audio.
- **The Dreamcast-style menu** (`reader/ui/dc_home.cpp`), on by default: see "The
  Dreamcast's look".
- **The desktop app** (Linux and Windows): the siblings' reading logic and windows
  (`reader/desktop`, `reader/qt`) over Flycast's own window: the layer over the game's
  picture, the popup, statistics, supported games, dictionaries, Anki setup, backlog,
  settings.
- **The Android app** (`io.github.sommepo.flycastreader`, "Flycast Reader"): the siblings'
  Kotlin reading layer with its bridge to the engine.
- **Seven games' profiles**, all Japanese versions, each seen on Linux without a display at
  the start of a new game and no further (its note says exactly what):

  | Game | ID | What is read | Note |
  | --- | --- | --- | --- |
  | Shenmue II | HDR-0164 | subtitles (seen on disc 1 of 4) | `shenmue2.md` |
  | What's Shenmue | 6107179 | subtitles (the game's settings must show them) | `whats-shenmue.md` |
  | Segagaga | HDR-0151 | the message window | `segagaga.md` |
  | Rent a Hero No.1 | HDR-0074 | the message window, with who speaks | `rent-a-hero.md` |
  | Sakura Taisen | HDR-0072 | the message window, timed choices (disc 2 not played) | `sakura-taisen.md` |
  | Kita e. White Illumination | T14301M | the message window (a Windows CE game) | `kita-e.md` |
  | Ayanami Ikusei Keikaku | T46303M | the message window | `ayanami-ikusei-keikaku.md` |
- **A controller's back buttons** are the reader's (`reader/qt/reader_pad`, the same file in
  every reader fork): see "The controller's back buttons".
- **Game scripts** installed from the list published with the scripts: see "Game scripts".
- **Save sync** (`reader/save_sync`): a game's own memory unit follows the user to their
  other devices, through the service the other reader apps use. Not in a published build.

**What is not there, or not known**

- **Hooks in a game's code** are not carried out by the emulator's recompiler
  (`DreamcastHost::InvalidateCode` in `reader/core/emulator.cpp` is where that would begin).
  A profile reads memory once a frame (`reader.on_frame`), which is what the siblings prefer
  anyway.
- **The Windows app has never been started**, and **the Android app has been on no
  device**. See "How it was checked".
- **The controller**: the Dreamcast-style menu reads the keys the emulator hands its
  interface (a controller's d-pad, A and B among them), but no controller was tried. The
  reader's cursor steered with a stick, and a statistics button taken from the console's
  own buttons, are not connected to Flycast's controller input on the desktop: nothing
  calls `Reader::Emu::FilterKey` or `FilterStick` (the back buttons do not need them). On Android the activity asks the reading
  layer about every key first, as in the siblings.
- **A real pointer** was not tried: clicks were sent over the development channel, which
  enters at the same function a real one does (`ReaderUi::PointerPress`) but not through SDL.
- **Where the game's picture is** in the window is taken from the emulator's own
  window-boxing (`getWindowboxDimensions`); a rotated picture, the widescreen settings and a
  stretched one were not looked at.
- **A card**: none was made. Whether the piece of sound cut for a line is that line's voice
  is not known.
- **No sound of the menu's own**, and no users' guide.

## Ground rules

- **Nothing goes to upstream Flycast from here.** The reading layer is AI-written. Do not
  open issues, pull requests or patches on `flyinghead/flycast` for it, and do not present
  this app as Flycast. The remote `upstream` cannot be pushed to.
- **No game data, no BIOS, in Git, ever.** Disc images, the console's BIOS and flash,
  anything extracted or derived from them (code, scripts, text, fonts, tables made from a
  game's font), savestates, memory units, screenshots: under `private/`, which Git ignores.
  A bundled profile holds **addresses and decoding logic only**. Tests use made-up text.
- **Nothing of the console maker's**: the menu's look is drawn here from lines and circles.
  No logo, picture, sound or font of the console's is used, and none is to be added.
- **Games are your own**, dumped from your own discs. Nothing here downloads them.
- **Upstream files are touched as little as possible.** The reader lives in `reader/`. Where
  an upstream file must change, the change is small and carries a comment that begins
  `Reader fork`, so that a new upstream release merges cleanly.
- **Bound what you run.** `tools/reader/limit.sh` runs a command under a memory limit (a
  systemd scope) and every script in `tools/reader/` uses it; compile jobs are `READER_JOBS`
  (8). Never run the Windows build under Wine as a test.
- **Save sync is tried against a service of your own** on a loopback port
  (`tools/reader/test-savesync.sh` starts two and removes them), never against one somebody
  uses.
- **Say what was checked and how.** A test with made-up text, the app on Linux without a
  display, a real device or a real Windows computer are different levels of evidence, and a
  note says which.

## Layout

| Path | |
| --- | --- |
| `reader/core/` | The text engine: the Lua profiles' API, text events, the audio history, the input filter. It knows nothing of the emulator; `emulator.cpp` is the one file that ties it to Flycast, and `emulator.h` is all that upstream files include. |
| `reader/lua/` | Lua 5.4, built as C++ (its errors unwind as exceptions). |
| `reader/profiles/` | **The game scripts** (profiles), one `<PRODUCT NUMBER>.lua` per game: built into the apps of one's own, and published as the list the apps install from ("Game scripts"). |
| `reader/desktop/script_index.*`, `.../reader/ScriptStore.kt` | The published list read, a script checked and installed or removed: the same rules in C++ and Kotlin. `reader/qt/reader_games.cpp` and `ui/ReaderGamesActivity.kt` are their screens. |
| `reader/ui/dc_home.*` | The Dreamcast-style menu and the console's colours for the emulator's other screens, drawn with the emulator's own interface library (Dear ImGui): the same code on Windows, Linux and Android. |
| `reader/desktop/` | The desktop app's reading logic, free of the emulator: dictionaries and lookup, cards and AnkiConnect, statistics, the backlog database. Tests in `tests/`. |
| `reader/qt/` | The reader's windows on the desktop. `host.cpp` ties them to Flycast and `install.h` is all the emulator's files see of them. |
| `reader/save_sync/` | Save sync: the Eden Reader fork's engine (`archive`, `remote`, `engine`) and what fits it to the Dreamcast (`host`). Tests in `tests/`. |
| `reader/android/reader_jni.cpp` | The Android app's bridge between the engine and the Kotlin layer. |
| `shell/android-studio/flycast/src/main/java/com/flycast/emulator/reader/` | The Android reading layer (Kotlin); tests in `src/test/`. `ReaderGlue`, `ReaderInput` and `ReaderNative` tie it to this emulator. |
| `reader/icon/` | The app's own icon; `tools/reader/icon.py` makes the set from `master.png`. |
| `reader/ext/` | cpp-httplib, nlohmann's JSON and a SHA-256, for save sync. |
| `tools/reader/` | Build, test and run scripts. `env.sh` has every path. |
| `private/` | Ignored by Git. Your games, test folders, screenshots, notes. |

Upstream files touched, each at a `Reader fork` comment: `CMakeLists.txt` (the reader's
folder; the video-routing library left out of the Windows build made on Linux),
`core/emulator.cpp` and `core/nullDC.cpp` (the engine installed), `core/audio/audiostream.cpp`
(what the console plays), `core/ui/mainui.cpp` (the reader's toolkit's events once a turn; a
frame while a window of the reader's is open; the main thread keeps the program's name), `core/sdl/sdl.cpp` (which window is the
emulator's, the pointer to the reader first, the window's name), `core/ui/gui.cpp` (the menu
in the game list's place; a game's cover and ID; the pause menu's Reader button), `core/ui/settings_general.cpp` (the
console's colours; the two switches), `core/linux-dist/main.cpp` (folders of the app's own),
`core/oslib/oslib.cpp` (where a game's own memory unit is kept), `core/hw/maple/maple_devs.cpp`
(save sync before a memory unit is read and after it is written), `shell/windows/flycast.rc`
(the icon), and in the Android project `build.gradle.kts`, `AndroidManifest.xml`,
`NativeGLActivity.java`, `BaseGLActivity.java` and `res/values/donottranslate.xml`.

Branch `reader`, based on upstream tag `v2.7` (a shallow clone; submodules fetched shallow:
`git submodule update --init --depth 1 --recursive`).

## The Dreamcast's look

On by default, as in the siblings. `reader/ui/dc_home.cpp` draws, on a 640x480 sheet scaled
to the window:

- **Start-up**: a white screen, an orange ball bouncing along and leaving the app's name
  behind it. Any key ends it.
- **The main menu**: four pictures in a row on a pale ground of slowly drifting tiles:
  **Play**, **File**, **Reader**, **Settings**. The chosen one is larger, bobs, and has an
  orange ring; what it is for is said on a band below; the date and the hour are in the
  bottom right corner and what the buttons do in the bottom left, in the controller's
  colours.
- **Play**: the games side by side as covers (a plain case with a disc and the game's name
  where the emulator has no cover), the chosen one in the middle and larger, its name and
  product number below, an orange box with a book on a game whose text can be read.
- **File** (with save sync; a published build has the shared memory units only): Save Sync (a page of its own, the one with something to type in), whether every
  game has a memory unit of its own, how many do, the shared memory units.
- **Reader**: Reading Statistics, Game Scripts, Dictionaries, Anki, Backlog, Reader
  Settings: each opens the reader's own window (desktop) or screen (Android).
- **Settings**: the emulator's settings, the game folders, the console's own menu (needs a
  BIOS), the two switches, a new look for games, Exit.
- Left and right, up and down, Enter or A, Esc, Backspace or B; the mouse or a finger (a
  click chooses, a second one enters; the right button goes back).
- **In a game**, the emulator's pause menu has a **Reader** button: what the reader offers
  for the running game. (Not pressed anywhere yet.)
- **The emulator's other screens have the menu's colours**, and so have the reader's own
  windows. **The word popup is plain white with a faint orange spiral in its corner, and the
  pointer over a game an orange spiral on a white disc**: the maintainer's choice of three
  looks. The spiral is drawn from a formula in `reader/qt/reader_overlay.cpp`; it is meant
  to call the console's mark to mind and is not that mark, which is its maker's. *Settings, General*
  has both switches: *Dreamcast menu as the main screen* and *Dreamcast colours in every
  screen*.

## Build and test

```sh
tools/reader/build-desktop.sh         # the desktop app for Linux: build-desktop/flycast
tools/reader/test-desktop.sh          # tests of the desktop reading logic (88)
tools/reader/test-savesync.sh         # tests of save sync, against services it starts itself (31)
tools/reader/desktop.sh &             # run the app without a display; dc.py talks to it
tools/reader/desktop-stop.sh
tools/reader/build-windows.sh         # the desktop app for Windows, cross-compiled with MinGW
tools/reader/package-windows.sh       # build-windows/package/FlycastReader-windows.zip
tools/reader/build-android.sh         # shell/android-studio/flycast/build/outputs/apk/debug/flycast-debug.apk
tools/reader/test-android.sh          # tests of the Android reading layer, off the device
```

They run on Linux (x86-64). `tools/reader/env.sh` names every path the scripts use, each a
variable that can be set; a file `private/env.sh` is read first, for a machine's own
settings. What is needed: a GCC 13 or newer with cmake and ninja; Qt 6.9 for Linux and, for
the Windows build, MinGW and Qt for MinGW; Mesa's and X11's development files
(`READER_MESA_PREFIX`); libcurl, libzip, ALSA, udev and evdev development files
(`READER_DEPS_PREFIX`, a conda-forge environment: `libcurl libzip alsa-lib libudev libevdev`);
for the APK a JDK 17 or newer and the Android SDK.

### The app without a display

`tools/reader/desktop.sh` runs the Linux build on a Weston compositor that draws to nothing,
with Xwayland, the picture drawn by Mesa in software. Its home is `private/desktop` (settings
in `config/flycast-reader`, everything else in `data/flycast-reader`, games in `games`): it
never touches a real setup. `tools/reader/dc.py` sends it commands over a socket that exists
only then (`reader/qt/reader_control.cpp` has them all):

```sh
python3 tools/reader/dc.py --socket private/desktop/sock status
python3 tools/reader/dc.py --socket private/desktop/sock "home-key Right" "home-key Enter"
python3 tools/reader/dc.py --socket private/desktop/sock "grab-window $PWD/private/desktop/shots/a.png"
python3 tools/reader/dc.py --socket private/desktop/sock "click 115 396" "grab $PWD/private/desktop/shots/b.png"
```

`home-key` (Left Right Up Down Enter Escape) and `home-click X Y` drive the emulator's own
interface; `grab-window` writes a picture of the emulator's window (OpenGL only), `grab` one
of the game's picture with the reader's layer and popup over it; `click`, `press`, `release`
and `move` are the pointer in the game's picture; `dump PATH` writes the console's main
memory, `lua CODE` runs a piece of Lua in the profile's state, `state save|load N` uses one
of the emulator's ten savestates; `pad BIT [MS]` presses a button of the
console's first controller (2 A, 1 B, 10 X, 9 Y, 3 Start, 4 up, 5 down, 6 left, 7 right)
and `analog X Y [MS]` holds its stick (each way from -100 to 100; a game with a pointer of
its own wants it);
`action reader_statistics` and its kind open the reader's windows, `dialog`, `dialog-grab`
and `dialog-close` look at them. A game starts without a BIOS (the emulator's own stand-in
for it), which is enough for most games.

### On X11, the reader's windows and the window manager

The layer over the game, the popup and the audio question hang on a window that is not Qt's,
and are kept out of the window manager's hands by default (`READER_OVERLAY_UNMANAGED=0` in
the environment for the other way). They then lie above every window on the screen, so they
go while the emulator's window is not the one in use. The see-through layer needs a
compositing manager: on a bare X11 window manager without one it is a black rectangle.

## The controller's back buttons

`reader/qt/reader_pad` reads the buttons no game uses, beside the emulator and without its
knowing: on Linux any controller the system offers that has the "extra" buttons
(`BTN_TRIGGER_HAPPY1` to `5`: what the Steam Controller bridge on a Batocera box makes of
the four grips and the "..." button); on Windows the Steam Controller's (2026) own reports,
read from the device beside whoever else reads it, nothing written. Out of the box:

| Button | | Key |
| --- | --- | --- |
| Grip 1 | **Pause the game** with its picture up, every word still to be looked up; again to go on. For text that does not wait (a cutscene's subtitles). Nothing is said on screen. | Ctrl+G |
| Grip 2 | Pause the statistics | Ctrl+T |
| Grip 3 | A card of the sentence | Ctrl+D |
| Grip 4 | The backlog | Ctrl+H |
| "..." | The reader's menu | |

*Reader settings, Back buttons* has a row for each (also: statistics, close the popup,
nothing). They act while a game is in front, not in the emulator's menus and not under one
of the reader's windows. The development channel's `back-button N` presses one.


## The Steam Controller without Steam (Windows)

To Windows the Steam Controller (2026) is no gamepad by itself: left alone it plays keyboard
and mouse. While Steam is not running, `reader/qt/reader_steam` reads the controller's own reports,
switches that emulation off, and offers a gamepad the emulator finds like any other (made
inside the program through SDL's virtual joystick: no driver), the right pad as the mouse
pointer (a trackball; pressed, a click), the left pad as the wheel (pressed, the right
button). `reader/desktop/steam_bridge` has what the reports mean and is the Batocera box's bridge
(`sc_bridge.py`) in C++. The grips stay the reader's (above). With Steam running nothing is
touched. The development channel's `steam-report HEX` plays a report on any system.

Checked (2026-10-10): tests of the reports' meaning with made-up reports; on Linux without a
display made-up reports made the gamepad and drove the Dreamcast-style menu. **Never run**: everything
that is Windows only (finding and reading the controller, switching its emulation off, the
mouse). On Linux this emulator took the new gamepad by itself and the menu answered its
d-pad and A.

## The CRT picture

*Reader settings, CRT picture* shows the game as a cathode-ray tube would: scan lines, a
phosphor pattern, bulging glass, glow, a warm white, each with a slider, and six ready-made
looks. **On from the first start here** (a strong picture; the switch turns it off). It is one shader and one table of sliders that every reader
fork carries (`reader/core/crt.*`, `crt_shader.glsl`); both settings pages, on a computer and
on Android, are built from the table. **`docs/reader/crt.md` has all of it**: what each
slider does, how a slider is added, where it is tied to this emulator, and what was checked
how. The shared files are changed **here** and copied to the sibling forks with `tools/reader/crt.py sync`. Upstream files touched for it: `core/rend/gles/quad.*` and `gldraw.cpp`, `core/rend/vulkan/quad.*` and `vulkan_context.*`, `core/rend/dx11/dx11_quad.h`, `dx11_renderer.cpp` and `dx11_shaders.h`.

## Adding a game

A profile is a Lua script that, each frame, reads the text the game is showing out of the
game's memory and reports it (`reader.emit`), with furigana and, where it can be had, the
place of every character on screen (`reader.layout`, in the units of the 640x480 picture),
so that a click finds its word. The API is the siblings' (`reader/core/lua_api.cpp`;
`docs/reader/profiles.md` in the Eden Reader fork describes it), with `text.eucjp` beside
`text.sjis`: Shenmue II's text is EUC-JP. `reader/profiles/HDR-0164.lua` is the shortest
example (`HDR-0072.lua` has a message window and choices, `T46303M.lua` an object that has
to be looked for on the heap), and `docs/reader/games/shenmue2.md` how its text was found: run the game without a display
to a line, `dump` the memory, look for the line's bytes in each encoding, and see what else
changes with it.

What is particular to the Dreamcast:

- **A game's ID is its disc's product number** as the disc's own header gives it
  (`HDR-0164`, `T-1214M`): the profile's file is `reader/profiles/<ID>.lua`, and one of the
  user's own goes in `reader/profiles/` of the app's data folder.
- **`reader.build_id`** is a checksum of the disc's header (product number, version, date,
  which disc of how many, boot file), as eight hexadecimal digits: a game on several discs
  has one per disc and one product number or several, and a profile says which it is for.
- **Memory**: the console's main memory is 16 MB, which a program sees at `0x8C000000` (its
  code is loaded at `0x8C010000`); the same memory answers at `0x0C000000` and the other
  mirrors. Video memory is at `0xA5000000`, sound memory at `0x00800000`. The SH-4 is
  little-endian. A game that runs Windows CE moves its memory around (it uses the MMU):
  the program's own addresses are fixed, their places in the console's memory are not, and
  nothing in the engine translates them. A profile can: `reader/profiles/T14301M.lua`
  follows the system's page tables itself (`docs/reader/games/kita-e.md` says how they
  were found; the table's place and the game's entry in it are that game's).
- **The profile begins with the lines the apps read**: `-- reader: title`, `-- reader:
  reads`, `-- reader: version`, `-- reader: no hooks`, and `-- reader: audio never` for a
  game without voices.
- What a good profile does: **each line once**, when it is on screen; **nothing while it is
  not readable**; furigana as the game gives them; choices as a choice; **where each
  character is**, checked over a picture; **only what was asked for**.

Notes on a game go in `docs/reader/games/<game>.md`: what is read, what is not and why, how
the game keeps its text, how it was checked at which level.

## Game scripts

The scripts the apps read games with can come from **the published list**:
`reader/profiles/index.json` in the public repository, made with the scripts by
`tools/reader/scripts-index.py` when the public repository is (a maintainer's step; the list is
not kept in Git here). *Game Scripts* (the menu's Reader page; on a computer also *Reader → Game
scripts…*, on Android also in Reader settings) fetches it, shows each game of the list or of
the app as *Not installed*, *Installed*, *Update available*, *Your own script* or *Needs a
newer app* (`-- reader: api N` above what the app has), and installs, updates and removes
scripts in the user's `reader/profiles` folder (which wins over a bundled script); every file
is checked against the list's size and SHA-256 before it is written, and `.installed.json`
there records what came from the list. *Install from a file* takes `<ID>.lua` and
`<ID>.<name>` files of one's own. `reader/desktop/script_index.*` and `ScriptStore.kt` are the
same rules as in the other reader forks: a change to the list's format goes to both, and to
`scripts-index.py`.

**A published build** comes with no scripts and without save sync:

```sh
READER_WINDOWS_BUILD=$PWD/build-windows-public \
  READER_WINDOWS_CMAKE_ARGS="-DREADER_BUNDLE_PROFILES=OFF -DREADER_SAVE_SYNC=OFF" \
  tools/reader/build-windows.sh
READER_WINDOWS_BUILD=$PWD/build-windows-public tools/reader/package-windows.sh
tools/reader/build-android.sh :flycast:assembleDebug -PreaderBundleScripts=false -PreaderSaveSync=false
```

**Checked**: tests of both with made-up scripts (`[scripts]`; `ScriptStoreTest`), and the
Android screen with a stand-in list, off the device.

## Save sync

A build made with `-DREADER_SAVE_SYNC=OFF` (CMake) or `-PreaderSaveSync=false` (Gradle) has
none of this: no page, nothing started, a game's memory unit where upstream Flycast keeps it,
no statistics sent anywhere. The published builds are made so.

A game's own memory unit (the first controller's first slot, with *A memory unit of its own
for every game* on, which is the emulator's default) is kept in `saves/<product number>/` of
the app's data folder, and that folder is what goes to the service. The newest save is
fetched before the game reads its memory unit and sent a moment after each write. The
service is the Eden Reader fork's (`tools/reader/savesync/server.py` there); a Dreamcast game
is named to it by `DC` and its product number counted out in 56 bits (`SaveSync::Host::
TitleOf`). *File, Save Sync* in the menu takes the service's address and code and settles
two devices' different saves. The other memory units are not sent, and a product number
with anything but capitals, digits and hyphens in it names no folder and is not synced.

## How it was checked

- **Logic**: 88 tests of the desktop reading logic, 31 of save sync, 193 of the Android
  reading layer, all with made-up text and saves.
- **The app on Linux without a display** (2026-10-10): the start-up screen, the main menu,
  Play (with five empty stand-in files, and with one real game), File, Save Sync, Reader,
  Settings and the emulator's settings in the console's colours, looked at in pictures and
  moved through with keys sent over the development channel. Statistics and Dictionaries
  opened from the Reader page; the emulator's window drawn behind an open one.
- **Shenmue II on Linux, drawn in software** (disc 1, a new game): the opening's three
  subtitles and a street musician's line reported as they came up; the game paused on that
  line with back button 1 (sent over the development channel), its first word clicked, the
  popup open with the word's entries. `docs/reader/games/shenmue2.md` has what was not seen.
- **The other six games**, the same way (2026-10-10): each from a new game, the first
  scenes only, the reported text read against pictures and the cells drawn over them.
  Their notes say what was seen and what was not; none was played further, none on a
  device, and none with a save loaded.
- **The back buttons**, presses sent over the development channel: pause and go on (the
  frame count stood still meanwhile), the statistics' mark, the backlog. **No real
  controller**: the Linux reading of one and all of the Windows part have not run.
- **Another game on Linux, drawn in software**: one game started from Play, without a BIOS. With
  a probe profile that reports a made-up Japanese line: the profile loaded, read the disc's
  header text out of the console's memory, the session line counted the line, and a click
  on its first word (sent over the development channel) opened the popup with the word's
  entries, the word marked.
- **Save sync in the app**, against a throwaway service on a loopback port: a marked memory
  unit was sent when the app started as one "device"; started again as another, with no
  memory unit and no notes of its own, the game's start fetched it before the game read it
  (the file was the first one's, byte for byte). **Not seen**: the send after a game saves
  (no game was played to a save), and two devices' different saves settled in the menu.
- **On a PC running Batocera** (X11, Openbox, a 4K TV), in screenshots taken on it: the
  menu full screen, and a game to its first logo. No controller, no pointer.
- **The Windows package**: it links, and every function a file of it takes from another is
  there. Never started.
- **The Android app**: the APK builds for arm64 and holds the bridge and the layer. On no
  device.

## Writing here

Guides and notes are written for the reader who was not there: whole sentences, what
something is before how it was found, and no claim of "works" without saying where it was
seen working. Commit messages say what changed and how it was checked.

## The second display's trackpad (2026-10-13)

On a device with two displays (an AYN Thor) the display the game is not on is the cursor's
trackpad **for as long as a game with a text profile runs, without a button**
(`HoverCursor.always`): drawn in the console's look (`ConsoleLook.ground` under a veil, the
console's pointer under the finger), the word *Trackpad* for a few seconds. The cursor is
moved by the finger alone there and shows on the game while it is used and four seconds
after. **Nothing of the controller is taken**: the cursor's button, the sticks and the d-pad
(which a controller reports beside the sticks, and which the reader swallowed with them
while the trackpad was held up) stay the game's. On one display everything is as it was:
the button holds the cursor, the sticks steer it. The same code in the PPSSPP, ARMSX2,
Flycast and Eden Reader forks; Azahar Reader is left out (the 3DS has a bottom screen of its
own there). Checked with `CursorModeTest` off the device, and a picture of the pad looked at
(`READER_PREVIEW_DIR`, `trackpad.png`). **On a device** (AYN Thor, 2026-10-13, ARMSX2 Reader
with ペルソナ4, touches sent over adb to the lower display): the pad came up by itself with
the first text, a stroke on it moved the cursor on the game, the cursor on 選択 opened its
entry, the console's pointer showed under the finger. **Not tried on a device**: a real
controller's d-pad and sticks while the pad is up (the fault this mends, covered by the test
only), and the other three apps.
