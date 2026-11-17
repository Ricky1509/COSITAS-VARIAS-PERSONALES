# -*- coding: utf-8 -*-
"""Genera PROMPT-UNICO-CLAUDE-CHROME.txt y las versiones HTML (con botón Copiar)."""
import io, contextlib, os, re, html
with contextlib.redirect_stdout(io.StringIO()):
    import prompt_chrome as P
RAIZ = P.RAIZ

def unico():
    v = "".join(P.bloque_video(i) for i in P.C.ORDEN)
    s = P.prompt_shorts(3); shorts = s[s.index("=============== SHORT"):].rsplit("```", 1)[0]
    reglas_s = ("REGLAS PARA LOS SHORTS (después de los 10 videos):\n"
        "- Búscalos en Contenido > pestaña Shorts (o Videos) por su ARCHIVO y pulsa \"Editar borrador\".\n"
        "- Título, Descripción (sin <<< >>>), Público \"No es para niños\", en \"Mostrar más\": Contenido alterado = Sí, Etiquetas, Idioma Español, Categoría Videojuegos.\n"
        "- \"Video relacionado\": elige el video cuyo título empieza por VIDEO RELACIONADO; si no aparece, déjalo vacío y avísame al final.\n"
        "- Lista: GTA 6: lo que tienes que saber. Sin pantalla final.\n- Visibilidad: Programar con su FECHA Y HORA.\n\n")
    return (P.REGLAS + "PRIMERO edita estos 10 videos en este orden (la DESCRIPCIÓN va entre <<< y >>>; no pegues esos símbolos):\n\n"
            + v + reglas_s + shorts.rstrip() +
            "\n\nCuando termines todo, dame una tabla resumen: video/short, título, fecha y hora programada, y cualquier cosa que no hayas podido hacer.")

def a_html(md, titulo, etiqueta="Copiar"):
    out = []; n = 0; L = md.split("\n"); i = 0
    inl = lambda t: re.sub(r"`(.+?)`", r"<code>\1</code>", re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html.escape(t)))
    while i < len(L):
        l = L[i]
        if l.startswith("```"):
            j = i + 1; buf = []
            while not L[j].startswith("```"): buf.append(L[j]); j += 1
            n += 1; out.append(f'<div class="c"><button onclick="cp({n},this)">{etiqueta}</button><pre id="c{n}">{html.escape(chr(10).join(buf))}</pre></div>'); i = j + 1; continue
        if l.startswith("|"):
            filas = []
            while i < len(L) and L[i].startswith("|"):
                if not re.match(r"^\|[-| ]+\|$", L[i]): filas.append([c.strip() for c in L[i].strip("|").split("|")])
                i += 1
            out.append("<table>" + "".join("<tr>" + "".join(f"<td>{inl(c)}</td>" for c in f) + "</tr>" for f in filas if any(f)) + "</table>"); continue
        if l.startswith("# "): out.append(f"<h1>{inl(l[2:])}</h1>")
        elif l.startswith("### "): pass
        elif l.startswith("## "): out.append(f"<h2>{inl(l[3:])}</h2>")
        elif l.strip() == "---": out.append("<hr>")
        elif l.strip(): out.append(f"<p>{inl(l)}</p>")
        i += 1
    return f'''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{titulo}</title><style>
body{{font-family:system-ui,sans-serif;background:#120a1c;color:#eee;max-width:900px;margin:0 auto;padding:24px;line-height:1.45}}
h1{{color:#ff40a0;border-bottom:2px solid #ff40a0;padding-bottom:6px;margin-top:40px}} h2{{color:#3ce6ff;margin-top:34px}}
table{{border-collapse:collapse;margin:8px 0}} td{{border:1px solid #3a2a50;padding:6px 10px}} code{{background:#2a1c3c;padding:1px 5px;border-radius:4px}}
.c{{position:relative;margin:6px 0 16px}} pre{{background:#1e1430;border:1px solid #3a2a50;border-radius:10px;padding:14px 120px 14px 14px;white-space:pre-wrap;word-break:break-word;margin:0;font-size:14px;max-height:420px;overflow:auto}}
button{{position:absolute;top:8px;right:8px;background:#ff40a0;color:#120a1c;border:0;border-radius:8px;padding:8px 14px;font-weight:700;cursor:pointer}} button.ok{{background:#46ffaa}} hr{{border:0;border-top:1px dashed #3a2a50;margin:30px 0}}
</style></head><body>{"".join(out)}<script>function cp(n,b){{const t=b.textContent;navigator.clipboard.writeText(document.getElementById("c"+n).innerText).then(()=>{{b.textContent="¡Copiado!";b.classList.add("ok");setTimeout(()=>{{b.textContent=t;b.classList.remove("ok")}},1500)}})}}</script></body></html>'''

txt = unico()
open(os.path.join(RAIZ, "PROMPT-UNICO-CLAUDE-CHROME.txt"), "w", encoding="utf-8").write(txt)
for nombre, tit, et in [("COPIAR-Y-PEGAR", "PUNTO NEÓN · Copiar y pegar", "Copiar"), ("PROMPTS-CLAUDE-CHROME", "Prompts para Claude en Chrome", "Copiar prompt")]:
    md = open(os.path.join(RAIZ, nombre + ".md"), encoding="utf-8").read()
    if nombre == "PROMPTS-CLAUDE-CHROME":
        md = "# Prompt único (todo de una vez)\n\nSube antes los 10 videos y los 5 Shorts como borradores. Luego copia esto en Claude en Chrome con YouTube Studio abierto en Contenido.\n\n```\n" + txt + "\n```\n\n---\n\n" + md
    open(os.path.join(RAIZ, nombre + ".html"), "w", encoding="utf-8").write(a_html(md, tit, et))
print(len(txt))
