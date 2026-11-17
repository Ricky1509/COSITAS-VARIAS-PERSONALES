# -*- coding: utf-8 -*-
"""Genera los gráficos del canal: avatar, banner y marca de agua."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFilter
import render as R
OUT = os.path.join(R.RAIZ, "canal"); os.makedirs(OUT, exist_ok=True)
P = R.PALETAS["rosa"]
bg = Image.fromarray(R.fondo_frames("rosa", n=1)[0])
bgb = Image.fromarray((np.asarray(bg).astype(np.float32) * 1.35).clip(0, 255).astype(np.uint8))

def logo(size):
    """Marca: círculo neón con un punto central (el 'punto' de PUNTO NEÓN)."""
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((s*0.08, s*0.08, s*0.92, s*0.92), outline=P["a"], width=int(s*0.07))
    d.ellipse((s*0.36, s*0.36, s*0.64, s*0.64), fill=P["b"])
    g = im.filter(ImageFilter.GaussianBlur(s*0.04))
    im = Image.alpha_composite(Image.alpha_composite(g, g), im)
    return im.resize((size, size), Image.LANCZOS)

# Avatar 800x800 (YouTube lo recorta en círculo)
av = bgb.crop((W0 := (1920-1080)//2, 0, W0+1080, 1080)).resize((800, 800), Image.LANCZOS).convert("RGBA")
av = Image.alpha_composite(av, Image.new("RGBA", av.size, (8, 2, 20, 120)))
av.alpha_composite(logo(520), (140, 140))  # sin texto: en el círculo pequeño no se leería
av.convert("RGB").save(os.path.join(OUT, "avatar-800x800.png"))

# Banner 2560x1440, todo lo importante dentro de la zona segura central 1546x423
ban = bgb.resize((2560, 1440), Image.LANCZOS).convert("RGBA")
cx, cy = 1280, 720
ban.alpha_composite(logo(300), (cx - 760, cy - 150))
t1 = R.capa_texto("PUNTO NEÓN", R.fuente(R.F_BLACK, 170), (255, 255, 255), glow=P["a"], stroke=5)
ban.alpha_composite(t1, (cx - 430, cy - 175))
t2 = R.capa_texto("GTA 6 · NOTICIAS · GUÍAS · TRUCOS", R.fuente(R.F_BLACK, 62), P["b"], stroke=3)
ban.alpha_composite(t2, (cx - 430, cy + 20))
t3 = R.capa_texto("Videos nuevos cada día", R.fuente(R.F_SEMI, 44), (235, 235, 245), stroke=2)
ban.alpha_composite(t3, (cx - 430, cy + 110))
ban.convert("RGB").save(os.path.join(OUT, "banner-2560x1440.png"), optimize=True)
# Vista previa con la zona segura marcada (solo para revisar)
pv = ban.copy(); d = ImageDraw.Draw(pv)
d.rectangle((cx-773, cy-211, cx+773, cy+211), outline=(255, 255, 0), width=6)
pv.convert("RGB").resize((1280, 720)).save(os.path.join(R.AQUI, "tmp", "banner-zona-segura.png"))

# Marca de agua 150x150 (PNG transparente)
logo(150).save(os.path.join(OUT, "marca-de-agua-150x150.png"))
print("ok", os.listdir(OUT))
