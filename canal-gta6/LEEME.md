# Canal GTA 6: PUNTO NEÓN

10 videos listos para subir el jueves 19 de noviembre de 2026, día de salida de GTA 6.

## Qué hay en esta carpeta

| Carpeta | Contenido |
|---|---|
| `videos/` | 10 MP4 en 1080p a 30 fps, H.264 + AAC, audio normalizado a -14 LUFS (el estándar de YouTube) |
| `miniaturas/` | 10 PNG de 1280x720 |
| `subtitulos/` | 10 `.srt` en español: súbelos en YouTube como subtítulos (los videos ya llevan subtítulos incrustados, estos son para buscadores y accesibilidad) |
| `metadatos/` | título, descripción con capítulos, etiquetas y guion de cada video |
| `GUIONES-Y-METADATOS.md` | todo lo anterior en un solo documento |
| `build/` | el código que lo genera todo; cambia un guion en `build/guiones.py` y ejecuta `python3 render.py 04` |

Los últimos 10 segundos de cada video son la pantalla final: hay dos huecos para colocar ahí los elementos de pantalla final de YouTube (siguiente video y video recomendado).

## Qué busca la gente (y por qué estos 10)

Las búsquedas que se disparan el día de salida de un juego así son prácticas: **hora**, **peso**, **precio y edición**, **PC**, **qué consola**, y a continuación los temas del juego (**mapa**, **personajes**) y la nostalgia (**historia de la saga**). Los 10 videos cubren exactamente eso, y ninguno depende de haber jugado, así que se pueden subir el primer día sin riesgo de decir algo falso sobre la partida.

## Orden de subida recomendado (jueves 19)

Lo ideal es que **01 y 03 salgan el miércoles 18 por la tarde**: son las búsquedas de "¿a qué hora sale?" y "¿cuánto pesa?", y se hacen *antes* de la medianoche. Si tienen que ser el jueves, súbelos los primeros, a primera hora.

| Hora (local) | Video | Por qué |
|---|---|---|
| 00:00 (o el miércoles por la tarde) | 01 ¿A qué hora sale? | pico de búsquedas justo antes del desbloqueo |
| 00:00 | 03 ¿Cuánto pesa? | la gente se queda sin espacio al instalar |
| 08:00 | 04 Estándar o Ultimate | quien compra por la mañana |
| 08:00 | 05 ¿GTA 6 en PC? | gran volumen, poca información oficial |
| 12:00 | 02 Todo lo que sabemos | para quien no ha seguido las noticias |
| 12:00 | 08 ¿Qué consola? | quien duda si comprar consola |
| 16:00 | 09 10 cosas antes de jugar | antes de la primera sesión larga |
| 18:00 | 06 El mapa de Leonida | cuando la gente ya está jugando |
| 20:00 | 07 Jason y Lucía | ídem |
| 22:00 | 10 Historia de la saga | nostalgia, larga duración |

Programa todos con "Programar" en YouTube Studio para no tener que estar despierto.

## Antes de publicar: comprueba esto

Los datos se verificaron el 17 de noviembre de 2026, pero algunos vienen de reportes y no de Rockstar:

- **Precio de la Ultimate (99,99 $) y que sea solo digital**: lo dan varios medios, sin confirmación oficial clara.
- **30 FPS y versión mejorada para PS5 Pro**: son reportes. El guion ya lo dice así ("según los reportes").
- **Horario de Xbox y de la nube**: las fuentes no coinciden. El video 01 manda a mirar la ficha de la tienda.
- Si Rockstar anuncia algo nuevo (fecha de PC, online), el video 05 se queda viejo: cambia el guion y vuelve a renderizar.

## Derechos y monetización

- **No se ha usado ni una imagen, logo, tráiler ni música de Rockstar.** Fondos, mapa, siluetas y música son originales y están generados por código. Así no hay reclamaciones de Content ID.
- El mapa de Leonida es un **esquema propio**; las posiciones de las regiones son aproximadas.
- La voz es una voz sintética (Kokoro "Dora" `ef_dora`, licencia Apache 2.0, uso comercial permitido). YouTube pide marcar **"contenido alterado o sintético"** solo cuando parece real y puede engañar; una voz en off de narración no suele requerirlo, pero si dudas, márcalo.
- En las descripciones va el aviso "canal no oficial".

## Fuentes

- Fecha, plataformas y retrasos: [GamesRadar](https://www.gamesradar.com/gta-6-guide/), [Variety](https://variety.com/2026/gaming/news/gta-6-release-details-1236846230/), [Yahoo Tech](https://tech.yahoo.com/gaming/articles/gta-6-releases-week-heres-110332150.html)
- Precio, tamaño y precarga: [Techloy](https://www.techloy.com/gta-6-preorder-prices-editions/), [GamingBible](https://www.gamingbible.com/news/gta-6-release-time-preload-download-size-editions-385283-20261012), [IBTimes](https://www.ibtimes.co.uk/gta-6-release-date-price-storage-console-launch-1831921)
- Horario por región: [TechTimes](https://www.techtimes.com/articles/330648/20261113/gta-6-release-time-west-coast-players-may-start-9-pm-wednesday-not-midnight-thursday.htm), [Keymap](https://keymap.io/releases/gta-6/)
- Regiones del mapa: [PCGamesN](https://www.pcgamesn.com/grand-theft-auto-6/map), [Screen Rant](https://screenrant.com/gta-6-full-map-reveal-regions/)
- Preguntas más buscadas: [Omelete](https://www.omelete.com.br/gta-6/gta-6-pesquisas-sobre-o-game-no-brasil-dobraram-em-24-horas), [Driffle](https://driffle.com/blog/100-most-asked-gta-6-questions-answered-check-full-list/)

## Regenerar videos (opcional)

Los modelos de voz no están en el repositorio (pesan casi 1 GB). Para volver a generar un video:

```bash
pip install sherpa-onnx==1.12.40 soundfile scipy numpy pillow
cd canal-gta6/build && mkdir -p voces && cd voces
curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-multi-lang-v1_0.tar.bz2
tar xjf kokoro-multi-lang-v1_0.tar.bz2 && cd ..
python3 render.py 04        # un video largo
python3 shorts.py S2        # un Short
python3 metadatos.py        # recalcula descripciones y capítulos
```
Hace falta `ffmpeg` instalado.
