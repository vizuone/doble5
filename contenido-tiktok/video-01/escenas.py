"""Video 01 — Dejá de tocar 'Promocionar'. Escenas sincronizadas a la voz (toma v4 A)."""
import math, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from motor import *  # noqa

HOOK = 'DEJÁ DE TOCAR "PROMOCIONAR"'


def p(t, t0, d):
    return clamp((t - t0) / d)


def build(wd, dur):
    T = {
        "promo": wd.at("Promocionar"), "frena": wd.at("FRENÁ"), "le": wd.at("Le"),
        "plata": wd.at("plata"), "meta": wd.at("Meta"), "ese": wd.at("Ese"), "no": wd.at("NO"),
        "ventas1": wd.at("ventas"), "te": wd.at("Te", 11), "likes": wd.at("likes"),
        "visitas": wd.at("visitas"), "gente": wd.at("gente"), "mira": wd.at("mira"),
        "seva": wd.at("va"), "lo": wd.at("Lo"), "una": wd.at("Una"), "admin": wd.at("Administrador"),
        "obj": wd.at("objetivo"), "VENTAS": wd.at("VENTAS"), "pixel": wd.at("píxel"),
        "anuncio": wd.at("anuncio"), "vos": wd.at("VOS"), "mismo": wd.at("Mismo"),
        "otro": wd.at("Otro"), "resultado": wd.at("resultado"), "si2": wd.at("Si", 29),
        "comenta": wd.at("comentá"), "revision": wd.at("REVISIÓN"),
    }
    cx = W // 2

    # ---------------- fondo ----------------
    def background(img, d, t):
        green = clamp(p(t, T["lo"], 0.3)) * (1 - clamp(p(t, T["si2"], 0.4)))
        base = tuple(int(lerp(a, b, green * 0.6)) for a, b in zip((17, 17, 20), (10, 30, 18)))
        off = (t * 70) % 240
        for x in range(-480, W + 480, 240):
            d.polygon([(x + off, 0), (x + off + 40, 0), (x + off - 300, H), (x + off - 340, H)], fill=base)

    # ---------------- escenas ----------------
    def phone(img, d, t, lt):
        # entra desde abajo
        e = back_out(lt / 0.45)
        y0 = 360 + (1 - e) * 900
        x0, x1, y1 = cx - 290, cx + 290, y0 + 880
        d.rounded_rectangle([x0, y0, x1, y1], 50, fill=(36, 36, 40), outline=(70, 70, 76), width=6)
        d.rounded_rectangle([x0 + 18, y0 + 18, x1 - 18, y1 - 18], 36, fill=(250, 250, 250))
        # cabecera del post
        d.ellipse([x0 + 44, y0 + 44, x0 + 104, y0 + 104], fill=(255, 140, 60))
        d.text((x0 + 122, y0 + 74), "tu_negocio", font=font(34, "Bold"), fill=(20, 20, 20), anchor="lm")
        # imagen del post
        d.rounded_rectangle([x0 + 40, y0 + 128, x1 - 40, y0 + 560], 20, fill=(225, 225, 232))
        text_c(d, (cx, y0 + 344), "TU PRODUCTO", font(46), (160, 160, 170))
        # iconos
        heart(d, x0 + 78, y0 + 612, 26, (30, 30, 30))
        d.ellipse([x0 + 128, y0 + 588, x0 + 176, y0 + 636], outline=(30, 30, 30), width=5)
        d.text((x0 + 44, y0 + 668), "128 Me gusta", font=font(30, "Bold"), fill=(30, 30, 30), anchor="lm")
        # botón Promocionar
        tap = T["promo"]
        pressed = tap <= t < tap + 0.25
        by0 = y0 + 720
        col = (0, 90, 200) if pressed else BLUE
        inset = 6 if pressed else 0
        d.rounded_rectangle([x0 + 40 + inset, by0 + inset, x1 - 40 - inset, by0 + 100 - inset], 18, fill=col)
        text_c(d, (cx, by0 + 50), "Promocionar publicación", font(36, "Bold"), (255, 255, 255))
        # dedo que viene a tocar
        if t < T["frena"]:
            fp = ease_in_out(p(t, 0.3, tap - 0.35))
            fx, fy = lerp(W + 60, cx + 40, fp), lerp(y0 + 500, by0 + 55, fp)
            if t >= tap:
                ripple(d, cx + 40, by0 + 55, (t - tap) / 0.5, (255, 255, 255, 255))
            finger(d, fx, fy, 38, pressed)
        # FRENÁ: cruz roja + sello
        if t >= T["frena"]:
            k = back_out((t - T["frena"]) / 0.25)
            d.rectangle([0, 0, W, H], fill=(255, 40, 40, int(70 * (1 - p(t, T["frena"], 0.5)))))
            cross(d, cx, by0 + 50, 70 * k, RED, 22)
            # sello
            s = font(int(190 * (1.6 - 0.6 * k)))
            stamp = Image.new("RGBA", (900, 320), (0, 0, 0, 0))
            sd = ImageDraw.Draw(stamp)
            sd.rounded_rectangle([20, 20, 880, 300], 30, outline=RED, width=16)
            sd.text((450, 165), "FRENÁ", font=s, fill=RED, anchor="mm")
            stamp = stamp.rotate(-8, expand=True, resample=Image.BICUBIC)
            img.paste(stamp, (cx - stamp.width // 2, 520), stamp)

    def money(img, d, t, lt):
        # billetes que vuelan desde "TU CAJA" hacia "META"
        bx, by = 260, 1080
        mx, my = W - 260, 470
        d.rounded_rectangle([bx - 170, by - 90, bx + 170, by + 90], 26, fill=CARD, outline=GREEN, width=5)
        text_c(d, (bx, by - 22), "TU PLATA", font(46), FG)
        # barra que se vacía
        lvl = 1 - 0.85 * ease_in_out(p(t, T["plata"], T["ese"] - T["plata"] - 0.2))
        d.rounded_rectangle([bx - 130, by + 25, bx + 130, by + 55], 12, fill=(50, 50, 55))
        d.rounded_rectangle([bx - 130, by + 25, bx - 130 + 260 * lvl, by + 55], 12, fill=GREEN if lvl > 0.4 else RED)
        km = back_out(p(t, T["meta"], 0.3))
        if t >= T["meta"] - 0.05:
            d.rounded_rectangle([mx - 170 * km, my - 80 * km, mx + 170 * km, my + 80 * km], 26, fill=BLUE)
            text_c(d, (mx, my), "META", font(int(64 * km) + 1), (255, 255, 255))
        rnd = random.Random(3)
        for i in range(14):
            st = T["plata"] - 0.1 + i * 0.09
            q = p(t, st, 0.8)
            if 0 < q < 1:
                arc = math.sin(q * math.pi) * -220
                x = lerp(bx, mx, ease_in_out(q)) + rnd.uniform(-60, 60)
                y = lerp(by, my, ease_in_out(q)) + arc
                bill(img, x, y, rnd.uniform(-40, 40) + q * 200 * (1 if i % 2 else -1), 1.0)
        if t >= T["meta"] + 0.5:
            text_c(d, (cx, 760), "+ $$$", font(110), GREEN, 6)
            text_c(d, (cx, 860), "para Meta, no para vos", font(44, "XBold"), FG)

    def objectives(img, d, t, lt):
        e = back_out(lt / 0.35)
        x0, x1 = 120, W - 120
        y0 = 360 + (1 - e) * 120
        d.rounded_rectangle([x0, y0, x1, y0 + 820], 36, fill=(250, 250, 250))
        d.text((x0 + 50, y0 + 70), "¿Qué querés lograr?", font=font(50, "XBold"), fill=(20, 20, 20), anchor="lm")
        opts = ["Más visitas al perfil", "Más visitas al sitio web", "Más mensajes", "VENTAS"]
        for i, o in enumerate(opts):
            oy = y0 + 160 + i * 150
            q = back_out(p(t, T["ese"] + 0.12 * i, 0.3))
            if q <= 0: continue
            last = i == 3
            shake = 0
            if last and t >= T["no"]:
                shake = math.sin((t - T["no"]) * 60) * 14 * (1 - p(t, T["no"], 0.5))
            bg = (255, 230, 230) if (last and t >= T["no"]) else (240, 240, 244)
            d.rounded_rectangle([x0 + 40 + shake, oy, x1 - 40 + shake, oy + 120], 22, fill=bg)
            d.ellipse([x0 + 70 + shake, oy + 38, x0 + 114 + shake, oy + 82], outline=(150, 150, 160), width=5)
            tc = (190, 190, 195) if last else (30, 30, 30)
            d.text((x0 + 140 + shake, oy + 60), o, font=font(44 if not last else 52, "XBold" if last else "Semi"),
                   fill=tc, anchor="lm")
            if last:
                ls = 26 * (1 + 0.35 * math.sin(p(t, T["ventas1"], 0.4) * math.pi))
                lock(d, x1 - 110 + shake, oy + 52, ls, RED if t >= T["no"] else (170, 170, 175))
        if t >= T["ventas1"]:
            k = back_out(p(t, T["ventas1"], 0.3))
            text_c(d, (cx, y0 + 920), "NO DISPONIBLE", font(int(84 * k) + 1), RED, 6)

    def vanity(img, d, t, lt):
        # corazones que suben + contadores (ilustrativos)
        rnd = random.Random(11)
        for i in range(26):
            st = T["likes"] - 0.3 + rnd.uniform(0, 1.8)
            q = (t - st) / 1.6
            if 0 < q < 1:
                x = rnd.uniform(140, W - 140) + math.sin(q * 6 + i) * 30
                y = 1250 - q * 900
                heart(d, x, y, rnd.uniform(26, 50), (255, 55, 95, int(255 * (1 - q))))
        likes = int(lerp(0, 1248, ease_out(p(t, T["likes"], 1.6))))
        vis = int(lerp(0, 316, ease_out(p(t, T["visitas"], 1.4))))
        for i, (lab, val, st) in enumerate([("Me gusta", likes, T["likes"]), ("Visitas al perfil", vis, T["visitas"])]):
            k = back_out(p(t, st - 0.1, 0.3))
            if k <= 0: continue
            y = 520 + i * 260
            d.rounded_rectangle([cx - 360 * k, y - 100, cx + 360 * k, y + 100], 30, fill=CARD)
            text_c(d, (cx, y - 30), f"+{val:,}".replace(",", "."), font(96), FG)
            text_c(d, (cx, y + 52), lab, font(40, "Bold"), DIM)

    def leave(img, d, t, lt):
        n = 5
        for i in range(n):
            x = 170 + i * 185
            k = back_out(p(t, T["gente"] + i * 0.06, 0.3))
            out = ease_in_out(p(t, T["seva"] - 0.2 + i * 0.05, 0.6))
            xx = x + out * 1200
            yy = 760 + (1 - k) * 200
            person(d, xx, yy, 90, (200, 200, 205))
            if t >= T["mira"]:
                eye(d, xx, yy - 160, 36, (255, 255, 255))
        if t >= T["seva"]:
            k = back_out(p(t, T["seva"] + 0.2, 0.35))
            d.rounded_rectangle([cx - 330 * k, 520 - 90 * k, cx + 330 * k, 520 + 90 * k], 28, fill=(60, 14, 14))
            text_c(d, (cx, 520), "VENTAS: 0", font(int(110 * k) + 1), RED)

    def turn(img, d, t, lt):
        k = back_out(lt / 0.3)
        text_c(d, (cx, 760), "¿LO QUE", font(int(150 * k) + 1), FG, 8)
        text_c(d, (cx, 930), "VENDE?", font(int(190 * k) + 1), GREEN, 8)

    def checklist(img, d, t, lt):
        e = back_out(lt / 0.35)
        x0, x1 = 90, W - 90
        y0 = 320 + (1 - e) * 200
        d.rounded_rectangle([x0, y0, x1, y0 + 900], 36, fill=CARD, outline=GREEN, width=5)
        text_c(d, (cx, y0 + 80), "CAMPAÑA QUE VENDE", font(56), GREEN)
        items = [(T["admin"], "Administrador de anuncios"), (T["obj"], "Objetivo: VENTAS"),
                 (T["pixel"], "Píxel midiendo"), (T["anuncio"], "Anuncio con un POR QUÉ")]
        for i, (st, label) in enumerate(items):
            q = back_out(p(t, st - 0.15, 0.3))
            if q <= 0: continue
            iy = y0 + 200 + i * 175
            xo = (1 - q) * 300
            d.rounded_rectangle([x0 + 40 + xo, iy, x1 - 40 + xo, iy + 145], 24, fill=(40, 40, 46))
            ck = back_out(p(t, st + 0.15, 0.3))
            r = 38 * ck
            d.ellipse([x0 + 115 - r + xo, iy + 72 - r, x0 + 115 + r + xo, iy + 72 + r], fill=GREEN)
            if ck > 0.3: check(d, x0 + 115 + xo, iy + 74, 26, (10, 30, 18), 9)
            lines = label.split("\n")
            for li, l in enumerate(lines):
                d.text((x0 + 180 + xo, iy + 72 + (li - (len(lines) - 1) / 2) * 52), l, font=font(46, "XBold"),
                       fill=FG, anchor="lm")
            if "Píxel" in label and t >= st:
                pr = (t - st) % 0.8 / 0.8
                px = x1 - 110 + xo
                d.ellipse([px - 14, iy + 58, px + 14, iy + 86], fill=GREEN)
                rr = 14 + 40 * pr
                d.ellipse([px - rr, iy + 72 - rr, px + rr, iy + 72 + rr], outline=(48, 209, 88, int(255 * (1 - pr))), width=5)
        if t >= T["vos"]:
            k = back_out(p(t, T["vos"], 0.3))
            iy = y0 + 200 + 3 * 175
            g = int(6 + 6 * (1 - k))
            d.rounded_rectangle([x0 + 40 - g, iy - g, x1 - 40 + g, iy + 145 + g], 28, outline=ACCENT, width=8)

    def compare(img, d, t, lt):
        cols = [(cx - 230, "PROMOCIONAR", RED, 0.12), (cx + 230, "CAMPAÑA", GREEN, 1.0)]
        base = 1180
        for x, lab, col, res in cols:
            k = back_out(p(t, T["mismo"] - 0.1, 0.35))
            text_c(d, (x, 420), lab, font(50), col)
            # presupuesto (igual)
            bh = 260 * ease_out(p(t, T["mismo"], 0.6))
            d.rounded_rectangle([x - 190, base - bh, x - 30, base], 16, fill=(90, 90, 98))
            text_c(d, (x - 110, base + 40), "$ gasto", font(32, "Bold"), DIM)
            # resultado
            rh = 640 * res * ease_out(p(t, T["resultado"], 0.7))
            if rh > 1:
                d.rounded_rectangle([x + 30, base - rh, x + 190, base], 16, fill=col)
            text_c(d, (x + 110, base + 40), "ventas", font(32, "Bold"), DIM)
        d.line([(80, base), (W - 80, base)], fill=(80, 80, 86), width=4)
        if t >= T["mismo"]:
            text_c(d, (cx, 300), "MISMO PRESUPUESTO", font(56), FG)

    def cta(img, d, t, lt):
        e = back_out(lt / 0.4)
        y0 = 560 + (1 - e) * 300
        text_c(d, (cx, 420), "¿QUERÉS QUE LO MIRE?", font(64), FG)
        d.rounded_rectangle([90, y0, W - 90, y0 + 150], 75, fill=(250, 250, 250))
        word = "REVISIÓN"
        nch = int(clamp((t - T["comenta"] - 0.2) / 0.08, 0, len(word)))
        typed = word[:nch]
        if typed:
            d.text((150, y0 + 75), typed, font=font(66), fill=(20, 20, 20), anchor="lm")
        else:
            d.text((150, y0 + 75), "Agregá un comentario…", font=font(42, "Semi"), fill=(150, 150, 155), anchor="lm")
        if (t * 2) % 1 < 0.5:
            cxp = 150 + d.textlength(typed, font=font(66)) + 6
            d.line([(cxp, y0 + 40), (cxp, y0 + 110)], fill=BLUE, width=5)
        sent = T["comenta"] + 0.2 + 0.08 * len(word) + 0.25
        bc = BLUE if nch == len(word) else (180, 180, 190)
        r = 52 * (0.85 if sent <= t < sent + 0.15 else 1)
        d.ellipse([W - 165 - r, y0 + 75 - r, W - 165 + r, y0 + 75 + r], fill=bc)
        d.polygon([(W - 190, y0 + 50), (W - 135, y0 + 75), (W - 190, y0 + 100)], fill=(255, 255, 255))
        if t >= sent:
            ripple(d, W - 165, y0 + 75, (t - sent) / 0.5, (10, 132, 255, 255))
            k = back_out(p(t, sent, 0.3))
            # comentario publicado
            d.rounded_rectangle([90, y0 + 210, W - 90, y0 + 210 + 150 * k], 30, fill=CARD)
            if k > 0.6:
                d.ellipse([120, y0 + 245, 200, y0 + 325], fill=(255, 140, 60))
                d.text((225, y0 + 262), "vos", font=font(32, "Bold"), fill=DIM, anchor="lm")
                d.text((225, y0 + 310), "REVISIÓN", font=font(52), fill=FG, anchor="lm")
                heart(d, W - 150, y0 + 285, 30 * back_out(p(t, sent + 0.25, 0.3)), (255, 55, 95))
        # flecha rebotando hacia los comentarios
        by = 1200 + math.sin(t * 9) * 25
        d.polygon([(W - 150, by), (W - 90, by), (W - 90, by + 70), (W - 50, by + 70), (W - 120, by + 150),
                   (W - 190, by + 70), (W - 150, by + 70)], fill=ACCENT)

    S = [
        dict(start=0, end=T["le"] - 0.05, draw=phone),
        dict(start=T["le"] - 0.05, end=T["ese"] - 0.05, draw=money),
        dict(start=T["ese"] - 0.05, end=T["te"] - 0.05, draw=objectives),
        dict(start=T["te"] - 0.05, end=T["gente"] - 0.25, draw=vanity),
        dict(start=T["gente"] - 0.25, end=T["lo"] - 0.05, draw=leave),
        dict(start=T["lo"] - 0.05, end=T["una"] - 0.05, draw=turn),
        dict(start=T["una"] - 0.05, end=T["mismo"] - 0.15, draw=checklist),
        dict(start=T["mismo"] - 0.15, end=T["si2"] - 0.05, draw=compare),
        dict(start=T["si2"] - 0.05, end=dur + 1, draw=cta),
    ]
    cuts = [s["start"] for s in S[1:]]

    def overlay(img, d, t):
        # cabecera con el gancho
        if t < 0.15:
            pass
        k = back_out(p(t, 0, 0.3))
        hf = font(int(52 * k) + 1)
        text_c(d, (cx, 175), HOOK, hf, ACCENT, 5)
        # progreso
        d.rectangle([0, 0, int(W * t / dur), 10], fill=ACCENT)
        d.text((cx, 1610), "@elagus", font=font(38, "Bold"), fill=DIM, anchor="mm")
        # flash en cada corte
        for c in cuts:
            if c <= t < c + 0.12:
                d.rectangle([0, 0, W, H], fill=(255, 255, 255, int(110 * (1 - (t - c) / 0.12))))

    punches = [T["promo"], T["no"], T["VENTAS"], T["vos"], T["resultado"], T["revision"]]

    def camera(t):
        z, sx, sy = 1.0, 0.0, 0.0
        for pt in punches:
            if pt <= t < pt + 0.3:
                z = max(z, 1 + 0.07 * (1 - (t - pt) / 0.3) ** 2)
        if T["frena"] <= t < T["frena"] + 0.5:
            a = 28 * (1 - (t - T["frena"]) / 0.5)
            sx, sy = math.sin(t * 95) * a, math.cos(t * 80) * a
            z = max(z, 1.04)
        return z, sx, sy

    sfx_ev = [(0.25, "whoosh", 0.9), (T["promo"], "click", 1.0), (T["frena"], "impact", 1.0),
              (T["frena"] + 0.02, "buzz", 0.8), (T["plata"] - 0.1, "whoosh", 0.8), (T["plata"], "cash", 1.0),
              (T["meta"] + 0.5, "cash", 0.7), (T["ese"], "whoosh", 0.7), (T["no"], "buzz", 0.7),
              (T["ventas1"], "impact", 0.6)]
    sfx_ev += [(T["likes"] + i * 0.18, "pop", 0.45) for i in range(8)]
    sfx_ev += [(T["gente"] - 0.25, "whoosh", 0.7), (T["seva"], "whoosh", 0.8), (T["seva"] + 0.25, "sad", 1.0),
               (T["lo"] - 0.6, "riser", 1.0), (T["lo"], "impact", 0.9)]
    sfx_ev += [(T[k] + 0.15, "ding", 0.9) for k in ("admin", "obj", "pixel", "anuncio")]
    sfx_ev += [(T["vos"], "impact", 0.7), (T["mismo"] - 0.15, "whoosh", 0.7), (T["resultado"], "cash", 1.0),
               (T["resultado"], "impact", 0.6), (T["si2"] - 0.05, "whoosh", 0.7)]
    sfx_ev += [(T["comenta"] + 0.2 + 0.08 * i, "type", 0.8) for i in range(8)]
    sfx_ev += [(T["comenta"] + 0.2 + 0.64 + 0.25, "pop", 1.0), (T["comenta"] + 1.4, "ding", 0.8)]

    return dict(background=background, scenes=S, overlay=overlay, camera=camera, sfx=sfx_ev,
                cap_y=1420, keywords=["promocionar", "frená", "plata", "meta", "no", "ventas", "likes",
                                      "administrador", "píxel", "vos", "presupuesto", "resultado", "revisión"])


if __name__ == "__main__":
    render(Path(__file__).resolve().parent, build)
