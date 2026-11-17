# -*- coding: utf-8 -*-
"""Shorts verticales 1080x1920 (menos de 60 s) con guion propio.

Uso: python3 shorts.py            (todos)   |   python3 shorts.py S1 S3
Reutiliza voz, música, fuentes y fondo de render.py.
"""
import os, sys, json, subprocess
import numpy as np
from PIL import Image, ImageDraw
import soundfile as sf
import render as R
import musica

SW, SH, FPS, SR = 1080, 1920, 30, R.SR

SHORTS = [
 dict(id="S1", slug="hora-gta6", paleta="rosa", largo="01",
  titulo="¿A qué hora sale GTA 6 en tu país? ⏰ #GTA6 #Shorts",
  tags=["gta 6","gta 6 hora","a que hora sale gta 6","gta 6 shorts"],
  escenas=[
   dict(vis=("numero", "00:00", "hora local · 19 de noviembre"),
        voz=["¿A qué hora sale GTA seis?", "A la medianoche, hora local, del diecinueve de noviembre."]),
   dict(vis=("lista", ["España · 00:00", "México · 00:00", "Argentina · 00:00", "Colombia · 00:00", "Chile · 00:00"]),
        voz=["En España y en toda Latinoamérica, a las doce de la noche del dieciocho al diecinueve."]),
   dict(vis=("numero", "21:00", "costa oeste de EE. UU. · miércoles 18"),
        voz=["Y en Estados Unidos abre a la vez en todo el país.", "En la costa oeste, desde las nueve de la noche del miércoles."]),
   dict(vis=("titulo", "¿NO TE ABRE?", "Ajustes › Restaurar licencias"),
        voz=["¿Llega la hora y no te abre? En PlayStation, restaura las licencias.", "Te lo explico entero en el video del canal."]),
  ]),
 dict(id="S2", slug="cuanto-pesa", paleta="cian", largo="03",
  titulo="¿Te cabe GTA 6? 212 GB 😳 #GTA6 #Shorts",
  tags=["gta 6 peso","cuanto pesa gta 6","gta 6 gb","gta 6 shorts"],
  escenas=[
   dict(vis=("numero", "212 GB", "lo que puede ocupar GTA 6"),
        voz=["GTA seis puede ocupar hasta doscientos doce gigas.", "¿Te cabe en la consola?"]),
   dict(vis=("lista", ["PS5 · 667 GB libres", "PS5 Slim · 848 GB", "Series X · 802 GB", "Series S · 364 GB"]),
        voz=["Esto es lo que queda libre de fábrica en cada consola.", "En la Series S, GTA seis se come más de la mitad."]),
   dict(vis=("lista", ["Borra juegos viejos", "Limpia capturas y clips", "Deja 50–100 GB extra"]),
        voz=["Borra lo que no juegues, limpia tus capturas, y deja espacio extra para el parche del día uno."]),
   dict(vis=("titulo", "SÍGUEME", "más guías de GTA 6"),
        voz=["Sígueme para más guías de GTA seis."]),
  ]),
 dict(id="S3", slug="gta6-pc", paleta="verde", largo="05",
  titulo="¿GTA 6 sale en PC? La respuesta 💻 #GTA6 #Shorts",
  tags=["gta 6 pc","gta 6 pc fecha","gta 6 steam","gta 6 shorts"],
  escenas=[
   dict(vis=("numero", "NO", "GTA 6 no sale en PC el 19 de noviembre"),
        voz=["¿GTA seis sale en PC? No.", "Rockstar no ha dado ni fecha ni ventana para ordenador."]),
   dict(vis=("lista", ["GTA IV · +8 meses", "GTA V · +19 meses", "RDR 2 · +13 meses"]),
        voz=["Rockstar siempre lanza primero en consola.", "GTA cinco tardó más de año y medio en llegar a PC."]),
   dict(vis=("titulo", "¡CUIDADO!", "No existe descarga para PC"),
        voz=["Y ojo: cualquier web que te ofrezca GTA seis para PC es una estafa o un virus.", "Sígueme para no perderte la fecha real."]),
  ]),
 dict(id="S4", slug="estandar-o-ultimate", paleta="dorado", largo="04",
  titulo="GTA 6: ¿Estándar o Ultimate? 💰 #GTA6 #Shorts",
  tags=["gta 6 precio","gta 6 ultimate","gta 6 edicion","gta 6 shorts"],
  escenas=[
   dict(vis=("numero", "79,99 $", "Edición estándar"),
        voz=["¿Estándar o Ultimate?", "La estándar cuesta setenta y nueve con noventa y nueve dólares."]),
   dict(vis=("numero", "99,99 $", "Ultimate · según los reportes"),
        voz=["La Ultimate, según los reportes, veinte dólares más, con coches, armas y ropa extra."]),
   dict(vis=("titulo", "LA HISTORIA ES LA MISMA", "La estándar es suficiente"),
        voz=["Pero la historia es exactamente la misma.", "Si vas a por la campaña, con la estándar te sobra."]),
  ]),
 dict(id="S5", slug="regiones-leonida", paleta="cian", largo="06",
  titulo="Las 6 regiones de Leonida en GTA 6 🗺️ #GTA6 #Shorts",
  tags=["gta 6 mapa","leonida","vice city","gta 6 shorts"],
  escenas=[
   dict(vis=("titulo", "LEONIDA", "6 regiones confirmadas"),
        voz=["Estas son las seis regiones de Leonida, el mapa de GTA seis."]),
   dict(vis=("lista", ["Vice City · Miami", "Leonida Keys · los cayos", "Grassrivers · los Everglades"]),
        voz=["Vice City, que es Miami.", "Los cayos de Leonida.", "Y Grassrivers, los pantanos de los Everglades."]),
   dict(vis=("lista", ["Port Gellhorn · la costa olvidada", "Ambrosia · el interior", "Mount Kalaga · parque nacional"]),
        voz=["Port Gellhorn, la costa olvidada.", "Ambrosia, el interior rural e industrial.", "Y el parque nacional de Mount Kalaga."]),
   dict(vis=("titulo", "¿CUÁL EXPLORAS PRIMERO?", "Dímelo en comentarios"),
        voz=["¿Cuál vas a explorar primero?"]),
  ]),
]

