# Changelog

*Léelo en otros idiomas: [English](CHANGELOG.md).*

Numeración: el número del medio sube cuando entra un sistema de juego nuevo
(`0.X.0`); el último es para más contenido, mejoras y arreglos (`0.X.Y`). El
juego se queda por debajo de 1.0 hasta que esté completo.

> **Sobre este historial.** Se reconstruyó en octubre de 2026 a partir de
> copias guardadas del código y de los cartuchos. Varias versiones habían
> perdido su número o compartían el mismo (0.1, 0.5, 0.8, 0.9…), así que se
> ordenaron por su contenido (cada una contiene la anterior y algo nuevo) y se
> renumeraron. Las fechas salen de los chats de desarrollo y de la fecha de
> guardado de los cartuchos; la marcada con `~` es aproximada. Entre el
> prototipo y la v0.1.0 hubo otro intento que se perdió.
>
> **Sobre el espacio.** Hasta la v0.4.1 el juego se hizo con la versión gratuita
> de TIC-80, donde todo el código tiene que caber en un banco de 64 KB. Por eso
> las versiones antiguas usan nombres cortos, sangría de 1 espacio y casi ningún
> comentario. La v0.5.0 es la primera hecha con TIC-80 PRO.

## v0.5.0 — 2026-10-08 — Reescritura legible con TIC-80 PRO

- Primera versión hecha con **TIC-80 PRO**: el código ya no tiene que caber en
  un banco de 64 KB, así que el fichero entero se reorganizó en 25 secciones
  comentadas con índice y glosario. Los mismos nombres de siempre; helpers
  nuevos para quitar código repetido (`dibujar_caja`, `roll_shop_items`,
  `nueva_partida`, `draw_tapete`, `draw_contadores`).
- Orden de puntuación fiel a Balatro: cartas jugadas → cartas en la mano
  (Steel, Baron…) → jokers.
- Jokers auditados contra la wiki: fuera los 30 inventados, quedan
  **93 jokers reales** (75 fieles y 18 marcados `#M` con su efecto real
  anotado). 16 rarezas y 3 nombres corregidos.
- `JSPR` comprobado contra los sprites del cartucho: estaba bien.
- Bugs arreglados: vender un joker durante la puntuación hacía petar el juego;
  el visor del mazo enseñaba cartas de la ronda anterior; una Stone podía
  formar pareja o color para los jokers de tipo de mano; en la pantalla de
  ciegas no se podía seleccionar un joker para venderlo.
- Probado en el emulador de TIC-80.

## v0.4.1 — 2026-06-11 — Mejoras de carta y 123 jokers

- Las mejoras de carta ya cuentan al puntuar (`apply_card_ef`): Bonus, Mult,
  Wild, Glass, Steel, Stone, Gold y Lucky.
- Jokers con valor de venta que sube (Egg) y que se comen las mejoras
  (Vampire).
- Jokers nuevos: Midas Mask, Golden Ticket y Lucky Cat (**123** en total).

## v0.4.0 — ~2026-06-09 — Planetas y niveles de mano

- **12 manos de póker**, incluidas las secretas Repóker, Full de color y Color
  de cinco, cada una con su nivel.
- **12 planetas** para subirlas de nivel: se compran en la tienda y se usan
  desde los huecos de consumibles.
- Vender jokers y consumibles, con botones de vender/usar y precio variable.
- Textos del juego en inglés.
- **120 jokers**.

## v0.3.0 — 2026-06-01 — Partida completa

- Pantalla de **ciegas** (pequeña / grande / jefe) con la puntuación de cada
  ante; los antes siguen escalando pasado el 8.
- **Cash out** al acabar la ronda: premio de la ciega, intereses, dinero por
  manos sobrantes y por jokers.
- **Tienda**: jokers por rareza (70 / 25 / 5 %), reroll que sube de precio,
  rerolls gratis y sobres Buffoon (normal, jumbo, mega).
