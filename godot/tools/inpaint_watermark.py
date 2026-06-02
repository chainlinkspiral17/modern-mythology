"""Clean Gemini ✦ marks from arcana PNGs.

For Empress this also: flips Nicola's NAMETAG to her right chest
(the burgundy / sensory side) and ghosts a faint emerald ARIA glow
where the nametag used to be — so the dual-POV split is reinforced
by where the human identity-label vs the data overlay lives.

Coordinates were eyeballed on tight crops in /tmp/<card>_corner.png
and /tmp/<card>_tag.png.

Usage:
    python3 godot/tools/inpaint_watermark.py empress
    python3 godot/tools/inpaint_watermark.py magician
    python3 godot/tools/inpaint_watermark.py all
"""
from __future__ import annotations
import sys
import numpy as np
import cv2
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

GAL = Path("godot/assets/gallery")

# (cx, cy, radius_px) of the Gemini ✦ in each card.
MARKS = {
    "empress":    (1830, 945,  46),
    "magician":   (2645, 1432, 54),
    "hierophant": (2640, 1413, 44),
    "chariot":    (2630, 1428, 50),
    "strength":   (2620, 1413, 75),
    "hermit":     (2640, 1420, 60),
    "fool":       (2655, 1410, 75),
}

# Empress-only: the current "NICOLA" nametag bbox (to be erased)
# and the mirror location on her right chest (to be re-drawn).
NAMETAG_OLD = (995, 478, 1055, 502)   # x0, y0, x1, y1
NAMETAG_NEW = (855, 478, 915, 502)


def inpaint_diamond(img: np.ndarray, cx: int, cy: int, r: int,
                    algorithm: int = cv2.INPAINT_TELEA) -> None:
    """OpenCV inpaint over a diamond mask sized for the Gemini sparkle."""
    pad = r + 6
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    pts = np.array([[cx, cy - pad], [cx + pad, cy],
                    [cx, cy + pad], [cx - pad, cy]], dtype=np.int32)
    cv2.fillPoly(mask, [pts], 255)
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
    res = cv2.inpaint(img, mask, 7, algorithm)
    img[:] = res


def fill_with_bg(img: np.ndarray, cx: int, cy: int, r: int,
                 sample_pts: list, texture_density: float = 0.08,
                 texture_color: tuple = (0, 200, 0)) -> None:
    """Solid-fill the diamond with the average colour of clean sample
    points, then scatter a few dim texture pixels back in so the patch
    blends with surrounding noise. BGR colour tuple.
    """
    pad = r + 2
    # Average colour across the sample points (3x3 mean each)
    cols = []
    for (sx, sy) in sample_pts:
        roi = img[max(0, sy-1):sy+2, max(0, sx-1):sx+2].astype(np.float32)
        cols.append(roi.reshape(-1, 3).mean(axis=0))
    avg = np.mean(cols, axis=0)
    avg = np.clip(avg, 0, 255).astype(np.uint8)
    # Build diamond mask
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    pts = np.array([[cx, cy - pad], [cx + pad, cy],
                    [cx, cy + pad], [cx - pad, cy]], dtype=np.int32)
    cv2.fillPoly(mask, [pts], 255)
    # Apply solid fill where mask is set
    img[mask > 0] = avg
    # Sprinkle texture noise to imitate the surrounding code-stream
    rng = np.random.default_rng(seed=cx + cy)
    ys, xs = np.where(mask > 0)
    n_pixels = len(xs)
    n_noise = int(n_pixels * texture_density)
    if n_noise > 0:
        idx = rng.choice(n_pixels, size=n_noise, replace=False)
        for k in idx:
            x_n, y_n = xs[k], ys[k]
            # Random intensity within a low range
            intensity = rng.integers(50, 180)
            tint = tuple(int(c * intensity / 255) for c in texture_color)
            img[y_n, x_n] = tint
    # Final Gaussian blur on the diamond region to soften the noise
    blur_pad = pad + 6
    by0, by1 = max(0, cy - blur_pad), min(img.shape[0], cy + blur_pad)
    bx0, bx1 = max(0, cx - blur_pad), min(img.shape[1], cx + blur_pad)
    region = img[by0:by1, bx0:bx1]
    blurred = cv2.GaussianBlur(region, (3, 3), 0)
    img[by0:by1, bx0:bx1] = blurred