def fuente(p, s): return R.fuente(p, s)

def capas_vis(vis, P, dur):
    tipo = vis[0]; a, b = P["a"], P["b"]; capas = []; cy = 760
    if tipo in ("numero", "titulo"):
        big = vis[1]
        f = fuente(R.F_BLACK, 230 if tipo == "numero" else 130)
        im = R.capa_texto(big, f, (255, 255, 255), ancho=960, glow=a, align="center", stroke=4)
        if im.width > SW:
            im = im.resize((SW, int(im.height * SW / im.width)))
        capas.append(R.Capa(im, (SW - im.width) / 2, cy - im.height / 2 - 40, 0.1, "zoom", 0.5))
        s = R.capa_texto(vis[2], fuente(R.F_BOLD, 54), b, ancho=920, align="center", stroke=3)
        capas.append(R.Capa(s, (SW - s.width) / 2, cy + im.height / 2 - 50, 0.5))
    elif tipo == "lista":
        items = vis[1]; n = len(items); alto = 130
        y0 = cy - n * alto / 2
        for i, (it, t0) in enumerate(zip(items, R.escalonar(n, dur, 0.25, 0.6))):
            bx = R.caja(960, alto - 22, fill=(12, 6, 30, 225), borde=a + (255,), r=22)
            d = ImageDraw.Draw(bx); d.rounded_rectangle((0, 0, 16, alto - 23), 8, fill=a)
            f = fuente(R.F_BOLD, 54)
            while f.getlength(it) > 880: f = fuente(R.F_BOLD, f.size - 2)
            d.text((44, (alto - 22) / 2), it, font=f, fill=(255, 255, 255), anchor="lm")
            capas.append(R.Capa(bx, (SW - 960) / 2, y0 + i * alto, t0, "izq"))
    return capas

