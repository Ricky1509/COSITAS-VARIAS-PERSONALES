# -*- coding: utf-8 -*-
"""Genera COPIAR-Y-PEGAR.md: cada campo de YouTube en su propio bloque."""
import os, re, json
import guiones as G
import shorts as S
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)

def bloque(t): return "```\n" + t.strip() + "\n```\n"
def desc_de(md):
    return re.search(r"## Descripción\n```\n(.*?)\n```", md, re.S).group(1)

LISTA_A = "GTA 6: lo que tienes que saber"
LISTA_B = "GTA 6: historia, mapa y personajes"
LISTAS = {**{k: LISTA_A for k in ["01","02","03","04","05","08","09"]}, **{k: LISTA_B for k in ["06","07","10"]}}
HORAS = {"01":"Miércoles 18 · 18:00","03":"Miércoles 18 · 19:00","04":"Jueves 19 · 08:00","05":"Jueves 19 · 09:00",
         "02":"Jueves 19 · 12:00","08":"Jueves 19 · 13:00","09":"Jueves 19 · 16:00","06":"Jueves 19 · 18:00",
         "07":"Jueves 19 · 20:00","10":"Jueves 19 · 22:00"}
ORDEN = ["01","03","04","05","02","08","09","06","07","10"]
COMENTARIO = {
 "01":"¿A qué hora vas a empezar a jugar? 👇 ¿Medianoche o mañana?",
 "02":"¿Qué es lo que más ganas tienes de hacer en GTA 6? 👇",
 "03":"¿Cuánto espacio libre te queda en la consola? 😅👇",
 "04":"¿Estándar o Ultimate? ¿Cuál compraste? 👇",
 "05":"¿Juegas en consola o estás esperando la versión de PC? 👇",
 "06":"¿Qué región vas a explorar primero? 🗺️👇",
 "07":"¿Jason o Lucía? 👇",
 "08":"¿En qué consola vas a jugar GTA 6? 👇",
 "09":"¿Qué consejo añadirías tú? 👇",
 "10":"¿Cuál ha sido tu GTA favorito hasta hoy? 👇",
}

o = ["# PUNTO NEÓN · Todo para copiar y pegar\n",
     "Cada recuadro gris es un campo de YouTube: copia el contenido entero y pégalo tal cual.\n"]
o += ["\n---\n\n# PARTE 1 · El canal\n",
      "## Nombre del canal\n", bloque("PUNTO NEÓN"),
      "## Identificador (@) · prueba en este orden\n", bloque("puntoneon"), bloque("puntoneongta"), bloque("puntoneon6"),
      "## Descripción del canal\n", bloque("""Todo sobre GTA 6 en español: noticias, guías, trucos, secretos y explicaciones de Leonida y Vice City.

🎮 Guías nuevas cada día desde el lanzamiento (19 de noviembre de 2026).
🗺️ Mapa, misiones, dinero, coches, easter eggs y todo lo que necesitas para jugar mejor.
🔔 Suscríbete y activa la campanita para no perderte nada.

Canal no oficial. No afiliado a Rockstar Games ni a Take-Two Interactive."""),
      "## Palabras clave del canal\n", bloque("GTA 6, GTA VI, Grand Theft Auto 6, GTA 6 español, guía GTA 6, trucos GTA 6, Leonida, Vice City, Jason y Lucía, noticias GTA 6"),
      "## Imágenes del canal (archivos)\n",
      "| Campo | Archivo |\n|---|---|\n| Foto | `canal/avatar-800x800.png` |\n| Banner | `canal/banner-2560x1440.png` |\n| Marca de agua | `canal/marca-de-agua-150x150.png` |\n",
      "## Listas de reproducción\n",
      f"**Lista 1 · nombre**\n", bloque(LISTA_A),
      "**Lista 1 · descripción**\n", bloque("Hora de salida, peso, precio, PC, consolas y consejos: todo lo práctico para empezar a jugar GTA 6."),
      f"**Lista 2 · nombre**\n", bloque(LISTA_B),
      "**Lista 2 · descripción**\n", bloque("El mapa de Leonida, Jason y Lucía, y la historia de la saga Grand Theft Auto."),
      "## Enlaces del canal (opcional)\n", "**Título del enlace**\n", bloque("Suscríbete"),
      "**URL** (cambia `puntoneon` si tu @ es otro)\n", bloque("https://www.youtube.com/@puntoneon?sub_confirmation=1"),
]
o.append("\n---\n\n# PARTE 2 · Los 10 videos (en orden de subida)\n")
for vid in ORDEN:
    v = next(x for x in G.VIDEOS if x["id"] == vid)
    base = f"{v['id']}-{v['slug']}"
    md = open(os.path.join(RAIZ, "metadatos", base + ".md"), encoding="utf-8").read()
    o += [f"\n## Video {v['id']}\n",
          f"| | |\n|---|---|\n| Archivo de video | `videos/{base}.mp4` |\n| Miniatura | `miniaturas/{base}.png` |\n"
          f"| Subtítulos | `subtitulos/{base}.es.srt` |\n| Lista | {LISTAS[vid]} |\n| Programar | **{HORAS[vid]}** |\n\n",
          "**Título**\n", bloque(v["titulo"]),
          "**Descripción**\n", bloque(desc_de(md)),
          "**Etiquetas**\n", bloque(", ".join(v["tags"])),
          "**Comentario para fijar** (publícalo tú cuando salga el video y fíjalo)\n", bloque(COMENTARIO[vid])]
o.append("\n---\n\n# PARTE 3 · Los 5 Shorts\n")
HS = {"S1":"Miércoles 18 · 20:00","S2":"Miércoles 18 · 21:00","S4":"Jueves 19 · 10:00","S3":"Jueves 19 · 14:00","S5":"Jueves 19 · 19:00"}
for sid in ["S1","S2","S4","S3","S5"]:
    s = next(x for x in S.SHORTS if x["id"] == sid)
    base = f"{s['id']}-{s['slug']}"
    md = open(os.path.join(RAIZ, "shorts", "metadatos", base + ".md"), encoding="utf-8").read()
    largo = next(x for x in G.VIDEOS if x["id"] == s["largo"])
    o += [f"\n## Short {sid}\n",
          f"| | |\n|---|---|\n| Archivo | `shorts/{base}.mp4` |\n| Video relacionado | {largo['id']} · {largo['titulo']} |\n| Programar | **{HS[sid]}** |\n\n",
          "**Título**\n", bloque(s["titulo"]),
          "**Descripción**\n", bloque(desc_de(md)),
          "**Etiquetas**\n", bloque(", ".join(s["tags"]))]
open(os.path.join(RAIZ, "COPIAR-Y-PEGAR.md"), "w", encoding="utf-8").write("".join(o))
print("ok")
