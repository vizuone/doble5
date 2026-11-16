"""Motor de render para TikToks @elagus: escenas animadas + subtítulos + SFX.

Cada video tiene su propio escenas.py con una función build(ctx) que devuelve
una lista de escenas y eventos de sonido. Ver video-01/escenas.py.
"""
import json, math, random, re, subprocess, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
SR = 44100
BG = (12, 12, 14)
FG = (245, 245, 240)
ACCENT = (255, 214, 0)
RED = (255, 69, 58)
GREEN = (48, 209, 88)
BLUE = (10, 132, 255)
CARD = (28, 28, 32)
DIM = (120, 120, 125)
FONT_DIR = "/usr/share/fonts/opentype/inter/"
_fc = {}


def font(size, weight="Black"):
    key = (size, weight)
    if key not in _fc:
        name = {"Black": "InterDisplay-Black.otf", "XBold": "InterDisplay-ExtraBold.otf",
                "Bold": "Inter-Bold.otf", "Semi": "Inter-SemiBold.otf", "Reg": "Inter-Regular.otf"}[weight]
        _fc[key] = ImageFont.truetype(FONT_DIR + name, size)
    return _fc[key]


# ---------- easing ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_in_out(x): x = clamp(x); return 3 * x * x - 2 * x * x * x
def back_out(x, s=1.9):
    x = clamp(x); x -= 1
    return x * x * ((s + 1) * x + s) + 1
def lerp(a, b, t): return a + (b - a) * t


# ---------- palabras ----------
def norm(t): return re.sub(r"[^\wáéíóúñü]", "", t.lower())


class Words:
    def __init__(self, path):
        self.w = [w for w in json.loads(Path(path).read_text())["words"] if w["type"] == "word"]
        for w in self.w:
            w["n"] = norm(w["text"])
        self._cursor = 0

    def at(self, word, after=0.0):
        """start time of first word == `word` starting at/after `after`."""
        target = norm(word)
        for w in self.w:
            if w["start"] >= after - 1e-6 and w["n"] == target:
                return w["start"]
        raise KeyError(f"palabra no encontrada: {word} (después de {after})")

    def end(self, word, after=0.0):
        target = norm(word)
        for w in self.w:
            if w["start"] >= after - 1e-6 and w["n"] == target:
                return w["end"]
        raise KeyError(word)


# ---------- dibujo ----------
def text_c(d, xy, s, f, fill, stroke=0, stroke_fill=BG):
    d.text(xy, s, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=stroke_fill)


def heart(d, cx, cy, r, fill):
    pts = []
    for i in range(60):
        t = 2 * math.pi * i / 60
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * r / 16, cy + y * r / 16))
    d.polygon(pts, fill=fill)


def check(d, cx, cy, r, fill, width=None):
    width = width or max(4, int(r / 3))
    d.line([(cx - r * 0.55, cy), (cx - r * 0.15, cy + r * 0.4), (cx + r * 0.6, cy - r * 0.45)],
           fill=fill, width=width, joint="curve")


def cross(d, cx, cy, r, fill, width=None):
    width = width or max(4, int(r / 3))
    d.line([(cx - r, cy - r), (cx + r, cy + r)], fill=fill, width=width)
    d.line([(cx - r, cy + r), (cx + r, cy - r)], fill=fill, width=width)


def lock(d, cx, cy, s, fill):
    d.rounded_rectangle([cx - s, cy - s * 0.2, cx + s, cy + s * 1.1], int(s * 0.25), fill=fill)
    d.arc([cx - s * 0.65, cy - s * 1.15, cx + s * 0.65, cy + s * 0.15], 180, 360, fill=fill, width=int(s * 0.28))


def person(d, cx, cy, s, fill):
    d.ellipse([cx - s * 0.35, cy - s, cx + s * 0.35, cy - s * 0.3], fill=fill)
    d.rounded_rectangle([cx - s * 0.55, cy - s * 0.2, cx + s * 0.55, cy + s * 0.9], int(s * 0.4), fill=fill)


def eye(d, cx, cy, s, fill, bg=BG):
    d.ellipse([cx - s, cy - s * 0.55, cx + s, cy + s * 0.55], fill=fill)
    d.ellipse([cx - s * 0.38, cy - s * 0.38, cx + s * 0.38, cy + s * 0.38], fill=bg)


