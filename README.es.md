# Bitlatro

> Una versión compacta y fiel de **Balatro** para la consola fantasía [TIC-80](https://tic80.com), escrita en Python.

*Léelo en otros idiomas: [English](README.md).*

## ¿Qué es?

Bitlatro es un roguelike de póker que mete el bucle central de Balatro en la
pantalla de 240×136 de TIC-80. Formas una mano de póker, la juegas por
fichas × multiplicador, encadenas **jokers** con sinergias, subes de nivel tus
manos con **planetas** y superas **ciegas** cada vez más duras a lo largo de
los antes, todo con una fuente de píxeles hecha a mano, widgets de UI propios y
una puntuación animada paso a paso.

Todo el pixel art y la música son originales.

## Características

- **8 barajas**, cada una con su regla (descarte extra, mano extra, baraja de
  economía sin intereses, empezar con $10, +1 hueco de joker / −1 mano, baraja
  de dos palos, solo del 1 al 10, rangos aleatorios).
- **93 jokers**, todos del juego real (75 fieles y 18 con un efecto
  provisional), en rarezas común / poco común / rara: mult plano y ×mult, por
  palo, por rango, por tipo de mano, *retriggers*, jokers que escalan, bonus
  por cartas en mano, jokers de economía y mecánicas de destrucción
  (Gros Michel → Cavendish).
- **12 manos de póker**, incluidas las secretas **Repóker**, **Full de color**
  y **Color de cinco**, cada una con su nivel y sus **12 planetas**.
- **Modificadores de carta**: 8 mejoras (Bonus, Mult, Wild, Glass, Steel,
  Stone, Gold, Lucky), ediciones foil/holo y 4 sellos.
- **Tienda** con rerolls, rerolls gratis y **sobres** (normal / jumbo / mega).
- **Ciegas** (pequeña / grande / jefe) con su puntuación y recompensa, **antes**
  que escalan más allá de los 8 base y un *cash out* con intereses.
- **Presentación con chicha**: puntuación animada por cola de eventos,
  partículas de fichas/mult/×mult/dinero, shake amortiguado, arrastrar y soltar
  cartas y jokers, y un visor del mazo con estadísticas en vivo.

## Cómo se juega

1. **Selecciona** hasta 5 cartas de tu mano (clic o arrastrando).
2. **Juega** la mano para puntuar `fichas × mult`, o **descarta** para cambiar
   cartas.
3. Supera la **puntuación de la ciega** antes de quedarte sin manos.
4. **Cobra** y gasta en la **tienda**: jokers, planetas y sobres, haz *reroll*
   y elige la siguiente ciega.
5. Aguanta todos los antes que puedas.

## Cómo ejecutarlo

1. Instala [TIC-80](https://tic80.com/create) (una versión con soporte de
   Python).
2. Descarga [`bitlatro.tic`](bitlatro.tic) y arrástralo a la ventana de TIC-80,
   o escribe `load bitlatro.tic` y luego `run` en la consola.

El cartucho lleva el código, los sprites, el mapa y la música. El mismo código
está en [`python/bitlatro.py`](python/bitlatro.py) para poder leerlo y ver los
cambios aquí.

## Estructura del código

Todo vive en un único script (`python/bitlatro.py`), repartido en 25 secciones
comentadas con un índice al principio:

| Área | Piezas clave |
|------|--------------|
| Texto y color | `mini_font`, `draw_text`, `set_col` / `reset_col` |
| Estado y datos | estado global `gs`, `SUITS`, `HAND_DEF`, `PLANETS`, `ANTE_BASE`, `BLIND_*` |
| Jokers | definiciones `JDEFS`, familias de efecto `F_*`, rarezas `JRAR` / `JPOOL`, sprites `JSPR` |
| Entidades | `Carta`, `Joker`, `Planeta`, `Mazo` |
| Dibujo | `draw_card_at`, `print_cards`, `dibujar_joker`, `dibujar_planeta`, tooltips, `PrintBox` / `Boton`, partículas |
| Lógica de manos | `detectar_mano`, `hand_score`, `calcular_mano_flags` |
| Puntuación | `build_event_queue`, `step_queue`, `apply_event`, `apply_joker_effect`, `apply_card_ef` |
| Economía / tienda | `roll_shop`, `buy_joker`, `buy_planeta`, `open_pack`, `pack_pick`, `cash_out_money` |
| Pantallas (`gm`) | `PantallaMenu` (0), `PantallaJuego` (1), `PantallaVisor` (2), `PantallaTienda` (3), `PantallaBlind` (4), `PantallaGameOver` (5) |
| Punto de entrada | `TIC()` |

El recorrido completo, función por función, está en la
[documentación técnica](docs/TECHNICAL.es.md).

## Cómo ha llegado hasta aquí

Bitlatro empezó en **junio de 2025** como una pequeña prueba de concepto en Lua
("Balaro", guardada en [`prototype/`](prototype/)): una mano que se manejaba
con el teclado y solo detectaba manos de póker. En **abril de 2026** empecé de
cero en Python y lo fui ampliando versión a versión: primero el motor de
puntuación, luego la partida completa y después los planetas y muchos más
jokers.

Hasta la **v0.4.1** usaba la versión gratuita de TIC-80, donde todo el código
tiene que caber en un único banco de 64 KB. La prioridad era el espacio:
nombres cortos, sangría de 1 espacio, sin comentarios y recortando todo lo
posible. La **v0.5.0** es la primera hecha con **TIC-80 PRO**: el límite de
64 KB ya no aplica, así que reescribí el código entero para que se pueda leer y
lo comenté.

El historial anterior a octubre de 2026 está reconstruido a partir de copias
guardadas. Varias versiones habían perdido su número o compartían el mismo, así
que se ordenaron por su contenido y se renumeraron. Cada versión tiene su tag y
el detalle completo está en el [CHANGELOG](CHANGELOG.es.md).

| Versión | Fecha | Lo principal |
|---------|-------|--------------|
| `v0.0.0` | jun 2025 | Prueba de concepto en Lua: mano de 8 cartas y detección de manos |
| `v0.0.1` | dic 2025 | Retoques del prototipo |
| `v0.1.0` | abr 2026 | Empiezo de cero en Python: menú de barajas, mano y visor del mazo |
| `v0.1.1` | may 2026 | Arreglo de bugs |
| `v0.2.0` | may 2026 | Motor de puntuación por cola de eventos y los primeros 24 jokers |
| `v0.2.1` | may 2026 | Partículas, shake y 29 jokers |
| `v0.2.2` | may 2026 | 57 jokers (incluidos los que escalan) y tooltips |
| `v0.2.3` | may 2026 | HUD rehecho, dinero y efectos de tamaño de mano |
| `v0.3.0` | jun 2026 | Partida completa: ciegas, cash out, tienda, sobres y game over |
| `v0.4.0` | jun 2026 | Planetas, niveles de mano, 12 manos y vender jokers |
| `v0.4.1` | jun 2026 | Mejoras de carta en la puntuación y 123 jokers |
| `v0.5.0` | oct 2026 | Reescritura con TIC-80 PRO: código legible y solo jokers reales (93) |

## Hoja de ruta

- [ ] Efectos fieles para los 18 jokers provisionales
- [ ] Variantes de ciega jefe
- [ ] Vales, cartas de tarot y espectrales
- [ ] Saltar ciegas y etiquetas
- [ ] Fondo animado estilo Balatro
- [ ] Guardar / continuar partida

## Créditos y licencia

Hecho por **LaCroquetona**, pixel art y música incluidos.

Bitlatro es un proyecto fan sin ánimo de lucro inspirado en *Balatro*, de
LocalThunk (publicado por Playstack). No tiene relación con ellos ni cuenta con
su respaldo, y todos los derechos de Balatro pertenecen a sus dueños. La
[licencia](LICENSE) MIT cubre solo el código y los recursos propios de este
proyecto.
