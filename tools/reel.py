#!/usr/bin/env python3
"""Keep hamster reel template.

Turns a 9:16 base clip into a finished IG reel:
  1. (optional) cuts the hamster out frame by frame and puts it on a new background photo
  2. burns in IG-style text (Nunito Black, white with dark outline, or white on a black box),
     with layers that can pop in at set times
  3. keeps the base clip's audio

Usage:
  python3 -I reel.py spec.json

spec.json:
{
  "base": "/path/to/base.mp4",
  "out": "/path/to/keep_reel_xx.mp4",
  "background": "/path/to/photo.jpg",      // optional; omit to keep the original scene
  "bg_focus_x": 0.5,                        // 0-1, where to centre the 9:16 crop of the photo
  "bg_blur": 2.2,                           // depth-of-field blur on the photo
  "bg_zoom": true,                          // slow push-in on the background
  "extend_body": true,                      // extend the torso to the frame bottom (fixes floating hamster)
  "work": "/path/to/workdir",               // masks are cached here; reruns skip the slow cutout
  "layers": [
    {"text": "Me after hiking 4 hours...", "start": 0, "y": 300, "style": "outline", "size": 78},
    {"text": "Good ones: 3 💀", "start": 3.5, "y": null, "style": "box", "size": 86}
  ]
}
"y": null stacks the layer under the previous one. Styles: "outline" | "box".
Keep text between y≈250 and y≈1650 (IG header / caption safe zone).

Setup (once per machine):
  npm install --prefix ~/bgr @imgly/background-removal-node@1.4.5   # cutout model (bundled weights)
  cd ~/fonts && npm pack @fontsource/nunito@5.3.0 && tar xzf fontsource-nunito-5.3.0.tgz
  Noto Color Emoji at /usr/share/fonts/truetype/noto/NotoColorEmoji.ttf, plus ffmpeg, Pillow, numpy.
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.expanduser("~/fonts/package/files/nunito-latin-900-normal.woff2")
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
BGR_DIR = os.path.expanduser("~/bgr")  # where @imgly/background-removal-node is installed
W, H = 1080, 1920

def run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)

# ---------------------------------------------------------------- text overlay
def is_emoji(ch):
    o = ord(ch)
    return o >= 0x1F000 or 0x2600 <= o <= 0x27BF

def tokens(line):
    out = []
    for ch in line:
        if ch == "️":
            continue
        if is_emoji(ch):
            out.append(("e", ch))
        elif out and out[-1][0] == "t":
            out[-1] = ("t", out[-1][1] + ch)
        else:
            out.append(("t", ch))
    return out

_ecache = {}
def emoji_img(ch, size):
    if (ch, size) not in _ecache:
        f = ImageFont.truetype(EMOJI, 109)
        im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
        im = im.crop(im.getbbox())
        s = size / max(im.size)
        _ecache[(ch, size)] = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    return _ecache[(ch, size)]

def line_width(line, font, size):
    return sum(font.getlength(t) if k == "t" else size * 1.05 for k, t in tokens(line))

def wrap(text, font, size, maxw):
    lines = []
    for para in text.split("\n"):
        words = []
        for word in para.split(" "):
            if words and all(is_emoji(c) or c == "️" for c in word):
                words[-1] += " " + word  # never leave an emoji alone on its own line
            else:
                words.append(word)
        cur = ""
        for word in words:
            test = (cur + " " + word).strip()
            if line_width(test, font, size) <= maxw or not cur:
                cur = test
            else:
                lines.append(cur); cur = word
        lines.append(cur)
    return lines

def render_text(text, y_top, style="outline", size=78, maxw=900, align="center", x_left=70):
    """align="left" starts every line at x_left (keeps text clear of IG's right-side buttons)."""
    xs = (lambda w_: x_left) if align == "left" else (lambda w_: (W - w_) / 2)
    font = ImageFont.truetype(FONT, size)
    lines = wrap(text, font, size, maxw)
    lh = int(size * 1.18)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    widths = [line_width(l, font, size) for l in lines]
    block_h = lh * len(lines)
    if style == "box":
        pad_x, pad_y = 34, 26
        bw = max(widths) + pad_x * 2
        x0 = (x_left - pad_x) if align == "left" else (W - bw) / 2
        ImageDraw.Draw(img).rounded_rectangle(
            [x0, y_top - pad_y, x0 + bw, y_top + block_h + pad_y - 10], radius=22, fill=(0, 0, 0, 235))
    else:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        for i, l in enumerate(lines):
            x, y = xs(widths[i]), y_top + i * lh
            for k, t in tokens(l):
                if k == "t":
                    sd.text((x + 3, y + 6), t, font=font, fill=(0, 0, 0, 150),
                            stroke_width=8, stroke_fill=(0, 0, 0, 150))
                    x += font.getlength(t)
                else:
                    x += size * 1.05
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(img)
    for i, l in enumerate(lines):
        x, y = xs(widths[i]), y_top + i * lh
        for k, t in tokens(l):
            if k == "t":
                if style == "box":
                    d.text((x, y), t, font=font, fill="white")
                else:
                    d.text((x, y), t, font=font, fill="white", stroke_width=6, stroke_fill=(40, 30, 30))
                x += font.getlength(t)
            else:
                img.alpha_composite(emoji_img(t, int(size * 0.92)), (int(x + size * 0.06), int(y + size * 0.16)))
                x += size * 1.05
    bottom = y_top + block_h + (16 if style == "box" else 0)
    return img, bottom

# ---------------------------------------------------------------- cutout + composite
def extrude_bottom(a, band=40):
    """The cutout model drops the shadowed body under the shirt, so the hamster
    floats. Extend the widest lower-torso cross-section down to the frame bottom."""
    rows = np.where((a > 128).sum(axis=1) > 40)[0]
    if len(rows) == 0:
        return a
    bottom = rows.max()
    start = max(rows.min(), bottom - band * 4)
    ref = start + int(np.argmax((a[start:bottom] > 128).sum(axis=1)))
    a = a.copy()
    a[ref:] = np.maximum(a[ref:], a[ref][None, :])
    return a

def green_key(img, lo=35, hi=95):
    """Exact green-screen key: alpha from how much greener than red/blue a pixel is,
    plus despill so fur edges don't keep a green fringe."""
    x = np.asarray(img, np.float32)
    r, g, b = x[..., 0], x[..., 1], x[..., 2]
    d = g - np.maximum(r, b)                      # ~170 on the backdrop, <=0 on the hamster
    alpha = 1 - np.clip((d - lo) / (hi - lo), 0, 1)
    x[..., 1] = np.minimum(g, np.maximum(r, b))   # despill: green never exceeds red/blue
    a = Image.fromarray((alpha * 255).astype(np.uint8))
    a = a.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.7))  # trim 1px edge
    return Image.fromarray(np.clip(x, 0, 255).astype(np.uint8)), a