def finger(d, x, y, s, pressed=False):
    """cursor de 'dedo' (círculo de toque)."""
    r = s * (0.8 if pressed else 1.0)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255), outline=(0, 0, 0), width=4)


def bill(img, cx, cy, ang, scale=1.0):
    w, h = int(150 * scale), int(78 * scale)
    b = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(b)
    bd.rounded_rectangle([0, 0, w - 1, h - 1], 10, fill=(60, 170, 90), outline=(25, 110, 50), width=4)
    bd.ellipse([w / 2 - h * 0.32, h * 0.18, w / 2 + h * 0.32, h * 0.82], outline=(25, 110, 50), width=4)
    bd.text((w / 2, h / 2), "$", font=font(int(40 * scale)), fill=(25, 110, 50), anchor="mm")
    b = b.rotate(ang, expand=True, resample=Image.BICUBIC)
    img.paste(b, (int(cx - b.width / 2), int(cy - b.height / 2)), b)


def ripple(d, x, y, p, color=(255, 255, 255)):
    if 0 <= p <= 1:
        r = 30 + 120 * ease_out(p)
        a = int(255 * (1 - p))
        d.ellipse([x - r, y - r, x + r, y + r], outline=tuple(color[:3]) + (a,), width=6)


# ---------- SFX sintetizados (sin licencias) ----------
def _env(n, a=0.005, r=0.1):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)
    return e


def sfx(kind):
    rng = np.random.default_rng(7)
    if kind == "click":
        n = int(0.06 * SR); t = np.arange(n) / SR
        return 0.6 * np.sin(2 * np.pi * 1800 * t) * _env(n, 0.001, 0.012)
    if kind == "pop":
        n = int(0.15 * SR); t = np.arange(n) / SR
        f = 500 + 900 * np.exp(-t / 0.03)
        return 0.55 * np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.002, 0.05)
    if kind == "whoosh":
        n = int(0.45 * SR); t = np.arange(n) / SR
        noise = rng.normal(0, 1, n)
        # filtro paso banda que sube: aproximado con diferencias
        env = np.sin(np.pi * t / t[-1]) ** 2
        lp = np.convolve(noise, np.ones(12) / 12, mode="same")
        return 0.35 * lp * env * 3
    if kind == "buzz":
        n = int(0.5 * SR); t = np.arange(n) / SR
        s = np.sign(np.sin(2 * np.pi * 110 * t)) * 0.5 + np.sin(2 * np.pi * 220 * t) * 0.3
        return 0.35 * s * _env(n, 0.005, 0.25)
    if kind == "impact":
        n = int(0.6 * SR); t = np.arange(n) / SR
        f = 40 + 120 * np.exp(-t / 0.05)
        body = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.001, 0.2)
        crack = rng.normal(0, 1, n) * _env(n, 0.0005, 0.02)
        return 0.8 * body + 0.25 * crack
    if kind == "cash":
        n = int(0.7 * SR); t = np.arange(n) / SR
        s = np.zeros(n)
        for f0, d0 in [(2093, 0.0), (2637, 0.08)]:
            m = t >= d0
            tt = t[m] - d0
            s[m] += np.sin(2 * np.pi * f0 * tt) * np.exp(-tt / 0.18) + 0.4 * np.sin(2 * np.pi * f0 * 2.01 * tt) * np.exp(-tt / 0.08)
        return 0.3 * s
    if kind == "ding":
        n = int(0.5 * SR); t = np.arange(n) / SR
        return 0.3 * (np.sin(2 * np.pi * 1320 * t) + 0.5 * np.sin(2 * np.pi * 1980 * t)) * _env(n, 0.002, 0.15)
    if kind == "type":
        n = int(0.035 * SR)
        return 0.35 * rng.normal(0, 1, n) * _env(n, 0.0005, 0.006)
    if kind == "riser":
        n = int(0.8 * SR); t = np.arange(n) / SR
        f = 200 + 900 * (t / t[-1]) ** 2
        return 0.18 * np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / t[-1])
    if kind == "sad":
        n = int(0.9 * SR); t = np.arange(n) / SR
        s = np.zeros(n)
        for i, f0 in enumerate([392, 370, 349, 330]):
            d0 = i * 0.18; m = t >= d0; tt = t[m] - d0
            s[m] += np.sign(np.sin(2 * np.pi * f0 * tt)) * np.exp(-tt / 0.15)
        return 0.12 * s
    raise ValueError(kind)


