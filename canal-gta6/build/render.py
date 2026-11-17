# -*- coding: utf-8 -*-
"""Renderiza un video completo: voz (TTS local) + música + animación + montaje.

Uso:  python3 render.py 01        (o "todos")
Salida en ../videos/, ../miniaturas/, ../subtitulos/, ../metadatos/
"""
import os, sys, math, json, subprocess, glob, textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import soundfile as sf

import guiones as G
import musica

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
W, H, FPS = 1920, 1080, 30
SR = 44100

F_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
F_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
F_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
F_MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf"
_fc = {}
def fuente(path, size):
    k = (path, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]

PALETAS = {
    "rosa":    dict(cielo=[(18,6,40),(120,20,90),(255,90,120)], sol=[(255,214,90),(255,60,140)], grid=(255,60,170), a=(255,64,160), b=(60,230,255)),
    "naranja": dict(cielo=[(20,8,36),(110,30,70),(255,130,60)],  sol=[(255,236,120),(255,90,60)],  grid=(255,120,60), a=(255,140,40), b=(255,60,150)),
    "cian":    dict(cielo=[(4,10,36),(20,50,110),(60,200,230)],  sol=[(200,255,250),(60,140,255)], grid=(40,220,255), a=(40,220,255), b=(255,70,170)),
    "verde":   dict(cielo=[(4,20,26),(10,70,70),(60,230,160)],   sol=[(240,255,170),(40,200,140)], grid=(60,255,170), a=(70,255,170), b=(255,200,60)),
    "dorado":  dict(cielo=[(22,12,8),(90,40,20),(250,180,70)],   sol=[(255,245,180),(255,150,40)], grid=(255,190,70), a=(255,196,60), b=(255,80,120)),
}

def ease(p):
    p = max(0.0, min(1.0, p)); return 1 - (1 - p) ** 3

# ------------------------------------------------------------------ voz
_tts = None
# Voz elegida con VOZ=kokoro (por defecto), VOZ=daniela o VOZ=sharvard
VOZ = os.environ.get("VOZ", "kokoro")
VOCES = {
    "kokoro":   dict(dir="kokoro-multi-lang-v1_0", sid=28, speed=1.05),   # ef_dora, mujer, español
    "daniela":  dict(dir="vits-piper-es_AR-daniela-high", sid=0, speed=1.0, ns=0.45, nw=0.55, ls=0.97),
    "sharvard": dict(dir="vits-piper-es_ES-sharvard-medium", sid=1, speed=1.0),
    "claude":   dict(dir="vits-piper-es_MX-claude-high", sid=0, speed=1.0),
}
# Procesado de voz: suave para Kokoro (ya es limpia), más intenso para Piper
CADENA_VOZ = {
    True: "highpass=f=70,deesser=i=0.25,equalizer=f=200:t=q:w=1:g=1.5,acompressor=threshold=0.12:ratio=2.5",
    False: ("highpass=f=80,afftdn=nr=10:nf=-40,deesser=i=0.4,equalizer=f=250:t=q:w=1:g=2,"
            "equalizer=f=3500:t=q:w=1.2:g=-2.5,equalizer=f=7500:t=q:w=1:g=-3,lowpass=f=10000,"
            "acompressor=threshold=0.1:ratio=3,aecho=0.8:0.5:22:0.06"),
}
def tts():
    global _tts
    if _tts is None:
        import sherpa_onnx as so
        d = os.path.join(AQUI, "voces", VOCES[VOZ]["dir"])
        if VOZ == "kokoro":
            m = so.OfflineTtsModelConfig(kokoro=so.OfflineTtsKokoroModelConfig(
                model=d + "/model.onnx", voices=d + "/voices.bin", tokens=d + "/tokens.txt",
                data_dir=d + "/espeak-ng-data", dict_dir=d + "/dict", lexicon=d + "/lexicon-us-en.txt", lang="es"),
                num_threads=2)
        else:
            m = so.OfflineTtsModelConfig(vits=so.OfflineTtsVitsModelConfig(
                model=glob.glob(d + "/*.onnx")[0], tokens=d + "/tokens.txt", data_dir=d + "/espeak-ng-data",
                noise_scale=VOCES[VOZ].get("ns", 0.667), noise_scale_w=VOCES[VOZ].get("nw", 0.8),
                length_scale=VOCES[VOZ].get("ls", 1.0)),
                num_threads=2)
        _tts = so.OfflineTts(so.OfflineTtsConfig(model=m))
    return _tts