def ground_shadow(a, strength=0.55):
    """Soft oval contact shadow under the feet (where the hamster meets the floor)."""
    m = np.asarray(a) > 128
    rows = np.where(m.sum(axis=1) > 8)[0]
    sh = Image.new("L", (W, H), 0)
    if len(rows) == 0:
        return sh
    bottom = rows.max()
    if bottom >= H - 4:      # body runs off the frame bottom: no visible feet, no ground shadow
        return a.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.35))
    cols = np.where(m[max(0, bottom - 60):bottom + 1].any(axis=0))[0]
    cx, half_w = (cols.min() + cols.max()) / 2, (cols.max() - cols.min()) / 2 * 1.25 + 30
    d = ImageDraw.Draw(sh)
    d.ellipse([cx - half_w, bottom - half_w * 0.13, cx + half_w, bottom + half_w * 0.13], fill=int(255 * strength))
    d.ellipse([cx - half_w * 0.6, bottom - half_w * 0.07, cx + half_w * 0.6, bottom + half_w * 0.07], fill=int(255 * min(1, strength * 1.5)))
    return sh.filter(ImageFilter.GaussianBlur(14))

def contact_shadow(a, strength=0.6, light_dx=0.12):
    """Ground shadow shaped like the characters: the silhouette squashed onto the floor
    (offset by light_dx so the light comes from one side) plus a tight dark contact under the feet."""
    A = np.asarray(a); rows = np.where((A > 128).sum(axis=1) > 8)[0]
    if len(rows) == 0:
        return Image.new("L", (W, H), 0)
    top, bottom = rows.min(), rows.max()
    if bottom >= H - 4:
        return a.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.35))
    sil = a.crop((0, top, W, bottom + 1))
    h = max(20, int((bottom - top) * 0.16))
    squash = sil.resize((W, h), Image.BILINEAR).transpose(Image.FLIP_TOP_BOTTOM)
    sh = Image.new("L", (W, H), 0)
    sh.paste(squash, (int(W * light_dx * 0.3), bottom - int(h * 0.35)))
    sh = sh.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(min(255, v * strength)))
    contact = Image.new("L", (W, H), 0)
    contact.paste(a.crop((0, bottom - 28, W, bottom + 1)), (0, bottom - 22))
    contact = contact.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(min(255, v * min(1, strength * 1.4))))
    return Image.fromarray(np.maximum(np.asarray(sh), np.asarray(contact)))

