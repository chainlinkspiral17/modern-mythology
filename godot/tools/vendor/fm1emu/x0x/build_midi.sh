#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-only
# Rebuild x0x_midi.wasm: upstream X0X's browser build (web/emu/build.sh) plus x0x_web_midi.patch (a web_midi
# export, so the page can play X0X's parts over MIDI and clock its sequencer), with clang + wasi-libc instead
# of Emscripten. The result renders sample-for-sample and pixel-for-pixel what the upstream x0x.wasm does.
#
#   build_midi.sh X0X_CHECKOUT WASI_SYSROOT [UPSTREAM_X0X_WASM]
#
#   X0X_CHECKOUT      git clone https://github.com/charlesvestal/fm1-x0x (commit in SOURCE.md); it is copied, not changed
#   WASI_SYSROOT      a wasi-libc sysroot: wasi-sdk's share/wasi-sysroot, or built from
#                     https://github.com/WebAssembly/wasi-libc (cmake -DTARGET_TRIPLE=wasm32-wasip1; make install)
#   UPSTREAM_X0X_WASM the upstream emu/x0x.wasm (default: ./x0x.wasm next to this script): its font tables are
#                     reused (font_from_wasm.py), so Pillow / FreeType / libraqm are not needed
# Needs clang >= 15 with the wasm32 target, wasm-ld, a host cc and python3. Then: python3 -I ../pack.py x0x
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
SRC=$(cd "$1" && pwd)
SYSROOT=$(cd "$2" && pwd)
UP=${3:-$HERE/x0x.wasm}
VERSION=${X0X_VERSION:-1.0.5}
W=$(mktemp -d)
trap 'rm -rf "$W"' EXIT
cp -R "$SRC/." "$W/"
cd "$W"
patch -p1 < "$HERE/x0x_web_midi.patch"
mkdir -p build/gen build/emu
python3 -I "$HERE/font_from_wasm.py" "$UP" build/gen/felucca_font.h
python3 tools/gen_drum_samples.py build/gen/x0x_drum_samples.h >/dev/null
sh tools/gen_builtin_break.sh build/gen >/dev/null
U="firmware/src/dsp/drum909.c firmware/src/dsp/drum808.c firmware/src/dsp/bass303.c firmware/src/dsp/breaks.c
   firmware/src/dsp/fxbus.c firmware/src/dsp/master.c firmware/src/seq/sequencer.c firmware/src/seq/tb3po.c
   firmware/src/seq/pattern.c firmware/src/seq/motion.c firmware/src/app/engine.c"
# shellcheck disable=SC2086
${CLANG:-clang} --target=wasm32-wasip1 --sysroot="$SYSROOT" -O2 -ffp-contract=off -std=gnu99 -w \
    -DX0X_HOST -DX0X_WEB "-DX0X_VERSION=\"$VERSION\"" -Ifirmware/src -Ifirmware/src/dsp -Ibuild/gen \
    -mexec-model=reactor -nodefaultlibs -Wl,--export-dynamic -Wl,--initial-memory=33554432 -Wl,-z,stack-size=1048576 \
    -o build/emu/x0x.wasm web/emu/x0x_web.c $U -lc -lm
cp build/emu/x0x.wasm "$HERE/x0x_midi.wasm"
echo "x0x_midi.wasm: $(wc -c < "$HERE/x0x_midi.wasm" | tr -d ' ') B"
