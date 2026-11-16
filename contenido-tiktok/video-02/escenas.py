"""Video 02 — 10.000 seguidores y 0 ventas. Escenas sincronizadas a la voz (toma v4 B)."""
import math, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from motor import *  # noqa

HOOK = "10.000 SEGUIDORES Y 0 VENTAS"


def p(t, t0, d):
    return clamp((t - t0) / d)


def robot(d, cx, cy, s, look=0.0, col=(150, 160, 175)):
    d.line([(cx, cy - s * 1.0), (cx, cy - s * 1.35)], fill=col, width=int(s * 0.08))
    d.ellipse([cx - s * 0.12, cy - s * 1.5, cx + s * 0.12, cy - s * 1.26], fill=RED)
    d.rounded_rectangle([cx - s, cy - s, cx + s, cy + s * 0.75], int(s * 0.3), fill=col)
    for ex in (-0.42, 0.42):
        d.ellipse([cx + s * (ex - 0.2), cy - s * 0.45, cx + s * (ex + 0.2), cy - s * 0.05], fill=(255, 255, 255))
        d.ellipse([cx + s * (ex - 0.08 + look * 0.1), cy - s * 0.33, cx + s * (ex + 0.08 + look * 0.1), cy - s * 0.17],
                  fill=BG)
    d.rounded_rectangle([cx - s * 0.45, cy + s * 0.25, cx + s * 0.45, cy + s * 0.42], 8, fill=(70, 75, 85))