def mix_audio(voice_mp3, events, dur, out_wav, bed=True):
    raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", str(voice_mp3), "-f", "s16le",
                                   "-ac", "1", "-ar", str(SR), "-"])
    voice = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    n = int(dur * SR)
    mix = np.zeros(n, dtype=np.float32)
    mix[:min(n, len(voice))] += voice[:n]
    fx = np.zeros(n, dtype=np.float32)
    for t, kind, vol in events:
        s = sfx(kind) * vol
        i = int(t * SR)
        if i >= n: continue
        j = min(n, i + len(s))
        fx[i:j] += s[:j - i]
    if bed:
        # pulso grave muy suave (kick cada 0.5 s) para que nunca quede vacío
        tt = np.arange(int(0.25 * SR)) / SR
        kick = (np.sin(2 * np.pi * (45 + 60 * np.exp(-tt / 0.03)) * tt) * np.exp(-tt / 0.09)).astype(np.float32)
        for k in np.arange(0, dur - 1.0, 0.5):
            i = int(k * SR); j = min(n, i + len(kick)); fx[i:j] += 0.10 * kick[:j - i]
    mix += fx * 0.55
    peak = np.max(np.abs(mix))
    if peak > 0.98: mix *= 0.98 / peak
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((mix * 32767).astype(np.int16).tobytes())


# ---------- subtítulos ----------
def chunk_words(words, max_words=3):
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= max_words or re.search(r"[.,!?…]$", w["text"].strip('"')) or w["text"].endswith("..."):
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    for i, c in enumerate(chunks):
        c_end = chunks[i + 1][0]["start"] if i + 1 < len(chunks) else c[-1]["end"] + 0.4
        c_end = min(c_end, c[-1]["end"] + 0.6)
        for w in c: w["_ce"] = c_end
    return chunks


def clean(t):
    return t.strip().strip('"“”').replace("…", "").replace("...", "").rstrip(".,!?").strip('"“”')


def draw_captions(d, chunks, t, y_center, keywords, until=None, size=92):
    if until is not None and t >= until: return
    f = font(size)
    cur = None
    for c in chunks:
        if c[0]["start"] - 0.05 <= t < c[-1]["_ce"]:
            cur = c
    if not cur: return
    texts = [clean(w["text"]).upper() for w in cur]
    sp = d.textlength(" ", font=f)
    widths = [d.textlength(s, font=f) for s in texts]
    lines, line, lw = [], [], 0
    for j, wdt in enumerate(widths):
        if line and lw + sp + wdt > W - 120:
            lines.append(line); line, lw = [], 0
        lw = lw + (sp if line else 0) + wdt; line.append(j)
    if line: lines.append(line)
    lh = int(size * 1.15)
    pop = back_out((t - cur[0]["start"]) / 0.18)
    y0 = y_center - len(lines) * lh / 2 + (1 - pop) * 30
    for li, ids in enumerate(lines):
        tot = sum(widths[j] for j in ids) + sp * (len(ids) - 1)
        x = W / 2 - tot / 2
        y = y0 + li * lh
        for j in ids:
            w = cur[j]
            active = w["start"] - 0.03 <= t
            kw = norm(w["text"]) in keywords
            col = (ACCENT if kw else FG) if active else (90, 90, 95)
            if kw and active:
                d.rounded_rectangle([x - 12, y - 4, x + widths[j] + 12, y + lh - 10], 16, fill=(70, 58, 0))
            d.text((x, y), texts[j], font=f, fill=col, stroke_width=5, stroke_fill=BG)
            x += widths[j] + sp