def decir(texto):
    a = tts().generate(texto, sid=VOCES[VOZ]["sid"], speed=VOCES[VOZ]["speed"])
    x = np.array(a.samples, dtype=np.float32)
    # remuestreo polifásico de calidad (la interpolación lineal añadía un brillo metálico)
    from scipy.signal import resample_poly
    from math import gcd
    g = gcd(SR, a.sample_rate)
    y = resample_poly(x, SR // g, a.sample_rate // g).astype(np.float32)
    # recorta silencios de los extremos
    m = np.where(np.abs(y) > 0.01)[0]
    if len(m): y = y[max(0, m[0] - 800): m[-1] + 1500]
    return y

# ------------------------------------------------------------------ fondo
def degradado(cols, h):
    ys = np.linspace(0, 1, h)[:, None]
    n = len(cols) - 1
    out = np.zeros((h, 3))
    for c in range(3):
        out[:, c] = np.interp(ys[:, 0], np.linspace(0, 1, n + 1), [col[c] for col in cols])
    return out

def palmera(d, x, y, s, col):
    # tronco curvo + hojas: dibujo propio
    pts = [(x + math.sin(i / 10) * 18 * s, y - i * 9 * s) for i in range(30)]
    d.line(pts, fill=col, width=int(12 * s))
    tx, ty = pts[-1]
    for ang in (-160, -130, -100, -70, -40, -10, 15):
        r = math.radians(ang)
        pts2 = []
        for i in range(12):
            k = i / 11
            pts2.append((tx + math.cos(r) * 130 * s * k, ty + math.sin(r) * 90 * s * k + (k ** 2) * 70 * s))
        d.line(pts2, fill=col, width=int(10 * s))

def fondo_frames(pal, n=30):
    P = PALETAS[pal]
    hor = int(H * 0.62)
    base = np.zeros((H, W, 3), dtype=np.float32)
    base[:hor] = degradado(P["cielo"], hor)[:, None, :]
    img = Image.fromarray(base.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    # estrellas
    rng = np.random.default_rng(7)
    for _ in range(160):
        x, y = rng.integers(0, W), rng.integers(0, int(hor * 0.55))
        v = int(rng.integers(120, 255)); d.point((x, y), fill=(v, v, v))
    # sol con franjas
    sol = Image.new("RGB", (560, 560)); sm = Image.new("L", (560, 560), 0)
    sg = degradado(P["sol"], 560); sol = Image.fromarray(np.repeat(sg[:, None, :], 560, 1).astype(np.uint8))
    ImageDraw.Draw(sm).ellipse((0, 0, 559, 559), fill=255)
    dm = ImageDraw.Draw(sm)
    for i in range(7):
        y0 = 300 + i * 36; dm.rectangle((0, y0, 560, y0 + 6 + i * 3), fill=0)
    glow = Image.new("RGB", (W, H), (0, 0, 0)); gm = Image.new("L", (W, H), 0)
    ImageDraw.Draw(gm).ellipse((W // 2 - 420, hor - 680, W // 2 + 420, hor + 160), fill=110)
    gm = gm.filter(ImageFilter.GaussianBlur(90))
    img.paste(Image.new("RGB", (W, H), P["sol"][1]), (0, 0), gm)
    img.paste(sol, (W // 2 - 280, hor - 470), sm)
    # skyline propio
    d = ImageDraw.Draw(img)
    sil = (12, 4, 22)
    rng = np.random.default_rng(3)
    x = 0
    while x < W:
        w = int(rng.integers(40, 120)); h = int(rng.integers(40, 230))
        if abs(x - W / 2) < 260: h = int(h * 0.5)
        d.rectangle((x, hor - h, x + w, hor), fill=sil)
        if rng.random() < 0.3: d.rectangle((x + w // 2 - 3, hor - h - 40, x + w // 2 + 3, hor - h), fill=sil)
        x += w + int(rng.integers(0, 8))
    palmera(d, 170, hor + 5, 1.6, sil); palmera(d, 330, hor + 5, 1.1, sil)
    palmera(d, W - 190, hor + 5, 1.7, sil); palmera(d, W - 360, hor + 5, 1.2, sil)
    top = np.asarray(img).astype(np.uint8).copy()
    # suelo + rejilla en perspectiva animada
    frames = []
    g = P["grid"]
    for f in range(n):
        im = Image.fromarray(top.copy()); d = ImageDraw.Draw(im)
        suelo = degradado([(10, 2, 20), (4, 0, 10)], H - hor)
        im.paste(Image.fromarray(np.repeat(suelo[:, None, :], W, 1).astype(np.uint8)), (0, hor))
        cx = W / 2
        for i in range(-24, 25):
            d.line((cx + i * 40, hor, cx + i * 260, H), fill=tuple(int(c * 0.55) for c in g), width=2)
        off = f / n
        for k in range(14):
            z = (k + 1 - off)
            y = hor + (H - hor) * (1 / (z * 0.55 + 0.45)) ** 1.0 * 0.0 + (H - hor) * (1 - 1 / (1 + (14 - z) * 0.18)) if False else hor + (H - hor) * ((14 - z) / 14) ** 2.2
            a = 0.25 + 0.75 * ((14 - z) / 14)
            d.line((0, y, W, y), fill=tuple(int(c * a * 0.7) for c in g), width=2)
        d.line((0, hor, W, hor), fill=g, width=3)
        arr = np.asarray(im).astype(np.float32)
        # viñeta
        frames.append(arr)
    yy, xx = np.mgrid[0:H, 0:W]
    vig = 1 - 0.55 * (((xx - W / 2) / (W / 1.3)) ** 2 + ((yy - H / 2) / (H / 1.2)) ** 2)
    vig = vig.clip(0.35, 1)[:, :, None]
    return [(fr * vig * 0.62).clip(0, 255).astype(np.uint8) for fr in frames]

# ------------------------------------------------------------------ utilidades de texto
def envolver(texto, font, ancho):
    palabras = texto.split(); lineas = []; cur = ""
    for p in palabras:
        t = (cur + " " + p).strip()
        if font.getlength(t) <= ancho: cur = t
        else:
            if cur: lineas.append(cur)
            cur = p
    if cur: lineas.append(cur)
    return lineas

def capa_texto(texto, font, color, ancho=None, glow=None, stroke=0, interlineado=1.15, align="left"):
    lineas = envolver(texto, font, ancho) if ancho else [texto]
    asc, desc = font.getmetrics(); lh = int((asc + desc) * interlineado)
    wmax = int(max(font.getlength(l) for l in lineas)) + 2 * stroke + 60
    hh = lh * len(lineas) + 2 * stroke + 60
    im = Image.new("RGBA", (wmax, hh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(lineas):
        x = 30 + stroke
        if align == "center": x = (wmax - font.getlength(l)) / 2
        d.text((x, 30 + stroke + i * lh), l, font=font, fill=color, stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    if glow:
        g = Image.new("RGBA", im.size, glow + (0,)); g.putalpha(im.getchannel("A").filter(ImageFilter.GaussianBlur(14)))
        im = Image.alpha_composite(g, Image.alpha_composite(g, im))
    return im

def caja(w, h, fill=(10, 6, 24, 200), borde=None, r=26, grosor=3):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), r, fill=fill, outline=borde, width=grosor if borde else 0)
    return im

# ------------------------------------------------------------------ capas por tipo de visual
class Capa:
    def __init__(self, img, x, y, t0, modo="sube", dur=0.45):
        self.img, self.x, self.y, self.t0, self.modo, self.dur = img, int(x), int(y), t0, modo, dur
        self.alpha = img.getchannel("A")

def escalonar(n, dur, inicio=0.35, fin=0.72):
    if n <= 1: return [inicio]
    return [inicio + i * (dur * fin - inicio) / (n - 1) for i in range(n)]

def visual_capas(vis, P, dur):
    """Devuelve (capas estáticas animadas, función dinámica opcional por frame)."""
    a, b = P["a"], P["b"]; capas = []; din = None
    t = vis["t"]
    cy = 470  # centro vertical del área de contenido
    if t == "titulo":
        im = capa_texto(vis["texto"], fuente(F_BLACK, 132), (255, 255, 255), ancho=1600, glow=a, align="center")
        capas.append(Capa(im, (W - im.width) / 2, cy - im.height / 2 - 40, 0.15, "zoom", 0.6))
        if vis.get("sub"):
            s = capa_texto(vis["sub"], fuente(F_SEMI, 46), b, ancho=1500, align="center")
            capas.append(Capa(s, (W - s.width) / 2, cy + im.height / 2 - 40, 0.6))
    elif t == "numero":
        im = capa_texto(vis["valor"], fuente(F_BLACK, 230), (255, 255, 255), glow=a, align="center")
        capas.append(Capa(im, (W - im.width) / 2, cy - im.height / 2 - 50, 0.15, "zoom", 0.6))
        s = capa_texto(vis["sub"], fuente(F_SEMI, 48), b, ancho=1500, align="center")
        capas.append(Capa(s, (W - s.width) / 2, cy + im.height / 2 - 70, 0.7))
    elif t == "lista":
        items = vis["items"]; n = len(items)
        fs = 58 if n <= 4 else 50
        alto = 104 if n <= 4 else 86
        y0 = cy - n * alto / 2
        for i, (it, t0) in enumerate(zip(items, escalonar(n, dur))):
            bx = caja(1240, alto - 18, fill=(12, 6, 30, 215), borde=a + (255,), r=20)
            d = ImageDraw.Draw(bx)
            d.rounded_rectangle((0, 0, 16, alto - 19), 8, fill=a)
            f = fuente(F_BOLD, fs)
            while f.getlength(it) > 1150 and f.size > 30: f = fuente(F_BOLD, f.size - 2)
            d.text((50, (alto - 18) / 2), it, font=f, fill=(255, 255, 255), anchor="lm")
            capas.append(Capa(bx, (W - 1240) / 2, y0 + i * alto, t0, "izq"))
    elif t == "tabla":
        filas = vis["filas"]; n = len(filas); alto = 92; y0 = cy - n * alto / 2
        for i, ((k, v), t0) in enumerate(zip(filas, escalonar(n, dur, 0.3, 0.55))):
            bx = caja(1300, alto - 14, fill=(12, 6, 30, 215) if i % 2 == 0 else (24, 10, 48, 215), r=16)
            d = ImageDraw.Draw(bx)
            d.text((40, (alto - 14) / 2), k, font=fuente(F_BOLD, 46), fill=(255, 255, 255), anchor="lm")
            d.text((1260, (alto - 14) / 2), v, font=fuente(F_MONO, 44), fill=b, anchor="rm")
            capas.append(Capa(bx, (W - 1300) / 2, y0 + i * alto, t0, "izq"))
    elif t == "tarjetas":
        cards = vis["cards"]; n = len(cards)
        cw = min(460, int(1640 / n) - 30); ch = 380
        x0 = (W - (n * cw + (n - 1) * 30)) / 2
        for i, ((tit, val, lin), t0) in enumerate(zip(cards, escalonar(n, dur, 0.3, 0.5))):
            bx = caja(cw, ch, fill=(12, 6, 30, 225), borde=(a if i % 2 == 0 else b) + (255,), r=28, grosor=4)
            d = ImageDraw.Draw(bx)
            ft = fuente(F_BLACK, 56)
            while ft.getlength(tit) > cw - 40: ft = fuente(F_BLACK, ft.size - 2)
            d.text((cw / 2, 80), tit, font=ft, fill=(255, 255, 255), anchor="mm")
            d.line((40, 135, cw - 40, 135), fill=(a if i % 2 == 0 else b), width=3)
            if val:
                fv = fuente(F_BLACK, 64)
                while fv.getlength(val) > cw - 40: fv = fuente(F_BLACK, fv.size - 2)
                d.text((cw / 2, 220), val, font=fv, fill=(a if i % 2 == 0 else b), anchor="mm")
            if lin:
                fl = fuente(F_SEMI, 34)
                for j, l in enumerate(envolver(lin, fl, cw - 50)):
                    d.text((cw / 2, 300 + j * 42), l, font=fl, fill=(220, 220, 235), anchor="mm")
            capas.append(Capa(bx, x0 + i * (cw + 30), cy - ch / 2, t0, "zoom"))
    elif t == "linea":
        ev = vis["eventos"]; n = len(ev)
        x0, x1 = 200, W - 200; yl = cy - 20
        tiempos = escalonar(n, dur, 0.3, 0.7)
        def din(d, tt, _ev=ev, _t=tiempos):
            p = ease((tt - 0.1) / (_t[-1] + 0.4))
            d.line((x0, yl, x0 + (x1 - x0) * p, yl), fill=a, width=8)
        for i, ((anio, txt), t0) in enumerate(zip(ev, tiempos)):
            x = x0 + (x1 - x0) * (i / max(1, n - 1)) if n > 1 else W / 2
            bx = Image.new("RGBA", (420, 340), (0, 0, 0, 0)); d = ImageDraw.Draw(bx)
            d.ellipse((180, 150, 240, 210), fill=b, outline=(255, 255, 255), width=5)
            fa = fuente(F_BLACK, 56)
            while fa.getlength(anio) > 400: fa = fuente(F_BLACK, fa.size - 2)
            d.text((210, 110), anio, font=fa, fill=(255, 255, 255), anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
            fl = fuente(F_SEMI, 34)
            for j, l in enumerate(envolver(txt, fl, 380)):
                d.text((210, 250 + j * 42), l, font=fl, fill=(235, 235, 245), anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))
            capas.append(Capa(bx, x - 210, yl - 180, t0, "zoom"))
    elif t == "barras":
        bs = vis["barras"]; n = len(bs); alto = 100; y0 = cy - n * alto / 2
        tiempos = escalonar(n, dur, 0.3, 0.55)
        etiquetas = []
        for i, (lab, val, mx) in enumerate(bs):
            im = capa_texto(lab, fuente(F_BOLD, 40), (255, 255, 255), stroke=2)
            capas.append(Capa(im, 160 - 30, y0 + i * alto - 30 + 8, tiempos[i], "izq"))
        def din(d, tt, _bs=bs, _t=tiempos):
            for i, (lab, val, mx) in enumerate(_bs):
                p = ease((tt - _t[i]) / 0.9)
                if p <= 0: continue
                xa = 760; wmax = 900
                col = b if lab.startswith("GTA") else a
                d.rounded_rectangle((xa, y0 + i * alto + 10, xa + max(20, wmax * val / mx * p), y0 + i * alto + 70), 12, fill=col)
                d.text((xa + wmax * val / mx * p + 20, y0 + i * alto + 40), f"{int(val * p)} GB", font=fuente(F_MONO, 40), fill=(255, 255, 255), anchor="lm", stroke_width=2, stroke_fill=(0, 0, 0))
    elif t == "aviso":
        bx = caja(1400, 380, fill=(30, 8, 20, 230), borde=(255, 210, 60, 255), r=30, grosor=5)
        d = ImageDraw.Draw(bx)
        d.polygon([(130, 90), (60, 220), (200, 220)], fill=(255, 210, 60))
        d.text((130, 175), "!", font=fuente(F_BLACK, 90), fill=(30, 8, 20), anchor="mm")
        fl = fuente(F_BOLD, 54)
        ls = envolver(vis["texto"], fl, 1100)
        y = 190 - len(ls) * 34
        for j, l in enumerate(ls):
            d.text((260, y + j * 68), l, font=fl, fill=(255, 255, 255))
        capas.append(Capa(bx, (W - 1400) / 2, cy - 190, 0.2, "zoom", 0.5))
    elif t == "personajes":
        ps = vis["p"]; n = len(ps)
        cw = 620 if n == 2 else 900; ch = 560
        x0 = (W - (n * cw + (n - 1) * 60)) / 2
        for i, ((nombre, lineas), t0) in enumerate(zip(ps, escalonar(n, dur, 0.3, 0.4))):
            col = a if i == 0 else b
            bx = caja(cw, ch, fill=(12, 6, 30, 225), borde=col + (255,), r=30, grosor=4)
            d = ImageDraw.Draw(bx)
            # silueta genérica (no representa a ningún personaje)
            cx = cw / 2 if not lineas or n == 2 else 200
            d.ellipse((cx - 70, 50, cx + 70, 190), fill=col)
            d.pieslice((cx - 150, 200, cx + 150, 480), 180, 360, fill=col)
            fn = fuente(F_BLACK, 58)
            while fn.getlength(nombre) > cw - 60: fn = fuente(F_BLACK, fn.size - 2)
            if n == 2 or not lineas:
                d.text((cw / 2, 400), nombre, font=fn, fill=(255, 255, 255), anchor="mm")
                for j, l in enumerate(lineas):
                    d.text((cw / 2, 460 + j * 44), l, font=fuente(F_SEMI, 34), fill=(225, 225, 240), anchor="mm")
            else:
                d.text((400, 110), nombre, font=fn, fill=(255, 255, 255), anchor="lm")
                for j, l in enumerate(lineas):
                    d.text((400, 220 + j * 80), "· " + l, font=fuente(F_BOLD, 44), fill=(230, 230, 245), anchor="lm")
            capas.append(Capa(bx, x0 + i * (cw + 60), cy - ch / 2, t0, "zoom"))
    elif t == "mapa":
        capas_m, din = mapa(vis.get("resaltar", []), P, dur)
        capas += capas_m
    return capas, din

# Mapa estilizado propio de Leonida (forma inventada, posiciones aproximadas)
REGIONES = {
    "MOUNT KALAGA": (0.50, 0.10), "PORT GELLHORN": (0.10, 0.17), "AMBROSIA": (0.55, 0.36),
    "GRASSRIVERS": (0.56, 0.57), "VICE CITY": (0.78, 0.70), "LEONIDA KEYS": (0.58, 0.93),
}
def mapa(resaltar, P, dur):
    a, b = P["a"], P["b"]
    mw, mh = 1000, 680
    ox, oy = (W - mw) / 2, 120
    poly = [(0.02, 0.10), (0.30, 0.06), (0.62, 0.04), (0.74, 0.08), (0.78, 0.22), (0.86, 0.42), (0.90, 0.58),
            (0.88, 0.76), (0.80, 0.86), (0.70, 0.84), (0.60, 0.72), (0.52, 0.56), (0.46, 0.40), (0.38, 0.30),
            (0.22, 0.30), (0.04, 0.26)]
    base = Image.new("RGBA", (mw, mh), (0, 0, 0, 0)); d = ImageDraw.Draw(base)
    pts = [(x * mw, y * mh) for x, y in poly]
    sombra = Image.new("RGBA", (mw, mh), (0, 0, 0, 0)); ImageDraw.Draw(sombra).polygon(pts, fill=a + (160,))
    base = Image.alpha_composite(base, sombra.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(base)
    d.polygon(pts, fill=(14, 10, 34, 240), outline=a + (255,))
    d.line(pts + [pts[0]], fill=a + (255,), width=5)
    for k in range(7):  # cayos
        x = 0.74 - k * 0.055; y = 0.90 + k * 0.012
        d.ellipse((x * mw - 14, y * mh - 7, x * mw + 14, y * mh + 7), fill=(14, 10, 34, 240), outline=a + (255,), width=3)
    capas = [Capa(base, ox, oy, 0.05, "zoom", 0.6)]
    hay = bool(resaltar)
    nombres = list(REGIONES)
    for i, nom in enumerate(nombres):
        rx, ry = REGIONES[nom]; x, y = ox + rx * mw, oy + ry * mh
        on = nom in resaltar
        col = (255, 255, 255) if (on or not hay) else (150, 150, 175)
        f = fuente(F_BLACK if on else F_BOLD, 46 if on else 32)
        lab = capa_texto(nom, f, col, stroke=3)
        t0 = 0.5 + (i * 0.25 if not hay else 0.0)
        capas.append(Capa(lab, x + 16 - 30, y - lab.height / 2, t0, "izq"))
    def din(d, tt):
        for nom in nombres:
            rx, ry = REGIONES[nom]; x, y = ox + rx * mw, oy + ry * mh
            on = nom in resaltar
            r = 13 if on else 9
            d.ellipse((x - r, y - r, x + r, y + r), fill=(b if on else (a if not hay else (120, 120, 140))))
            if on and len(resaltar) <= 2:
                ph = (tt * 1.2) % 1.0
                rr = 18 + ph * 60
                c = tuple(int(v * (1 - ph)) for v in b)
                d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=c, width=5)
    return capas, din

# ------------------------------------------------------------------ composición por frame
def pegar(frame, capa, tt):
    p = (tt - capa.t0) / capa.dur
    if p <= 0: return
    e = ease(p)
    img, alpha = capa.img, capa.alpha
    x, y = capa.x, capa.y
    if p < 1:
        if capa.modo == "sube": y += int((1 - e) * 50)
        elif capa.modo == "izq": x -= int((1 - e) * 80)
        elif capa.modo == "zoom":
            s = 0.85 + 0.15 * e
            nw, nh = max(1, int(img.width * s)), max(1, int(img.height * s))
            x += (img.width - nw) // 2; y += (img.height - nh) // 2
            img = img.resize((nw, nh), Image.BILINEAR); alpha = img.getchannel("A")
        alpha = alpha.point(lambda v, e=e: int(v * e))
    frame.paste(img, (x, y), alpha)

def cabecera(h, P):
    f = fuente(F_BLACK, 40)
    w = int(f.getlength(h)) + 70
    im = caja(w, 74, fill=P["a"] + (255,), r=14)
    ImageDraw.Draw(im).text((35, 37), h, font=f, fill=(10, 4, 20), anchor="lm")
    return im

def subtitulo_img(texto):
    f = fuente(F_BOLD, 50)
    ls = envolver(texto, f, 1500)
    if len(ls) > 2:  # reduce para que quepa en 2 líneas
        f = fuente(F_BOLD, 42); ls = envolver(texto, f, 1600)
    lh = 64 if f.size == 50 else 56
    hh = lh * len(ls) + 36
    im = Image.new("RGBA", (W, hh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    wmax = max(f.getlength(l) for l in ls)
    d.rounded_rectangle(((W - wmax) / 2 - 30, 0, (W + wmax) / 2 + 30, hh), 18, fill=(0, 0, 0, 170))
    for i, l in enumerate(ls):
        d.text((W / 2, 18 + i * lh + lh / 2), l, font=f, fill=(255, 255, 255), anchor="mm")
    return im

def marca(P):
    im = Image.new("RGBA", (520, 80), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((500, 40), G.CANAL, font=fuente(F_BLACK, 38), fill=(255, 255, 255, 210), anchor="rm")
    d.ellipse((500 - fuente(F_BLACK, 38).getlength(G.CANAL) - 34, 30, 500 - fuente(F_BLACK, 38).getlength(G.CANAL) - 14, 50), fill=P["a"])
    return im

# ------------------------------------------------------------------ intro y cierre
def intro_capas(v, P):
    t1 = capa_texto(G.CANAL, fuente(F_BLACK, 150), (255, 255, 255), glow=P["a"], align="center")
    t2 = capa_texto(G.LEMA, fuente(F_SEMI, 44), P["b"], align="center")
    return [Capa(t1, (W - t1.width) / 2, 330, 0.05, "zoom", 0.5), Capa(t2, (W - t2.width) / 2, 330 + t1.height - 40, 0.45)]

def final_capas(P):
    c = []
    t = capa_texto("¡SUSCRÍBETE!", fuente(F_BLACK, 110), (255, 255, 255), glow=P["a"], align="center")
    c.append(Capa(t, (W - t.width) / 2, 90, 0.1, "zoom", 0.5))
    for i in range(2):  # huecos para elementos de pantalla final de YouTube
        bx = caja(720, 405, fill=(255, 255, 255, 18), borde=(P["a"] if i == 0 else P["b"]) + (200,), r=18, grosor=4)
        ImageDraw.Draw(bx).text((360, 202), "▶  SIGUIENTE VIDEO" if i == 0 else "▶  TE RECOMIENDO", font=fuente(F_BOLD, 40), fill=(255, 255, 255, 200), anchor="mm")
        c.append(Capa(bx, 180 + i * 840, 420, 0.4 + 0.2 * i, "zoom"))
    s = capa_texto("Canal no oficial · no afiliado a Rockstar Games", fuente(F_SEMI, 32), (200, 200, 215), align="center")
    c.append(Capa(s, (W - s.width) / 2, 900, 0.8))
    return c

# ------------------------------------------------------------------ construcción
def construir(v):
    P = PALETAS[v["paleta"]]
    os.makedirs(os.path.join(RAIZ, "videos"), exist_ok=True)
    tmp = os.path.join(AQUI, "tmp", v["id"]); os.makedirs(tmp, exist_ok=True)
    INTRO, FINAL = 2.6, 10.0
    # 1. voz y línea de tiempo
    voz = [np.zeros(int(INTRO * SR), np.float32)]
    t = INTRO; escenas = []; subs = []
    for e in v["escenas"]:
        ini = t; frases = []
        voz.append(np.zeros(int(0.35 * SR), np.float32)); t += 0.35
        for fr in e["voz"]:
            y = decir(fr)
            frases.append((t, t + len(y) / SR, fr))
            subs.append((t, t + len(y) / SR, fr))
            voz.append(y); t += len(y) / SR
            pausa = 0.28; voz.append(np.zeros(int(pausa * SR), np.float32)); t += pausa
        voz.append(np.zeros(int(0.45 * SR), np.float32)); t += 0.45
        escenas.append(dict(e, ini=ini, fin=t, frases=frases))
    voz.append(np.zeros(int(FINAL * SR), np.float32)); t += FINAL
    total = t
    vz = np.concatenate(voz)
    vz = vz / (np.max(np.abs(vz)) + 1e-9) * 0.9
    sf.write(os.path.join(tmp, "voz.wav"), vz, SR)
    sf.write(os.path.join(tmp, "musica.wav"), musica.pista(total + 0.5, semilla=int(v["id"])), SR)
    # 2. audio final: música con ducking bajo la voz y normalización a -14 LUFS (YouTube)
    audio = os.path.join(tmp, "mezcla.m4a")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(tmp, "voz.wav"), "-i", os.path.join(tmp, "musica.wav"),
        "-filter_complex",
        "[0:a]aformat=channel_layouts=stereo,asplit=2[v1][v2];[1:a]aformat=channel_layouts=stereo,volume=0.32[m];"
        "[m][v2]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[md];"
        "[v1]" + CADENA_VOZ[VOZ == "kokoro"] + "[vv];"
        "[vv][md]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]",
        "-map", "[out]", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", audio], check=True)
    # 3. fotogramas
    bgs = fondo_frames(v["paleta"])
    marca_img = marca(P)
    for e in escenas:
        e["capas"], e["din"] = visual_capas(e["vis"], P, e["fin"] - e["ini"])
        e["cab"] = cabecera(e["h"], P)
    sub_imgs = [(a0, a1, subtitulo_img(txt)) for a0, a1, txt in subs]
    intro = intro_capas(v, P); final = final_capas(P)
    nfr = int(total * FPS)
    salida = os.path.join(RAIZ, "videos", f"{v['id']}-{v['slug']}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", "-movflags", "+faststart", salida], stdin=subprocess.PIPE)
    si = 0
    for fi in range(nfr):
        tt = fi / FPS
        fr = Image.fromarray(bgs[fi % len(bgs)])
        if tt < INTRO:
            for c in intro: pegar(fr, c, tt)
            # fundido de entrada
        elif tt >= total - FINAL:
            for c in final: pegar(fr, c, tt - (total - FINAL))
        else:
            e = next((e for e in escenas if e["ini"] <= tt < e["fin"]), escenas[-1])
            lt = tt - e["ini"]
            # transición: barrido de salida en el último 0.25 s
            pegar(fr, Capa(e["cab"], 80, 60, 0.0, "izq", 0.35), lt)
            d = ImageDraw.Draw(fr)
            despues = e["vis"]["t"] == "mapa"
            if e["din"] and not despues: e["din"](d, lt)
            for c in e["capas"]: pegar(fr, c, lt)
            if e["din"] and despues and lt > 0.5: e["din"](ImageDraw.Draw(fr), lt)
            while si < len(sub_imgs) and sub_imgs[si][1] < tt: si += 1
            if si < len(sub_imgs) and sub_imgs[si][0] <= tt <= sub_imgs[si][1] + 0.28:
                s = sub_imgs[si][2]; fr.paste(s, (0, H - s.height - 70), s)
        fr.paste(marca_img, (W - 560, 50), marca_img)
        d = ImageDraw.Draw(fr)
        d.rectangle((0, H - 10, W * tt / total, H), fill=P["a"])
        arr = np.asarray(fr)
        # fundidos a negro al inicio y final, y destello suave en cambios de escena
        k = 1.0
        if tt < 0.4: k = tt / 0.4
        if tt > total - 0.6: k = max(0, (total - tt) / 0.6)
        for e in escenas:
            dt = tt - e["ini"]
            if 0 <= dt < 0.18: k = min(k, 0.55 + dt / 0.18 * 0.45)
        if k < 1: arr = (arr * k).astype(np.uint8)
        ff.stdin.write(arr.tobytes())
    ff.stdin.close(); ff.wait()
    # 4. subtítulos SRT
    os.makedirs(os.path.join(RAIZ, "subtitulos"), exist_ok=True)
    def ts(x):
        ms = int(round(x * 1000)); return f"{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}"
    with open(os.path.join(RAIZ, "subtitulos", f"{v['id']}-{v['slug']}.es.srt"), "w", encoding="utf-8") as f:
        for i, (a0, a1, txt) in enumerate(subs, 1):
            f.write(f"{i}\n{ts(a0)} --> {ts(a1 + 0.2)}\n{txt}\n\n")
    json.dump([dict(h=e["h"], ini=e["ini"]) for e in escenas] + [dict(total=total)],
              open(os.path.join(tmp, "capitulos.json"), "w"), ensure_ascii=False)
    return salida, total

# ------------------------------------------------------------------ miniatura
def miniatura(v):
    P = PALETAS[v["paleta"]]
    bg = Image.fromarray(fondo_frames(v["paleta"], n=1)[0]).resize((1280, 720), Image.LANCZOS)
    arr = (np.asarray(bg).astype(np.float32) * 1.5).clip(0, 255).astype(np.uint8)
    im = Image.fromarray(arr).convert("RGBA")
    l1, l2 = v["mini"]
    def grande(txt, col, maxw, size):
        f = fuente(F_BLACK, size)
        while f.getlength(txt) > maxw: f = fuente(F_BLACK, f.size - 4)
        return capa_texto(txt, f, col, stroke=10, glow=P["a"] if col == (255, 255, 255) else None)
    a = grande(l1, (255, 255, 255), 1180, 170)
    b = grande(l2, P["b"] if v["paleta"] != "cian" else (255, 225, 60), 1180, 190)
    im.alpha_composite(a, (int((1280 - a.width) / 2), 90))
    im.alpha_composite(b, (int((1280 - b.width) / 2), 90 + a.height - 70))
    d = ImageDraw.Draw(im)
    tag = "GTA 6"
    f = fuente(F_BLACK, 58); w = f.getlength(tag) + 50
    d.rounded_rectangle((40, 30, 40 + w, 110), 16, fill=P["a"])
    d.text((40 + w / 2, 70), tag, font=f, fill=(10, 4, 20), anchor="mm")
    os.makedirs(os.path.join(RAIZ, "miniaturas"), exist_ok=True)
    ruta = os.path.join(RAIZ, "miniaturas", f"{v['id']}-{v['slug']}.png")
    im.convert("RGB").save(ruta)
    return ruta

if __name__ == "__main__":
    ids = [a for a in sys.argv[1:] if not a.startswith("--")] or ["todos"]
    sel = G.VIDEOS if ids == ["todos"] else [v for v in G.VIDEOS if v["id"] in ids]
    for v in sel:
        print("miniatura", miniatura(v), flush=True)
        if "--solo-mini" in sys.argv: continue
        s, tot = construir(v)
        print("listo", s, f"{tot:.1f}s", flush=True)
