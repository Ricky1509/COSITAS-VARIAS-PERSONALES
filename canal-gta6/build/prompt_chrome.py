# -*- coding: utf-8 -*-
"""Genera los prompts para que Claude en Chrome rellene los borradores en YouTube Studio."""
import os, re
import guiones as G, shorts as S
import copiar_pegar as C  # reutiliza LISTAS, HORAS, ORDEN
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
desc = lambda md: re.search(r"## Descripción\n```\n(.*?)\n```", md, re.S).group(1)

REGLAS = """Estoy en YouTube Studio (canal PUNTO NEÓN). Ya subí los videos y están en Contenido como BORRADORES. Quiero que edites cada borrador tú, en el navegador, uno por uno, con los datos de abajo. Reglas:

- Para encontrar cada video, ve a Contenido y busca el borrador cuyo nombre de archivo coincida con "ARCHIVO" (el título provisional del borrador es el nombre del archivo). Pulsa "Editar borrador".
- Pantalla DETALLES:
  · Título: pega TÍTULO exactamente.
  · Descripción: pega DESCRIPCIÓN exactamente, con sus saltos de línea y emojis.
  · Listas de reproducción: marca la lista LISTA (ya existe; si no existe, créala con ese nombre y visibilidad Pública).
  · Público: "No, no es contenido creado para niños".
  · Pulsa "Mostrar más": Contenido alterado o sintético = Sí. Etiquetas: pega ETIQUETAS. Idioma del video: Español. Categoría: Videojuegos.
  · NO toques la miniatura ni los subtítulos: los subo yo.
- Pantalla ELEMENTOS DEL VIDEO:
  · Pantalla final: si ya configuraste otro video, usa "Importar desde video" y elige ese. Si es el primero: añade "Video > El más reciente" encima del recuadro izquierdo que dice SIGUIENTE VIDEO, "Video > Mejor para el espectador" encima del recuadro derecho que dice TE RECOMIENDO, y "Suscribirse" debajo del texto ¡SUSCRÍBETE! (todo en los últimos 10 segundos). Guarda.
  · NO añadas tarjetas ni subtítulos.
- Pantalla COMPROBACIONES: espera a que termine y continúa.
- Pantalla VISIBILIDAD: elige "Programar" y pon la FECHA Y HORA indicada (año 2026, noviembre, hora local de la cuenta). Pulsa "Programar".
- Si algo no coincide con estas instrucciones, si un botón no existe o si YouTube muestra un aviso o error, PARA y pregúntame. No publiques nada como "Público" inmediato. No borres nada.
- Al terminar cada video dime "Video XX listo" y sigue con el siguiente. Al final dame un resumen con lo que quedó programado y cualquier problema.

"""

def bloque_video(vid):
    v = next(x for x in G.VIDEOS if x["id"] == vid)
    base = f"{v['id']}-{v['slug']}"
    md = open(os.path.join(RAIZ, "metadatos", base + ".md"), encoding="utf-8").read()
    dia, hora = C.HORAS[vid].split(" · ")
    num = dia.split()[-1]
    return (f"=============== VIDEO {vid} ===============\n"
            f"ARCHIVO: {base}.mp4\n"
            f"LISTA: {C.LISTAS[vid]}\n"
            f"FECHA Y HORA: {num} de noviembre de 2026, {hora}\n"
            f"TÍTULO:\n{v['titulo']}\n"
            f"DESCRIPCIÓN:\n<<<\n{desc(md)}\n>>>\n"
            f"ETIQUETAS:\n{', '.join(v['tags'])}\n\n")

def prompt_videos(ids, n):
    return (f"### PROMPT {n}\n\n```\n" + REGLAS +
            f"Edita estos {len(ids)} videos en este orden (la DESCRIPCIÓN va entre <<< y >>>; no pegues esos símbolos):\n\n" +
            "".join(bloque_video(i) for i in ids) + "```\n")

