# Bitlatro — Documentación técnica del código

Guía completa de cómo funciona `python/bitlatro.py`, pensada para que puedas **entenderlo y explicarlo** de principio a fin. Está ordenada de lo más general a lo más concreto: primero la arquitectura, luego cada subsistema, y al final un recorrido completo de "qué pasa cuando juegas una mano".

> **Versión 0.5.0 (8 oct 2026):** primera versión hecha con TIC-80 PRO, versión Python ordenada y comentada. El código ya no tiene que caber en un banco de 64 KB: está repartido en 25 secciones con un índice al principio del fichero, y los 30 jokers inventados se han quitado (quedan 93). Ver §18 Novedades.
>
> **Convención del proyecto:** indentación de 1 espacio, sin docstrings, comentarios en español sin tildes (el editor de TIC-80 solo muestra ASCII). Los nombres de las claves de `gs` y de las familias `F_*` son la columna vertebral de todo, así que conviene tenerlos a mano (hay un glosario al final).

---

## Índice

1. [Visión general y arquitectura](#1-visión-general-y-arquitectura)
2. [El bucle principal `TIC()` y la máquina de estados](#2-el-bucle-principal-tic-y-la-máquina-de-estados)
3. [El estado global `gs`](#3-el-estado-global-gs)
4. [Dibujo de bajo nivel (fuente, paleta, cajas, botones)](#4-dibujo-de-bajo-nivel)
5. [Animación: `onda_y`, `shake_offset` y `counter`](#5-animación-onda_y-shake_offset-y-counter)
6. [Modelo de datos: `Carta`, `Joker`, `Planeta`, `Mazo`](#6-modelo-de-datos-carta-joker-planeta-mazo)
7. [Cartas, manos y niveles](#7-cartas-manos-y-niveles)
8. [El sistema de jokers: familias, `JDEFS`, `JSPR`, sticky](#8-el-sistema-de-jokers)
9. [El motor de puntuación por cola de eventos](#9-el-motor-de-puntuación-por-cola-de-eventos)
10. [Sistema de partículas y "shakes"](#10-sistema-de-partículas-y-shakes)
11. [Dibujo de cartas, jokers y consumibles en pantalla](#11-dibujo-de-cartas-jokers-y-consumibles-en-pantalla)
12. [Las seis pantallas](#12-las-seis-pantallas)
13. [Fin de ronda, scroll vertical y Cash Out](#125-fin-de-ronda-scroll-vertical-y-cash-out)
14. [La tienda](#126-la-tienda)
15. [Paquetes (Booster Packs)](#127-paquetes-booster-packs)
16. [Selección de joker/consumible: vender y usar](#128-selección-de-jokerconsumible-vender-y-usar)
17. [Código de prueba](#13-código-de-prueba)
18. [Recorrido completo de una mano (end-to-end)](#14-recorrido-completo-de-una-mano)
19. [Limitaciones y `#TODO`](#15-limitaciones-y-todo)
20. [Glosario rápido](#16-glosario-rápido)
21. [Compatibilidad con pocketpy y tamaño](#17-compatibilidad-con-pocketpy-y-tamaño)
22. [Novedades](#18-novedades)

---

## 1. Visión general y arquitectura

Bitlatro es un clon compacto de *Balatro* escrito en **Python para TIC-80** (intérprete pocketpy). TIC-80 llama 60 veces por segundo a una función `TIC()`, que es donde se dibuja y se procesa todo cada fotograma. No hay hilos ni temporizadores externos: **todo el tiempo se mide en fotogramas** (contadores que suben o bajan en cada `TIC()`).

La arquitectura tiene tres capas:

- **Capa de dibujo de bajo nivel**: una fuente de píxeles propia (`mini_font`), una función `draw_text` para escribir texto, funciones para manipular la paleta (`set_col`), y dibujar cajas y botones con sprites (`PrintBox`, `Boton`).
- **Capa de modelo y reglas**: las clases `Carta`, `Joker`, `Planeta`, `Mazo`; la detección de manos de póker; el **sistema de niveles de manos** (cada tipo sube de nivel con planetas); y sobre todo el **sistema de jokers** (las tablas `JDEFS`/`JSPR` y las "familias" `F_*`).
- **Capa de juego/pantallas**: seis pantallas (menú, juego, visor de mazo, tienda, selección de blind, game over) controladas por una máquina de estados, y un **motor de puntuación basado en una cola de eventos** que reproduce la animación de la puntuación paso a paso, igual que el Balatro original.

Todo el estado mutable vive en un único diccionario global llamado `gs` (*game state*). No hay clases de "partida": se modifica `gs` directamente desde cualquier función.

### Organización del fichero

El fichero empieza con un índice y un glosario de abreviaturas, y sigue este orden (cada sección abre con un bloque de comentario `# ====`):

- **Datos (1-7):** texto y color (`mini_font`), cartas (`SUITS`, `EFFECTS`, `DECK_INFO`), manos (`H_*`, `HAND_DEF`, `PLANETS`), jokers (`F_*` con la leyenda de parámetros de cada familia, `SC_*`, `JDEFS`, `JRAR`, `JPOOL`, `JSPR`), rondas y tienda (`ANTE_BASE`, `BLIND_*`, `PACK_DEF`), motor de eventos (`E_*`, `EDUR`, `PARTICLE_KINDS`) y el estado `gs`, con un comentario por clave.
- **Lógica (8-19):** animación, cajas y botones, modelo (`Carta`, `Joker`, `Planeta`, `Mazo`), reglas de mano, reglas de partida, cuándo actúan los jokers, qué hacen, partículas, motor de puntuación, fin de ronda y cash out, tienda y sobres, vender y usar.
- **Dibujo y pantallas (20-25):** textos de joker (`JVT`, `JBOX`), dibujo de cartas/jokers/planetas, tooltips, HUD, las seis pantallas y, al final, el arranque y `TIC()`.

Marcas en comentarios: `#DBG` (línea de prueba), `FIX:` (arreglo de un bug, explica cuál) y `#M` (joker real cuyo efecto aquí no es el de Balatro).

---

## 2. El bucle principal `TIC()` y la máquina de estados

`TIC()` (al final del fichero) es el punto de entrada que TIC-80 ejecuta cada fotograma:

```python
def TIC():
 gs["tt_target"] = None
 raton = mouse()
 gm = gs["gm"]
 if gm == 0:
  PantallaMenu(raton)
 elif gm == 1:
  PantallaJuego(raton)
 ...
 elif gm == 5:
  PantallaGameOver(raton)
 tt = gs["tt_target"]
 if tt:
  if tt[0] == "card":
   tt_card(tt[1], tt[2], tt[3])
  ...
 gs["Clk0"] = raton[2]
```

- `mouse()` devuelve `(x, y, pulsado_izquierdo, ...)`. Se guarda en `raton`.
- `gs["gm"]` es el **estado de pantalla** (game mode): `0` = menú, `1` = juego, `2` = visor, `3` = tienda, `4` = selección de blind, `5` = game over. Es una máquina de estados sencilla: cada valor enruta a una función de pantalla distinta.
- `gs["tt_target"]` se **resetea al inicio** y se **dibuja al final**. Las pantallas activas solo *almacenan* qué tooltip mostrar (en `print_cards`/`print_jokers`/`print_consumibles`) en vez de pintarlo al vuelo; así el tooltip queda por encima de todo lo que se haya dibujado en el fotograma. Hay tres tipos de tooltip: `"card"`, `"joker"` y `"planeta"`.
- `gs["Clk0"]` guarda **si el ratón estaba pulsado en el fotograma anterior**. Esto es clave: para detectar un "clic nuevo" se comprueba `raton[2] and not gs["Clk0"]` (está pulsado ahora pero no lo estaba antes = flanco de bajada → clic único). Sin esto, mantener pulsado el botón dispararía la acción 60 veces por segundo. **También se usa para detectar "soltar el ratón"** (`not raton[2] and gs["Clk0"]`), que es lo que cierra una operación de arrastre.

**Idea importante:** las funciones de pantalla hacen *render + lógica* en la misma pasada. No hay separación update/draw; se dibuja el botón y, justo después, se comprueba si se ha clicado.

---

## 3. El estado global `gs`

`gs` es el diccionario que contiene **toda** la partida. Agrupado por temas:

**Control de pantalla / input**
- `gm`: pantalla actual (0–5).
- `Clk0`: ratón pulsado el fotograma anterior (anti-repetición de clic).
- `visor_from`: pantalla desde la que se entró al visor (1 = juego, 3 = tienda). Al salir del visor se vuelve a esa pantalla.

**Menú**
- `DS`: índice de baraja seleccionada en el menú (0–7).
- `num1`, `num2`: sprites aleatorios para decorar el logo del menú.

**Recursos del jugador (la "cabecera" del juego)**
- `rs`: *round score*, la puntuación acumulada de la ronda.
- `hd`: manos restantes (*hands*).
- `ds`: descartes restantes (*discards*).
- `mn`: dinero (*money*).
- `ant`: *ante* actual.
- `rd`: *round* actual.
- `hs`: tamaño de mano (*hand size*) — **dinámico**, recalculado por `recalc_hs()` según los jokers equipados (Stuntman lo baja, Juggler lo sube).
- `jslots`: huecos de joker disponibles (`5` normal, `6` con baraja negra). Se fija al empezar partida con `joker_slots()`.

**Cartas y mazo**
- `baraja`: instancia de `Mazo`.
- `hand`: lista de `Carta` en la mano.
- `b`: las cartas **jugadas** en la mano actual (las que se están puntuando).
- `jokers`: lista de `Joker` equipados.
- `consu`: consumibles (instancias de `Planeta`). Máximo 2.

**Fase de puntuación (motor de eventos)**
- `fase_puntos`: `0` = interacción (seleccionar/jugar/descartar); `1` = animación de puntuación en curso; `2` = ronda ganada, **subiendo la pantalla** hacia el cash out; `3` = cash out fijo arriba, esperando clic para cobrar.
- `tot_chips`, `tot_mult`: acumuladores de fichas y multiplicador de la mano que se está puntuando.
- `scoring_cards`: las cartas que realmente puntúan (p. ej. solo la pareja, no las 5; o todas si Splash está activo).
- `nombre_mano`: nombre del tipo de mano detectado al jugar (`"PAIR"`, `"FLUSH HOUSE"`, etc.). Se usa solo para mostrar.
- `hand_idx_play`: **índice** (en `H_*`/`HAND_DEF`) del tipo de mano jugado. Se usa para consultar el nivel actual y mostrar `lvl N` debajo del nombre durante el scoring.
- `mano_flags`: lista de **12 booleanos** (uno por tipo de mano `H_*`) que indica qué tipos están presentes en la mano jugada. La usan los jokers tipo "si la mano contiene X".
- `ev_queue`, `ev_idx`, `ev_timer`: la **cola de eventos**, el índice del evento en curso y su temporizador en fotogramas.
- `active_joker_idx`: índice del joker que está "actuando" ahora mismo (para resaltarlo visualmente). `-1` = ninguno.
- `first_match`: diccionario `{joker_idx: card_idx}` para jokers que solo afectan a la **primera** carta que cumple (Photograph).

**Niveles de manos**
- `hl`: lista de 12 enteros con el **nivel actual** de cada tipo de mano (`hl[H_PAR]`, `hl[H_FUL]`, …). Empieza en `1` para todos. Sube con planetas.
- `hp`: lista de 12 booleanos que marca **qué tipos de mano se han jugado** alguna vez. Lo usa `roll_planeta_unique` para que ciertos planetas top-tier (Planet X, Ceres, Eris — las manos secretas) no aparezcan en la tienda hasta que descubras la mano correspondiente.

**Rondas / Cash Out**
- `blind`: blind actual de la ronda (`0` = small, `1` = big, `2` = boss).
- `voff`: *vertical offset* del scroll. `0` mientras juegas; sube hasta `SCREEN_H` (136) cuando ganas, arrastrando con él los elementos del "mundo" para que el cash out entre desde abajo.
- `co_wait`: contador de pausa antes de empezar a subir la pantalla (en frames). Permite que los jokers hagan sus animaciones de fin de ronda antes del scroll.
- `co_reward`, `co_hands`, `co_interest`, `co_disc`, `co_extra`, `co_total`: desglose del dinero a cobrar. `co_disc` solo se usa con la **baraja amarilla** (2 $ por mano + 1 $ por descarte, en vez de interés). `co_extra` agrupa todos los ingresos de jokers de fin de ronda (Golden Joker, Cloud 9, Delayed Gratification, etc.).
- `co_req`: puntos que se necesitaban para ganar la ronda (mostrado en el panel para referencia).

**Tienda**
- `shop_j`: lista de 2 slots de "compra principal". Cada slot es `[item, precio, vendido, tipo]` donde `tipo` es `0` para joker y `1` para planeta. Es decir, los slots de joker pueden contener planetas (25 % de probabilidad por slot al rerollear).
- `shop_p`: lista de 2 slots de **packs** (booster packs). Cada slot es `[k, precio, abierto]` con `k` el índice en `PACK_DEF`.
- `reroll`: coste actual del reroll. Empieza en `SHOP_BASE_REROLL` (5) y sube +1 por reroll.
- `free_rr`: rerolls gratis disponibles esta visita. Se pone a `1` si tienes algún joker `F_FREE_REROLL` (Chaos the Clown).
- `pack`: si hay un pack abierto, dict `{"k", "choices", "picks"}` con el tipo, las opciones que quedan y cuántas más puedes elegir. `None` cuando no hay pack abierto.

**Animación / feedback**
- `up`: desplazamiento vertical de subida de la zona de cartas/botones (animación de entrada).
- `particles`: lista de partículas activas (los números que vuelan: +chips, xmult, $, etc.).
- `shake_chips`, `shake_mult`, `shake_nombre`, `shake_money`: temporizadores de vibración de cada contador del HUD.

**Visor**
- `pal`: qué baraja mostrar en el visor (`"total"` o `"actual"`).
- `vc`, `vk`: caché del visor (datos calculados y su "clave") para no recalcular cada fotograma. `Mazo.repartir()` y `reset_round()` ponen `vk = None` para que se recalcule cuando cambian las cartas.

**Orden de mano y arrastre**
- `sort_mode`: `0` = ordenar por **rango** (A, K, Q, J, 10, …, 2), `1` = ordenar por **palo**. Lo cambia el botón Rango/Palo.
- `drag_card`, `drag_active`, `drag_px`, `drag_py`: estado del arrastre **de cartas** en la mano.
- `drag_joker`: análogo para **arrastrar jokers** y reordenarlos. Comparte los campos `drag_px`/`drag_py`/`drag_active` con el de cartas (no se pueden estar arrastrando los dos a la vez).

**Selección de joker/consumible (para vender/usar)**
- `sel_joker`: índice del joker seleccionado (`-1` = ninguno). Sobre el joker seleccionado aparece un botón `$N` para venderlo.
- `sel_consu`: índice del consumible seleccionado (`-1` = ninguno). Sobre el consumible seleccionado aparecen `$1` (vender) y `use` (usar el planeta).
- Selección y arrastre comparten el clic sobre el joker: si el ratón **no se mueve** más de 3 px tras pulsar, se considera selección (toggle); si se mueve, se considera arrastre.

**Tooltip diferido**
- `tt_target`: tupla con el tooltip a dibujar **al final del fotograma**. Formato `("card", carta, x, y)`, `("joker", joker, x, y)` o `("planeta", planeta, x, y)`. Se resetea a `None` al inicio de `TIC()`; las funciones de dibujo la rellenan cuando detectan hover; `TIC()` dibuja el tooltip justo antes de cerrar el fotograma.

---

## 4. Dibujo de bajo nivel

TIC-80 trae una fuente, pero aquí se usa una **fuente de píxeles propia** porque la del sistema es demasiado grande para los huecos del HUD.

- `mini_font`: diccionario `carácter → 5 filas de 3 píxeles` (cada fila es un string de `"0"`/`"1"`). Es una fuente de 3×5.
- `draw_text(txt, x, y, col)`: escribe una cadena pintando cada glifo píxel a píxel con `pix()`. Para ahorrar tokens, el dibujo de cada carácter se hace **inline** dentro del bucle (no hay una función `draw_char` separada como en versiones anteriores). Avanza 4 px por carácter (3 de glifo + 1 de separación).

**Paleta:**
- `set_col(slot, col)`: reasigna un color de la paleta de TIC-80 escribiendo en memoria con `poke4`. Truco para "teñir" sprites sin tener variantes de cada sprite (p. ej. cambiar el color 14 al 2 para pintar palos rojos).
- `reset_col()`: restaura los slots que se suelen tocar (6, 7, 14, 2) a su valor por defecto.

**Cajas y botones (estética Balatro):**
- `dibujar_caja(x, y, w, h, iner, bor, sombra)`: dibuja una caja redondeada de `w×h` celdas de 8 px con tiles de esquina (243/244), borde y relleno (227/228). Con `sombra=True` añade la línea de sombra inferior de los botones sin pulsar. La usan `PrintBox` y `Boton.pintar`.
- `PrintBox(col, x, y, w, h)`: caja decorativa (1 px más abajo de `y`). `col` indexa la paleta `Boton.paletas`, que define color interior y de borde.
- `Boton`: clase para botones clicables.
  - `__init__`: guarda texto, posición, tamaño y si está activo, y resuelve sus dos colores desde `Boton.paletas`.
  - `pintar()`: dibuja la caja con sprites; si está clicado o inactivo lo dibuja "hundido" (desplazado 1 px) para dar feedback. Devuelve si está siendo clicado.
  - `clicado()`: comprueba si el ratón está pulsado dentro del rectángulo del botón.

**Constantes de descripción:**
- `EFFECTS`: tupla con los nombres de efectos de carta (Bonus, Mult, Wild, Glass, Steel, Stone, Gold, Lucky). Indexada por `c.ef`.
- `SEAL_NAMES`: tupla con los nombres de sellos (Red, Blue, Gold, Purple). Indexada por `c.st`.
- `SEAL_COL`: pares `(color_interior, color_borde)` para cada sello. Reservada para el reskin del sprite de sello con palette swaps (sprite #60).

---

## 5. Animación: `onda_y`, `shake_offset` y `counter`

- `onda_y(an)`: devuelve un desplazamiento vertical suave (suma de dos senos con periodos distintos) en función del tiempo `time()` y de un desfase `an` propio de cada carta/joker/planeta. Esto hace que cada elemento "flote" con su propia fase, no todos a la vez.
- `shake_offset(fl, du, ax, ay, fr)`: **onda amortiguada** reutilizable para vibraciones. `fl` = fotogramas restantes, `du` = duración total, `ax`/`ay` = amplitud en X/Y, `fr` = frecuencia. Devuelve `(dx, dy)`. La amplitud decae conforme `fl` baja (factor `k = fl/du`), así que la vibración empieza fuerte y se apaga. La usan los contadores del HUD (chips/mult/dinero/nombre) cuando reciben un golpe.
- `counter(st, cur, end, inc, rep)`: utilidad para **interpolar un número** hacia un objetivo. Mueve `cur` hacia `end` en pasos de `inc`; si `rep` es cierto y ya llegó, reinicia a `st`. Se usa para animaciones cíclicas (ediciones foil/holo de las cartas) y para la subida `up`.

> Nota del proyecto: queda pendiente aplicar `shake_offset` también a las **cartas y jokers** en hover/clic (ahora solo lo usan los contadores del HUD). La función ya es genérica; solo falta añadir timers por carta/joker y llamarla en `print_cards`/`print_jokers` al detectar interacción.

---

## 6. Modelo de datos: `Carta`, `Joker`, `Planeta`, `Mazo`

### `Carta`
Representa una carta física.
- Campos principales: `su` (palo 0–3: picas, corazones, tréboles, diamantes), `va` (valor 1–13, donde 1 = As), `ef` (efecto/enhancement: índice en `EFFECTS`), `st` (sello/seal: índice en `SEAL_NAMES`), `ed` (edición: foil/holo), `bc` (*bonus chips*: fichas extra añadidas dinámicamente, p. ej. por Hiker).
- `an`: desfase aleatorio para la animación de flotación.
- `sel`: si está seleccionada por el jugador.
- `offset_eval`: desplazamiento vertical temporal durante la puntuación (el "bote" cuando la carta puntúa).
- `bk`: `1` si es una Glass que se ha roto; se quita del mazo al acabar la mano.
- El `__init__` también randomiza la edición concreta dentro de su rango si `ed` es 1 o 2 (foil anima de 1 a 5, holo de 49 a 53).

### `Joker`
Representa un joker equipado. **Es deliberadamente ligero**: casi toda la información del joker está en la tabla `JDEFS` (definición estática compartida); la instancia solo guarda el estado mutable.
- `id`: índice en `JDEFS` (define qué joker es y su comportamiento).
- `st`: estado acumulado (*state*). Lo usan los jokers "sticky" (Green Joker, Wee Joker…), los descendentes (Ice Cream guarda aquí las fichas que le quedan, Popcorn los puntos de mult restantes).
- `xm`: multiplicador mutable (Ramen empieza en 2.0 y baja; Vampire y Lucky Cat empiezan en 1.0 y suben).
- `sv`: valor de venta extra (Egg gana $3 por ronda).
- `an`: desfase de flotación. `ht`: contador de *hover* (para el tooltip con retardo).
- El `__init__` inicializa `xm`/`st` según la familia: Ramen arranca con `xm = 2.0`, Ice Cream con `st = fichas iniciales`, Popcorn con `st = mult inicial`, etc.

### `Planeta`
Representa un consumible de tipo planeta.
- `id`: índice en `PLANETS` (define qué planeta es, qué mano sube, y qué sprite usa).
- `an`, `ht`: animación de flotación y hover (igual que en `Joker`).
- No tiene `xm`. **Esta es la firma que distingue `Joker` de `Planeta`**: en pocketpy `isinstance` no es fiable para clases definidas en el script, así que se usa `hasattr(x, "xm")` como check rápido — `True` para `Joker`, `False` para `Planeta`. Esto aparece en `roll_planeta_unique`, `pack_pick`, `draw_shop_jslot`, etc.

### `Mazo`
Gestiona el conjunto de cartas.
- `dt`: tipo de baraja (0–7), define cómo se genera y su efecto especial.
- `cartas`: cartas que quedan por repartir. `total`: copia del mazo completo (para el visor y para jokers que cuentan cartas totales).
- `generar_mazo()`: crea las 52 (o las que toque según el tipo) cartas. Hay barajas especiales: solo picas+corazones, 1–10, 52 randomizadas, etc.
- `mostrar(...)`: dibuja el lomo de la baraja y, opcionalmente, el texto que describe su efecto (en el menú).
- `mezclar()` / `ordenar()`: barajan o ordenan por valor.
- `repartir()`: rellena `hand` hasta `gs["hs"]` cartas sacando de `cartas`, y reordena la mano con `sort_hand()` (que respeta `gs["sort_mode"]`). **Usa `gs["hs"]`** (tamaño dinámico), no una constante, para que jokers como Stuntman o Juggler cambien cuántas cartas se reparten. Al acabar invalida la caché del visor (`gs["vk"] = None`).

---

## 7. Cartas, manos y niveles

### `eval_hand()`, `chips_c(card)`
- `eval_hand()`: devuelve las cartas seleccionadas de la mano (`c.sel`).
- `chips_c(card)`: fichas base que aporta una carta al puntuar. Stone = 50, As = 11, figuras (J/Q/K) = 10, resto = su número. Suma `card.bc` (bonus dinámico).

### Los **12 tipos de mano** (`H_*`)
Antes había 7. Ahora son 12 para soportar las manos secretas que se desbloquean con `Five of a Kind`-style:

| Constante | Tipo | Idx |
|---|---|---|
| `H_PAR` | Pair | 0 |
| `H_DPA` | Two Pair | 1 |
| `H_TRI` | Three of a Kind | 2 |
| `H_ESC` | Straight | 3 |
| `H_COL` | Flush | 4 |
| `H_FUL` | Full House | 5 |
| `H_POK` | Four of a Kind | 6 |
| `H_HC`  | High Card | 7 |
| `H_SF`  | Straight Flush | 8 |
| `H_5K`  | Five of a Kind | 9 |
| `H_FH`  | Flush House | 10 |
| `H_5KF` | Flush Five | 11 |

Cuando se carga una partida nueva, `gs["hl"]` y `gs["hp"]` se inicializan **a tamaño 12** (`[1]*12` y `[False]*12`).

### `HAND_DEF`: definición base + escalado por nivel
Tupla indexada por el idx de mano. Cada entrada es `(nombre, chips_base, mult_base, chips_por_nivel, mult_por_nivel)`. Por ejemplo:

```python
("PAIR",10,2,15,1),         # nivel 1: 10/2, nivel 2: 25/3, nivel 3: 40/4, ...
("FULL HOUSE",40,4,25,2),
("FOUR KIND",60,7,30,3),
...
```

### `hand_score(hi)` — la fórmula del nivel
Combina la definición con el nivel actual:

```python
def hand_score(hi):
 if hi < 0:
  return ("", 0, 0)
 d = HAND_DEF[hi]
 lv = gs["hl"][hi]
 return d[0], d[1] + d[3] * (lv - 1), d[2] + d[4] * (lv - 1)
```

Devuelve `(nombre, chips, mult)` listos para usar. Es lo que llaman tanto `handle_play` (al jugar la mano) como `draw_score_hud` (al previsualizar la mano seleccionada).

### `detectar_mano(cartas)` — devuelve **índice**, no nombre
Versión refactorizada de la función. Ya **no** devuelve `(nombre, chips, mult, scoring)`; ahora devuelve **solo** `(hand_index, scoring_cards)`. El nombre y los valores se sacan después con `hand_score`. Este cambio fue necesario para encajar el sistema de niveles: el detector identifica *qué* mano es, y la puntuación se calcula aparte mirando el nivel actual.

Detecta las 12 manos en orden de prioridad: Flush Five → Flush House → Five of a Kind → Straight Flush → Four of a Kind → Full House → Flush → Straight → Three of a Kind → Two Pair → Pair → High Card. Para pareja/trío/póker devuelve **solo las cartas del grupo**; para escalera/color/full/flush five/etc. devuelve **todas** las cartas.

### `calcular_mano_flags(cartas)` — ahora devuelve 12 booleanos
A diferencia de `detectar_mano` (que da *la* mejor mano), `calcular_mano_flags` marca **todos** los tipos presentes a la vez. La lista resultante tiene **12 entradas** (una por `H_*`). La usan los jokers tipo "si la mano contiene X" (Jolly Joker, etc.), que deben dispararse aunque la mano sea un full. Si la mano está vacía devuelve `[False]*12`. `handle_play` la llama **sin las cartas Stone**, igual que `detectar_mano` (las Stone no cuentan para formar la mano, pero siempre puntúan).

### `PLANETS`: la tabla de planetas
12 planetas, uno por tipo de mano. Cada entrada es `(nombre, hand_idx, sprite_id)`:

```python
("MERCURY",H_PAR,208),
("VENUS",H_TRI,209),
("EARTH",H_FUL,210),
("MARS",H_POK,211),
("JUPITER",H_COL,212),
("SATURN",H_ESC,213),
("URANUS",H_DPA,214),
("NEPTUNE",H_SF,215),
("PLUTO",H_HC,216),
("X",H_5K,217),         # mano secreta
("CERES",H_FH,218),     # mano secreta
("ERIS",H_5KF,219),     # mano secreta
```

`use_planeta(idx)` aplica el planeta:

```python
def use_planeta(idx):
 if idx >= len(gs["consu"]):
  return
 p = gs["consu"][idx]
 d = PLANETS[p.id]
 gs["hl"][d[1]] += 1  # +1 al nivel de la mano que corresponda
 gs["consu"].pop(idx)
```

`gs["hp"]` se actualiza en `handle_play` cuando se juega una mano: `gs["hp"][hi]=True`. Lo usa `roll_planeta_unique` para que los planetas de manos secretas (id ≥ 9) **no aparezcan** en la tienda hasta haber descubierto la mano correspondiente. Esto replica el comportamiento de Balatro real: hasta que no consigues un Five of a Kind, nunca ves Planet X en la tienda.

---

## 8. El sistema de jokers

Este es el corazón del juego y el sitio donde más conviene entender el diseño.

### La idea central: "familias"

Hay decenas de jokers pero solo un puñado de **patrones de comportamiento**. Cada patrón es una **familia** (`F_*`, un entero). En lugar de programar cada joker por separado, cada joker se declara como "soy de la familia X con estos parámetros". Toda la lógica vive en funciones que hacen `switch` sobre la familia. Añadir un joker que encaje en una familia existente = una línea en la tabla; añadir uno con comportamiento nuevo = una familia nueva.

### `JDEFS`: la tabla de definiciones

`JDEFS` es una lista de tuplas. **El índice en la lista es el `id` del joker.** Formato:

```
(nombre, familia, *parámetros)
```

Los parámetros dependen de la familia. Ejemplos:
- `("Joker", F_FMUL, 4)` → +4 mult siempre.
- `("Greedy Joker", F_SMUL, 3, 3)` → +3 mult por cada carta de palo 3 (diamantes).
- `("Scholar", F_RCM, 20, 4, (1,))` → por cada As (rango 1): +20 fichas **y** +4 mult.
- `("Baron", F_HELD_R, 1.5, (13,), 1)` → por cada Rey **retenido en mano**: ×1.5 mult (el `1` final = modo multiplicativo).
- `("Steel Joker", F_XMUL_PER_EF, 0.2, 5)` → ×(1 + 0.2 × nº cartas con efecto Steel) mult.

Cada línea de `JDEFS` lleva a la derecha un comentario con columnas: **id**, **rareza**, **marcas** (`F` = funciona comprobado, `S` = tiene sprite) y **estado**: vacío si el joker es real y fiel a Balatro, o `#M` + el efecto real si aquí hace otra cosa.

**Auditoría (8 oct 2026, contra balatrowiki.org):** de los 123 jokers que había, **30 eran inventados y se han quitado** (Driver Snail, Quasar, Comet, Nebula, Pluto Eye, Cosmic Joker, Bus Driver, Marauder, Vault, Spectral, Bricks, Smith, Welder, Diamond/Heart/Club/Spade Joker, Gold Cards, Court Card, Low Tide, High Tide, Mariner, Magic Hat, Wheel of Fortune, Jester, Snowman, Lava, Tundra, Coupon y Telescope). Quedan **93**: **75 fieles** y **18 `#M`** (Burglar, Pareidolia, Stone Joker, Showman, Throwback, Hologram, Castle, Faceless Joker, Cartomancer, Marble Joker, Drunkard, Reserved Parking, Mime, Triboulet, Yorick, Constellation, Madness, Vagabond). Al quitar los inventados los ids a partir del 75 se desplazaron; `JRAR` y `JSPR` se reindexaron a la vez. También se corrigieron 3 nombres: Mr. Bones, Chaos the Clown y Faceless Joker.

### Las familias (resumen completo)

| Familia | Qué hace | Disparo |
|---|---|---|
| `F_FMUL` | +mult fijo | siempre (independiente) |
| `F_FCHP` | +fichas fijas | siempre |
| `F_XMUL` | ×mult fijo | siempre |
| `F_HMUL` | +mult si la mano contiene un tipo | independiente, condicionado a `mano_flags` |
| `F_HCHP` | +fichas si la mano contiene un tipo | ídem |
| `F_HXMUL` | ×mult si la mano contiene un tipo | ídem |
| `F_SMUL` | +mult por carta de un palo | al puntuar cada carta |
| `F_SCHP` | +fichas por carta de un palo | al puntuar cada carta |
| `F_RMUL` | +mult por carta de un rango | al puntuar cada carta |
| `F_RCHP` | +fichas por carta de un rango | al puntuar cada carta |
| `F_RCM` | +fichas **y** +mult por carta de un rango (Scholar, Walkie Talkie) | al puntuar cada carta |
| `F_SMONEY` | +dinero por carta de un palo (Rough Gem) | al puntuar cada carta |
| `F_SXPROB` | ×mult con probabilidad por carta de un palo (Bloodstone) | al puntuar cada carta |
| `F_RTRG` | **retrigger**: vuelve a puntuar cartas de un rango (Hack, Sock and Buskin; Mime `#M`) | modifica el conteo de repeticiones |
| `F_DUSK` | retrigger de todas las cartas en la mano final | ídem (depende de `hd`) |
| `F_RXFIRST` | ×mult solo en la **primera** carta de un rango (Photograph) | una carta concreta |
| `F_SZMUL` | +mult si jugaste pocas cartas (Half Joker) | independiente, condicionado al tamaño de `b` |
| `F_STENCIL` | ×mult por hueco de joker vacío (Joker Stencil) | independiente |
| `F_CHIP_DISC` | +fichas por descarte restante (Banner) | independiente |
| `F_NJOK_M` | +mult por número de jokers (Abstract Joker; Madness `#M`) | independiente |
| `F_NODISC_M` | +mult si no quedan descartes (Mystic Summit) | independiente, condicionado a `ds==0` |
| `F_HD_LAST_X` | ×mult en la última mano (Acrobat) | independiente, condicionado a `hd==1` |
| `F_BULL` | +fichas por dinero (Bull) | independiente |
| `F_BOOTS` | +mult escalado con dinero (Bootstraps; Vagabond `#M`) | independiente |
| `F_RAND_M` | +mult aleatorio (Misprint) | independiente |
| `F_HIKER` | añade fichas **permanentes** a cada carta puntuada (`bc`) | en el evento de cada carta |
| `F_STICKY_M` | +mult acumulado que crece/decrece según condición | independiente si `st>0` |
| `F_STICKY_C` | +fichas acumuladas que crecen según condición | independiente si `st>0` |
| `F_HELD_R` | +mult o ×mult por carta **retenida en mano** (Baron, Shoot the Moon; Reserved Parking `#M`) | un evento por carta retenida, en la fase de cartas en la mano |
| `F_RAMEN` | ×mult que decae al descartar (Ramen) | independiente; se autodestruye en ×1 |
| `F_FCHP_DEC` | +fichas que decrecen por mano jugada (Ice Cream) | independiente; se autodestruye en 0 |
| `F_FMUL_DEC` | +mult que decrece **al ganar una ronda** (Popcorn) | independiente; se autodestruye en 0 al final de ronda |
| `F_HS_MOD` | +fichas y modifica el tamaño de mano (Stuntman) | independiente; el `hs` lo aplica `recalc_hs` |
| `F_HAND_SIZE` | sube el tamaño de mano sin más (Juggler) | sin efecto en puntuación |
| `F_DECK_C` | +fichas por carta **que queda en el mazo** (Blue Joker) | independiente |
| `F_XMUL_PER_EF` | ×mult escalado por cartas con cierto **efecto** en el mazo (Steel Joker) | independiente |
| `F_EOR_MONEY` | dinero al final de ronda (Golden Joker; Faceless Joker `#M`) | en el cash out |
| `F_EOR_DISC` | dinero por descarte no usado al final de ronda (Delayed Gratification) | en el cash out |
| `F_EOR_INT` | interés extra: cada uno suma otra vez el interés base (To the Moon) | en el cash out |
| `F_EOR_DECK_RANK` | dinero por cada carta del mazo con cierto rango (Cloud 9) | en el cash out |
| `F_SPLASH` | **todas** las cartas jugadas puntúan, no solo las del grupo (Splash) | modifica `scoring_cards` |
| `F_FIRST_RTRG` | retriggers extra solo a la **primera** carta puntuada (Hanging Chad) | en `build_event_queue` |
| `F_BONES` | evita game over si llegas a ≥ ¼ de la blind (Mr. Bones); se autodestruye | en `try_mr_bones` |
| `F_FREE_REROLL` | un reroll gratis por visita a la tienda (Chaos the Clown) | en `enter_shop` |
| `F_XMUL_PER_EF` | ×(1 + paso × cartas del mazo con cierto efecto) (Steel Joker) | independiente |
| `F_EOR_SV` | su valor de venta sube cada ronda ganada (Egg) | en `start_round_win` |
| `F_MIDAS` | las figuras puntuadas se vuelven Gold (Midas Mask) | en `apply_card_ef` |
| `F_GTICK` | +$4 por carta Gold puntuada (Golden Ticket) | en `apply_card_ef` |
| `F_VAMP` | ×mult que gana 0.1 por carta con efecto puntuada y le quita el efecto (Vampire) | en `apply_card_ef` + independiente |
| `F_LUCKY` | ×mult que gana 0.25 cada vez que una Lucky acierta (Lucky Cat) | en `apply_card_ef` + independiente |

### Condiciones "sticky" (`SC_*`)

Los jokers `F_STICKY_M`/`F_STICKY_C` guardan un valor en `j.st` que cambia entre manos. La condición de cómo cambia es uno de:
- `SC_NO_FACE`: crece si **no** jugaste figuras; se resetea a 0 si jugaste alguna (Ride the Bus).
- `SC_PLAYED`: crece cada mano jugada; Green Joker **pierde 1 al descartar** (Green Joker; Castle `#M`).
- `SC_HAND_FLAG`: crece si la mano contiene cierto tipo (Spare Trousers, Runner).
- `SC_SIZE_EQ`: crece si jugaste exactamente N cartas (Square Joker).
- `SC_RANK_SCORED`: crece por cada carta de cierto rango que puntúa (Wee Joker: +8 por cada 2).

La actualización ocurre en `update_sticky(...)`, llamada **una vez al jugar la mano**, antes de construir la cola de eventos.

### `JSPR`: la tabla de sprites

`JSPR` mapea `id_de_joker → cómo dibujarlo`. Está separada de `JDEFS` porque no todos los jokers tienen arte todavía (los que no están en `JSPR` se dibujan con una caja de respaldo que muestra su valor). Formatos:
- `(0, sprite)`: sprite de 2×3 tiles tal cual;
- `(1, sprite)`: sprite de 2×2 tiles, sin marco;
- `(2, sprite)`: marco de carta de joker + sprite de 2×2 dentro;
- `(3, modo, sprite, [(slot, color), ...])`: igual que `modo` pero antes **reasigna colores de la paleta**, para teñir el mismo dibujo base (así muchos jokers comparten arte).

**Comprobado contra los sprites del cartucho `bitlatro.tic` (8 oct 2026): las claves están bien, no hay desfase.** Con las claves actuales, 60 es un cubo de palomitas (Popcorn), 62 un reloj de arena (Delayed Gratification), 63 una gráfica de bolsa (To the Moon) y 65 una papeleta (Hanging Chad). Tienen entrada en `JSPR`: 0–25, 28–31, 39 (Misprint), 43 (Ice Cream), 49 (Green Joker), 57 (Walkie Talkie), 58 (Blue Joker), 60, 62, 63, 65 y 79 (Faceless Joker, sprite 386; antes id 80).

`dibujar_joker(x, y, j, sc=1)` lee `JSPR[j.id]`, aplica los cambios de paleta si los hay, pinta el/los sprite(s) y restaura la paleta. El parámetro **`sc`** es nuevo: permite dibujar el joker a tamaño doble (`sc=2`), lo que usa el pack picker para mostrar las opciones a 2× tamaño. Devuelve `False` si el joker no tiene entrada (entonces el llamador dibuja la caja de respaldo).

> **Cuidado importante:** como el `id` es el índice en `JDEFS` y `JSPR` está indexado por ese mismo `id`, **el orden de `JDEFS` no se puede reordenar sin reordenar también `JSPR`**, o los sprites saldrían cambiados. Lo mismo aplica a `JRAR`.

### `JRAR`: rareza de cada joker

Diccionario `id → rareza` (`0` común, `1` poco común, `2` raro). Corregido según la wiki en oct 2026: a común Gros Michel, Cavendish, Misprint, Shoot the Moon, Chaos the Clown y Reserved Parking; a poco común Cloud 9, Burglar, Stone Joker, Steel Joker, Showman, Throwback, Mime y Constellation; a raro Wee Joker y Vagabond. Triboulet y Yorick son legendarios en Balatro (no salen en la tienda); aquí no hay rareza legendaria y quedan como raros. Lo usan:
- `roll_rarity()`: tira la rareza con probabilidades 70/25/5.
- `roll_joker()`: una vez decidida la rareza, escoge un joker uniformemente entre los de esa rareza usando `JPOOL`.
- `joker_price(jid)`: precio en `JCOST = (4, 6, 8)` según rareza.
- `joker_sell_value(j)`: precio de venta = precio/2 + `j.sv`, mínimo 1. Los precios van por rareza, no son el precio exacto de cada joker en Balatro.

### `JPOOL`: índice precalculado por rareza

`JPOOL[rar]` es la lista de IDs de jokers con esa rareza. Se construye una vez al cargar el script:

```python
JPOOL = [[], [], []]
for _jid, _rar in JRAR.items():
 JPOOL[_rar].append(_jid)
```

### `JDEP`: dependencias entre jokers

Diccionario `id_dependiente → id_requerido`. Por ahora solo tiene una entrada:
- `J_CAVE` (Cavendish) depende de `J_GROS` (Gros Michel): **Cavendish no aparece en la tienda hasta que tienes Gros Michel equipado**. En Balatro la regla es otra: Cavendish solo sale cuando un Gros Michel se ha extinguido (y entonces Gros Michel deja de salir).

Lo aplica `roll_joker_unique(used)`, que:
1. evita IDs ya en `used` (no repetir entre slots del mismo reroll),
2. evita IDs que ya tienes equipados (no comprar duplicados),
3. comprueba `JDEP`: si el joker depende de otro, exige que ese otro esté en tus jokers.

---

## 9. El motor de puntuación por cola de eventos

### ¿Por qué una cola?

En Balatro, al jugar una mano la puntuación no aparece de golpe: cada carta "bota" y suma sus fichas, luego cada joker actúa con su animación, y los contadores suben uno a uno. Para reproducir eso sin bloquear el bucle de 60 fps, Bitlatro **descompone toda la puntuación en una lista de "eventos"** y reproduce uno cada cierto número de fotogramas. Eso es `ev_queue`.

### Tipos de evento (`E_*`) y duración (`EDUR`)

| Evento | Significado | Duración (frames) |
|---|---|---|
| `E_RISE` | animación de subida de las cartas jugadas | 35 |
| `E_OPLAY` | un joker actúa "al jugar" (reservado) | 45 |
| `E_CSCORE` | una carta puntúa sus fichas | 50 |
| `E_OSCORE` | un joker actúa por una carta concreta | 42 |
| `E_IND` | un joker actúa de forma independiente | 45 |
| `E_FINAL` | cierre de la animación | 80 |
| `E_HELD` | una carta retenida en mano actúa: su Steel (×1.5) o un joker de mano retenida | 42 |

`EDUR` es la lista de duraciones indexada por el tipo de evento.

### Construcción de la cola: `build_event_queue(scoring)`

Se llama al pulsar "play". Construye la lista **en el orden exacto** en que debe animarse:

1. `E_RISE` (las cartas suben).
2. (Pre-cálculo) Para jokers `F_RXFIRST` (Photograph), localiza la primera carta que cumple y la guarda en `first_match`. También cuenta `first_rt` (retriggers extra a la primera carta) sumando los `F_FIRST_RTRG` equipados.
3. Eventos `E_OPLAY` (jokers "al jugar"; ahora `joker_fires_play` siempre devuelve `False`, reservado para el futuro).
4. Por cada carta que puntúa, en orden:
   - calcula sus **retriggers** con `count_retriggers` (y añade `first_rt` si es la primera carta);
   - repite el bloque `1 + retriggers` veces;
   - añade `E_CSCORE` (la carta suma fichas; el tercer campo marca si es un retrigger);
   - tras cada `E_CSCORE`, añade un `E_OSCORE` por cada joker que se dispara con esa carta (`joker_fires_score`) o que la tiene marcada en `first_match`.
5. **Cartas que se quedan en la mano**, de izquierda a derecha. Por cada una: primero su propio efecto (`E_HELD` con `ji = -1` si es Steel, ×1.5) y después un `E_HELD` por cada joker `F_HELD_R` cuyo rango la incluya (Baron, Shoot the Moon…).
6. **Jokers independientes**, de izquierda a derecha: un `E_IND` por cada joker para el que `joker_fires_ind` diga que sí.
7. `E_FINAL`.

> **Orden fiel a Balatro (8 oct 2026):** cartas jugadas → cartas en la mano → jokers. Antes los `F_HELD_R` actuaban en su posición de la fila de jokers y las Steel al final de todo, multiplicando también el mult de los demás jokers. Ejemplo de prueba (mult 2, mano con K Steel, Q y K; Joker + Baron + Shoot the Moon): ahora da ×30.25 (antes ×39.75).

### Las tres funciones de "disparo"

Deciden **cuándo** actúa un joker. Separarlas por momento es lo que evita redundancias:
- `joker_fires_play(j)`: al jugar la mano (reservado, hoy siempre `False`).
- `joker_fires_score(j, card)`: al puntuar **una carta concreta** (jokers por palo/rango). Aquí también se tira la **probabilidad** de Bloodstone (`F_SXPROB`): si no sale, el evento ni se encola.
- `joker_fires_ind(j)`: jokers **independientes** de carta. Cubre `F_FMUL`, `F_FCHP`, `F_XMUL`, `F_STENCIL`, `F_CHIP_DISC`, `F_RAMEN`, `F_NJOK_M`, `F_BULL`, `F_RAND_M`, `F_HMUL`/`F_HCHP`/`F_HXMUL` (condicionados a `mano_flags`), `F_SZMUL`, `F_NODISC_M`, `F_HD_LAST_X`, `F_STICKY_M`/`F_STICKY_C` (si `st>0`), `F_BOOTS`, `F_HS_MOD`, `F_FCHP_DEC` (si `st>0`), `F_DECK_C`, `F_FMUL_DEC` (si `st>0`), y `F_XMUL_PER_EF`. Ojo: `F_HELD_R` y `F_DUSK` **no** disparan aquí a propósito (tienen su propio camino: `E_HELD` y los retriggers).

### Retriggers: `count_retriggers(card)`

Devuelve cuántas veces extra debe puntuar una carta: +1 por cada joker `F_RTRG` cuyo rango incluya la carta (Hack 2-5, Sock and Buskin J/Q/K, Mime A-K = todos; el Mime real repite los efectos de las cartas en la mano, por eso está marcado `#M`), y +1 si hay un `F_DUSK` y estamos en la mano final (`hd==1` en el momento de construir la cola). A esto se le suman los retriggers de Hanging Chad (`F_FIRST_RTRG`) si la carta es la primera. El bucle de `build_event_queue` repite el `E_CSCORE` y sus `E_OSCORE` esas veces de más.

### Aplicar efectos: `apply_event(e)` y `apply_joker_effect(j)`

`apply_event` se ejecuta **una sola vez** al empezar cada evento (cuando `ev_timer == 0`). Según el tipo:
- `E_CSCORE`: aplica Hiker (suma `bc` permanente a la carta), suma `chips_c(carta)` a `tot_chips`, lanza la partícula de fichas (y una de "TRIGER" si es retrigger).
- `E_OPLAY` / `E_OSCORE` / `E_IND`: llaman a `apply_joker_effect(joker)` y lanzan la partícula correspondiente con `spawn_for_joker`.
- `E_HELD`: si `ji = -1` aplica el ×1.5 de la carta Steel; si no, el +mult o ×mult del joker de mano retenida. La partícula sale **sobre la carta retenida** (usando `hand_card_center`).

`apply_joker_effect(j)` es el gran `switch` por familia que modifica `tot_chips`/`tot_mult` (o `mn` en el caso de Rough Gem). Es donde se concreta el efecto numérico de cada familia. Casos destacables:

- **`F_DECK_C`** suma `d[2] * len(gs["baraja"].cartas)` (las cartas **que quedan en el mazo**, no el total). Esto es importante: el valor de Blue Joker baja conforme repartes la mano dentro de la misma ronda.
- **`F_XMUL_PER_EF`** cuenta cuántas cartas del mazo total (`gs["baraja"].total`) tienen `c.ef == d[3]`, y multiplica `tot_mult` por `1 + d[2] * count`. Ejemplo: Steel Joker (`d[2]=0.2, d[3]=5`) con 3 cartas Steel → ×1.6 mult.
- `F_HELD_R` **no está** en `apply_joker_effect`: se aplica directamente dentro del `E_HELD` en `apply_event`.

### Avance temporal: `step_queue()`

Llamada cada fotograma durante la puntuación. Si quedan eventos:
- en el primer frame del evento (`ev_timer == 0`) ejecuta `apply_event`;
- incrementa `ev_timer`;
- cuando `ev_timer` alcanza `EDUR[tipo]`, pasa al siguiente evento.

Cuando se acaban los eventos, llama a `finalize_score()`.

### Cierre: `finalize_score()`

- Aplica los **decrementos de jokers descendentes** (`F_FCHP_DEC`: Ice Cream −5). Si `st<=d[4]` (límite), el joker se destruye.
- Quita del mazo total las Glass que se han roto (`c.bk`).
- Recalcula el tamaño de mano (`recalc_hs`).
- Suma `tot_chips * tot_mult` a `rs` (la puntuación de la ronda).
- Quita de la mano las cartas jugadas y limpia los acumuladores.
- **Bifurcación de salida**:
  - Si `rs >= blind_req()` → ronda ganada: llama a `start_round_win()`.
  - Si `hd <= 0` (te quedaste sin manos): intenta `try_mr_bones()`. Si tienes un Mr Bones y `rs >= blind_req()//4`, el joker se sacrifica y `rs` se sube al requisito, ganando la ronda. Si no, `gm = 5` (Game Over).
  - Si no ganaste pero te quedan manos: reparte y vuelve a `fase_puntos = 0`.

### Tamaño de mano dinámico: `recalc_hs()`

Parte de 8, suma el modificador de cada joker `F_HS_MOD` equipado (Stuntman: −2) y `F_HAND_SIZE` (Juggler: +1), con mínimo de 1. Hay que llamarlo **siempre que cambie la lista de jokers** (al equipar, al destruir uno, al iniciar partida). Por eso aparece en `finalize_score`, en los handlers de descarte, al comprar/vender jokers y al arrancar partida.

### Visual de la puntuación: `update_event_visuals()`

Cada fotograma, decide qué resaltar según el evento en curso: hace "botar" la carta puntuando (`offset_eval` con una curva senoidal), resalta el joker activo (`active_joker_idx`), y en los retriggers resalta el joker `F_RTRG`/`F_DUSK` responsable. Para `E_HELD`, bota la carta retenida correspondiente.

---

## 10. Sistema de partículas y "shakes"

Las partículas son los números que flotan al puntuar (los "+8", "x3", "$1"…).

- `PARTICLE_KINDS`: mapea tipo → `(color_del_rombo, prefijo_de_texto)`. Tipos: `chip`, `mult` (+), `xmult` (x), `trigger`, `money` ($), `loss_m` (−, para la pérdida de mult de Green Joker al descartar).
- `draw_diamond(cx, cy, w, h, col)`: dibuja el rombo de fondo de la partícula con dos triángulos (`tri`).
- `card_center_xy(ci)` / `joker_center_xy(ji)` / `hand_card_center(hi)`: calculan dónde nace la partícula (sobre una carta puntuando, sobre un joker, o sobre una carta retenida en mano respectivamente). Replican la misma fórmula de reparto horizontal que `print_cards`/`print_jokers` para que la partícula caiga justo encima del elemento correcto. **`joker_center_xy`** y `joker_x_pos` tienen un caso especial para `n==1` (un único joker se centra en el carril en vez de quedarse pegado a la izquierda).
- `spawn_particle(cx, cy, value, kind)`: crea la partícula y, según el tipo, dispara el **shake** del contador del HUD asociado (fichas, mult o dinero).
- `spawn_for_joker(ji)`: elige qué partícula lanzar según la familia del joker (el valor que muestra coincide con lo que aplica `apply_joker_effect`, incluyendo los casos nuevos `F_XMUL_PER_EF` y `F_FMUL_DEC`).
- `update_and_draw_particles()`: cada fotograma anima todas las partículas (escala de aparición/permanencia/desaparición, subida vertical) y descarta las muertas.

Los **shakes** (`shake_chips`, `shake_mult`, `shake_nombre`, `shake_money`) son temporizadores que se ponen a 15 (o 22) al recibir un golpe y bajan cada fotograma; mientras tanto, `shake_offset` desplaza el contador correspondiente con la onda amortiguada.

---

## 11. Dibujo de cartas, jokers y consumibles en pantalla

### `draw_card_at(carta, xc, yc)`
Pinta una sola carta en `(xc, y)` con todas sus capas: marco/efecto, palo, valor (teñido a rojo si el palo es impar), sello y, si tiene edición, la animación foil/holo encima. Está extraída para poder reutilizarse desde dos sitios distintos de `print_cards`: una vez en su posición "normal" dentro de la fila, y otra vez **siguiendo al ratón** cuando se está arrastrando.

### `sort_hand()`
Ordena `gs["hand"]` según `gs["sort_mode"]`:
- `0` = **por rango**, descendente con As = 14 (orden A K Q J 10 9 8 7 6 5 4 3 2). Es el orden por defecto en Balatro.
- `1` = **por palo**, y dentro de cada palo por rango descendente. La clave es `(c.su, -valor)`.

La llaman: `Mazo.repartir()` tras rellenar, `handle_sort` al pulsar el botón Rango/Palo, y `handle_discard` indirectamente vía `repartir`.

### `print_cards(x, y, xf, cards, permite_seleccion)`

Dibuja una fila de cartas repartidas entre `x` y `xf`. Calcula la separación para que quepan, aplica la flotación (`onda_y`) y el bote de puntuación (`offset_eval`), y salta las cartas que están en `b` cuando dibuja la mano.

**Selección + drag & drop (solo si `permite_seleccion` *y* `cards is hand`):** la entrada se distingue entre clic-simple (toggle de selección) y arrastre-real (reordenar la mano) por **umbral de movimiento**:

1. Al pulsar sobre una carta se guarda como candidata en `gs["drag_card"]` y se anota la posición `gs["drag_px"]/drag_py`. Aún no se hace nada con `c.sel`.
2. Mientras el ratón está pulsado, si se aleja más de 3 px del punto de pulsación, `gs["drag_active"]` pasa a `True`. La carta arrastrada **se omite del bucle de dibujo** y se pinta al final siguiendo al ratón con `draw_card_at(dc, mx-8, my-12)`.
3. Al soltar el ratón (`not mb and gs["Clk0"]`):
   - Si fue un **arrastre real** (`drag_active`), se calcula el índice destino con `round((mx - x - 8) / sep)`, se hace `hand.pop(oi)` + `hand.insert(ni, dc)`. Las demás cartas no se desplazan para hacer hueco; simplemente al soltar la carta encaja en el slot más cercano.
   - Si fue un **clic limpio** (sin movimiento), se conmuta `dc.sel` con el tope habitual de 5 seleccionadas.

En ambos casos `drag_card` y `drag_active` vuelven a su estado inicial.

El orden manual conseguido con drag **dura hasta el siguiente reparto**; tras una mano jugada o un descarte, `repartir()` llama a `sort_hand()` y reordena según `sort_mode`. Si se quisiera que el orden manual persistiera entre manos, habría que añadir un flag (`sort_locked`) y respetarlo en `sort_hand`.

**Tooltip de carta (en el visor):** si `gs["gm"]==2` y el ratón está sobre una carta, en vez de dibujar el tooltip ahí mismo, se guarda en `gs["tt_target"] = ("card", carta, xc, y)`. `TIC()` lo pinta al final del fotograma.

### `print_jokers(oy=0)`
Análogo para los jokers; el parámetro **`oy`** es un desplazamiento vertical para poder pintar la fila de jokers en cualquier altura (lo usa el sistema de scroll para dibujar dos copias). Reparte, flota, resalta el `active_joker_idx`, gestiona el *hover* con retardo para el tooltip (`j.ht`) y, si un joker no tiene sprite, dibuja la **caja de respaldo** con su valor calculado según la familia. El tooltip se difiere a `gs["tt_target"]` igual que con las cartas, y solo se registra si `fase_puntos < 2` (no durante la animación de cash out).

**Drag + selección sobre jokers** (solo si `gm in (1, 3, 4)` y `fase_puntos == 0` y `oy == 0`; la pantalla de ciegas se añadió en oct 2026):
- Funciona igual que con las cartas: clic limpio → **toggle de selección** (`gs["sel_joker"]`); arrastre con movimiento > 3 px → **reordenar**.
- Si seleccionas un joker, se deselecciona el consumible (`sel_consu = -1`), y viceversa. Solo puede haber un objeto seleccionado al tiempo.

Para el caso `n == 1` se centra el único joker en el carril (mismo arreglo que en `joker_center_xy`).

### `print_consumibles(oy=0)` — nueva función
Dibuja la fila de **planetas** que tienes en `gs["consu"]`. Solo hay 2 huecos (limitación del juego), así que es una fila pequeña, dibujada a la derecha del HUD a partir de `x=189`, separación 18 px.

- Llama a `dibujar_planeta(xp, yp, p)` para pintar cada planeta (sprite 71 a la izquierda y reflejado a la derecha + el sprite del planeta concreto en medio, ver `PLANETS`).
- Gestiona hover → tooltip diferido `("planeta", p, xp, yp)`.
- Gestiona clic → toggle de `gs["sel_consu"]` (con el mismo "sólo uno seleccionado" frente a `sel_joker`).

### `dibujar_planeta(x, y, p, sc=1)`
Pinta el planeta: dos halos del sprite #71 (uno normal y otro espejado) más el sprite concreto del planeta sobre ellos. Acepta el parámetro `sc` para tamaño doble en el pack picker.

### `tt_planeta(p, xc, yc)` y `tt_card` — tooltips

- `tt_card(c, xc, yc)`: dibuja una caja con el nombre de la carta (`"K of HEARTS"` etc., en inglés), sus chips, y si tiene efecto o sello muestra el **nombre exacto** desde `EFFECTS` y `SEAL_NAMES` (p. ej. `"Gold Card"`, `"Red Seal"`). También clampea la caja para que no se salga por arriba (`ty < 0`) ni por abajo (`ty + th > 136`); si se saldría, se la pone encima de la carta en vez de debajo.
- `tt_joker(j, xj, yj)`: nombre + descripción corta (`joker_value_text`).
- `tt_planeta(p, xc, yc)`: 4 líneas debajo del nombre — `LVL N>N+1` (el salto de nivel), `+XF` (chips por nivel), `+XM` (mult por nivel) y el nombre del tipo de mano que sube. Lee del `HAND_DEF` correspondiente.

### `joker_value_text(j)` y `JVT`

Para que el tooltip y la caja de respaldo den la misma info, las descripciones se generan con `JVT`, un diccionario `familia → patrón de plantilla` con la forma `(prefijo1, modo1, sufijo, modo2, sufijo_extra)`. `_jvt_v(j, d, m)` resuelve cada "modo": 1 = `d[2]`, 2 = `d[3]`, 3 = `j.st`, 4 = `round(j.xm, 2)`. Esto evita un `switch` gigante; añadir un joker que use una familia existente no requiere tocar `joker_value_text`.

`F_HELD_R` se trata como caso especial fuera de `JVT` (porque el prefijo depende de `d[4]`).

### `draw_joker_box(xj, yj, j, sc=1)` y `JBOX`
Mismo patrón pero para la **caja de respaldo** (cuando el joker no tiene sprite). `JBOX` es otro diccionario con plantillas de 3 elementos `(prefijo, modo, color)`. La función pinta un rectángulo, el código de 3 letras del joker, y debajo el valor calculado. `F_HELD_R` y `F_DECK_C` son casos especiales porque dependen del estado del juego (mano y mazo), no solo de parámetros estáticos.

---

## 12. Las seis pantallas

### `PantallaMenu(raton)` (gm=0)
Dibuja el logo, el lomo de la baraja seleccionada con su descripción, y botones `<`/`>` para cambiar de baraja y `play` para empezar. Al pulsar `play` llama a `nueva_partida()`, que resetea los recursos (`hd/ds/mn/ant/rd`, `hs=8`, partículas, shakes, `blind=0`, `voff=0`, `co_wait=0`, **`hl=[1]*12`**, **`hp=[False]*12`**, **`sel_joker=-1`**, **`sel_consu=-1`**, `pack=None`), genera y mezcla el mazo, **equipa los jokers de prueba**, llama a `recalc_hs()` y **va directamente a la pantalla de blind** (`gm = 4`). Ya no entra al juego: pasa por la selección de blind primero.

> El joker de prueba está en `nueva_partida()`, en la línea `gs["jokers"] = [Joker(43)]  #DBG` (43 = Ice Cream). Cambia ese número por el `id` del joker que quieras probar, o déjalo en `[]` para la versión final.

### `PantallaJuego(raton)` (gm=1)
Es la pantalla principal. Para no superar el límite de variables locales de pocketpy, su lógica está repartida en auxiliares:
- `draw_money_box()`: dibuja el contador de dinero con su shake. **Posición fija en pantalla** (no se mueve con el scroll).
- `draw_score_hud(permitir)`: dibuja las cajas de fichas/mult, el nombre de la mano y, **debajo, `lvl N`** (el nivel actual de esa mano). Tanto la previsualización (mano seleccionada) como el scoring usan `hand_score(hi)` para obtener nombre + chips + mult con el nivel aplicado. El nombre va a `y=36` y el nivel a `y=44` (antes el nombre estaba a 44). El bloque HUD principal es ahora **8 px más alto** (de `h=4` a `h=5`) para meter la línea de nivel.
- `draw_side_hud(permitir)`: dibuja todo el HUD lateral (ROUND SCORE, HANDS, Discards, ANTE, ROUND, money, score hud). El bloque del round score se subió 8 px (de `y=25` a `y=17` para la caja) para compactar el HUD.
- `handle_discard(up)`: el botón "discard" — quita las cartas seleccionadas, reparte, gasta un descarte y aplica los efectos de descarte: Ramen (`F_RAMEN`) pierde `0.01 × nº_cartas` (y se autodestruye en ×1), Green Joker (`F_STICKY_M` con `SC_PLAYED`) pierde 1 de mult (con partícula `loss_m`), y recalcula `hs`.
- `handle_play(up)`: el botón "play" — detecta la mano con `detectar_mano` (que ahora devuelve `(hi, sc)`), saca nombre/chips/mult con `hand_score(hi)`, marca `gs["hp"][hi]=True` (esa mano ya se descubrió, así puede aparecer su planeta en la tienda), aplica Splash si toca (`scoring_cards = b[:]`, todas puntúan), calcula `mano_flags` sin las Stone, construye la cola y entra en `fase_puntos = 1`.
- `handle_sort(up)`: alterna entre ordenar por **Rango** y por **Palo**.

Otros auxiliares: `draw_tapete(yt)` (el tapete de la mano) y `draw_contadores(oy, con_mazo)` (los contadores `n/5`, `n/2` y `n/52`, que también usan la tienda y la pantalla de ciegas).

El resto de `PantallaJuego` dibuja el HUD fijo, los jokers (`print_jokers(-voff)`), los consumibles (`print_consumibles(-voff)`), la mano (que ahora se pinta **al final**, después de las partículas, para que ninguna partícula tape la mano), las cartas jugadas subiendo durante el scoring, las partículas, y los botones de vender/usar (`draw_sell_use_buttons`). También detecta el clic en el lomo del mazo (a través de `check_mazo_click`, que también guarda en `visor_from` la pantalla actual para que el visor sepa a dónde volver). Si `fase_puntos >= 2` (ronda ganada) gestiona el scroll y dibuja el panel de cash out (ver §12.5).

### `PantallaVisor(raton)` (gm=2)
Muestra estadísticas del mazo: cuántas cartas quedan de cada valor y palo, y las cartas agrupadas por palo. Cachea el cálculo en `vc`/`vk` para no recalcular cada fotograma (la caché se invalida cada vez que se reparte o se empieza ronda). Antes de cachear, ordena cada lista de palo por valor. Un botón alterna entre el mazo "total" y el "actual" (lo que queda). Clic en la esquina (sobre el lomo grande) **vuelve a la pantalla de donde se vino** (`gs["visor_from"]`), no siempre al juego. Esto permite consultar el mazo también desde la tienda sin volver al juego.

### `PantallaTienda(raton)` (gm=3)
Detallada en §12.6 más abajo.

### `PantallaBlind(raton)` (gm=4)
Pantalla intermedia entre tienda y juego: muestra los **tres blinds del ante actual** (small, big, boss) con un círculo del color correspondiente (6 = verde, 8 = naranja, 2 = rojo), el requisito de puntuación y la recompensa. El blind actual (el que toca jugar) muestra un botón **play**; los otros dos muestran solo su recompensa en `$`. También dibuja el HUD lateral, los jokers, los consumibles y los botones de vender/usar (puedes seleccionar y vender un joker, reordenarlos o usar un planeta antes de entrar al blind).

Al pulsar `play`: `start_blind()` resetea la ronda (`reset_round`, `voff=0`, `fase_puntos=0`), reparte y entra al juego (`gm=1`).

`blind_panel(bi, x, y, raton)` es el auxiliar que pinta cada uno de los tres paneles.

### `PantallaGameOver(raton)` (gm=5)
Se entra aquí cuando te quedas sin manos sin alcanzar el requisito y no tienes un Mr Bones que te salve. Pinta `"GAME OVER"`, el ante/ronda donde caíste y el dinero final. Un botón `menu` vuelve al menú principal, reseteando jokers/consumibles/mano/baraja.

---

## 12.5. Fin de ronda, scroll vertical y Cash Out

Al alcanzar la puntuación requerida, la pantalla del juego **sube** dejando ver un panel de cash out que entra desde abajo. Es animación pura: todo se hace con un único entero, `gs["voff"]`, que va de `0` a `SCREEN_H` (136 px).

### La mecánica del scroll

El truco es que cada elemento dibujado decide **cómo se relaciona** con `voff`:

- **Elementos que suben con la cámara (mundo de juego)** — se dibujan con `y - voff`: jokers (`print_jokers(-voff)`), consumibles (`print_consumibles(-voff)`), el tapete de cartas (sprites 189/190/191/206/207), la mano del jugador (`print_cards(80, 140-up-voff, …)`), el contador de tamaño de mano, los botones **play**/**discard**/sort, los tres contadores **x/5** (jokers), **0/2** (consumibles) y **xx/52** (cartas en mazo), y el lomo del mazo (`baraja.mostrar(216, 104-voff, …)`).
- **Elementos fijos en pantalla (HUD)** — se dibujan sin restar `voff`, así que se quedan donde están aunque la cámara suba. Aquí va todo el HUD lateral.
- **Elementos del cash out (pantalla nueva)** — se dibujan con `y + (SCREEN_H - voff)`. Cuando `voff` es 0 están a `+136` (fuera por abajo); cuando `voff` llega a `SCREEN_H` están en su sitio. Esto lo hace `draw_cash_out(oy)` recibiendo `oy = SCREEN_H - voff`.
- **Copias de los elementos del mundo en la pantalla del cash out** — para que cuando la cámara suba al panel de cash out el jugador vea **dónde han quedado** sus jokers, consumibles y mazo, los mismos elementos se vuelven a dibujar con `y + SCREEN_H - voff`. Esto se hace **solo cuando `fp >= 2`** (no malgastas dibujos durante el juego normal) y aplica a: `print_jokers(SCREEN_H - voff)`, `print_consumibles(SCREEN_H - voff)`, los contadores, y el lomo del mazo.

Resumen: el mismo elemento aparece a la vez en dos sitios durante la transición porque hay dos llamadas, una con `-voff` y otra con `+SCREEN_H-voff`. Cuando la cámara está a medio camino, ves uno saliendo por arriba y el otro entrando por abajo en su posición final.

### Constantes editables

- `SCREEN_H = 136` — alto de la pantalla de TIC-80.
- `ANTE_BASE = (300, 800, 2800, 6000, 11000, 20000, 35000, 50000)` — chips base por ante 1–8 (valores de release, no demo).
- `BLIND_MULT = (1.0, 1.5, 2.0)` — multiplicador de chips de small / big / boss.
- `BLIND_REWARD = (3, 4, 5)` — dinero base por vencer small / big / boss.
- `BLIND_NAME = ("SMALL", "BIG", "BOSS")` — texto del círculo en el panel.
- `INTEREST_CAP = 5` — tope del interés (1 $ por cada 5 $, máximo 5 $). Cada To the Moon (`F_EOR_INT`) suma otra vez ese interés.
- `CASH_SPEED = 2` — píxeles por frame que sube la pantalla.
- `CASH_WAIT = 20` — frames de pausa antes de empezar a subir.

### Funciones

- `blind_req()` → puntos necesarios = `ante_base(ant) * BLIND_MULT[gs["blind"]]`. `ante_base(a)` ahora maneja **endless**: a partir de ante 9, multiplica por 1.6 sucesivamente desde el valor del ante 8.
- `cash_out_money()` → `(reward, hands, interest, disc, extra)`:
  - `reward`: `BLIND_REWARD[blind]`.
  - **Si la baraja es la amarilla** (dt=2): `hands = hd*2`, `interest = 0`, `disc = ds` (gana 2 $ por mano restante y 1 $ por descarte restante en vez de interés).
  - **En las demás barajas**: `hands = hd`, `interest = min(INTEREST_CAP, mn//5) * (1 + nº de To the Moon)`, `disc = 0`.
  - `extra = joker_round_money()`: suma de `F_EOR_MONEY` (Golden Joker +4 $; Faceless Joker +5 $, `#M`), `F_EOR_DISC` (Delayed Gratification +2 $ por descarte sin usar, solo si no usaste ninguno), `F_EOR_DECK_RANK` (Cloud 9 +1 $ por cada 9 del mazo) y +3 $ por cada carta Gold que se quede en la mano.
- `start_round_win()` — se llama desde `finalize_score` cuando `rs >= blind_req()`. Hace primero los **jokers que se autodestruyen al final de ronda**:
  - **Gros Michel**: 1/6 de autodestruirse.
  - **Cavendish**: 1/1000 de autodestruirse.
  - **`F_FMUL_DEC`** (Popcorn): `st -= d[3]`, y si llega a ≤ 0 el joker se destruye.
  - **`F_EOR_SV`** (Egg): su valor de venta sube 3 $.

  Luego recalcula `hs`, calcula el desglose del cash out (`co_reward`, `co_hands`, `co_interest`, `co_disc`, `co_extra`, `co_total`, `co_req`), pone `voff = 0`, arranca el contador `co_wait` y entra en `fase_puntos = 2`.
- `try_mr_bones()` — recorre los jokers buscando un `F_BONES`. Si lo encuentra y `rs >= blind_req()//4`, sacrifica el joker, sube `rs` al requisito y devuelve `True`. Lo llama `finalize_score` justo antes de declarar game over.
- `collect_cash_out()` — se llama al cobrar: suma `co_total` al dinero y entra a la tienda (`enter_shop()`).
- `enter_shop()` — entra a la tienda: pone `voff=0`, `fase_puntos=0`, `pack=None`, reset del reroll (`reroll=SHOP_BASE_REROLL=5`), `free_rr=1` si tienes algún joker `F_FREE_REROLL`. Resetea también `rs/hd/ds` y llama a `reset_round()` (devuelve cartas al mazo, mezcla, vacía mano). Llama a `roll_shop()` y pone `gm=3`.
- `shop_next_round()` — desde la tienda, avanza al siguiente blind: `blind++`, si pasa de 2 → `blind=0, ant++`. Incrementa `rd` y va a `gm=4` (selección de blind).
- `start_blind()` — desde la selección de blind, resetea la ronda y entra al juego.
- `reset_round()` — devuelve todas las cartas al mazo, invalida la caché del visor, vacía `hand`/`b`/`scoring_cards`, limpia `nombre_mano`/`hand_idx_play`, resetea acumuladores y partículas, mezcla y deja la mano vacía (no reparte aquí — eso lo hace `start_blind` o `repartir` cuando lo pida la pantalla).
- `draw_cash_out(oy)` — dibuja la barra naranja "CASH OUT: $X" y el panel con 3–4 líneas (blind requirement + $, manos restantes/descartes restantes según baraja, interés + $, y opcionalmente "JOKER/BARAJA" + $ si `co_extra > 0`). Función deliberadamente compacta.

### Flujo (lo que pasa al ganar)

1. `finalize_score()` ve `rs >= blind_req()` y llama a `start_round_win()`. La fase pasa a `2`.
2. Cada frame, mientras `fp == 2`:
   - Si `co_wait > 0`, decrementa (pausa).
   - Si no, `voff += CASH_SPEED` y comprueba si llegó a `SCREEN_H` → fase pasa a `3`.
   - Se dibujan los elementos con sus tres relaciones a `voff`.
3. En `fp == 3`, el panel está fijo arriba. Un clic dentro del rectángulo del panel (`97 <= x < 193, 53 <= y < 69`) llama a `collect_cash_out()`, que suma el dinero y **entra a la tienda** (`gm=3`).
4. En la tienda, al pulsar **next**, `shop_next_round()` avanza el blind y pasa a la selección de blind (`gm=4`).
5. Al pulsar **play** en el panel del blind seleccionado, `start_blind()` entra al juego (`gm=1`) con la ronda preparada.

---

## 12.6. La tienda

La tienda (`PantallaTienda`, `gm=3`) tiene tres bloques:

**Bloque izquierdo — Next + Reroll**
- Botón `next` (rojo): llama a `shop_next_round()`.
- Botón `reroll` debajo: si `free_rr > 0` muestra `free`; si no, muestra `$N` con el coste actual. Activo si tienes free rerolls o dinero suficiente. Llama a `do_reroll()`.

**Bloque derecho arriba — 2 slots de compra principal**
- Cada slot puede tener un **joker** o un **planeta**. La probabilidad de que un slot sea planeta es 25 % (`random.randint(1, 4) == 1` en `roll_shop`).
- `draw_shop_jslot(slot, x, y, raton)` dibuja el slot: precio arriba en una mini-caja, y debajo el ítem (joker o planeta a tamaño normal). Si está vendido (`e[2]`), se omite el dibujo (el hueco se vacía). Al pulsar, llama a `buy_joker(slot)` o `buy_planeta(slot)` según `e[3]`.
- `buy_joker(slot)`: comprueba que tienes hueco (`< jslots`) y dinero, equipa el joker, marca como vendido y recalcula `hs`.
- `buy_planeta(slot)`: comprueba que tienes hueco de consumibles (`< 2`) y dinero, lo añade a `gs["consu"]`.

**Bloque derecho abajo — 2 slots de packs**
- `draw_shop_pslot(slot, x, y, raton)`: dibuja el slot del pack. Si está abierto, se oculta el slot. El color de la caja viene de `PACK_COL[k]`: 3 (rosa) para buffoon, 4 (naranja) para celestial.
- Al pulsar, `open_pack(slot)` genera las opciones y abre el picker.

**Rerolls (`do_reroll`)**
- Si tienes `free_rr > 0`, lo gastas. Si no, gastas el coste actual del reroll y subes el coste en 1.
- Vuelve a rellenar los 2 slots de compra principal con `roll_shop_items()`, la misma función que usa `roll_shop()` (regla 75/25 joker/planeta). Los sobres no cambian.

**Generación de ítems únicos:**
- `roll_joker_unique(used)`: tira jokers hasta encontrar uno que (a) no esté ya en `used` (otros slots del mismo reroll), (b) no esté ya equipado, y (c) cumpla `JDEP` (Cavendish requiere Gros Michel).
- `roll_planeta_unique(used)`: similar pero para planetas. Excluye los que ya tienes en `consu`, los que ya están en `used`, y los de **manos secretas no descubiertas** (id ≥ 9 si `hp[hand_idx] == False`).

Si tras 40 intentos no encuentra uno válido, devuelve uno al azar como fallback.

---

## 12.7. Paquetes (Booster Packs)

Cuando abres un pack se entra al "pack picker": una pantalla superpuesta donde eliges una o varias cartas (jokers o planetas) de un conjunto generado.

### `PACK_DEF`, `PACK_NAME`, `PACK_COL`

```python
PACK_DEF=(
 (2,1,4,0),   # BUF: Buffoon — 2 jokers, eliges 1, $4
 (4,1,6,0),   # JBF: Jumbo Buffoon — 4 jokers, eliges 1, $6
 (4,2,8,0),   # MGB: Mega Buffoon — 4 jokers, eliges 2, $8
 (4,1,4,1),   # CEL: Celestial — 4 planetas, eliges 1, $4
 (5,1,6,1),   # JCL: Jumbo Celestial — 5 planetas, eliges 1, $6
 (5,2,8,1),   # MCL: Mega Celestial — 5 planetas, eliges 2, $8
)
```

Cada entrada es `(opciones, picks, precio, tipo)` donde `tipo` 0 = jokers, 1 = planetas. `PACK_NAME` tiene el nombre corto que se dibuja en el slot; `PACK_COL` el color de la caja (3 buffoon, 4 celestial).

Distribución al rerollear/generar (`roll_shop`): 20 % BUF, 10 % JBF, 5 % MGB, 45 % CEL, 10 % JCL, 10 % MCL. Es decir, los celestial son más comunes (eran necesarios en Balatro para subir manos).

### `open_pack(slot)`

Cobra el precio y genera las opciones. Si es buffoon, llama a `roll_joker_unique` varias veces; si es celestial, a `roll_planeta_unique`. Para celestial, **construye el "used" tomando también lo que ya está en `gs["consu"]` y en los slots de la tienda no vendidos**, así nunca te ofrece duplicados de algo que ya tienes o puedes comprar fuera.

Guarda en `gs["pack"]` un dict `{"k": k, "choices": ch, "picks": n_picks}`.

### `draw_pack_picker(raton)`

Pinta el picker:
- Título con el nombre del pack.
- Texto `"Choose N"` con el número de picks restantes.
- Las opciones se pintan a **tamaño doble** (`sc=2`) usando `dibujar_planeta(xj, yj, it, 2)` o `dibujar_joker(xj, yj, it, 2)`. Esto es lo nuevo: el picker da más protagonismo al ítem.
- Si la opción es un planeta, se le **superpone el sprite #106** centrado debajo, como adorno (el "halo" del planeta a tamaño grande).
- Al hover, se muestra el tooltip del ítem (`tt_joker` o `tt_planeta`).
- Al clicar, `pack_pick(idx)` añade el ítem a `jokers` o `consu` según corresponda (distinguiendo por `hasattr(it, "xm")`), comprueba huecos, y decrementa `picks`.
- Botón `skip` para descartar el pack sin tomar todas las opciones.

### `pack_pick(idx)`

- Si el ítem es un joker (`hasattr(it, "xm")`): comprueba huecos de joker, lo añade a `gs["jokers"]`, recalcula `hs`.
- Si es planeta: comprueba huecos de consumibles, lo añade a `gs["consu"]`.
- En ambos casos lo saca de `p["choices"]` (no `pop(idx)` después de añadir — se hace antes de comprobar para no añadirlo dos veces).
- Decrementa `picks`. Si `picks <= 0` o no quedan opciones, cierra el pack.

### `pack_skip()`

Simplemente pone `gs["pack"] = None`.

---

## 12.8. Selección de joker/consumible: vender y usar

Esto añade interactividad in-game a los jokers y consumibles equipados.

### Estado

- `gs["sel_joker"]`: índice del joker seleccionado, `-1` si ninguno.
- `gs["sel_consu"]`: índice del consumible seleccionado, `-1` si ninguno.
- Solo puede haber uno seleccionado al tiempo (los click handlers de `print_jokers` y `print_consumibles` se ocupan de mutarlos a la vez).

### Cómo se selecciona

- En `print_jokers`, al soltar el ratón tras un clic sobre un joker **sin movimiento** (no fue un arrastre): si ya era el seleccionado lo deseleccionas (toggle), si no, lo seleccionas (y deseleccionas el consumible).
- En `print_consumibles`, al pulsar (sí, aquí no hay drag, así que se gestiona con `mb and not Clk0`): mismo toggle.

### Botones contextuales

`draw_sell_use_buttons(raton)` se llama desde las tres pantallas que tienen jokers visibles (`PantallaJuego`, `PantallaTienda`, `PantallaBlind`). **Solo actúa con `fase_puntos == 0`**: antes se podía vender un joker mientras se puntuaba la mano y la cola de eventos apuntaba a un índice que ya no existía (el juego petaba). Dibuja botones pequeños (`Boton` de 2×1 tiles) sobre el ítem seleccionado:

- **Joker seleccionado**: un único botón `$N` debajo del joker con su precio de venta. Al pulsarlo → `sell_joker(idx)` que añade el dinero, quita el joker, `sel_joker = -1` y recalcula `hs`.
- **Consumible seleccionado**: dos botones, `$1` (vender, fija 1 $) y `use` (usar el planeta). Al usar, `use_planeta(idx)` sube el nivel de la mano correspondiente y consume el planeta.

`joker_x_pos(ji, n)` es un auxiliar que reproduce la fórmula de reparto horizontal de `print_jokers` para saber **dónde** poner el botón pequeño justo debajo del joker correcto.

### Precios

- `joker_sell_value(j)`: `JCOST[rar] // 2 + j.sv`, mínimo 1. Común = 2 $, poco común = 3 $, raro = 4 $ (más lo que haya ganado Egg).
- Vender consumible: fijo 1 $.

---

## 13. Código de prueba

Esta versión no trae modo debug (no hay `DEBUG`, `get_event_name` ni `draw_debug`). Lo único de prueba es la línea marcada `#DBG` en `nueva_partida()`, que da un Ice Cream gratis al empezar cada partida. Para la versión final hay que dejarla en `gs["jokers"] = []`.

---

## 14. Recorrido completo de una mano

Para fijar todo lo anterior, esto es lo que ocurre, en orden, desde que seleccionas cartas hasta que ves la puntuación:

1. **Selección** (`fase_puntos == 0`): en `print_cards`, al hacer clic sobre una carta se alterna `c.sel` (máx. 5). `draw_score_hud` muestra una previsualización usando `detectar_mano` → `(hi, sc)` → `hand_score(hi)` → `(nombre, chips, mult)`. Si la mano tiene nivel > 1, las cifras de previsualización ya incluyen el escalado.
2. **Pulsas "play"** (`handle_play`): se obtienen las cartas seleccionadas (`b`), se detecta la mano (`detectar_mano` → `(hi, sc)`), se sacan nombre/chips/mult con `hand_score(hi)`, se marca `gs["hp"][hi] = True` (esa mano queda registrada como descubierta), se aplica Splash si toca, se fijan los bases (`tot_chips = cb`, `tot_mult = mb`), se calculan `mano_flags`, se actualizan los jokers sticky (`update_sticky`), y se construye la cola con `build_event_queue`. Se entra en `fase_puntos = 1` y se gasta una mano (`hd -= 1`).
3. **Animación** (cada fotograma, mientras `fase_puntos == 1`): `update_event_visuals` resalta lo que toca y `step_queue` avanza la cola. Cada evento, al empezar, ejecuta `apply_event`:
   - las cartas suben (`E_RISE`),
   - cada carta suma sus fichas y lanza su partícula (`E_CSCORE`), repitiéndose si hay retriggers (incluyendo el extra de Hanging Chad en la primera),
   - los jokers que se disparan por carta suman lo suyo (`E_OSCORE`),
   - las cartas que se quedan en la mano actúan una a una (`E_HELD`: su Steel y luego Baron, Shoot the Moon…),
   - los jokers independientes actúan (`E_IND`).

   Los contadores del HUD vibran (shakes) conforme reciben los golpes.
4. **Cierre** (`finalize_score`, al vaciarse la cola): se aplican los jokers descendentes (`F_FCHP_DEC`: Ice Cream −5, autodestrucción si llega al límite), se recalcula `hs`, se suma `tot_chips × tot_mult` a la puntuación de ronda, y se descartan las cartas jugadas. Bifurcación:
   - Si `rs >= blind_req()` → **ronda ganada**: se llama a `start_round_win()`, que aplica los efectos de fin de ronda (Gros Michel 1/6, Cavendish 1/1000, `F_FMUL_DEC` decrementa y posible autodestrucción, Egg sube su valor), calcula el desglose del cash out y resetea `voff`. Fase pasa a `2`.
   - Si `hd <= 0` → intenta `try_mr_bones()`. Si tienes Mr. Bones y `rs >= blind_req()//4`, te salva y vas a `start_round_win`. Si no, **Game Over** (`gm=5`).
   - Si no → sigues jugando: se reparte de nuevo y se vuelve a `fase_puntos = 0`.
5. **Cash out** (`fase_puntos == 2`, §12.5): tras la pausa `co_wait`, `voff` sube hasta `SCREEN_H` arrastrando jokers, cartas, botones, consumibles y contadores; el HUD se queda fijo; el panel de cash out entra desde abajo con sus copias del mundo. Al llegar arriba, fase pasa a `3` y el siguiente clic en el panel llama a `collect_cash_out()`: dinero al monedero y **vas a la tienda** (`enter_shop()` → `gm=3`).
6. **Tienda** (`gm=3`, §12.6): puedes comprar jokers/planetas, abrir packs, vender jokers, usar planetas para subir manos, rerollear, y al final pulsar **next**.
7. **Selección de blind** (`gm=4`): avanzas `blind++` (con vuelta a small y `ant++` cada 3), y eliges entrar al siguiente. `start_blind()` → vuelta a `gm=1`.

---

## 15. Limitaciones y `#TODO`

Cosas que **aún no** están implementadas:

- **Boss blind**: los efectos especiales (bloquear palos, deshabilitar jokers, palabras…) no están implementados. El boss hoy solo es un blind con multiplicador 2× y más recompensa.
- **Tarot cards y Spectral cards**: las cartas tarot y espectrales no existen; solo planetas (`Planeta`). El campo `consu` está pensado para mezclarlos pero hoy todos son planetas.
- **Efectos y sellos de carta**: las constantes `EFFECTS` (Bonus, Mult, Wild, Glass, Steel, Stone, Gold, Lucky) y `SEAL_NAMES` (Red, Blue, Gold, Purple) están definidas y el tooltip las muestra correctamente, pero **no hay forma de aplicarlas a una carta en el juego** (no hay tarot que las añada). Steel Joker (`F_XMUL_PER_EF`) ya lee cartas Steel del mazo, así que el motor de puntuación las soporta — falta el sistema de aplicar el efecto a la carta. El swap de paleta de los sellos (sprite #60 con `SEAL_COL`) tampoco está enganchado al dibujo de carta todavía.
- **Vouchers** (mejoras permanentes que se compran en la tienda boss): no implementados.
- **`E_OPLAY` / `joker_fires_play`**: el camino "joker actúa al jugar la mano" existe pero hoy nunca dispara (reservado).
- **`shake_offset` en cartas/jokers**: la función está lista pero solo se usa en los contadores del HUD; falta engancharla al hover/clic de cartas y jokers.
- **Orden manual no persistente**: el orden conseguido arrastrando cartas a mano dura solo hasta el siguiente reparto (`repartir()` llama a `sort_hand()` y reordena según `sort_mode`).
- **Tooltips de joker/planeta**: las cajas se clampean en X (no se salen por los lados) pero no en Y (pueden salirse por arriba/abajo si el joker está en una posición extrema). `tt_card` sí clampea en Y.
- **Strings en español pendientes**: `DECK_INFO` (texto de cada baraja en el menú) y los textos de `draw_cash_out` están en español aunque el resto de la UI está en inglés. Hay que traducirlos para consistencia.
- **Skip de blind / Tag system**: no se puede saltar un blind (en Balatro real, saltar te da un "Tag" con recompensa).
- **Animaciones de transición**: pasar de juego → cash out tiene scroll, pero tienda → blind y blind → juego son cortes secos.
- **18 jokers `#M`**: son reales pero aquí tienen un efecto provisional (en `JDEFS` está escrito el efecto real). Varios necesitan sistemas que no existen todavía: tarots (Cartomancer, Vagabond), saltar ciega (Throwback), elegir ciega (Burglar, Marble Joker, Madness), añadir cartas al mazo (Hologram), planetas usados (Constellation), cartas en la mano repetidas (Mime), palo de la ronda (Castle) o descartes de figuras (Faceless Joker). Triboulet y Yorick además deberían ser legendarios.
- **Precios por rareza** (`JCOST`) en vez del precio de cada joker.
- **Cavendish / Gros Michel**: Cavendish sale si tienes Gros Michel equipado; en Balatro sale cuando Gros Michel se ha extinguido.
- **Joker de prueba** `#DBG` en `nueva_partida()` (ver §13).
- Muchos jokers aún no tienen `JSPR` y se dibujan con la caja de respaldo (ver §8 para la lista de los que sí).

---

## 16. Glosario rápido

**Claves de `gs` más usadas**
- `gm` pantalla (0 menú · 1 juego · 2 visor · 3 tienda · 4 blind · 5 game over) · `fase_puntos` 0=interacción / 1=puntuando / 2=subiendo pantalla / 3=cash out fijo
- `hand` mano · `b` cartas jugadas · `jokers` jokers · `consu` consumibles (planetas) · `baraja` mazo
- `hd` manos · `ds` descartes · `mn` dinero · `hs` tamaño de mano · `rs` puntuación de ronda · `ant` ante · `rd` ronda · `jslots` huecos de joker
- `tot_chips`/`tot_mult` acumuladores de la mano · `scoring_cards` cartas que puntúan · `mano_flags` (12 bools) tipos presentes · `hand_idx_play` índice de la mano jugada
- `hl` (12 ints) niveles de cada mano · `hp` (12 bools) manos descubiertas
- `ev_queue`/`ev_idx`/`ev_timer` cola de eventos · `active_joker_idx` joker resaltado · `first_match` carta objetivo de Photograph
- `particles` partículas · `shake_*` vibraciones del HUD
- `blind` 0/1/2 (small/big/boss) · `voff` scroll vertical 0→136 al ganar · `co_wait` pausa pre-scroll
- `co_reward`/`co_hands`/`co_interest`/`co_disc`/`co_extra`/`co_total` desglose del cash out · `co_req` puntos requeridos
- `sort_mode` 0=rango / 1=palo · `drag_card`/`drag_joker`/`drag_active`/`drag_px`/`drag_py` estado del arrastre
- `sel_joker`/`sel_consu` ítem seleccionado para vender/usar (`-1` si ninguno)
- `shop_j`/`shop_p` slots de tienda · `pack` pack abierto (dict o None) · `reroll`/`free_rr` coste/rerolls gratis
- `tt_target` tooltip diferido (`("card", …)` / `("joker", …)` / `("planeta", …)`)
- `visor_from` pantalla desde la que se entró al visor

**Prefijos de constantes**
- `E_*` tipos de evento de la cola
- `F_*` familias de joker (patrones de comportamiento)
- `SC_*` condiciones de los jokers sticky
- `H_*` tipos de mano de póker (12 índices de `mano_flags`/`hl`/`hp`)

**Tablas estáticas**
- `JDEFS` definición de cada joker `(nombre, familia, *params)`; el índice = `id`. 93 jokers (ids 0–92)
- `JSPR` cómo dibujar cada joker (indexado por el mismo `id`)
- `JRAR` rareza de cada joker · `JPOOL` IDs agrupados por rareza · `JDEP` dependencias entre jokers (Cavendish → Gros Michel)
- `JCOST = (4, 6, 8)` precio de compra por rareza · `joker_sell_value` precio de venta (mitad, mínimo 1)
- `HAND_DEF` definición de cada tipo de mano `(nombre, chips_base, mult_base, chips_por_lvl, mult_por_lvl)`
- `PLANETS` definición de cada planeta `(nombre, hand_idx, sprite_id)`
- `PACK_DEF`/`PACK_NAME`/`PACK_COL` definición de los 6 tipos de pack
- `EDUR` duración en frames de cada tipo de evento
- `PARTICLE_KINDS` color y prefijo de cada tipo de partícula
- `EFFECTS`/`SEAL_NAMES`/`SEAL_COL` nombres y paletas de efectos de carta y sellos
- `JVT`/`JBOX` plantillas para tooltips y caja de respaldo de joker (evitan switches gigantes)
- `mini_font` fuente de píxeles 3×5
- `ANTE_BASE` / `BLIND_MULT` / `BLIND_REWARD` / `BLIND_NAME` / `INTEREST_CAP` / `CASH_SPEED` / `CASH_WAIT` / `SCREEN_H` — parámetros del sistema de rondas y cash out

**Funciones clave por capa**
- Dibujo: `draw_text`, `dibujar_caja`, `PrintBox`, `Boton`, `dibujar_joker`, `dibujar_planeta`, `draw_card_at`, `draw_tapete`, `draw_contadores`
- Reglas de mano: `detectar_mano` (→ `(hi, sc)`), `hand_score(hi)` (→ `(nombre, chips, mult)`), `calcular_mano_flags` (→ 12 bools), `chips_c`
- Mano / orden: `sort_hand` (rango / palo, respeta `gs["sort_mode"]`)
- Motor de puntuación: `build_event_queue` → `step_queue` → `apply_event`/`apply_joker_effect` → `finalize_score`
- Disparo de jokers: `joker_fires_score`, `joker_fires_ind`, `count_retriggers`, `update_sticky`
- Tooltips: `tt_card`, `tt_joker`, `tt_planeta`, `joker_value_text`
- Pantallas: `PantallaMenu`, `PantallaJuego` (+`draw_money_box`/`draw_side_hud`/`draw_score_hud`/`handle_discard`/`handle_play`/`handle_sort`/`check_mazo_click`), `PantallaVisor`, `PantallaTienda` (+`draw_shop_jslot`/`draw_shop_pslot`/`draw_pack_picker`), `PantallaBlind` (+`blind_panel`), `PantallaGameOver`
- Tienda y packs: `enter_shop`, `roll_shop`, `roll_shop_items`, `do_reroll`, `buy_joker`, `buy_planeta`, `open_pack`, `pack_pick`, `pack_skip`, `roll_joker_unique`, `roll_planeta_unique`
- Sell/use: `sell_joker`, `sell_consu`, `use_planeta`, `joker_sell_value`, `joker_x_pos`, `draw_sell_use_buttons`
- Cash out / rondas: `blind_req`, `ante_base`, `cash_out_money`, `joker_round_money`, `start_round_win`, `try_mr_bones`, `reset_round`, `collect_cash_out`, `shop_next_round`, `start_blind`, `draw_cash_out`
- Setup: `nueva_partida`, `base_hands`, `base_discards`, `start_money`, `joker_slots`, `splash_active`, `has_free_reroll`, `recalc_hs`, `roll_rarity`, `roll_joker`, `joker_price`

---

## 17. Compatibilidad con pocketpy y tamaño

El código se prueba con los dos intérpretes pocketpy que trae TIC-80: el de la 1.1 y el de la 1.2/1.3. Para que funcione en los dos:

- **Nada de generadores dentro de llamadas** (`sorted(x for x in l)`, `any(...)`, `sum(...)`): usar listas por comprensión o bucles.
- **Condiciones en una sola línea.** Un `if (a\n and b):` partido en varias líneas falla en la 1.1.
- **Sin coma final en los parámetros de un `def`**, sin concatenación implícita de strings (`"a" "b"`) y sin `except Error as e` (la 1.1 no lo admite).
- **Ni punto y coma ni `isinstance`** con clases propias: para distinguir `Joker` de `Planeta` se usa `hasattr(x, "xm")`.
- Los comentarios y las líneas en blanco dentro de funciones funcionan bien en las dos.
- **Solo ASCII**: el editor de TIC-80 no muestra tildes ni ñ.

**Tamaño:** el fichero ordenado pesa unos 122 KB. El editor de TIC-80 gratis admite 64 KB de código y el PRO 512 KB (8 bancos); al pegar más de lo que cabe, el editor lo recorta sin avisar.

---

## 18. Novedades

### 0.5.0 (8 oct 2026) — Python ordenado (TIC-80 PRO)

- Código reordenado en 25 secciones con índice, glosario y comentarios; sangría de 1 espacio. Mismos nombres de siempre. Helpers nuevos para quitar código repetido: `dibujar_caja`, `roll_shop_items`, `nueva_partida`, `draw_tapete` y `draw_contadores`.
- Orden de puntuación fiel a Balatro: cartas jugadas → cartas en la mano (Steel, Baron…) → jokers (§9).
- Jokers auditados contra la wiki: fuera los 30 inventados (quedan 93: 75 fieles y 18 `#M`), 16 rarezas corregidas y 3 nombres corregidos (§8).
- `JSPR` comprobado contra los sprites del cartucho: no había desfase; la lista de esta doc era la que estaba mal (§8).
- Bugs arreglados: vender un joker durante la puntuación hacía petar el juego; el visor del mazo enseñaba cartas de la ronda anterior; una Stone podía formar pareja o color para los jokers de tipo de mano; en la pantalla de ciegas no se podía seleccionar un joker para venderlo.
- Verificación: un bot jugando miles de fotogramas (partidas, tienda, sobres, visor, ventas, arrastres) en CPython y en los pocketpy de TIC-80 1.1 y 1.3.1, sin errores, y una mano + descarte + cobro con cada uno de los 93 jokers. Probado también en el emulador de TIC-80 (PRO).

### Versiones anteriores

- Hasta la 0.4.1 el código tenía que caber en los 64 KB de la versión gratuita de TIC-80, por eso priorizaba el espacio. El historial completo está en el [CHANGELOG](../CHANGELOG.es.md).