def patch_clone(img: np.ndarray, cx: int, cy: int, r: int,
                src_dx: int = -260, src_dy: int = 0) -> None:
    """Feathered patch-clone from a clean offset.

    Used to erase the watermark without algorithmic-inpaint smearing.
    src_dx / src_dy let you steer the source patch into known-clean
    texture (e.g. the dark bands between code-stream rows).
    """
    pad = r + 12
    sy0, sy1 = cy - pad, cy + pad
    sx0, sx1 = cx - pad, cx + pad
    src_y0, src_y1 = sy0 + src_dy, sy1 + src_dy
    src_x0, src_x1 = sx0 + src_dx, sx1 + src_dx
    # Clamp source to image bounds, sliding if necessary
    h, w = img.shape[:2]
    if src_x0 < 0:
        src_x1 += -src_x0
        src_x0 = 0
    if src_x1 > w:
        src_x0 -= (src_x1 - w)
        src_x1 = w
    if src_y0 < 0:
        src_y1 += -src_y0
        src_y0 = 0
    if src_y1 > h:
        src_y0 -= (src_y1 - h)
        src_y1 = h
    patch = img[src_y0:src_y1, src_x0:src_x1].copy()
    # Make sure patch matches dest shape exactly (in case of clamp)
    dh, dw = sy1 - sy0, sx1 - sx0
    patch = cv2.resize(patch, (dw, dh), interpolation=cv2.INTER_AREA)
    yy, xx = np.ogrid[:dh, :dw]
    ccy, ccx = dh // 2, dw // 2
    dist = np.sqrt((xx - ccx) ** 2 + (yy - ccy) ** 2)
    # Smaller falloff radius — keep the cloned core sharp
    soft = np.clip(1.0 - (dist - (pad - 10)) / 10.0, 0.0, 1.0)
    soft = soft.astype(np.float32)[..., None]
    dest = img[sy0:sy1, sx0:sx1].astype(np.float32)
    blended = dest * (1.0 - soft) + patch.astype(np.float32) * soft
    img[sy0:sy1, sx0:sx1] = np.clip(blended, 0, 255).astype(np.uint8)


def erase_nametag(img: np.ndarray, bbox: tuple) -> None:
    """Replace the existing nametag rectangle with a sampled vest patch."""
    x0, y0, x1, y1 = bbox
    h = y1 - y0
    # Sample vest texture from just below the tag, where the vest continues.
    sample_y = y1 + 4
    patch = img[sample_y:sample_y + h, x0:x1].copy()
    img[y0:y1, x0:x1] = patch
    # Soft Gaussian on the seam border to hide the cut line
    border = 5
    bx0, by0 = max(0, x0 - border), max(0, y0 - border)
    bx1, by1 = min(img.shape[1], x1 + border), min(img.shape[0], y1 + border)
    region = img[by0:by1, bx0:bx1].astype(np.float32)
    blur = cv2.GaussianBlur(region, (7, 7), 0)
    mask = np.zeros(region.shape[:2], dtype=np.float32)
    lx, ly = x0 - bx0, y0 - by0
    cv2.rectangle(mask, (lx, ly), (lx + (x1 - x0), ly + (y1 - y0)),
                  1.0, border)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)[..., None]
    img[by0:by1, bx0:bx1] = np.clip(
        region * (1 - mask) + blur * mask, 0, 255
    ).astype(np.uint8)


def paint_aria_glow(img: np.ndarray, bbox: tuple) -> None:
    """Soft elliptical emerald glow at the old nametag spot."""
    x0, y0, x1, y1 = bbox
    cx_g, cy_g = (x0 + x1) // 2, (y0 + y1) // 2
    rad_x, rad_y = 60, 28
    pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).convert("RGBA")
    glow = Image.new("RGBA", pil.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    # Concentric ellipses from outside in, each more opaque.
    # Brighter centre + softer falloff so it reads as an Aria ghost
    # rather than just noise.
    for step in range(rad_x, 2, -2):
        t = 1.0 - step / rad_x
        alpha = int(150 * (t ** 1.3))
        ry = max(1, int(step * rad_y / rad_x))
        gd.ellipse(
            (cx_g - step, cy_g - ry, cx_g + step, cy_g + ry),
            fill=(98, 232, 110, alpha)
        )
    pil = Image.alpha_composite(pil, glow)
    img[:] = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)