REGLAS_SHORTS = """Estoy en YouTube Studio (canal PUNTO NEÓN). Ya subí 5 Shorts y están en Contenido como BORRADORES (pestaña Shorts o Videos). Edita cada borrador tú, uno por uno:

- Búscalo por su nombre de archivo (ARCHIVO) y pulsa "Editar borrador".
- DETALLES: Título = TÍTULO. Descripción = DESCRIPCIÓN (entre <<< y >>>, sin esos símbolos). Público: "No, no es contenido creado para niños". En "Mostrar más": Contenido alterado o sintético = Sí; Etiquetas = ETIQUETAS; Idioma: Español; Categoría: Videojuegos. En "Video relacionado", si te deja, elige el video cuyo título empieza por VIDEO RELACIONADO; si no aparece, déjalo vacío y avísame.
- Lista: GTA 6: lo que tienes que saber (para todos).
- No añadas pantalla final (los Shorts no la usan).
- VISIBILIDAD: "Programar" con la FECHA Y HORA indicada (2026, hora local de la cuenta).
- Si algo no coincide o hay un aviso, PARA y pregúntame. No publiques nada al momento. No borres nada.
- Al terminar dime "Short SX listo" y al final dame un resumen.

"""

def prompt_shorts(n):
    o = [f"### PROMPT {n}\n\n```\n" + REGLAS_SHORTS]
    for sid in ["S1", "S2", "S4", "S3", "S5"]:
        s = next(x for x in S.SHORTS if x["id"] == sid)
        base = f"{s['id']}-{s['slug']}"
        md = open(os.path.join(RAIZ, "shorts", "metadatos", base + ".md"), encoding="utf-8").read()
        largo = next(x for x in G.VIDEOS if x["id"] == s["largo"])
        dia, hora = C.HS[sid].split(" · ") if hasattr(C, "HS") else ("", "")
        o.append(f"=============== SHORT {sid} ===============\nARCHIVO: {base}.mp4\n"
                 f"FECHA Y HORA: {dia.split()[-1]} de noviembre de 2026, {hora}\n"
                 f"VIDEO RELACIONADO: {largo['titulo']}\nTÍTULO:\n{s['titulo']}\n"
                 f"DESCRIPCIÓN:\n<<<\n{desc(md)}\n>>>\nETIQUETAS:\n{', '.join(s['tags'])}\n\n")
    o.append("```\n")
    return "".join(o)

A = C.ORDEN[:5]; B = C.ORDEN[5:]
doc = f"""# Prompts para Claude en Chrome

Úsalos en este orden. **Antes de cada prompt haz tú la parte de archivos**: la extensión no puede elegir archivos de tu ordenador.

## Antes de empezar (tú)
1. YouTube Studio › **Crear › Subir videos** › selecciona los **10 MP4** de `videos/` › cuando empiecen a subirse, **cierra** la ventana. Quedan como borradores.
2. Repite con los **5 MP4** de `shorts/`.
3. Comprueba que existen las dos listas (si no, el prompt las crea).

## Prompt 1 · Videos {", ".join(A)}
Pégalo entero en el panel de Claude en Chrome con YouTube Studio abierto en **Contenido**.

{prompt_videos(A, 1)}
## Prompt 2 · Videos {", ".join(B)}
Cuando termine el anterior, abre un chat nuevo en la extensión (icono de nuevo chat) y pega este.

{prompt_videos(B, 2)}
## Prompt 3 · Los 5 Shorts

{prompt_shorts(3)}
## Al final (tú, 10 minutos)
Para cada uno de los 10 videos: **Contenido › lápiz (Detalles)**:
- **Miniatura** › Subir archivo › `miniaturas/` el del mismo número › **Guardar**
- **Subtítulos** (menú izquierdo) › Añadir idioma Español › **Subir archivo › Con sincronización** › el `.srt` de `subtitulos/`

**Hazlo antes del miércoles 18 a las 18:00**, que es cuando sale el primero (01).
"""
open(os.path.join(RAIZ, "PROMPTS-CLAUDE-CHROME.md"), "w", encoding="utf-8").write(doc)
print(len(doc))
