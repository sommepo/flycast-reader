#!/usr/bin/env python3
# SPDX-FileCopyrightText: Reader fork contributors
# SPDX-License-Identifier: GPL-2.0-or-later
"""The CRT picture's files, which every reader fork carries.

    crt.py inc     writes reader/core/crt_shader.inc (the shader's text as a C++ string)
                   from crt_shader.glsl, here. Run after every change to the shader.
    crt.py sync    the same, and then copies the shared files from this fork (where they
                   are changed) to the sibling forks beside it, each to its own place.
    crt.py check   says which sibling's copy differs.

The shared files: crt.h, crt.cpp, crt_shader.glsl, crt_shader.inc, the test, the settings
page for computers (reader_crt_page), the one for Android (CrtSettings.kt) and its bridge to
the native side (crt_jni.h). A copy differs
from this fork's file only in its #include paths (or its package line), which are each
fork's own. The PPSSPP fork also gets the shader as two of its post-processing files.
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parents[2]
FORKS = HERE.parent

# Fork folder -> where each kind of file lives there (None: the fork has no such part), and
# what its C++ files call the three folders (core, desktop logic, windows) in an #include.
SIBLINGS = {
    "flycast-reader-fork": dict(
        core="reader/core", qt="reader/qt", tests="reader/desktop/tests",
        kotlin="shell/android-studio/flycast/src/main/java/com/flycast/emulator/reader/ui",
        include=("reader/core/", "reader/desktop/", "reader/qt/")),
    "ppsspp-reader-fork": dict(
        core="reader/core", qt="reader/qt", tests="reader/desktop/tests",
        kotlin="android/src/org/ppsspp/ppsspp/reader/ui",
        include=("reader/core/", "reader/desktop/", "reader/qt/"),
        # This emulator's post-processing shaders are files of its own kind.
        fsh="assets/shaders"),
    "pcsx2-reader-fork": dict(
        core="reader/core", qt="reader/qt", tests="reader/desktop/tests", kotlin=None,
        include=("reader/core/", "reader/desktop/", "reader/qt/")),
    "armsx2-reader-fork": dict(
        core="ARMSX2/app/src/main/cpp/reader/core", qt=None, tests=None,
        kotlin="ARMSX2/app/src/main/java/com/armsx2/reader/ui",
        include=("reader/core/", "reader/desktop/", "reader/qt/")),
    "eden-reader-fork": dict(
        core="src/core/reader", qt="src/yuzu/reader", tests="src/reader_desktop/tests",
        kotlin="src/android/app/src/main/java/org/yuzu/yuzu_emu/reader/ui",
        include=("core/reader/", "reader_desktop/", "yuzu/reader/"),
        # This emulator's shaders are built with the program: the shader as files of its.
        frag=("src/video_core/host_shaders", "EDEN_FRAG")),
    "azahar reader fork": dict(
        core="src/core/reader", qt="src/citra_qt/reader", tests="src/reader_desktop/tests",
        kotlin="src/android/app/src/main/java/org/citra/citra_emu/reader/ui",
        include=("core/reader/", "reader_desktop/", "citra_qt/reader/")),
}
FILES = {
    "core": ["crt.h", "crt.cpp", "crt_jni.h", "crt_frame.h", "crt_shader.glsl", "crt_shader.inc"],
    "qt": ["reader_crt_page.h", "reader_crt_page.cpp", "reader_crt_frame.h", "reader_crt_frame.cpp"],
    "tests": ["crt_test.cpp"],
    "kotlin": ["CrtSettings.kt", "CrtFrameView.kt"],
}

FSH_HEAD = """// Reader fork: the CRT picture (reader/core/crt.h) as one of this emulator's post-processing
// shaders. Made by the Flycast Reader fork's tools/reader/crt.py from crt_shader.glsl: do
// not edit, change the shader there and run `crt.py sync`.

#ifdef GL_ES
precision highp float;
precision highp int;
#endif

uniform sampler2D sampler0;
varying vec2 v_texcoord0;

uniform vec4 u_crt0;
uniform vec4 u_crt1;
uniform vec4 u_crt2;
uniform vec4 u_crt3;
uniform vec4 u_crt4;
uniform vec4 u_crt5;
uniform vec4 u_crt6;
uniform vec4 u_crt7;

#define CRT_TEX(uv) texture2D(sampler0, uv)
#define CRT_QUALITY %d

"""
FSH_TAIL = """
void main() {
    gl_FragColor = vec4(ReaderCrt(v_texcoord0), 1.0);
}
"""


MADE = """// Reader fork: the CRT picture (core/reader/crt.h). Made by the Flycast Reader fork's
// tools/reader/crt.py from crt_shader.glsl: do not edit, change the shader there and run
// `crt.py sync`.
"""

# The place in the picture from the texture coordinate the presenter's vertices carry: the
# way back through origin, right and down (the picture may be turned in its texture).
PLACE = """    vec2 t = %s - CRT_U(0).xy;
    vec2 r = CRT_U(0).zw;
    vec2 d = CRT_U(1).xy;
    vec2 p = vec2(t.x * d.y - t.y * d.x, r.x * t.y - r.y * t.x) / (r.x * d.y - r.y * d.x);