def build(wd, dur):
    T = {k: wd.at(v, a) for k, (v, a) in {
        "seg": ("seguidores", 0), "cero": ("CERO", 0), "y": ("Y", 4), "culpa": ("culpa", 0),
        "algo": ("algoritmo", 0), "no": ("No", 6.5), "tu": ("Tu", 8), "entre": ("entretiene", 0),
        "pero": ("pero", 0), "que": ("QUÉ", 0), "cuanto": ("CUÁNTO", 0), "ahora": ("AHORA", 0),
        "hace": ("Hacé", 0), "perfil": ("perfil", 0), "nueve": ("nueve", 0), "en": ("En", 18),
        "clara": ("clara", 0), "si": ("Si", 21), "cero2": ("cero", 21), "problema": ("problema", 0),
        "los": ("Los", 24), "seg2": ("seguidores", 24), "cuentas": ("cuentas", 0),
        "clientes": ("clientes", 0), "comenta": ("Comentá", 0), "oferta": ("OFERTA", 29)}.items()}
    cx = W // 2

    def background(img, d, t):
        off = (t * 70) % 240
        for x in range(-480, W + 480, 240):
            d.polygon([(x + off, 0), (x + off + 40, 0), (x + off - 300, H), (x + off - 340, H)], fill=(17, 17, 20))

    # A — perfil con seguidores que suben
    def profile(img, d, t, lt, small=False):
        e = back_out(lt / 0.4)
        y0 = 360 + (1 - e) * 700
        d.rounded_rectangle([80, y0, W - 80, y0 + 470], 40, fill=(250, 250, 250))
        # avatar con aro
        d.ellipse([130, y0 + 50, 310, y0 + 230], fill=(255, 90, 120))
        d.ellipse([142, y0 + 62, 298, y0 + 218], fill=(250, 250, 250))
        d.ellipse([152, y0 + 72, 288, y0 + 208], fill=(255, 140, 60))
        d.text((360, y0 + 100), "tu_negocio", font=font(48, "XBold"), fill=(20, 20, 20), anchor="lm")
        d.text((360, y0 + 160), "Tienda online · Envíos a todo el país", font=font(28, "Semi"), fill=(110, 110, 115), anchor="lm")
        segs = int(lerp(0, 10000, ease_out(p(t, 0.3, T["seg"] + 0.6 - 0.3))))
        stats = [("Publicaciones", "248"), ("Seguidores", f"{segs:,}".replace(",", ".")), ("Seguidos", "512")]
        for i, (lab, val) in enumerate(stats):
            sx = 230 + i * 310
            hl = i == 1 and t >= T["seg"]
            fv = font(70 if hl else 56)
            d.text((sx, y0 + 330), val, font=fv, fill=(255, 55, 95) if hl else (20, 20, 20), anchor="mm")
            d.text((sx, y0 + 400), lab, font=font(30, "Semi"), fill=(110, 110, 115), anchor="mm")
        # confeti sarcástico al llegar a 10.000
        tc = T["seg"] + 0.6
        if t >= tc:
            rnd = random.Random(5)
            for i in range(40):
                q = (t - tc) / 1.4
                if q > 1: break
                ang = rnd.uniform(0, 2 * math.pi); sp = rnd.uniform(300, 700)
                x = 540 + math.cos(ang) * sp * q
                y = y0 + 330 + math.sin(ang) * sp * q + 600 * q * q
                col = rnd.choice([ACCENT, (255, 55, 95), BLUE, GREEN])
                d.rectangle([x - 9, y - 5, x + 9, y + 5], fill=col + (int(255 * (1 - q)),))

    def sales(img, d, t, lt):
        profile(img, d, t, 10)  # perfil quieto arriba
        k = back_out(p(t, T["cero"] - 0.05, 0.25))
        y = 1060
        d.rounded_rectangle([cx - 400 * k, y - 170 * k, cx + 400 * k, y + 170 * k], 36, fill=(60, 14, 14),
                            outline=RED, width=6)
        if k > 0.3:
            text_c(d, (cx, y - 85), "VENTAS DEL MES", font(46, "XBold"), FG)
            text_c(d, (cx, y + 40), "$0", font(int(170 * k)), RED)
        if t >= T["cero"] + 0.6:
            q = p(t, T["cero"] + 0.6, 0.3)
            d.text((W - 150, 860 - 20 * math.sin(t * 12)), "cri cri…", font=font(40, "Semi"),
                   fill=(160, 160, 165, int(255 * q)), anchor="mm")

    # C — la culpa al algoritmo
    def blame(img, d, t, lt):
        e = back_out(lt / 0.35)
        fall = ease_in_out(p(t, T["no"] + 0.95, 0.55))
        rcx, rcy = cx, 760 + (1 - e) * 300 + fall * 1400
        look = math.sin(t * 6) if t < T["no"] else -1
        robot(d, rcx, rcy, 210, look)
        text_c(d, (rcx, rcy + 260), "ALGORITMO", font(70), (150, 160, 175))
        if t >= T["culpa"] - 0.1:
            k = back_out(p(t, T["culpa"] - 0.1, 0.3))
            ex, ey = lerp(150, 330, k), lerp(400, 590, k)
            d.line([(130, 380), (ex - 30, ey - 30)], fill=RED, width=26)
            ang = math.atan2(ey - 380, ex - 130)
            d.polygon([(ex + 30 * math.cos(ang), ey + 30 * math.sin(ang)),
                       (ex - 60 * math.cos(ang) + 50 * math.sin(ang), ey - 60 * math.sin(ang) - 50 * math.cos(ang)),
                       (ex - 60 * math.cos(ang) - 50 * math.sin(ang), ey - 60 * math.sin(ang) + 50 * math.cos(ang))], fill=RED)
            d.text((90, 330), "LA CULPA ES DE…", font=font(46, "XBold"), fill=RED, anchor="lm")
        if t >= T["no"]:
            k = back_out(p(t, T["no"], 0.25))
            cross(d, rcx, rcy - 50, 230 * k, RED, 30)
            bub = p(t, T["no"] + 0.3, 0.25)
            if bub > 0:
                bx, by = W - 260, 430
                d.rounded_rectangle([bx - 190, by - 70, bx + 190, by + 70], 40, fill=(250, 250, 250, int(255 * bub)))
                d.polygon([(bx - 80, by + 60), (bx - 140, by + 140), (bx - 20, by + 65)], fill=(250, 250, 250, int(255 * bub)))
                text_c(d, (bx, by), "¡no fui yo!", font(48, "XBold"), (20, 20, 20, int(255 * bub)))

    # D — feed que entretiene pero no vende
    def feed(img, d, t, lt):
        posts = [("MEME", (120, 90, 220)), ("REEL\nBAILANDO", (255, 120, 60)), ("FOTO\nLINDA", (40, 170, 190))]
        dim = p(t, T["pero"], 0.4)
        for i, (lab, col) in enumerate(posts):
            k = back_out(p(t, T["tu"] - 0.1 + i * 0.12, 0.35))
            x0 = 70 + i * 320
            y0 = 330 + (1 - k) * 600
            c = tuple(int(lerp(v, 60, dim * 0.6)) for v in col)
            d.rounded_rectangle([x0, y0, x0 + 300, y0 + 360], 28, fill=c)
            for li, l in enumerate(lab.split("\n")):
                text_c(d, (x0 + 150, y0 + 150 + li * 56 - (len(lab.split("\n")) - 1) * 28), l, font(50), (255, 255, 255))
            if t >= T["entre"]:
                hb = 1 + 0.25 * math.sin((t - T["entre"]) * 10 + i)
                heart(d, x0 + 60, y0 + 310, 22 * hb, (255, 255, 255))
                d.text((x0 + 95, y0 + 312), f"{[3.2, 5.8, 1.9][i]}K", font=font(34, "XBold"), fill=(255, 255, 255), anchor="lm")
        qs = [(T["que"], "¿QUÉ", " comprar?"), (T["cuanto"], "¿CUÁNTO", " sale?"), (T["ahora"], "¿Por qué", " AHORA?")]
        for i, (st, a, b) in enumerate(qs):
            k = back_out(p(t, st - 0.1, 0.3))
            if k <= 0: continue
            y = 790 + i * 160
            xo = (1 - k) * 700
            d.rounded_rectangle([80 + xo, y, W - 80 + xo, y + 135], 28, fill=CARD, outline=RED, width=4)
            d.ellipse([110 + xo, y + 22, 200 + xo, y + 112], fill=RED)
            text_c(d, (155 + xo, y + 68), "?", font(70), (255, 255, 255))
            fa = font(54)
            d.text((230 + xo, y + 68), a, font=fa, fill=ACCENT, anchor="lm")
            d.text((230 + xo + d.textlength(a, font=fa), y + 68), b, font=font(54, "XBold"), fill=FG, anchor="lm")

    # E — grilla de 9 posteos, escáner de ofertas
    def grid(img, d, t, lt):
        size, gap = 290, 16
        gx0 = cx - (3 * size + 2 * gap) / 2
        gy0 = 380
        rnd = random.Random(9)
        cols = [(120, 90, 220), (255, 120, 60), (40, 170, 190), (230, 70, 120), (90, 180, 90), (200, 160, 60),
                (70, 110, 200), (180, 80, 200), (60, 160, 140)]
        labels = ["meme", "reel", "foto", "frase", "mate", "detrás", "meme", "sorteo", "paisaje"]
        scan_y = gy0 + (3 * size + 2 * gap + 80) * ease_in_out(p(t, T["en"], T["clara"] + 0.5 - T["en"])) - 40
        for i in range(9):
            r, c = divmod(i, 3)
            st = T["perfil"] - 0.2 + i * 0.1
            k = back_out(p(t, st, 0.3))
            if k <= 0: continue
            x = gx0 + c * (size + gap); y = gy0 + r * (size + gap)
            s = size * k
            d.rounded_rectangle([x + (size - s) / 2, y + (size - s) / 2, x + (size + s) / 2, y + (size + s) / 2], 18, fill=cols[i])
            if k > 0.8:
                text_c(d, (x + size / 2, y + size / 2), labels[i], font(44, "XBold"), (255, 255, 255))
            if t >= T["en"] and scan_y > y + size * 0.6:
                d.rectangle([x, y, x + size, y + size], fill=(0, 0, 0, 120))
                cross(d, x + size / 2, y + size / 2, 70, RED, 18)
        if T["nueve"] - 0.1 <= t < T["en"]:
            k = back_out(p(t, T["nueve"] - 0.1, 0.3))
            d.rounded_rectangle([cx - 150 * k, 1290 - 60 * k, cx + 150 * k, 1290 + 60 * k], 30, fill=ACCENT)
            text_c(d, (cx, 1290), "ÚLTIMOS 9", font(int(54 * k) + 1), BG)
        if t >= T["en"] and scan_y < gy0 + 3 * size + 2 * gap + 20:
            d.rectangle([gx0 - 30, scan_y - 4, W - gx0 + 30, scan_y + 4], fill=GREEN)
            d.rectangle([gx0 - 30, scan_y - 40, W - gx0 + 30, scan_y], fill=(48, 209, 88, 50))
        if t >= T["clara"]:
            k = back_out(p(t, T["clara"] + 0.3, 0.3))
            d.rounded_rectangle([cx - 330 * k, 1290 - 60 * k, cx + 330 * k, 1290 + 60 * k], 30, fill=(60, 14, 14), outline=RED, width=4)
            text_c(d, (cx, 1290), "CON OFERTA: 0 / 9", font(int(56 * k) + 1), RED)

    # F — ahí está el problema
    def problem(img, d, t, lt):
        k = back_out(lt / 0.3)
        text_c(d, (cx, 700), "0 / 9", font(int(260 * k) + 1), RED, 8)
        text_c(d, (cx, 870), "posteos que venden", font(56, "XBold"), DIM)
        if t >= T["problema"]:
            q = back_out(p(t, T["problema"], 0.25))
            stamp = Image.new("RGBA", (960, 260), (0, 0, 0, 0))
            sd = ImageDraw.Draw(stamp)
            sd.rounded_rectangle([14, 14, 946, 246], 26, outline=ACCENT, width=14)
            sd.text((480, 132), "AHÍ ESTÁ EL PROBLEMA", font=font(int(76 * (1.4 - 0.4 * q))), fill=ACCENT, anchor="mm")
            stamp = stamp.rotate(-6, expand=True, resample=Image.BICUBIC)
            img.paste(stamp, (cx - stamp.width // 2, 1020), stamp)

    # G — las cuentas no se pagan con seguidores
    def bills(img, d, t, lt):
        e = back_out(lt / 0.35)
        x0, x1, y0 = 150, W - 150, 360 + (1 - e) * 400
        d.rounded_rectangle([x0, y0, x1, y0 + 780], 24, fill=(250, 250, 245))
        d.text((x0 + 50, y0 + 70), "CUENTAS DEL MES", font=font(52), fill=(20, 20, 20), anchor="lm")
        for i, it in enumerate(["Alquiler", "Luz y gas", "Sueldos", "Proveedores", "Impuestos"]):
            yy = y0 + 170 + i * 95
            d.text((x0 + 50, yy), it, font=font(42, "Semi"), fill=(60, 60, 65), anchor="lm")
            d.text((x1 - 50, yy), "$ ••••••", font=font(42, "Bold"), fill=(60, 60, 65), anchor="rm")
            d.line([(x0 + 50, yy + 42), (x1 - 50, yy + 42)], fill=(220, 220, 220), width=2)
        # corazones que rebotan contra la factura
        rnd = random.Random(2)
        for i in range(10):
            st = T["seg2"] + i * 0.12
            q = p(t, st, 0.9)
            if 0 < q < 1:
                sx = rnd.uniform(100, W - 100)
                if q < 0.45:
                    y = lerp(1500, y0 + 400, q / 0.45)
                else:
                    y = y0 + 400 + (q - 0.45) / 0.55 * 900
                    sx += (q - 0.45) * 400 * (1 if i % 2 else -1)
                heart(d, sx, y, 34, (255, 55, 95, int(255 * (1 - q * 0.6))))
        if T["cuentas"] <= t < T["clientes"]:
            k = back_out(p(t, T["cuentas"], 0.25))
            text_c(d, (cx, y0 + 690), "NO SE PAGA CON LIKES", font(int(58 * k) + 1), RED)
        if t >= T["clientes"]:
            k = back_out(p(t, T["clientes"], 0.25))
            stamp = Image.new("RGBA", (700, 240), (0, 0, 0, 0))
            sd = ImageDraw.Draw(stamp)
            sd.rounded_rectangle([12, 12, 688, 228], 24, outline=GREEN, width=14)
            sd.text((350, 122), "PAGADO", font=font(int(130 * (1.5 - 0.5 * k))), fill=GREEN, anchor="mm")
            stamp = stamp.rotate(8, expand=True, resample=Image.BICUBIC)
            img.paste(stamp, (cx - stamp.width // 2, int(y0 + 420)), stamp)
            for i in range(4):
                pk = back_out(p(t, T["clientes"] + 0.1 + i * 0.1, 0.3))
                px = 200 + i * 225
                person(d, px, 1240 + (1 - pk) * 300, 58, GREEN)

    cta_draw, cta_sfx = make_cta(T["comenta"], "OFERTA", "¿QUERÉS ARMAR LA TUYA?")

    S = [
        dict(start=0, end=T["cero"] - 0.1, draw=profile),
        dict(start=T["cero"] - 0.1, end=T["y"] - 0.05, draw=sales),
        dict(start=T["y"] - 0.05, end=T["tu"] - 0.1, draw=blame),
        dict(start=T["tu"] - 0.1, end=T["hace"] - 0.05, draw=feed),
        dict(start=T["hace"] - 0.05, end=T["si"] - 0.05, draw=grid),
        dict(start=T["si"] - 0.05, end=T["los"] - 0.05, draw=problem),
        dict(start=T["los"] - 0.05, end=T["comenta"] - 0.05, draw=bills),
        dict(start=T["comenta"] - 0.05, end=dur + 1, draw=cta_draw),
    ]
    cuts = [s["start"] for s in S[1:]]

    def overlay(img, d, t):
        k = back_out(p(t, 0, 0.3))
        text_c(d, (cx, 175), HOOK, font(int(52 * k) + 1), ACCENT, 5)
        d.rectangle([0, 0, int(W * t / dur), 10], fill=ACCENT)
        d.text((cx, 1610), "@elagus", font=font(38, "Bold"), fill=DIM, anchor="mm")
        for c in cuts:
            if c <= t < c + 0.12:
                d.rectangle([0, 0, W, H], fill=(255, 255, 255, int(110 * (1 - (t - c) / 0.12))))

    punches = [T["seg"], T["no"], T["que"], T["cuanto"], T["ahora"], T["problema"], T["clientes"], T["oferta"]]

    def camera(t):
        z, sx, sy = 1.0, 0.0, 0.0
        for pt in punches:
            if pt <= t < pt + 0.3:
                z = max(z, 1 + 0.06 * (1 - (t - pt) / 0.3) ** 2)
        for st in (T["cero"], T["no"]):
            if st <= t < st + 0.45:
                a = 26 * (1 - (t - st) / 0.45)
                sx, sy = math.sin(t * 95) * a, math.cos(t * 80) * a
                z = max(z, 1.04)
        return z, sx, sy

    ev = [(0.2, "whoosh", 0.9), (0.4, "riser", 0.6), (T["seg"] + 0.6, "ding", 1.0), (T["seg"] + 0.6, "pop", 0.8),
          (T["cero"], "impact", 1.0), (T["cero"] + 0.05, "sad", 0.9), (T["y"], "whoosh", 0.7),
          (T["culpa"], "pop", 0.8), (T["no"], "buzz", 0.9), (T["no"] + 0.3, "pop", 0.7),
          (T["no"] + 0.95, "whoosh", 0.8), (T["tu"], "whoosh", 0.7)]
    ev += [(T["tu"] + i * 0.12, "pop", 0.5) for i in range(3)]
    ev += [(T[k] - 0.05, "impact", 0.55) for k in ("que", "cuanto", "ahora")]
    ev += [(T["hace"], "whoosh", 0.7)] + [(T["perfil"] - 0.2 + i * 0.1, "pop", 0.35) for i in range(9)]
    ev += [(T["en"], "riser", 0.8), (T["clara"] + 0.3, "buzz", 0.8), (T["si"], "whoosh", 0.6), (T["cero2"], "sad", 0.9),
           (T["problema"], "impact", 1.0), (T["los"], "whoosh", 0.7), (T["seg2"], "pop", 0.4),
           (T["cuentas"], "buzz", 0.6), (T["clientes"], "impact", 0.8), (T["clientes"] + 0.05, "cash", 1.0),
           (T["comenta"] - 0.05, "whoosh", 0.7)]
    ev += cta_sfx

    return dict(background=background, scenes=S, overlay=overlay, camera=camera, sfx=ev, cap_y=1420,
                keywords=["seguidores", "cero", "algoritmo", "entretiene", "qué", "cuánto", "ahora", "nueve",
                          "oferta", "problema", "cuentas", "clientes"])


if __name__ == "__main__":
    render(Path(__file__).resolve().parent, build)