def paint_nametag(img: np.ndarray, bbox: tuple, text: str = "NICOLA") -> None:
    """Paint a white rectangular nametag with text at the mirror position."""
    x0, y0, x1, y1 = bbox
    pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(pil)
    # Drop shadow then face
    d.rectangle((x0 + 1, y0 + 2, x1 + 1, y1 + 2), fill=(28, 20, 14))
    d.rectangle((x0, y0, x1, y1), fill=(238, 230, 216))
    # Slight inner stroke
    d.rectangle((x0, y0, x1, y1), outline=(60, 45, 30), width=1)
    font = None
    for fp in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
    ):
        try:
            font = ImageFont.truetype(fp, 16)
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default()
    bb = d.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    cx_t, cy_t = (x0 + x1) // 2, (y0 + y1) // 2
    d.text((cx_t - tw // 2, cy_t - th // 2 - 3), text,
           fill=(28, 18, 12), font=font)
    img[:] = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


def save_with_alpha(out_img: np.ndarray, original_rgba: np.ndarray,
                    has_alpha: bool, path: Path) -> None:
    if has_alpha:
        out = cv2.cvtColor(out_img, cv2.COLOR_BGR2BGRA)
        out[..., 3] = original_rgba[..., 3]
    else:
        out = out_img
    cv2.imwrite(str(path), out)


def load_bgr(path: Path):
    rgba = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    has_a = rgba.ndim == 3 and rgba.shape[2] == 4
    bgr = cv2.cvtColor(rgba, cv2.COLOR_BGRA2BGR) if has_a else rgba.copy()
    return bgr, rgba, has_a


def process_empress() -> None:
    src = GAL / "empress.png"
    img, rgba, has_a = load_bgr(src)
    print(f"  · empress: erase watermark, flip nametag, ghost Aria glow")
    cx, cy, r = MARKS["empress"]
    # NS inpaint over a large diamond mask. Result: a slightly-smoother
    # patch than the surrounding code-stream texture, but no Gemini ✦
    # left visible. Tried Telea+patch-clone and solid-fill — both
    # introduced artifacts (text bleed, rectangular fill shape). This
    # leaves a faint "absence" where the mark was, which reads as
    # camera vignetting rather than a removed watermark.
    inpaint_diamond(img, cx, cy, r, algorithm=cv2.INPAINT_NS)
    erase_nametag(img, NAMETAG_OLD)
    paint_aria_glow(img, NAMETAG_OLD)
    paint_nametag(img, NAMETAG_NEW)
    save_with_alpha(img, rgba, has_a, src)
    # QA preview of the chest area
    qa = img[420:560, 740:1100]
    cv2.imwrite("/tmp/empress_chest_after.png", qa)
    qa2 = img[max(0, cy - 90): cy + 90, max(0, cx - 130): cx + 130]
    cv2.imwrite("/tmp/empress_watermark_after.png", qa2)
    print(f"    QA: /tmp/empress_chest_after.png · /tmp/empress_watermark_after.png")


def process_magician() -> None:
    src = GAL / "magician.png"
    img, rgba, has_a = load_bgr(src)
    print(f"  · magician: erase watermark")
    cx, cy, r = MARKS["magician"]
    inpaint_diamond(img, cx, cy, r, algorithm=cv2.INPAINT_NS)
    save_with_alpha(img, rgba, has_a, src)
    qa = img[max(0, cy - 90): cy + 90, max(0, cx - 130): cx + 130]
    cv2.imwrite("/tmp/magician_watermark_after.png", qa)
    print(f"    QA: /tmp/magician_watermark_after.png")


def process_simple(name: str) -> None:
    """Simple watermark-only erase for cards that don't need any extra
    compositing (no nametag flip, no Aria glow, etc.)."""
    src = GAL / f"{name}.png"
    if not src.exists():
        print(f"  ! missing: {src}")
        return
    img, rgba, has_a = load_bgr(src)
    print(f"  · {name}: erase watermark")
    cx, cy, r = MARKS[name]
    inpaint_diamond(img, cx, cy, r, algorithm=cv2.INPAINT_NS)
    save_with_alpha(img, rgba, has_a, src)
    qa = img[max(0, cy - 90): cy + 90, max(0, cx - 130): cx + 130]
    cv2.imwrite(f"/tmp/{name}_watermark_after.png", qa)
    print(f"    QA: /tmp/{name}_watermark_after.png")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    target = sys.argv[1]
    # Two cards have bespoke routines (Empress flips a nametag, Magician
    # had its own historical entry point); everything else flows through
    # process_simple(). MARKS is the source of truth for what's known.
    BESPOKE = {"empress": process_empress, "magician": process_magician}
    valid = set(MARKS.keys()) | {"all"}
    if target not in valid:
        print(f"unknown target: {target}  (valid: {sorted(valid)})")
        sys.exit(1)
    targets = list(MARKS.keys()) if target == "all" else [target]
    for name in targets:
        if name in BESPOKE:
            BESPOKE[name]()
        else:
            process_simple(name)