def subt(texto):
    f = fuente(R.F_BLACK, 66)
    ls = R.envolver(texto, f, 900)
    lh = 84; hh = lh * len(ls) + 40
    im = Image.new("RGBA", (SW, hh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(ls):
        d.text((SW / 2, 20 + i * lh + lh / 2), l, font=f, fill=(255, 238, 90) if i == 0 else (255, 255, 255),
               anchor="mm", stroke_width=8, stroke_fill=(0, 0, 0))
    return im

def construir(s):
    P = R.PALETAS[s["paleta"]]
    tmp = os.path.join(R.AQUI, "tmp", s["id"]); os.makedirs(tmp, exist_ok=True)
    FIN = 2.2
    voz = [np.zeros(int(0.15 * SR), np.float32)]; t = 0.15; escenas = []; subs = []
    for e in s["escenas"]:
        ini = t
        for fr in e["voz"]:
            y = R.decir(fr); subs.append((t, t + len(y) / SR, fr))
            voz += [y, np.zeros(int(0.18 * SR), np.float32)]; t += len(y) / SR + 0.18
        voz.append(np.zeros(int(0.25 * SR), np.float32)); t += 0.25
        escenas.append(dict(e, ini=ini, fin=t))
    voz.append(np.zeros(int(FIN * SR), np.float32)); t += FIN; total = t
    assert total < 59.5, f"{s['id']} dura {total:.1f}s (los Shorts deben durar menos de 60 s)"
    vz = np.concatenate(voz); vz = vz / (np.max(np.abs(vz)) + 1e-9) * 0.9
    sf.write(os.path.join(tmp, "voz.wav"), vz, SR)
    sf.write(os.path.join(tmp, "musica.wav"), musica.pista(total + 0.5, semilla=int(s["id"][1]) + 20, bpm=104), SR)
    audio = os.path.join(tmp, "mezcla.m4a")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(tmp, "voz.wav"), "-i", os.path.join(tmp, "musica.wav"),
        "-filter_complex",
        "[0:a]aformat=channel_layouts=stereo,asplit=2[v1][v2];[1:a]aformat=channel_layouts=stereo,volume=0.38[m];"
        "[m][v2]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=300[md];"
        "[v1]" + R.CADENA_VOZ[R.VOZ == "kokoro"] + "[vv];"
        "[vv][md]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]",
        "-map", "[out]", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", audio], check=True)
    # fondo vertical: se reutiliza el generador con otras dimensiones
    R.W, R.H = SW, SH
    try: bgs = R.fondo_frames(s["paleta"])
    finally: R.W, R.H = 1920, 1080
    for e in escenas: e["capas"] = capas_vis(e["vis"], P, e["fin"] - e["ini"])
    sub_imgs = [(a0, a1, subt(x)) for a0, a1, x in subs]
    marca = R.capa_texto("● " + R.G.CANAL, fuente(R.F_BLACK, 46), (255, 255, 255), stroke=3, align="center")
    fin_t = R.capa_texto("SUSCRÍBETE", fuente(R.F_BLACK, 120), (255, 255, 255), glow=P["a"], align="center", stroke=4)
    fin_s = R.capa_texto(f"Video completo en el canal", fuente(R.F_BOLD, 52), P["b"], align="center", stroke=3)
    fin = [R.Capa(fin_t, (SW - fin_t.width) / 2, 620, 0.05, "zoom", 0.4), R.Capa(fin_s, (SW - fin_s.width) / 2, 620 + fin_t.height - 40, 0.3)]
    gancho = R.capa_texto("GTA 6", fuente(R.F_BLACK, 64), (10, 4, 20), align="center")
    os.makedirs(os.path.join(R.RAIZ, "shorts"), exist_ok=True)
    salida = os.path.join(R.RAIZ, "shorts", f"{s['id']}-{s['slug']}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{SW}x{SH}", "-r", str(FPS),
        "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", "-movflags", "+faststart", salida], stdin=subprocess.PIPE)
    si = 0
    for fi in range(int(total * FPS)):
        tt = fi / FPS
        fr = Image.fromarray(bgs[fi % len(bgs)])
        d = ImageDraw.Draw(fr)
        # etiqueta superior
        d.rounded_rectangle((SW / 2 - 130, 170, SW / 2 + 130, 260), 18, fill=P["a"])
        fr.paste(gancho, (int((SW - gancho.width) / 2), 215 - gancho.height // 2), gancho)
        fr.paste(marca, (int((SW - marca.width) / 2), 70), marca)
        if tt >= total - FIN:
            for c in fin: R.pegar(fr, c, tt - (total - FIN))
        else:
            e = next((e for e in escenas if e["ini"] <= tt < e["fin"]), escenas[-1])
            for c in e["capas"]: R.pegar(fr, c, tt - e["ini"])
            while si < len(sub_imgs) and sub_imgs[si][1] < tt: si += 1
            if si < len(sub_imgs) and sub_imgs[si][0] <= tt <= sub_imgs[si][1] + 0.18:
                im = sub_imgs[si][2]
                # pequeño "pop" al aparecer cada subtítulo
                p = R.ease((tt - sub_imgs[si][0]) / 0.15)
                if p < 1:
                    im = im.resize((max(1, int(im.width * (0.9 + 0.1 * p))), max(1, int(im.height * (0.9 + 0.1 * p)))))
                fr.paste(im, (int((SW - im.width) / 2), 1290), im)
        d = ImageDraw.Draw(fr)
        d.rectangle((0, 0, SW * tt / total, 12), fill=P["a"])
        arr = np.asarray(fr)
        for e in escenas:
            dt = tt - e["ini"]
            if 0 < dt < 0.15: arr = (arr * (0.6 + dt / 0.15 * 0.4)).astype(np.uint8)
        ff.stdin.write(arr.tobytes())
    ff.stdin.close(); ff.wait()
    # metadatos del Short
    largo = next(v for v in R.G.VIDEOS if v["id"] == s["largo"])
    md = (f"# {s['id']} · Short\n\n**Archivo:** `shorts/{s['id']}-{s['slug']}.mp4` ({total:.0f} s)\n\n"
          f"## Título\n{s['titulo']}\n\n## Descripción\n```\n" + R.G.DESCRIPCIONES_SHORTS[s['id']] +
          f"\n\n▶️ Video completo: «{largo['titulo']}» (enlázalo aquí cuando esté publicado)\n\n#GTA6 #GTAVI #Shorts\n```\n\n"
          f"## Video relacionado (campo \"Video relacionado\" de YouTube)\n{largo['id']} · {largo['titulo']}\n\n"
          f"## Etiquetas\n{', '.join(s['tags'])}\n")
    os.makedirs(os.path.join(R.RAIZ, "shorts", "metadatos"), exist_ok=True)
    open(os.path.join(R.RAIZ, "shorts", "metadatos", f"{s['id']}-{s['slug']}.md"), "w", encoding="utf-8").write(md)
    return salida, total

def solo_metadatos(s):
    """Reescribe la ficha .md sin volver a renderizar (usa la duración del MP4)."""
    import subprocess as sp
    f = os.path.join(R.RAIZ, "shorts", f"{s['id']}-{s['slug']}.mp4")
    tot = float(sp.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f],capture_output=True,text=True).stdout)
    largo = next(v for v in R.G.VIDEOS if v["id"] == s["largo"])
    md = (f"# {s['id']} · Short\n\n**Archivo:** `shorts/{s['id']}-{s['slug']}.mp4` ({tot:.0f} s)\n\n"
          f"## Título\n{s['titulo']}\n\n## Descripción\n```\n" + R.G.DESCRIPCIONES_SHORTS[s['id']] +
          f"\n\n▶️ Video completo en el canal: «{largo['titulo']}»\n\n🔔 Suscríbete a {R.G.CANAL} para más guías de GTA 6.\n\n#GTA6 #GTAVI #Shorts\n```\n\n"
          f"## Video relacionado (campo \"Video relacionado\" de YouTube)\n{largo['id']} · {largo['titulo']}\n\n"
          f"## Etiquetas\n{', '.join(s['tags'])}\n")
    open(os.path.join(R.RAIZ, "shorts", "metadatos", f"{s['id']}-{s['slug']}.md"), "w", encoding="utf-8").write(md)

if __name__ == "__main__":
    if "--metadatos" in sys.argv:
        for s in SHORTS: solo_metadatos(s)
        sys.exit()
    ids = sys.argv[1:]
    for s in SHORTS:
        if ids and s["id"] not in ids: continue
        out, tot = construir(s)
        print("listo", out, f"{tot:.1f}s", flush=True)