def match_colour(fg, a, bg, k=0.28):
    """Nudge the subject's colour balance toward the background's, so it sits in the scene's light."""
    A = np.asarray(a) > 128
    if A.sum() < 100:
        return fg
    f = np.asarray(fg).astype(np.float32); b = np.asarray(bg).astype(np.float32)
    ys, xs = np.where(A); y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    region = b[max(0, y0 - 150):min(H, y1 + 150), max(0, x0 - 200):min(W, x1 + 200)].reshape(-1, 3).mean(axis=0)
    subj = f[A].mean(axis=0)
    gain = (region / np.maximum(subj, 1)) ** k
    gain = np.clip(gain / gain.mean(), 0.8, 1.2)          # tint only, keep overall brightness
    bright = np.clip((region.mean() / max(subj.mean(), 1)) ** (k * 0.5), 0.85, 1.1)
    return Image.fromarray(np.clip(f * gain * bright, 0, 255).astype(np.uint8))

def composite(spec, base, work):
    frames = os.path.join(work, "frames"); half = os.path.join(work, "half")
    masks = os.path.join(work, "masks"); comp = os.path.join(work, "comp")
    for d in (frames, half, masks, comp):
        os.makedirs(d, exist_ok=True)
    if not os.listdir(frames):
        run(["ffmpeg", "-v", "error", "-y", "-i", base, os.path.join(frames, "%04d.png")])
    names = sorted(f for f in os.listdir(frames) if f.endswith(".png"))
    green = spec.get("key") == "green"
    n_total = len(names)
    if spec.get("preview_frame"):
        names = [f"{int(spec['preview_frame']):04d}.png"]
    # AI cutout: mask every other frame (halves the slow cutout); in-between frames average their neighbours
    for f in ([] if green else names):
        if int(f[:-4]) % 2 == 1 and not os.path.exists(os.path.join(half, f)):
            os.symlink(os.path.join(frames, f), os.path.join(half, f))
    if not green and len(os.listdir(masks)) < len(os.listdir(half)):
        print("cutting out hamster (≈7 s per frame)…", flush=True)
        # ESM imports resolve next to the script, so run cut.mjs from the install folder
        import shutil
        shutil.copy(os.path.join(HERE, "cut.mjs"), os.path.join(BGR_DIR, "cut.mjs"))
        run(["node", os.path.join(BGR_DIR, "cut.mjs"), half, masks, "medium"], cwd=BGR_DIR)

    def alpha_of(i):
        p = os.path.join(masks, f"{i:04d}.png")
        return np.asarray(Image.open(p).convert("RGBA").getchannel("A"), np.float32) if os.path.exists(p) else None

    def alpha(i):
        a = alpha_of(i)
        if a is None:
            p, n = alpha_of(i - 1), alpha_of(i + 1)
            a = (p + n) / 2 if p is not None and n is not None else (p if p is not None else n)
        return extrude_bottom(a) if spec.get("extend_body", True) else a

    bg = Image.open(spec["background"]).convert("RGB")
    bw, bh = bg.size
    if bw / bh > 9 / 16:
        cw = int(bh * 9 / 16)
        x0 = max(0, min(bw - cw, int(bw * spec.get("bg_focus_x", 0.5)) - cw // 2))
        bg = bg.crop((x0, 0, x0 + cw, bh))
    else:
        ch = int(bw * 16 / 9)
        bg = bg.crop((0, (bh - ch) // 2, bw, (bh - ch) // 2 + ch))
    zoom = spec.get("bg_zoom", True)
    plate_sharp = ImageEnhance.Brightness(bg.resize((int(W * 1.12), int(H * 1.12)), Image.LANCZOS)).enhance(0.92)
    plate = plate_sharp.filter(ImageFilter.GaussianBlur(spec.get("bg_blur", 2.2)))
    n = n_total
    for f in names:
        i = int(f[:-4])
        t = (i - 1) / max(1, n - 1)
        s = 1.12 - 0.06 * t if zoom else 1.06
        pw, ph = int(W * s), int(H * s)
        box = ((pw - W) // 2, (ph - H) // 2, (pw - W) // 2 + W, (ph - H) // 2 + H)
        bgf = plate.resize((pw, ph), Image.BILINEAR).crop(box)
        bgs = plate_sharp.resize((pw, ph), Image.BILINEAR).crop(box)
        if green:
            fg, a = green_key(Image.open(os.path.join(frames, f)).convert("RGB"), spec.get("key_lo", 35), spec.get("key_hi", 95))
        else:
            fg = ImageEnhance.Color(Image.open(os.path.join(frames, f)).convert("RGB")).enhance(0.9)
            a = Image.fromarray(np.clip(alpha(i), 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
        fs, ox = spec.get("fg_scale", 1.0), int(spec.get("fg_offset_x", 0))
        if fs != 1.0 or ox:
            # shrink the hamster around a ground point (e.g. its feet) so there is room for text above
            ay = spec.get("fg_anchor_y", H)
            nw, nh = int(W * fs), int(H * fs)
            px, py = int(W / 2 - W / 2 * fs) + ox, int(ay - ay * fs)  # ox: shift left/right
            fg2, a2 = Image.new("RGB", (W, H)), Image.new("L", (W, H), 0)
            fg2.paste(fg.resize((nw, nh), Image.LANCZOS), (px, py))
            a2.paste(a.resize((nw, nh), Image.LANCZOS), (px, py))
            fg, a = fg2, a2
        if spec.get("ground", True):
            # depth of field: the floor is sharp where the feet touch it and blurs with distance
            rows = np.where((np.asarray(a) > 128).sum(axis=1) > 8)[0]
            if len(rows) and rows.max() < H - 4:
                fy = rows.max()
                yy = np.abs(np.arange(H) - fy).astype(np.float32)
                focus = np.clip(1 - (yy - 120) / 500, 0, 1)      # 1 = sharp within 120px of the feet
                m = Image.fromarray((focus[:, None] * np.ones((1, W)) * 255).astype(np.uint8))
                bgf = Image.composite(bgs, bgf, m)
            fg = match_colour(fg, a, bgf, spec.get("colour_match", 0.28))
        if spec.get("shadow", "ground") == "ground":
            shadow = contact_shadow(a, spec.get("shadow_strength", 0.6), spec.get("light_dx", 0.12))
        else:  # older soft glow around the whole hamster
            shadow = a.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.45))
        out = Image.composite(Image.new("RGB", (W, H), (10, 12, 25)), bgf, shadow)
        Image.composite(fg, out, a).save(os.path.join(comp, f), compress_level=1)
    if spec.get("preview_frame"):
        return os.path.join(comp, names[0])
    fps = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=r_frame_rate", "-of", "csv=p=0", base],
                         capture_output=True, text=True).stdout.strip()
    out = os.path.join(work, "composited.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-framerate", fps, "-i", os.path.join(comp, "%04d.png"),
         "-i", base, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", out])
    return out

# ---------------------------------------------------------------- main
def main(spec_path):
    spec = json.load(open(spec_path))
    base = spec["base"]
    work = spec.get("work") or os.path.splitext(spec["out"])[0] + "_work"
    os.makedirs(work, exist_ok=True)
    if spec.get("background"):
        base = composite(spec, base, work)
        if spec.get("preview_frame"):
            print("preview frame:", base)
            return
    args = ["ffmpeg", "-v", "error", "-y", "-i", base]
    filt, last, bottom = [], "[0:v]", 0
    fps = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=r_frame_rate", "-of", "csv=p=0", base], capture_output=True, text=True).stdout.strip()
    fpsf = eval(fps) if "/" in fps else float(fps or 24)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", base],
                               capture_output=True, text=True).stdout.strip())
    for i, L in enumerate(spec.get("layers", [])):
        style = L.get("style", "outline")
        y = L.get("y")
        if y is None:
            y = bottom + (60 if style == "box" else 30)
        opts = dict(maxw=L.get("maxw", 900), align=L.get("align", "center"), x_left=L.get("x", 70))
        if L.get("type") == "counter":
            # a number that counts up: "{label}" with {n} replaced by the current value
            cdir = os.path.join(work, f"counter_{i}"); os.makedirs(cdir, exist_ok=True)
            a0, a1, s0, s1 = L.get("from", 0), L["to"], L.get("count_start", L.get("start", 0)), L.get("count_end", 8)
            for k in range(int(dur * fpsf) + 2):
                t = k / fpsf
                u = min(1, max(0, (t - s0) / max(1e-6, s1 - s0)))
                v = a0 + (a1 - a0) * (1 - (1 - u) ** 3)  # ease-out
                im, b = render_text(L["text"].replace("{n}", f"{int(round(v)):,}"), y, style, L.get("size", 78), **opts)
                im.save(os.path.join(cdir, f"{k:04d}.png"), compress_level=1)
            bottom = b
            args += ["-framerate", fps, "-i", os.path.join(cdir, "%04d.png")]
        else:
            im, bottom = render_text(L["text"], y, style, L.get("size", 78), **opts)
            png = os.path.join(work, f"text_{i}.png"); im.save(png)
            args += ["-i", png]
        filt.append(f"{last}[{i+1}:v]overlay=0:0:enable='between(t,{L.get('start', 0)},{L.get('end', 999)})'[v{i}]")
        last = f"[v{i}]"
    if filt:
        args += ["-filter_complex", ";".join(filt), "-map", last]
    else:
        args += ["-map", "0:v"]
    audio = ["-an"] if spec.get("mute") else ["-map", "0:a?", "-c:a", "copy"]
    args += audio + ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
             "-pix_fmt", "yuv420p", "-movflags", "+faststart", spec["out"]]
    run(args)
    print("wrote", spec["out"])

if __name__ == "__main__":
    main(sys.argv[1])