"""

# Eden Reader, Vulkan: the window adapt pass's fragment shader. Its 128 bytes of push
# constants lie behind the vertex shader's 128.
EDEN_FRAG = MADE + """
#version 460 core

layout (location = 0) in vec2 frag_tex_coord;

layout (location = 0) out vec4 color;

layout (binding = 0) uniform sampler2D color_texture;

layout (push_constant) uniform ReaderCrtConstants {
    layout (offset = 128) vec4 u_crt[8];
};

#define CRT_TEX(uv) texture(color_texture, uv)
#define CRT_U(i) u_crt[i]
#define CRT_QUALITY %d

{body}
void main() {
""" + PLACE % "frag_tex_coord" + """    color = vec4(ReaderCrt(p), 1.0);
}
"""

FRAGS = {"EDEN_FRAG": EDEN_FRAG}


def make_frags(folder: pathlib.Path, template: str) -> dict:
    """The shader as two fragment shader files of a fork's own kind: name -> text."""
    body = (folder / "crt_shader.glsl").read_text(encoding="utf-8")
    return {
        "present_reader_crt.frag": (template % 1).replace("{body}", body),
        "present_reader_crt_mobile.frag": (template % 0).replace("{body}", body),
    }


def make_inc(folder: pathlib.Path) -> None:
    text = (folder / "crt_shader.glsl").read_text(encoding="utf-8")
    out = ["// Made by tools/reader/crt.py from crt_shader.glsl. Do not edit.\n"]
    # In pieces: one compiler takes no string literal longer than 16 KB.
    piece = ""
    for line in text.splitlines(keepends=True):
        if len(piece) + len(line) > 8000:
            out.append('R"crt(' + piece + ')crt"\n')
            piece = ""
        piece += line
    out.append('R"crt(' + piece + ')crt"\n')
    (folder / "crt_shader.inc").write_text("".join(out), encoding="utf-8")


def make_fsh(folder: pathlib.Path) -> dict:
    """The shader as PPSSPP post-processing files: name -> text."""
    body = (folder / "crt_shader.glsl").read_text(encoding="utf-8")
    # Its translator drops every line with the word "uniform " in it, and the oldest GLSL
    # it is written in cannot paste names together.
    body = re.sub(r"CRT_U\((\d)\)", r"u_crt\1", body)
    assert "uniform " not in body, "a line of the shader has the word 'uniform ' in it"
    return {
        "reader_crt.fsh": FSH_HEAD % 1 + body + FSH_TAIL,
        "reader_crt_mobile.fsh": FSH_HEAD % 0 + body + FSH_TAIL,
    }


def package_of(path: pathlib.Path) -> str:
    for other in sorted(path.parent.glob("*.kt")):
        if other.name != path.name:
            match = re.search(r"^package\s+(\S+)", other.read_text(encoding="utf-8"), re.M)
            if match:
                return match.group(1)
    raise SystemExit(f"no Kotlin file beside {path} to take the package from")


def resources_of(path: pathlib.Path) -> str:
    for other in sorted(path.parent.glob("*.kt")):
        if other.name != path.name:
            match = re.search(r"^import (\S+\.R)$", other.read_text(encoding="utf-8"), re.M)
            if match:
                return match.group(1)
    raise SystemExit(f"no Kotlin file beside {path} that imports the app's R")


def wanted_files(name: str) -> dict:
    """What the fork `name` should hold: target path -> text."""
    here = SIBLINGS[HERE.name]
    there = SIBLINGS[name]
    root = FORKS / name
    result = {}
    for kind, files in FILES.items():
        if here.get(kind) is None or there.get(kind) is None:
            continue
        for file in files:
            source = HERE / here[kind] / file
            if not source.exists():
                continue
            target = root / there[kind] / file
            text = source.read_text(encoding="utf-8")
            if kind == "kotlin":
                # The package, and the app's resource class, are each fork's own.
                package = package_of(target)
                text = re.sub(r"^package\s+\S+", "package " + package, text, count=1, flags=re.M)
                text = re.sub(r"^import \S+\.R$", "import " + resources_of(target), text, count=1, flags=re.M)
            elif file.endswith((".h", ".cpp")):
                for mine, theirs in zip(here["include"], there["include"]):
                    text = text.replace('#include "' + mine, '#include "' + theirs)
            result[target] = text
    if there.get("fsh"):
        for file, text in make_fsh(HERE / here["core"]).items():
            result[root / there["fsh"] / file] = text
    if there.get("frag"):
        folder, template = there["frag"]
        for file, text in make_frags(HERE / here["core"], FRAGS[template]).items():
            result[root / folder / file] = text
    return result


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command not in ("inc", "sync", "check"):
        print(__doc__)
        return 2
    if command in ("inc", "sync"):
        make_inc(HERE / SIBLINGS[HERE.name]["core"])
    if command == "inc":
        return 0
    differs = 0
    for name in SIBLINGS:
        if name == HERE.name or not (FORKS / name).is_dir():
            continue
        for target, wanted in wanted_files(name).items():
            have = target.read_text(encoding="utf-8") if target.exists() else None
            if have == wanted:
                continue
            differs += 1
            if command == "check":
                print("differs:", target)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(wanted, encoding="utf-8")
                print("wrote", target)
    return 1 if command == "check" and differs else 0


if __name__ == "__main__":
    sys.exit(main())