# ---------- render ----------
def render(vdir, build):
    vdir = Path(vdir)
    words = Words(vdir / "palabras.json")
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", str(vdir / "voz.mp3")]).strip()) + 0.8
    spec = build(words, dur)
    mix_audio(vdir / "voz.mp3", spec["sfx"], dur, vdir / "mezcla.wav")
    chunks = chunk_words(words.w)
    keywords = {norm(k) for k in spec.get("keywords", [])}

    out = vdir / "video.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(vdir / "mezcla.wav"),
                           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-t", f"{dur:.3f}", "-movflags", "+faststart", str(out)],
                          stdin=subprocess.PIPE)
    for fi in range(int(dur * FPS)):
        t = fi / FPS
        img = Image.new("RGB", (W, H), spec.get("bg", lambda t: BG)(t))
        d = ImageDraw.Draw(img, "RGBA")
        spec["background"](img, d, t)
        for sc in spec["scenes"]:
            if sc["start"] <= t < sc["end"]:
                sc["draw"](img, d, t, (t - sc["start"]))
        if spec.get("captions", True):
            draw_captions(d, chunks, t, spec.get("cap_y", 1400), keywords, until=spec.get("cap_until"))
        spec["overlay"](img, d, t)
        # cámara: zoom punch + shake
        z, sx, sy = spec["camera"](t)
        if z != 1.0 or sx or sy:
            nw, nh = int(W * z), int(H * z)
            big = img.resize((nw, nh), Image.BILINEAR)
            left = (nw - W) // 2 - int(sx); top = (nh - H) // 2 - int(sy)
            img = big.crop((left, top, left + W, top + H))
        ff.stdin.write(img.tobytes())
    ff.stdin.close(); ff.wait()
    print("OK", out, f"{dur:.1f}s")


# ---------- cierre reutilizable: caja de comentario que se escribe sola ----------
def make_cta(t_comenta, word, title):
    cx = W // 2
    t_type = t_comenta + 0.2
    sent = t_type + 0.08 * len(word) + 0.25

    def draw(img, d, t, lt):
        e = back_out(lt / 0.4)
        y0 = 560 + (1 - e) * 300
        text_c(d, (cx, 420), title, font(64), FG)
        d.rounded_rectangle([90, y0, W - 90, y0 + 150], 75, fill=(250, 250, 250))
        nch = int(clamp((t - t_type) / 0.08, 0, len(word)))
        typed = word[:nch]
        if typed:
            d.text((150, y0 + 75), typed, font=font(66), fill=(20, 20, 20), anchor="lm")
        else:
            d.text((150, y0 + 75), "Agregá un comentario…", font=font(42, "Semi"), fill=(150, 150, 155), anchor="lm")
        if (t * 2) % 1 < 0.5:
            cxp = 150 + d.textlength(typed, font=font(66)) + 6
            d.line([(cxp, y0 + 40), (cxp, y0 + 110)], fill=BLUE, width=5)
        bc = BLUE if nch == len(word) else (180, 180, 190)
        r = 52 * (0.85 if sent <= t < sent + 0.15 else 1)
        d.ellipse([W - 165 - r, y0 + 75 - r, W - 165 + r, y0 + 75 + r], fill=bc)
        d.polygon([(W - 190, y0 + 50), (W - 135, y0 + 75), (W - 190, y0 + 100)], fill=(255, 255, 255))
        if t >= sent:
            ripple(d, W - 165, y0 + 75, (t - sent) / 0.5, BLUE)
            k = back_out(clamp((t - sent) / 0.3))
            d.rounded_rectangle([90, y0 + 210, W - 90, y0 + 210 + 150 * k], 30, fill=CARD)
            if k > 0.6:
                d.ellipse([120, y0 + 245, 200, y0 + 325], fill=(255, 140, 60))
                d.text((225, y0 + 262), "vos", font=font(32, "Bold"), fill=DIM, anchor="lm")
                d.text((225, y0 + 310), word, font=font(52), fill=FG, anchor="lm")
                heart(d, W - 150, y0 + 285, 30 * back_out(clamp((t - sent - 0.25) / 0.3)), (255, 55, 95))
        by = 1200 + math.sin(t * 9) * 25
        d.polygon([(W - 150, by), (W - 90, by), (W - 90, by + 70), (W - 50, by + 70), (W - 120, by + 150),
                   (W - 190, by + 70), (W - 150, by + 70)], fill=ACCENT)

    sfx_ev = [(t_type + 0.08 * i, "type", 0.8) for i in range(len(word))]
    sfx_ev += [(sent, "pop", 1.0), (sent + 0.5, "ding", 0.8)]
    return draw, sfx_ev
