#!/usr/bin/env python3
"""music_encode.py — turn DAW / tape / field WAVs into the files the music catalog names.

The DAW's TEMP TRACKS and INTO GAME write `<src base>.wav` (+ `<base>.stems/*.wav` and
`<base>.stems.json`) because a browser can't encode Vorbis. AudioMgr plays those .wav
siblings fine, but they're big. This encodes them to the catalog's real path:

    python3 -I godot/tools/music_encode.py                # every catalog track that has a .wav but no real file
    python3 -I godot/tools/music_encode.py vol1_title …   # just these ids
    options: --quality 5 (Vorbis -q, mix) --stem-quality 4 --keep-wav --dry-run --force

    .ogg → libvorbis · .mp3 → libmp3lame VBR · stems → .ogg, manifest paths rewritten
Needs ffmpeg on PATH. Never touches music_catalog.json.
"""
import argparse, json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GODOT = os.path.dirname(HERE)


def ffmpeg(src, dst, codec_args):
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', src, *codec_args, dst]
    subprocess.run(cmd, check=True)


def codec_for(path, quality):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.ogg':
        return ['-c:a', 'libvorbis', '-q:a', str(quality)]
    if ext == '.mp3':
        return ['-c:a', 'libmp3lame', '-q:a', '2']
    raise ValueError('no encoder for ' + ext)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('ids', nargs='*')
    ap.add_argument('--quality', type=float, default=5)
    ap.add_argument('--stem-quality', type=float, default=4)
    ap.add_argument('--keep-wav', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--force', action='store_true', help='re-encode even if the real file exists')
    a = ap.parse_args()
    if not shutil.which('ffmpeg'):
        sys.exit('ffmpeg not found on PATH')
    cat = json.load(open(os.path.join(GODOT, 'resources', 'music_catalog.json'), encoding='utf-8'))
    want = set(a.ids)
    n = 0
    for t in cat:
        if want and t['id'] not in want:
            continue
        src = os.path.join(GODOT, t['src'])
        base = os.path.splitext(src)[0]
        wav = base + '.wav'
        if not os.path.exists(wav) or os.path.splitext(src)[1].lower() == '.wav':
            continue
        if os.path.exists(src) and not a.force:
            print(f"· {t['id']}: {t['src']} already exists — skipped (--force to replace)")
            continue
        print(f"· {t['id']}: {os.path.relpath(wav, GODOT)} → {t['src']}")
        if a.dry_run:
            continue
        ffmpeg(wav, src, codec_for(src, a.quality))
        man_path = base + '.stems.json'
        if os.path.exists(man_path):
            man = json.load(open(man_path, encoding='utf-8'))
            for st in man.get('stems', []):
                f = os.path.join(GODOT, st['file'])
                if f.lower().endswith('.wav') and os.path.exists(f):
                    ogg = os.path.splitext(f)[0] + '.ogg'
                    ffmpeg(f, ogg, ['-c:a', 'libvorbis', '-q:a', str(a.stem_quality)])
                    st['file'] = os.path.relpath(ogg, GODOT).replace(os.sep, '/')
                    if not a.keep_wav:
                        os.remove(f)
            man['mix'] = t['src']
            json.dump(man, open(man_path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
            print(f"    stems → .ogg ({len(man.get('stems', []))}), manifest updated")
        cred = wav + '.credits.txt'
        if os.path.exists(cred):
            os.replace(cred, src + '.credits.txt')
        if not a.keep_wav:
            os.remove(wav)
        n += 1
    print(f'encoded {n} track(s)')


if __name__ == '__main__':
    main()
