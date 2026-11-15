#!/usr/bin/env python3
"""Render a 1080x1920 TikTok video: voice audio + word-synced kinetic captions.

Usage: python3 render_tiktok.py <video_dir>
<video_dir> must contain: voz.mp3, palabras.json (ElevenLabs Scribe words), config.json
config.json: {"hook": "...", "cta_word": "REVISIÓN", "cta_from": 28.1,
              "keywords": ["plata", ...], "handle": "@elagus"}
"""
import json, math, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
BG = (12, 12, 14)
FG = (245, 245, 240)
ACCENT = (255, 214, 0)      # amarillo: palabra activa / claves
RED = (255, 69, 58)
DIM = (120, 120, 125)
FONT_DIR = "/usr/share/fonts/opentype/inter/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


def clean(t):
    return t.strip().strip('"“”').rstrip(".,!?…").replace("...", "")


def chunk_words(words, max_words=3):
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= max_words or re.search(r"[.,!?…]$|\.\.\.$", w["text"].strip('"')):
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    return chunks


def wrap(draw, text, fnt, max_w):
    lines, line = [], ""
    for word in text.split():
        test = (line + " " + word).strip()
        if draw.textlength(test, font=fnt) <= max_w:
            line = test
        else:
            if line: lines.append(line)
            line = word
    if line: lines.append(line)
    return lines


def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def main(vdir):
    vdir = Path(vdir)
    cfg = json.loads((vdir / "config.json").read_text())
    words = [w for w in json.loads((vdir / "palabras.json").read_text())["words"] if w["type"] == "word"]
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", str(vdir / "voz.mp3")]).strip()) + 0.6
    keywords = {k.lower() for k in cfg.get("keywords", [])}
    cta_from = cfg["cta_from"]
    hook_until = cfg.get("hook_until", 3.0)
    chunks = [c for c in chunk_words(words) if c[0]["start"] < cta_from]
    for i, c in enumerate(chunks):
        c_end = chunks[i + 1][0]["start"] if i + 1 < len(chunks) else cta_from
        for w in c: w["_chunk_end"] = c_end

    f_cap = font("InterDisplay-Black.otf", 118)
    f_hook = font("InterDisplay-Black.otf", 124)
    f_head = font("InterDisplay-ExtraBold.otf", 44)
    f_handle = font("Inter-Bold.otf", 40)
    f_cta_s = font("InterDisplay-ExtraBold.otf", 70)
    f_cta = font("InterDisplay-Black.otf", 150)

    out = vdir / "video.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(vdir / "voz.mp3"),
                           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                           "-af", "apad", "-c:a", "aac", "-b:a", "192k", "-t", f"{dur:.3f}", "-movflags", "+faststart", str(out)],
                          stdin=subprocess.PIPE)

    n = int(dur * FPS)
    for fi in range(n):
        t = fi / FPS
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)

        # fondo: barra diagonal sutil en movimiento
        off = (t * 60) % 240
        for x in range(-480, W + 480, 240):
            d.polygon([(x + off, 0), (x + off + 40, 0), (x + off - 300, H), (x + off - 340, H)], fill=(17, 17, 20))

        # barra de progreso
        d.rectangle([0, 0, int(W * t / dur), 10], fill=ACCENT)
        # handle
        d.text((W // 2, H - 520), cfg.get("handle", "@elagus"), font=f_handle, fill=DIM, anchor="mm")

        if t < hook_until:
            # GANCHO: grande en el centro, entra con pop
            s = ease_out(t / 0.25)
            fh = f_hook
            for size in range(124, 60, -4):
                fh = font("InterDisplay-Black.otf", size)
                lines = wrap(d, cfg["hook"], fh, W - 240)
                if max(d.textlength(l, font=fh) for l in lines) <= W - 240:
                    break
            lh = int(size * 1.13)
            y0 = H // 2 - (len(lines) * lh) // 2 + int((1 - s) * 60)
            pad = 30
            box_w = max(d.textlength(l, font=fh) for l in lines)
            d.rounded_rectangle([W // 2 - box_w / 2 - pad, y0 - pad - 10,
                                 W // 2 + box_w / 2 + pad, y0 + len(lines) * lh + pad - 20], 28, fill=RED)
            for i, l in enumerate(lines):
                d.text((W // 2, y0 + i * lh + lh // 2 - 10), l, font=fh, fill=FG, anchor="mm")
        else:
            # cabecera persistente con el gancho (para quien entra a mitad)
            head = wrap(d, cfg["hook"], f_head, W - 160)
            for i, l in enumerate(head):
                d.text((W // 2, 190 + i * 56), l, font=f_head, fill=ACCENT, anchor="mm")

        if t >= cta_from:
            s = ease_out((t - cta_from) / 0.3)
            d.text((W // 2, H // 2 - 170), "COMENTÁ", font=f_cta_s, fill=FG, anchor="mm")
            size = int(150 * (0.7 + 0.3 * s))
            fc = font("InterDisplay-Black.otf", size)
            tw = d.textlength(cfg["cta_word"], font=fc)
            d.rounded_rectangle([W // 2 - tw / 2 - 40, H // 2 - 100, W // 2 + tw / 2 + 40, H // 2 + 100], 30, fill=ACCENT)
            d.text((W // 2, H // 2), cfg["cta_word"], font=fc, fill=BG, anchor="mm")
            d.text((W // 2, H // 2 + 200), "y te digo qué cambiar", font=f_cta_s, fill=FG, anchor="mm")
        elif t >= hook_until - 0.0:
            # subtítulo del bloque actual, palabra activa resaltada
            cur = None
            for c in chunks:
                if c[0]["start"] - 0.05 <= t < c[-1]["_chunk_end"]:
                    cur = c
            if cur:
                texts = [clean(w["text"]).upper() for w in cur]
                full = " ".join(texts)
                lines = wrap(d, full, f_cap, W - 120)
                # mapear palabras a líneas
                idx, layout = 0, []
                for l in lines:
                    k = len(l.split()); layout.append(list(range(idx, idx + k))); idx += k
                lh = 135
                pop = ease_out((t - cur[0]["start"]) / 0.15)
                y0 = H // 2 - (len(lines) * lh) // 2 + int((1 - pop) * 40)
                for li, ids in enumerate(layout):
                    lw = sum(d.textlength(texts[j], font=f_cap) for j in ids) + d.textlength(" ", font=f_cap) * (len(ids) - 1)
                    x = W // 2 - lw / 2
                    y = y0 + li * lh
                    for j in ids:
                        w = cur[j]
                        active = w["start"] - 0.03 <= t
                        is_kw = clean(w["text"]).lower() in keywords
                        col = ACCENT if (is_kw and active) else (FG if active else (70, 70, 75))
                        if is_kw and active:
                            tw = d.textlength(texts[j], font=f_cap)
                            d.rounded_rectangle([x - 14, y - 8, x + tw + 14, y + lh - 14], 18, fill=(60, 50, 0))
                        d.text((x, y), texts[j], font=f_cap, fill=col, stroke_width=4, stroke_fill=BG)
                        x += d.textlength(texts[j] + " ", font=f_cap)

        ff.stdin.write(img.tobytes())
    ff.stdin.close()
    ff.wait()
    print("OK", out, f"{dur:.1f}s")


if __name__ == "__main__":
    main(sys.argv[1])