- Pantalla de **game over**, y Mr. Bones para salvarte una vez.
- Ordenar la mano por rango o palo, arrastrar cartas para reordenarlas y
  tooltips de joker de dos líneas.
- **70 jokers** (Walkie Talkie, Blue Joker, Juggler, Popcorn, Golden Joker, To
  the Moon, Splash, Cloud 9, Chaos the Clown…).

## v0.2.3 — 2026-05-28 — HUD y dinero

- HUD separado en sus propias funciones (`draw_score_hud`, `draw_money_box`,
  `handle_play`, `handle_discard`).
- El tamaño de la mano puede cambiar durante la partida.
- Scholar, Bloodstone, Rough Gem, Stuntman e Ice Cream pasan a tener su efecto
  real (5 familias de efecto nuevas).

## v0.2.2 — 2026-05-28 — 57 jokers y tooltips

- **57 jokers**: la familia de ×mult (The Duo, Trio, Family, Order, Tribe),
  jokers que escalan (Ride the Bus, Green Joker, Runner, Square Joker, Spare
  Trousers), jokers de cartas en mano (Baron, Shoot the Moon), Hiker, Ramen,
  Bull, Bootstraps, Misprint, Dusk, Abstract Joker, Mystic Summit, Acrobat…
- Tooltips de cartas y jokers.
- Algunos todavía tenían bugs conocidos, apuntados en los comentarios del
  código.

## v0.2.1 — 2026-05-24 — Partículas y shake

- Partículas en forma de rombo para chips, mult, ×mult y retriggers.
- Shake amortiguado en las cajas de chips y mult y en el nombre de la mano.
- 5 jokers nuevos: Fibonacci, Hack, Arrowhead, Bloodstone y Banner (**29**).
- Recolores de Jimbo para reutilizar un sprite en varios jokers; los jokers
  flotan.

## v0.2.0 — 2026-05-23 — Motor de puntuación

- Todo el estado de la partida vive en un diccionario (`gs`) y cada pantalla
  es su propia función.
- `detectar_mano`: de carta alta a escalera de color, con sus chips y mult
  base, y solo cuentan las cartas que puntúan.
- **Cola de eventos**: cada carta y cada joker puntúa por turnos con su
  animación, como en Balatro.
- **24 jokers** en `JDEFS`, agrupados en familias de efecto (`F_*`).
- HUD con puntuación de la ronda, manos, descartes, dinero, ante y ronda;
  máximo 5 cartas seleccionadas.
- Modo debug para avanzar la cola evento a evento con Z.

## v0.1.1 — 2026-05-08 — Arreglo de bugs

- `repartir` podía leer fuera del mazo; ahora roba de arriba del mazo mezclado
  y para si se vacía.
- `print_cards` ya no divide entre cero con 0 o 1 cartas.
- `eval_hand` usaba una variable que no existía.
- El selector de baraja da la vuelta y solo rehace el mazo si cambia.
- Antirrebote del clic en la pila del mazo y en el visor.

## v0.1.0 — 2026-04-21 — Empiezo de cero en Python

- Empiezo de cero en Python (pocketpy).
- Menú principal con el título animado y **8 barajas**, cada una con su regla.
- Mano de 8 cartas con onda, clic para seleccionar, jugar y descartar.
- Visor del mazo con recuento por palo y rango.
- Fuente de píxeles propia de 3×5 y botones con sprites y cambio de paleta.

## v0.0.1 — 2025-12-18 — Retoques del prototipo

- Dos cajas más de interfaz y limpieza en el prototipo de Lua.

## v0.0.0 — 2025-06-20 — Prueba de concepto en Lua

- "Balaro": mano de 8 cartas de un mazo mezclado, elegidas con un cursor de
  teclado (hasta 5).
- Detecta manos de póker de carta alta a escalera real y enseña sus chips y
  mult base.
