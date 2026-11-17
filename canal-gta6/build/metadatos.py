# -*- coding: utf-8 -*-
"""Genera título, descripción con capítulos y etiquetas de cada video."""
import os, json
import guiones as G

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)

import re
PROPIOS = ["GTA", "PS5", "Pro", "PC", "Xbox", "Series", "S", "FPS", "Ultimate", "Lucía", "Jason", "Duval", "Caminos",
           "Leonida", "Vice", "City", "Keys", "Grassrivers", "Port", "Gellhorn", "Ambrosia", "Mount", "Kalaga"]
def cap(h):
    h = h.lower()
    for p in PROPIOS:
        h = re.sub(r"(?<!\w)" + p.lower() + r"(?!\w)", p, h)
    i = 1 if h[:1] in "¿¡" else 0
    return h[:i] + h[i:i+1].upper() + h[i+1:]

def mmss(x):
    x = int(x); return f"{x // 60}:{x % 60:02}"

def capitulos(caps):
    # YouTube: primer capítulo en 0:00, mínimo 3, cada uno de 10 s o más
    caps = caps[:-1]
    out = [(0.0, cap(caps[0]["h"]))]
    for c in caps[1:]:
        if c["ini"] - out[-1][0] >= 10: out.append((c["ini"], cap(c["h"])))
        else: out[-1] = (out[-1][0], out[-1][1] + " / " + cap(c["h"]))  # capítulo corto: se une al anterior
    return "\n".join(f"{mmss(t)} {h}" for t, h in out)

HASHTAG = {"01": "GTA6HoraDeSalida", "02": "GTA6Resumen", "03": "GTA6Peso", "04": "GTA6Precio", "05": "GTA6PC",
           "06": "GTA6Mapa", "07": "JasonYLucia", "08": "GTA6PS5", "09": "GTA6Consejos", "10": "HistoriaDeGTA"}
os.makedirs(os.path.join(RAIZ, "metadatos"), exist_ok=True)
todo = []
for v in G.VIDEOS:
    cj = os.path.join(AQUI, "tmp", v["id"], "capitulos.json")
    caps = json.load(open(cj, encoding="utf-8")) if os.path.exists(cj) else None
    resumen = G.DESCRIPCIONES[v["id"]]
    desc = f"""{resumen}

⏱️ CAPÍTULOS
{capitulos(caps) if caps else '(se generan al renderizar)'}

🔔 Suscríbete a {G.CANAL}: {G.LEMA[0].lower() + G.LEMA[1:]}. Guías nuevas cada día desde el lanzamiento.

⚠️ Canal no oficial. No estamos afiliados a Rockstar Games ni a Take-Two Interactive. GTA, Grand Theft Auto y Leonida son marcas de sus respectivos dueños. Datos a 17 de noviembre de 2026; lo que no es oficial se indica como "según los reportes".

#GTA6 #GTAVI #{HASHTAG[v['id']]}"""
    md = f"# {v['id']} · {v['titulo']}\n\n**Archivo:** `videos/{v['id']}-{v['slug']}.mp4`  \n**Miniatura:** `miniaturas/{v['id']}-{v['slug']}.png`  \n**Subtítulos:** `subtitulos/{v['id']}-{v['slug']}.es.srt`\n\n## Título\n{v['titulo']}\n\n## Descripción\n```\n{desc}\n```\n\n## Etiquetas\n{', '.join(v['tags'])}\n\n## Guion\n"
    for e in v["escenas"]:
        md += f"\n**[{e['h']}]**\n\n" + "\n".join("> " + f for f in e["voz"]) + "\n"
    open(os.path.join(RAIZ, "metadatos", f"{v['id']}-{v['slug']}.md"), "w", encoding="utf-8").write(md)
    todo.append(md)
open(os.path.join(RAIZ, "GUIONES-Y-METADATOS.md"), "w", encoding="utf-8").write("\n\n---\n\n".join(todo))
print("ok")
