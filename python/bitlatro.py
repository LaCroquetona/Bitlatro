# title:   Bitlatro
# author:  Croquetona
# desc:    this is a compact version of Balatro
# license: MIT License
# version: 0.5.1
# script:  python

# =============================================================================
#  BITLATRO - version reducida de Balatro para TIC-80 (Python / pocketpy)
# =============================================================================
#
#  TIC-80 llama a TIC() 60 veces por segundo. Todo el tiempo del juego se mide
#  en fotogramas (contadores que suben o bajan en cada TIC()). Toda la partida
#  vive en un unico diccionario global: gs ("game state").
#
#  INDICE (cada seccion empieza con un bloque como este)
#
#   DATOS
#    1. Texto y color ............ mini_font, draw_text, set_col, reset_col
#    2. Cartas ................... SUITS, EFFECTS, SEAL_NAMES, DECK_INFO
#    3. Manos de poker ........... H_*, HAND_DEF, PLANETS
#    4. Jokers: datos ............ F_*, SC_*, JDEFS, JRAR, JPOOL, JSPR, JDEP
#    5. Rondas, ciegas y tienda .. ANTE_BASE, BLIND_*, PACK_DEF, ...
#    6. Motor de eventos ......... E_*, EDUR, PARTICLE_KINDS
#    7. Estado global ............ gs
#   LOGICA
#    8. Animacion ................ onda_y, shake_offset, counter
#    9. Cajas, botones, raton .... dibujar_caja, PrintBox, Boton, boton_clic,
#                                  raton_en, clic_nuevo
#   10. Modelo ................... Carta, Joker, Planeta, Mazo
#   11. Reglas de mano ........... analizar_cartas, detectar_mano, ...
#   12. Reglas de partida ........ manos/descartes/dinero base, recalc_hs,
#                                  jokers_de, ...
#   13. Jokers: cuando actuan .... joker_fires_*, count_retriggers, update_sticky
#   14. Jokers y cartas: efecto .. joker_aporte, apply_joker_effect, apply_card_ef
#   15. Particulas ............... spawn_particle, update_and_draw_particles
#   16. Motor de puntuacion ...... build_event_queue, step_queue, finalize_score
#   17. Fin de ronda y cash out .. start_round_win, cash_out_money, ...
#   18. Tienda y sobres .......... roll_shop, buy_*, open_pack, ...
#   19. Vender y usar ............ sell_joker, use_planeta, ...
#   DIBUJO Y PANTALLAS
#   20. Textos de joker .......... JVT, joker_value_text, JDESC, JBOX
#   21. Cartas, jokers, planetas . draw_card_at, print_cards, print_jokers, ...
#   22. Tooltips ................. dibujar_tooltip, tt_card, tt_joker, tt_planeta
#   23. HUD ...................... draw_side_hud, draw_score_hud, draw_cash_out
#   24. Pantallas ................ PantallaMenu, PantallaJuego, ... (gs["gm"])
#   25. Arranque y TIC()
#
#  GLOSARIO DE ABREVIATURAS (claves de gs y variables cortas)
#   gm  pantalla (GM_*)       fp / fase_puntos  fase de la mano (FP_*)
#   hd  manos restantes       ds  descartes restantes
#   mn  dinero                hs  tamano de mano (cartas que se reparten)
#   rs  puntuacion de ronda   ant / rd  ante / ronda
#   b   cartas jugadas        hl / hp  nivel / descubierta de cada mano
#   su  palo de una carta     va  valor (1 = As, 11 = J, 12 = Q, 13 = K)
#   ef  efecto (mejora)       st  sello (Carta) o estado acumulado (Joker)
#   ed  edicion foil/holo     xm  multiplicador mutable de un Joker
#   an  desfase de flotacion  ht  contador de hover para el tooltip
#   d   = JDEFS[j.id], la definicion del joker (d[0] nombre, d[1] familia,
#         d[2], d[3]... parametros, ver la leyenda de familias en la seccion 4)
#
#  Marcas en comentarios:  #DBG = linea de prueba, quitar en la version final
#                          FIX: = arreglo de un bug (explica cual)
#                          #M   = joker real con efecto no fiel a Balatro
# =============================================================================

import random
import math


# =============================================================================
#  1. TEXTO Y COLOR
# =============================================================================
# La fuente de TIC-80 es demasiado grande para el HUD, asi que usamos una
# fuente propia de 3x5 pixeles: cada caracter son 5 filas de 3 pixeles
# ("1" = pixel encendido). Solo existen estos caracteres: si se intenta
# escribir otro, draw_text falla.

mini_font = {
 "A": ["010", "101", "111", "101", "101"],
 "B": ["110", "101", "110", "101", "110"],
 "C": ["011", "100", "100", "100", "011"],
 "D": ["110", "101", "101", "101", "110"],
 "E": ["111", "100", "110", "100", "111"],
 "F": ["111", "100", "110", "100", "100"],
 "G": ["011", "100", "101", "101", "011"],
 "H": ["101", "101", "111", "101", "101"],
 "I": ["111", "010", "010", "010", "111"],
 "J": ["001", "001", "001", "101", "010"],
 "K": ["101", "101", "110", "101", "101"],
 "L": ["100", "100", "100", "100", "111"],
 "M": ["111", "111", "101", "101", "101"],
 "N": ["110", "101", "101", "101", "101"],
 "O": ["010", "101", "101", "101", "010"],
 "P": ["110", "101", "110", "100", "100"],
 "Q": ["010", "101", "101", "111", "011"],
 "R": ["110", "101", "111", "110", "101"],
 "S": ["011", "100", "010", "001", "110"],
 "T": ["111", "010", "010", "010", "010"],
 "U": ["101", "101", "101", "101", "011"],
 "V": ["101", "101", "101", "101", "010"],
 "W": ["101", "101", "111", "111", "101"],
 "X": ["101", "101", "010", "101", "101"],
 "Y": ["101", "101", "010", "010", "010"],
 "Z": ["111", "001", "010", "100", "111"],
 "0": ["011", "101", "101", "101", "110"],
 "1": ["010", "110", "010", "010", "111"],
 "2": ["110", "001", "010", "100", "111"],
 "3": ["110", "001", "010", "001", "110"],
 "4": ["101", "101", "111", "001", "001"],
 "5": ["111", "100", "110", "001", "110"],
 "6": ["011", "100", "111", "101", "111"],
 "7": ["111", "001", "010", "100", "100"],
 "8": ["111", "101", "111", "101", "111"],
 "9": ["111", "101", "111", "001", "111"],
 " ": ["000", "000", "000", "000", "000"],
 ",": ["000", "000", "000", "010", "001"],
 "$": ["011", "110", "011", "110", "010"],
 "/": ["001", "010", "010", "010", "100"],
 "<": ["001", "010", "100", "010", "001"],
 ">": ["100", "010", "001", "010", "100"],
 ":": ["000", "010", "000", "010", "000"],
 "+": ["000", "010", "111", "010", "000"],
 "-": ["000", "000", "111", "000", "000"],
 ".": ["000", "000", "000", "000", "010"],
 "[": ["011", "010", "010", "010", "011"],
 "]": ["110", "010", "010", "010", "110"],
 "?": ["111", "001", "010", "000", "010"],
 "=": ["000", "111", "000", "111", "000"],
 "(": ["001", "010", "010", "010", "001"],
 ")": ["100", "010", "010", "010", "100"],
}


def draw_text(txt, x, y, col):
 # Pinta txt pixel a pixel con mini_font. Cada caracter ocupa 3 px de
 # ancho + 1 de separacion (avanza 4 px). Admite minusculas (se pasan a
 # mayusculas para buscar el glifo).
 for i in txt:
  glyph = mini_font[i.upper()]
  for m in glyph:
   # m es una fila del glifo: volvemos 3 px a la izquierda y bajamos 1
   x -= 3
   y += 1
   for j in m:
    x += 1
    if j == "1":
     pix(x, y, col)
  # deshacemos las 5 bajadas y pasamos al siguiente caracter
  y -= 5
  x += 4


def set_col(slot, col):
 # Cambia el color 'slot' de la paleta por el color 'col' escribiendo en el
 # mapa de paleta de la VRAM (0x3FF0). Sirve para "tenir" sprites sin tener
 # una copia del sprite por cada color.
 poke4(0x3FF0 * 2 + slot, col)


def reset_col():
 # Devuelve a su color original los slots de paleta que solemos tocar.
 set_col(6, 6)
 set_col(7, 7)
 set_col(14, 14)
 set_col(2, 2)


# =============================================================================
#  2. CARTAS
# =============================================================================
# Palos (c.su): 0 picas, 1 corazones, 2 treboles, 3 diamantes.
# Los palos impares (corazones y diamantes) se pintan en rojo.
SUITS = ("SPADES", "HEARTS", "CLUBS", "DIAMONDS")

# Efectos / mejoras de carta (c.ef). 0 = sin efecto.
EF_BONUS = 1  # +30 fichas al puntuar
EF_MULT = 2   # +4 mult al puntuar
EF_WILD = 3   # cuenta como cualquier palo
EF_GLASS = 4  # x2 mult al puntuar, 1 entre 4 de romperse
EF_STEEL = 5  # x1.5 mult si se queda en la mano (no jugada)
EF_STONE = 6  # 50 fichas fijas, no cuenta para formar la mano
EF_GOLD = 7   # $3 al final de ronda si se queda en la mano
EF_LUCKY = 8  # 1/5: +20 mult, 1/15: +$20
# Nombre de cada efecto (por indice EF_*), para el tooltip
EFFECTS = ("", "Bonus", "Mult", "Wild", "Glass", "Steel", "Stone", "Gold", "Lucky")

# Sellos (c.st). De momento solo se muestran en el tooltip.
SEAL_NAMES = ("", "Red", "Blue", "Gold", "Purple")
# (color_interior, color_borde) de cada sello. Reservado para tenir el
# sprite del sello (#60) con cambios de paleta; todavia no se usa.
SEAL_COL = ((3, 2), (11, 12), (10, 9), (1, 13))

# Barajas del menu (Mazo.dt), con su nombre en Balatro
BAR_ROJA = 0        # Red Deck:       +1 descarte
BAR_AZUL = 1        # Blue Deck:      +1 mano
BAR_VERDE = 2       # Green Deck:     sin interes; $2 por mano y $1 por descarte que queden
BAR_AMARILLA = 3    # Yellow Deck:    empiezas con $10 extra ($14)
BAR_NEGRA = 4       # Black Deck:     +1 hueco de joker, -1 mano
BAR_DAMERO = 5      # Checkered Deck: solo picas y corazones (cada carta x2)
BAR_ABANDONADA = 6  # Abandoned Deck: sin figuras (del 1 al 10)
BAR_ERRATICA = 7    # Erratic Deck:   52 cartas con valor y palo al azar

# Dibujo y texto de cada baraja en el menu (por indice BAR_*):
#   (sprite_del_lomo, color_para_el_slot_2, lineas_de_descripcion)
# y cada linea es (texto, color).
DECK_INFO = (
 (64, 2, (("tienes un", 2), ("descarte mas", 2))),
 (64, 7, (("tienes una", 7), ("mano mas", 7))),
 (64, 1, (("no genera interese,", 1), ("2$ por mano y 1$ por", 1), ("descarte restante", 1))),
 (64, 8, (("comienzas con 14$", 8),)),
 (64, 15, (("tienes un joker", 14), ("mas, pero una", 14), ("mano menos", 14))),
 (65, 2, (("una baraja que", 2), ("solo tiene picas", 14), ("y corazones", 2))),
 (66, 2, (("una baraja", 9), ("con numeros", 10), ("del 1 al 10", 9))),
 (67, 2, (("baraja de 52 cartas", 8), ("pero los numeros", 3), ("estan randomizados", 7))),
)


# =============================================================================
#  3. MANOS DE POKER
# =============================================================================
# Indice de cada tipo de mano. Se usa en HAND_DEF, PLANETS, gs["hl"] (niveles),
# gs["hp"] (manos descubiertas) y gs["mano_flags"].
H_PAR = 0   # Pair
H_DPA = 1   # Two Pair
H_TRI = 2   # Three of a Kind
H_ESC = 3   # Straight
H_COL = 4   # Flush
H_FUL = 5   # Full House
H_POK = 6   # Four of a Kind
H_HC = 7    # High Card
H_SF = 8    # Straight Flush
H_5K = 9    # Five of a Kind   (secreta)
H_FH = 10   # Flush House      (secreta)
H_5KF = 11  # Flush Five       (secreta)

# (nombre, fichas_base, mult_base, fichas_por_nivel, mult_por_nivel)
# Nivel 1 = base. Cada nivel extra suma fichas_por_nivel y mult_por_nivel.
HAND_DEF = (
 ("PAIR", 10, 2, 15, 1),
 ("TWO PAIR", 20, 2, 20, 1),
 ("THREE KIND", 30, 3, 20, 2),
 ("STRAIGHT", 30, 4, 30, 3),
 ("FLUSH", 35, 4, 15, 2),
 ("FULL HOUSE", 40, 4, 25, 2),
 ("FOUR KIND", 60, 7, 30, 3),
 ("HIGH CARD", 5, 1, 10, 1),
 ("STR. FLUSH", 100, 8, 40, 4),
 ("FIVE KIND", 120, 12, 35, 3),
 ("FLUSH HOUSE", 140, 14, 40, 4),
 ("FLUSH FIVE", 160, 16, 50, 3),
)

# Planetas: (nombre, mano_que_sube, sprite). Usar uno = +1 nivel a esa mano.
# Los 3 ultimos (manos secretas) no salen en la tienda hasta que juegas
# esa mano al menos una vez (ver roll_planeta_unique).
PLANETS = (
 ("MERCURY", H_PAR, 208),
 ("VENUS", H_TRI, 209),
 ("EARTH", H_FUL, 210),
 ("MARS", H_POK, 211),
 ("JUPITER", H_COL, 212),
 ("SATURN", H_ESC, 213),
 ("URANUS", H_DPA, 214),
 ("NEPTUNE", H_SF, 215),
 ("PLUTO", H_HC, 216),
 ("PLANET X", H_5K, 217),
 ("CERES", H_FH, 218),
 ("ERIS", H_5KF, 219),
)


# =============================================================================
#  4. JOKERS: DATOS
# =============================================================================
# Hay muchos jokers pero pocos comportamientos. Cada comportamiento es una
# FAMILIA (F_*). Un joker se declara en JDEFS como (nombre, familia, params...)
# y toda la logica hace "switch" sobre la familia. Un joker nuevo que encaje
# en una familia existente = una linea en JDEFS.
#
# Leyenda: que significa cada parametro segun la familia.
#   d[2], d[3], d[4] son los parametros (d[0] es el nombre, d[1] la familia).
#   "palo" es 0-3 (ver SUITS), "rangos" es una tupla de valores (1 = As).

#   --- puntuacion fija / por tipo de mano ---
F_FMUL = 0            # +d[2] mult siempre
F_FCHP = 1            # +d[2] fichas siempre
F_XMUL = 2            # x d[2] mult siempre
F_HMUL = 3            # +d[2] mult si la mano contiene el tipo d[3] (H_*)
F_HCHP = 4            # +d[2] fichas si la mano contiene el tipo d[3]
#   --- por carta puntuada ---
F_SMUL = 5            # +d[2] mult por carta del palo d[3] (o Wild)
F_RMUL = 6            # +d[2] mult por carta con rango en d[3]
F_SCHP = 7            # +d[2] fichas por carta del palo d[3] (o Wild)
F_RCHP = 8            # +d[2] fichas por carta con rango en d[3]
F_RTRG = 9            # retrigger: repite las cartas con rango en d[2]
F_SZMUL = 10          # +d[2] mult si juegas d[3] cartas o menos
F_RXFIRST = 11        # x d[2] mult en la PRIMERA carta puntuada con rango en d[3]
F_STENCIL = 12        # x1 mult por hueco de joker vacio (el propio cuenta)
F_CHIP_DISC = 13      # +d[2] fichas por descarte que te queda
F_NJOK_M = 14         # +d[2] mult por joker equipado
F_NODISC_M = 15       # +d[2] mult si no te quedan descartes
F_HD_LAST_X = 16      # x d[2] mult en la ultima mano de la ronda
F_BULL = 17           # +d[2] fichas por cada $ que tienes
F_STICKY_M = 18       # +j.st mult; j.st crece d[2] segun la condicion d[3] (SC_*), param d[4]
F_STICKY_C = 19       # +j.st fichas; igual que F_STICKY_M
F_HELD_R = 20         # por carta EN LA MANO (no jugada) con rango en d[3]: d[2] mult
                      #   d[4] = 0 -> suma (+mult), d[4] = 1 -> multiplica (x mult)
F_HXMUL = 21          # x d[2] mult si la mano contiene el tipo d[3]
F_HIKER = 22          # cada carta puntuada gana +d[2] fichas para siempre (c.bc)
F_RAND_M = 23         # +0..d[2] mult al azar
F_BOOTS = 24          # +d[2] mult por cada d[3] $ que tienes
F_DUSK = 25           # retrigger de todas las cartas en la ultima mano
F_RAMEN = 26          # x j.xm mult (empieza en d[2]); pierde 0.01 por carta descartada,
                      #   se destruye al llegar a x1
F_RCM = 27            # +d[2] fichas y +d[3] mult por carta con rango en d[4]
F_FCHP_DEC = 28       # +j.st fichas (empieza en d[2]); baja d[3] por mano jugada,
                      #   se destruye al llegar a d[4]
F_SXPROB = 29         # x d[2] mult por carta del palo d[4], con probabilidad 1/d[3]
F_HS_MOD = 30         # +d[2] fichas y cambia el tamano de mano en d[3]
F_SMONEY = 31         # +$d[2] por carta puntuada del palo d[3]
F_DECK_C = 32         # +d[2] fichas por carta que queda en el mazo
F_FMUL_DEC = 33       # +j.st mult (empieza en d[2]); baja d[3] al ganar una ronda,
                      #   se destruye al llegar a 0
#   --- fin de ronda (cash out) ---
F_EOR_MONEY = 34      # +$d[2] al final de ronda
F_EOR_DISC = 35       # +$d[2] por descarte si no usaste ninguno
F_EOR_INT = 36        # interes extra (cada uno suma otra vez el interes base)
F_EOR_DECK_RANK = 37  # +$d[2] por cada carta del mazo de rango d[3]
#   --- reglas especiales ---
F_SPLASH = 38         # todas las cartas jugadas puntuan
F_FIRST_RTRG = 39     # +d[2] retriggers a la primera carta puntuada
F_HAND_SIZE = 40      # +d[2] tamano de mano
F_BONES = 41          # te salva de perder si llegas a 1/4 de la ciega (y se destruye)
F_FREE_REROLL = 42    # 1 reroll gratis en cada visita a la tienda
F_XMUL_PER_EF = 43    # x(1 + d[2] * cartas del mazo con efecto d[3] (EF_*)) mult
F_EOR_SV = 44         # su valor de venta sube $d[2] cada ronda ganada
F_MIDAS = 45          # las figuras puntuadas se vuelven Gold
F_GTICK = 46          # +$4 por cada carta Gold puntuada
F_VAMP = 47           # x j.xm mult; +0.1 por carta con efecto puntuada (y le quita el efecto)
F_LUCKY = 48          # x j.xm mult; +0.25 cada vez que una carta Lucky acierta

# Condiciones de crecimiento de F_STICKY_M / F_STICKY_C (d[3]).
# Se evaluan una vez al jugar la mano, en update_sticky().
SC_NO_FACE = 0      # crece si no puntua ninguna figura; si puntua alguna vuelve a 0
SC_PLAYED = 1       # crece en cada mano jugada (Green Joker pierde 1 al descartar)
SC_HAND_FLAG = 2    # crece si la mano contiene el tipo d[4]
SC_SIZE_EQ = 3      # crece si juegas exactamente d[4] cartas
SC_RANK_SCORED = 4  # crece por cada carta puntuada con rango en d[4]

# Jokers con reglas propias (por id)
J_GROS = 20  # Gros Michel: 1/6 de destruirse al ganar una ronda
J_CAVE = 30  # Cavendish:   1/1000 de destruirse al ganar una ronda

# Dependencias: {joker: joker_requerido}. Cavendish solo sale en la tienda si
# tienes a Gros Michel equipado.
JDEP = {J_CAVE: J_GROS}

# Precio de compra por rareza (0 comun, 1 poco comun, 2 raro).
# Se venden por la mitad (minimo $1), ver joker_sell_value.
JCOST = (4, 6, 8)

# Definicion de cada joker. EL INDICE EN LA LISTA ES SU ID: no reordenar ni
# borrar lineas sin actualizar tambien JRAR y JSPR (van por el mismo id).
# Columnas de la derecha:
#   marcas: F = funciona comprobado, S = tiene sprite propio
#   estado: (vacio) = real y fiel a Balatro
#           #M      = real pero su efecto aqui NO es el de Balatro (se dice el real)
# Auditado contra balatrowiki.org en oct 2026: de 123 jokers, 30 eran
# inventados y se han quitado. Quedan 93: 75 fieles y 18 #M.
# Los precios son por rareza (JCOST), no el precio exacto de cada joker.
JDEFS = [
 # (nombre, familia, parametros...)                                id  rareza  marcas  estado
 ("Joker", F_FMUL, 4),                                           #   0  comun   F S
 ("Jolly Joker", F_HMUL, 8, H_PAR),                              #   1  comun   F S
 ("Zany Joker", F_HMUL, 12, H_TRI),                              #   2  comun   F S
 ("Mad Joker", F_HMUL, 10, H_DPA),                               #   3  comun   F S
 ("Crazy Joker", F_HMUL, 12, H_ESC),                             #   4  comun   F S
 ("Droll Joker", F_HMUL, 10, H_COL),                             #   5  comun   F S
 ("Sly Joker", F_HCHP, 50, H_PAR),                               #   6  comun   F S
 ("Wily Joker", F_HCHP, 100, H_TRI),                             #   7  comun   F S
 ("Clever Joker", F_HCHP, 80, H_DPA),                            #   8  comun   F S
 ("Devious Joker", F_HCHP, 100, H_ESC),                          #   9  comun   F S
 ("Crafty Joker", F_HCHP, 80, H_COL),                            #  10  comun   F S
 ("Greedy Joker", F_SMUL, 3, 3),                                 #  11  comun   F S
 ("Lusty Joker", F_SMUL, 3, 1),                                  #  12  comun   F S
 ("Wrathful Joker", F_SMUL, 3, 0),                               #  13  comun   F S
 ("Gluttonous Joker", F_SMUL, 3, 2),                             #  14  comun   F
 ("Scholar", F_RCM, 20, 4, (1,)),                                #  15  comun   F S
 ("Smiley Face", F_RMUL, 5, (11, 12, 13)),                       #  16  comun   F S
 ("Even Steven", F_RMUL, 4, (2, 4, 6, 8, 10)),                   #  17  comun   F S
 ("Odd Todd", F_RCHP, 31, (1, 3, 5, 7, 9)),                      #  18  comun   F S
 ("Sock and Buskin", F_RTRG, (11, 12, 13)),                      #  19  poco    F S
 ("Gros Michel", F_FMUL, 15),                                    #  20  comun   F S
 ("Half Joker", F_SZMUL, 20, 3),                                 #  21  comun   F S
 ("Photograph", F_RXFIRST, 2, (11, 12, 13)),                     #  22  comun   F S
 ("Joker Stencil", F_STENCIL, 0),                                #  23  poco    F S
 ("Fibonacci", F_RMUL, 8, (1, 2, 3, 5, 8)),                      #  24  poco    F S
 ("Hack", F_RTRG, (2, 3, 4, 5)),                                 #  25  poco    F S
 ("Arrowhead", F_SCHP, 50, 0),                                   #  26  poco    F
 ("Bloodstone", F_SXPROB, 1.5, 2, 1),                            #  27  poco    F
 ("Banner", F_CHIP_DISC, 30),                                    #  28  comun   F S
 ("Scary Face", F_RCHP, 30, (11, 12, 13)),                       #  29  comun   F S
 ("Cavendish", F_XMUL, 3),                                       #  30  comun   F S
 ("Wee Joker", F_STICKY_C, 8, SC_RANK_SCORED, (2,)),             #  31  raro    F S
 ("Onyx Agate", F_SMUL, 7, 2),                                   #  32  poco    F
 ("The Duo", F_HXMUL, 2, H_PAR),                                 #  33  raro    F
 ("The Tribe", F_HXMUL, 2, H_COL),                               #  34  raro    F
 ("The Order", F_HXMUL, 3, H_ESC),                               #  35  raro    F
 ("The Trio", F_HXMUL, 3, H_TRI),                                #  36  raro    F
 ("The Family", F_HXMUL, 4, H_POK),                              #  37  raro    F
 ("Rough Gem", F_SMONEY, 1, 3),                                  #  38  poco    F
 ("Misprint", F_RAND_M, 23),                                     #  39  comun   F S     (ajustar animacion)
 ("Dusk", F_DUSK),                                               #  40  poco    F
 ("Bootstraps", F_BOOTS, 2, 5),                                  #  41  poco    F
 ("Stuntman", F_HS_MOD, 250, -2),                                #  42  raro    F
 ("Ice Cream", F_FCHP_DEC, 100, 5, 0),                           #  43  comun   F S
 ("Abstract Joker", F_NJOK_M, 3),                                #  44  comun   F
 ("Mystic Summit", F_NODISC_M, 15),                              #  45  comun   F
 ("Acrobat", F_HD_LAST_X, 3),                                    #  46  poco    F
 ("Bull", F_BULL, 2),                                            #  47  poco    F
 ("Ride the Bus", F_STICKY_M, 1, SC_NO_FACE, 0),                 #  48  comun   F
 ("Green Joker", F_STICKY_M, 1, SC_PLAYED, 0),                   #  49  comun   F
 ("Hiker", F_HIKER, 5),                                          #  50  poco    F
 ("Ramen", F_RAMEN, 2),                                          #  51  poco    F
 ("Runner", F_STICKY_C, 15, SC_HAND_FLAG, H_ESC),                #  52  comun   F
 ("Square Joker", F_STICKY_C, 4, SC_SIZE_EQ, 4),                 #  53  comun   F
 ("Spare Trousers", F_STICKY_M, 2, SC_HAND_FLAG, H_DPA),         #  54  poco    F
 ("Shoot the Moon", F_HELD_R, 13, (12,), 0),                     #  55  comun   F
 ("Baron", F_HELD_R, 1.5, (13,), 1),                             #  56  raro    F
 ("Walkie Talkie", F_RCM, 10, 4, (10, 4)),                       #  57  comun   F
 ("Blue Joker", F_DECK_C, 2),                                    #  58  comun   F S
 ("Juggler", F_HAND_SIZE, 1),                                    #  59  comun
 ("Popcorn", F_FMUL_DEC, 20, 4),                                 #  60  comun   F
 ("Golden Joker", F_EOR_MONEY, 4),                               #  61  comun
 ("Delayed Gratification", F_EOR_DISC, 2),                       #  62  comun
 ("To the Moon", F_EOR_INT),                                     #  63  poco
 ("Splash", F_SPLASH),                                           #  64  comun
 ("Hanging Chad", F_FIRST_RTRG, 2),                              #  65  comun
 ("Cloud 9", F_EOR_DECK_RANK, 1, 9),                             #  66  poco
 ("Mr. Bones", F_BONES),                                         #  67  poco
 ("Chaos the Clown", F_FREE_REROLL),                             #  68  comun
 ("Burglar", F_HMUL, 4, H_HC),                                   #  69  poco            #M real: al elegir ciega +3 manos y pierdes los descartes
 ("Pareidolia", F_RMUL, 8, (1, 11, 12, 13)),                     #  70  poco            #M real: todas las cartas cuentan como figura
 ("Stone Joker", F_FCHP, 25),                                    #  71  poco            #M real: +25 fichas por carta Stone del mazo
 ("Steel Joker", F_XMUL_PER_EF, 0.2, EF_STEEL),                  #  72  poco
 ("Showman", F_FCHP, 15),                                        #  73  poco            #M real: los jokers pueden repetirse en la tienda
 ("Throwback", F_FMUL, 6),                                       #  74  poco            #M real: X0.25 por ciega saltada (no hay saltar ciega)
 ("Hologram", F_HMUL, 10, H_FH),                                 #  75  poco            #M real: gana X0.25 por carta anadida al mazo
 ("Vampire", F_VAMP),                                            #  76  poco
 ("Castle", F_STICKY_C, 3, SC_PLAYED, 0),                        #  77  poco            #M real: +3 fichas por descarte del palo de la ronda
 ("Egg", F_EOR_SV, 3),                                           #  78  comun
 ("Faceless Joker", F_EOR_MONEY, 5),                             #  79  comun           #M real: $5 si descartas 3+ figuras de golpe
 ("Cartomancer", F_HCHP, 80, H_SF),                              #  80  poco            #M real: crea un tarot al elegir ciega (no hay tarots)
 ("Marble Joker", F_HCHP, 50, H_5KF),                            #  81  poco            #M real: anade una Stone al mazo al elegir ciega
 ("Drunkard", F_HMUL, 6, H_DPA),                                 #  82  comun           #M real: +1 descarte por ronda
 ("Reserved Parking", F_HELD_R, 1, (11, 12, 13), 0),             #  83  comun           #M real: cada figura en la mano, 1/2 de dar $1
 ("Mime", F_RTRG, (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)),  #  84  poco            #M real: repite los efectos de las cartas en la mano
 ("Triboulet", F_HXMUL, 2, H_5K),                                #  85  raro            #M real: K y Q puntuadas dan X2 (legendario)
 ("Yorick", F_HXMUL, 3, H_FH),                                   #  86  raro            #M real: gana X1 cada 23 cartas descartadas (legendario)
 ("Constellation", F_FMUL, 7),                                   #  87  poco            #M real: gana X0.1 por cada planeta usado
 ("Madness", F_NJOK_M, 2),                                       #  88  poco            #M real: al elegir ciega peq./grande gana X0.5 y destruye un joker
 ("Vagabond", F_BOOTS, 3, 4),                                    #  89  raro            #M real: crea un tarot si juegas con $4 o menos (no hay tarots)
 ("Midas Mask", F_MIDAS),                                        #  90  poco
 ("Golden Ticket", F_GTICK),                                     #  91  comun
 ("Lucky Cat", F_LUCKY),                                         #  92  poco
]

# Rareza de cada joker: {id: rareza} con 0 comun, 1 poco comun, 2 raro.
# FIX: rarezas corregidas segun la wiki. A comun: Gros Michel, Cavendish,
# Misprint, Shoot the Moon, Chaos the Clown, Reserved Parking. A poco comun:
# Cloud 9, Burglar, Stone Joker, Steel Joker, Showman, Throwback, Mime,
# Constellation. A raro: Wee Joker, Vagabond.
# Triboulet y Yorick son legendarios en Balatro (no salen en la tienda); aqui
# no hay rareza legendaria y se quedan como raros.
JRAR = {
 0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0,            # 0-9
 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 1,  # 10-19
 20: 0, 21: 0, 22: 0, 23: 1, 24: 1, 25: 1, 26: 1, 27: 1, 28: 0, 29: 0,  # 20-29
 30: 0, 31: 2, 32: 1, 33: 2, 34: 2, 35: 2, 36: 2, 37: 2, 38: 1, 39: 0,  # 30-39
 40: 1, 41: 1, 42: 2, 43: 0, 44: 0, 45: 0, 46: 1, 47: 1, 48: 0, 49: 0,  # 40-49
 50: 1, 51: 1, 52: 0, 53: 0, 54: 1, 55: 0, 56: 2, 57: 0, 58: 0, 59: 0,  # 50-59
 60: 0, 61: 0, 62: 0, 63: 1, 64: 0, 65: 0, 66: 1, 67: 1, 68: 0, 69: 1,  # 60-69
 70: 1, 71: 1, 72: 1, 73: 1, 74: 1, 75: 1, 76: 1, 77: 1, 78: 0, 79: 0,  # 70-79
 80: 1, 81: 1, 82: 0, 83: 0, 84: 1, 85: 2, 86: 2, 87: 1, 88: 1, 89: 2,  # 80-89
 90: 1, 91: 0, 92: 1,                                                   # 90-92
}

# JPOOL[rareza] = lista de ids con esa rareza. Se calcula una vez al cargar
# para que roll_joker elija rapido dentro de una rareza.
JPOOL = [[], [], []]
for _jid, _rar in JRAR.items():
 JPOOL[_rar].append(_jid)

# Como dibujar cada joker (por id). Los que no estan aqui se dibujan con una
# caja de respaldo que muestra su valor (draw_joker_box).
#   (0, sprite)            sprite de 2x3 tiles tal cual
#   (1, sprite)            sprite de 2x2 tiles, sin marco
#   (2, sprite)            marco de carta de joker + sprite de 2x2 dentro
#   (3, modo, sprite, [(slot, color), ...])
#                          igual que 'modo' (0, 1 o 2) pero antes cambia esos
#                          colores de la paleta: asi muchos jokers comparten
#                          el mismo dibujo base tenido de otro color
# OJO: va por id igual que JDEFS.
# Comprobado contra los sprites del cartucho (oct 2026): las claves estan
# bien, no hay desfase (60 palomitas = Popcorn, 62 reloj de arena = Delayed
# Gratification, 63 grafica = To the Moon, 65 papeleta = Hanging Chad).
JSPR = {
 0: (2, 394),                                                            # Joker
 1: (3, 2, 394, [(3, 6), (8, 7)]),                                       # Jolly Joker
 2: (3, 2, 394, [(3, 1), (8, 5), (7, 1), (6, 5)]),                       # Zany Joker
 3: (3, 2, 394, [(3, 2), (8, 3), (6, 3), (7, 2)]),                       # Mad Joker
 4: (3, 2, 394, [(3, 2), (8, 7), (6, 10), (7, 9)]),                      # Crazy Joker
 5: (3, 2, 394, [(8, 14), (6, 12), (7, 13)]),                            # Droll Joker
 6: (3, 2, 420, [(4, 6), (3, 6), (2, 7), (8, 7), (10, 6)]),              # Sly Joker
 7: (3, 2, 420, [(4, 5), (8, 6), (3, 1), (2, 5), (10, 7)]),              # Wily Joker
 8: (3, 2, 420, [(7, 9), (8, 9), (4, 2), (2, 4), (3, 2)]),               # Clever Joker
 9: (3, 2, 420, [(7, 2), (3, 10), (2, 9), (4, 7), (8, 3), (10, 2)]),     # Devious Joker
 10: (3, 2, 420, [(7, 2), (4, 14), (3, 14), (2, 13), (8, 3), (10, 2)]),  # Crafty Joker
 11: (3, 2, 456, [(11, 8), (2, 8), (3, 10)]),                            # Greedy Joker
 12: (3, 2, 456, [(11, 2)]),                                             # Lusty Joker
 13: (3, 2, 456, [(11, 4), (2, 4), (3, 6)]),                             # Wrathful Joker
 14: (3, 2, 456, [(11, 1), (2, 1), (3, 5)]),                             # Gluttonous Joker
 15: (2, 418),                                                           # Scholar
 16: (3, 2, 416, [(11, 8)]),                                             # Smiley Face
 17: (2, 398),                                                           # Even Steven
 18: (2, 396),                                                           # Odd Todd
 19: (0, 262),                                                           # Sock and Buskin
 20: (2, 392),                                                           # Gros Michel
 21: (1, 356),                                                           # Half Joker
 22: (1, 352),                                                           # Photograph
 23: (2, 390),                                                           # Joker Stencil
 24: (0, 258),                                                           # Fibonacci
 25: (3, 2, 422, [(11, 2)]),                                             # Hack
 28: (2, 424),                                                           # Banner
 29: (3, 2, 426, [(11, 15)]),                                            # Scary Face
 30: (3, 2, 392, [(11, 1)]),                                             # Cavendish
 31: (1, 354),                                                           # Wee Joker
 39: (2, 458),                                                           # Misprint
 43: (3, 2, 452, [(11, 7)]),                                             # Ice Cream
 49: (3, 2, 394, [(8, 5), (3, 1), (2, 1), (7, 1), (6, 5)]),              # Green Joker
 57: (2, 428),                                                           # Walkie Talkie
 58: (3, 2, 454, [(11, 7)]),                                             # Blue Joker
 60: (3, 2, 430, [(11, 2)]),                                             # Popcorn
 62: (2, 450),                                                           # Delayed Gratification
 63: (3, 2, 448, [(11, 14)]),                                            # To the Moon
 65: (0, 266),                                                           # Hanging Chad
 79: (2, 386),                                                           # Faceless Joker
}


# =============================================================================
#  5. RONDAS, CIEGAS Y TIENDA: DATOS
# =============================================================================
SCREEN_W = 240  # ancho de la pantalla de TIC-80
SCREEN_H = 136  # alto

# Posiciones fijas (px) de la pantalla de juego y la tienda. Las usan tanto
# el dibujo como la deteccion del raton y las particulas: si se mueve algo,
# se mueve en todos los sitios a la vez.
FILA_Y = 8       # y de la fila de jokers y de la de consumibles
JOK_X0 = 83      # fila de jokers: repartidos de x = JOK_X0 ...
JOK_XF = 172     #   ... a x = JOK_XF (un joker solo va centrado)
CONSU_X0 = 189   # consumibles: el primero en x = CONSU_X0 ...
CONSU_DX = 18    #   ... y cada uno CONSU_DX px a la derecha
MAX_CONSU = 2    # huecos de consumible
MANO_X0 = 80     # mano: repartida de x = MANO_X0 ...
MANO_XF = 193    #   ... a x = MANO_XF
MANO_Y = 140     #   y = MANO_Y - up (up sube de 0 a 50 al empezar la ronda)
BOT_Y = 166      # botones play / discard / orden: y = BOT_Y - up
JUG_Y0 = 83      # cartas jugadas: suben de y = JUG_Y0 ...
JUG_Y = 53       #   ... a y = JUG_Y mientras puntuan
MAZO_X = 216     # lomo del mazo (16 x 24 px), abajo a la derecha
MAZO_Y = 104
MAX_SEL = 5      # cartas que se pueden seleccionar a la vez

# Fichas base de la ciega pequena en los antes 1-8. Desde el ante 9 se
# multiplica x1.6 por cada ante extra (ver ante_base).
ANTE_BASE = (300, 800, 2800, 6000, 11000, 20000, 35000, 50000)
BLIND_MULT = (1.0, 1.5, 2.0)          # pequena / grande / jefe
BLIND_REWARD = (3, 4, 5)              # $ por superar cada ciega
BLIND_NAME = ("SMALL", "BIG", "BOSS")

INTEREST_CAP = 5  # interes: $1 por cada $5, como mucho $5
CASH_SPEED = 2    # px por fotograma que sube la pantalla al ganar la ronda
CASH_WAIT = 20    # fotogramas de pausa antes de empezar a subir

SHOP_BASE_REROLL = 5  # precio del primer reroll en cada visita (+1 por reroll)

# Sobres: (opciones, cuantas_eliges, precio, tipo) con tipo 0 = jokers,
# 1 = planetas. Mismo indice en PACK_NAME (texto) y PACK_COL (color de caja).
PACK_DEF = (
 (2, 1, 4, 0),  # BUF  Buffoon
 (4, 1, 6, 0),  # JBF  Jumbo Buffoon
 (4, 2, 8, 0),  # MGB  Mega Buffoon
 (4, 1, 4, 1),  # CEL  Celestial
 (5, 1, 6, 1),  # JCL  Jumbo Celestial
 (5, 2, 8, 1),  # MCL  Mega Celestial
)
PACK_NAME = ("BUF", "JBF", "MGB", "CEL", "JCL", "MCL")
PACK_COL = (3, 3, 3, 4, 4, 4)
AVISO_DUR = 120  # fotogramas que se ve el aviso del sobre (2 s)


# =============================================================================
#  6. MOTOR DE EVENTOS: DATOS
# =============================================================================
# Al jugar una mano la puntuacion no se calcula de golpe: se monta una cola de
# eventos (build_event_queue) y se reproduce uno detras de otro, cada uno
# durante EDUR[tipo] fotogramas, para animarla paso a paso como en Balatro.
# Cada evento es una lista [tipo, datos, ...].
E_RISE = 0    # las cartas jugadas suben                    [E_RISE, None]
E_OPLAY = 1   # un joker actua "al jugar" (reservado)       [E_OPLAY, ji]
E_CSCORE = 2  # una carta puntua sus fichas                 [E_CSCORE, ci, es_retrigger]
E_OSCORE = 3  # un joker actua por una carta concreta       [E_OSCORE, (ji, ci)]
E_IND = 4     # un joker actua por su cuenta                [E_IND, ji]
E_FINAL = 5   # cierre de la animacion                      [E_FINAL, None]
E_HELD = 6    # actua una carta que se queda en la mano     [E_HELD, (ji, hi)]
              #   (ji = -1 si es una carta Steel, sin joker)
# ji = indice en gs["jokers"], ci = indice en gs["scoring_cards"],
# hi = indice en gs["hand"]

# Duracion en fotogramas de cada tipo de evento (por indice E_*)
EDUR = [35, 45, 50, 42, 45, 80, 42]

# Particulas (los numeros que flotan al puntuar):
# tipo -> (color_del_rombo, prefijo_del_texto)
PARTICLE_KINDS = {
 "chip": (6, ""),
 "mult": (3, "+"),
 "xmult": (2, "x"),
 "trigger": (9, ""),
 "money": (9, "$"),
 "loss_m": (2, "-"),
}


# =============================================================================
#  7. ESTADO GLOBAL: gs
# =============================================================================
# Pantallas (gs["gm"]). TIC() llama a la funcion Pantalla* que toque.
GM_MENU = 0
GM_JUEGO = 1
GM_VISOR = 2      # visor del mazo
GM_TIENDA = 3
GM_CIEGAS = 4     # seleccion de ciega
GM_GAMEOVER = 5

# Fases de la pantalla de juego (gs["fase_puntos"])
FP_ELEGIR = 0     # eligiendo cartas
FP_PUNTUAR = 1    # reproduciendo la cola de eventos de la mano
FP_SUBIR = 2      # ronda ganada: la pantalla sube hacia el cash out
FP_COBRAR = 3     # cash out quieto, esperando el clic para cobrar

# TODO lo que cambia durante la partida vive aqui. Cualquier funcion lo lee
# y lo modifica directamente.
gs = {
 # --- pantalla e input ---
 "gm": GM_MENU,       # pantalla actual (GM_*)
 "Clk0": False,       # el raton estaba pulsado el fotograma anterior.
                      #   clic nuevo = pulsado ahora y no antes; soltar = al reves
 "visor_from": GM_JUEGO,  # pantalla a la que vuelve el visor del mazo
 "tt_target": None,   # tooltip a pintar al final del fotograma, ver TIC()
 # --- menu ---
 "DS": 0,             # baraja elegida en el menu (0-7)
 "num1": random.randint(0, 7) + 17,   # sprites al azar para decorar el logo
 "num2": random.randint(0, 3) * 16,
 # --- cartas ---
 "baraja": None,      # el Mazo (se crea al final del archivo)
 "jokers": [],        # jokers equipados (Joker)
 "consu": [],         # consumibles (Planeta), como mucho MAX_CONSU
 "hand": [],          # cartas en la mano
 "b": [],             # cartas jugadas en la mano que se esta puntuando
 "hs": 8,             # tamano de mano, lo recalcula recalc_hs()
 "jslots": 5,         # huecos de joker
 "sort_mode": 0,      # orden de la mano: 0 por rango, 1 por palo
 # --- recursos de la ronda ---
 "rs": 0,             # puntuacion acumulada de la ronda
 "hd": 4,             # manos que quedan
 "ds": 4,             # descartes que quedan
 "mn": 4,             # dinero
 "ant": 1,            # ante
 "rd": 1,             # ronda
 "blind": 0,          # ciega actual: 0 pequena, 1 grande, 2 jefe
 "hl": [1] * 12,      # nivel de cada tipo de mano (indice H_*)
 "hp": [False] * 12,  # que tipos de mano has jugado alguna vez
 # --- puntuacion de la mano (motor de eventos) ---
 "fase_puntos": FP_ELEGIR,  # fase de la pantalla de juego (FP_*)
 "tot_chips": 0,      # fichas acumuladas de la mano
 "tot_mult": 1,       # mult acumulado de la mano
 "scoring_cards": [], # cartas que puntuan de verdad (p.ej. solo la pareja)
 "nombre_mano": "",   # nombre de la mano jugada (para mostrar)
 "hand_idx_play": -1, # tipo de mano jugada (H_*)
 "mano_flags": [False] * 12,  # que tipos de mano CONTIENE la jugada
 "ev_queue": [],      # cola de eventos
 "ev_idx": 0,         # evento en curso
 "ev_timer": 0,       # fotogramas que lleva el evento en curso
 "active_joker_idx": -1,  # joker resaltado ahora mismo (-1 ninguno)
 "first_match": {},   # {indice_joker: indice_carta} para Photograph
 # --- animacion y feedback ---
 "up": 0,             # subida de la zona de la mano al empezar (0 -> 50)
 "particles": [],     # particulas vivas
 "shake_chips": 0,    # temblor de cada contador del HUD (fotogramas restantes)
 "shake_mult": 0,
 "shake_nombre": 0,
 "shake_money": 0,
 # --- fin de ronda y cash out ---
 "voff": 0,           # desplazamiento vertical de la "camara": 0 -> SCREEN_H al ganar
 "co_wait": 0,        # pausa antes de subir
 "co_reward": 0,      # desglose del cobro: recompensa de la ciega,
 "co_hands": 0,       #   manos restantes,
 "co_interest": 0,    #   interes,
 "co_disc": 0,        #   descartes restantes (solo baraja verde),
 "co_extra": 0,       #   jokers y cartas Gold,
 "co_total": 0,       #   total
 "co_req": 0,         # puntos que pedia la ciega
 # --- tienda ---
 "shop_j": [],        # 2 huecos: [objeto, precio, vendido, tipo(0 joker, 1 planeta)]
 "shop_p": [],        # 2 sobres: [indice_PACK_DEF, precio, abierto]
 "reroll": 5,         # precio del reroll
 "free_rr": 0,        # rerolls gratis que quedan
 "pack": None,        # sobre abierto: {"k", "choices", "picks"} o None
 "aviso": "",         # mensaje del selector del sobre (p.ej. sin hueco)
 "aviso_t": 0,        #   fotogramas que le quedan en pantalla
 # --- visor del mazo ---
 "pal": "total",      # que se ve: "total" (todo el mazo) o "actual" (lo que queda)
 "vc": None,          # cache de las estadisticas del visor
 "vk": None,          # clave de esa cache
 # --- arrastrar y seleccionar ---
 "drag_card": None,   # carta pulsada (candidata a arrastre)
 "drag_joker": None,  # joker pulsado (candidato a arrastre)
 "drag_active": False,  # el raton se ha movido > 3 px: es arrastre, no clic
 "drag_px": 0,        # donde se pulso
 "drag_py": 0,
 "arrastre": None,    # ("carta"/"joker", objeto, x, y): se pinta al final, ver TIC()
 "sel_joker": -1,    # joker seleccionado para vender (-1 ninguno)
 "sel_joker_obj": None,  # ese mismo joker (objeto), ver sel_joker_pon
 "sel_consu": -1,     # consumible seleccionado para vender/usar (-1 ninguno)
}


# =============================================================================
#  8. ANIMACION
# =============================================================================
def onda_y(an):
 # Desplazamiento vertical suave (suma de dos senos) para que cartas,
 # jokers y planetas "floten". 'an' es el desfase propio de cada objeto,
 # asi no se mueven todos a la vez.
 t = time()
 return math.sin((t + an) / 250) * 0.75 + math.sin((t + an) / 150) * 0.3


def shake_offset(fl, du, ax, ay, fr):
 # Temblor amortiguado: devuelve (dx, dy).
 #   fl = fotogramas que quedan, du = duracion total,
 #   ax / ay = amplitud en X / Y, fr = frecuencia.
 # La amplitud baja con k = fl / du: empieza fuerte y se apaga.
 if fl <= 0:
  return (0, 0)
 t = du - fl
 k = fl / du
 a = (t / du) * fr * math.pi * 2
 return (math.sin(a) * ax * k, math.sin(a * 1.3 + 1) * ay * k)


def counter(st, cur, end, inc, rep):
 # Mueve 'cur' hacia 'end' en pasos de 'inc'. Si ya llego y rep es True,
 # vuelve a empezar desde 'st' (animaciones en bucle, p.ej. foil/holo).
 if cur != end:
  if cur < end:
   cur += inc
   if cur > end:
    cur = end
  elif cur > end:
   cur -= inc
   if cur < end:
    cur = end
 elif rep:
  cur = st
 return cur


# =============================================================================
#  9. CAJAS, BOTONES Y RATON
# =============================================================================
# Las cajas estilo Balatro se dibujan con tiles de 8x8: esquinas (243/244),
# bordes y relleno (227/228). Los colores 6 (borde) y 7 (interior) del sprite
# se cambian con set_col segun la paleta elegida.

def raton_en(x, y, w, h):
 # True si el raton esta dentro del rectangulo de w x h px en (x, y).
 m = mouse()
 return m[0] >= x and m[0] < x + w and m[1] >= y and m[1] < y + h


def clic_nuevo():
 # True solo en el fotograma en que se pulsa el boton izquierdo (en el
 # anterior estaba suelto, ver gs["Clk0"]). Mantenerlo pulsado no repite.
 return mouse()[2] and not gs["Clk0"]


def dibujar_caja(x, y, w, h, iner, bor, sombra, extra=0):
 # Caja de w x h tiles en (x, y). Si sombra es True, dibuja ademas la linea
 # de sombra de abajo (los botones sin pulsar la tienen). extra = px de mas
 # de alto: la ultima fila se pinta otra vez 'extra' px mas abajo (su parte
 # de arriba es igual que una fila del medio, asi que no se nota el empalme).
 for i in range(w):
  for j in range(h):
   desp = (0,)
   if j == h - 1 and h > 1 and extra > 0:
    desp = (0, extra)
   for e in desp:
    yj = y + j * 8 + e
    if i == 0:
     # columna izquierda
     if j == h - 1:
      if h == 1:
       spr(244, x, yj, 0)
      else:
       spr(243, x, yj, 0, 1, 2)
      if sombra:
       line(x + 1, yj + 8, x + 7, yj + 8, bor)
       pix(x, yj + 7, bor)
     elif j == 0:
      spr(243, x, yj, 0)
     else:
      spr(227, x, yj, 0, 1, 0, 3)
    elif i == w - 1:
     # columna derecha
     if j == h - 1:
      if h == 1:
       spr(244, x + (i * 8), yj, 0, 1, 0, 2)
      else:
       spr(243, x + (i * 8), yj, 0, 1, 0, 2)
      if sombra:
       line(x + (i * 8), yj + 8, x + (i * 8) + 6, yj + 8, bor)
       pix(x + (i * 8) + 7, yj + 7, bor)
     elif j == 0:
      spr(243, x + (i * 8), yj, 0, 1, 1)
     else:
      spr(227, x + (i * 8), yj, 0, 1, 0, 1)
    else:
     # columnas del medio
     if j == h - 1:
      if h == 1:
       spr(228, x + (i * 8), yj, 0)
      else:
       spr(227, x + (i * 8), yj, 0, 1, 2)
      if sombra:
       line(x + (i * 8), yj + 8, x + (i * 8) + 8, yj + 8, bor)
     elif j == 0:
      spr(227, x + (i * 8), yj, 0)
     else:
      spr(227, x + (i * 8), yj, 0)
      line(x + (i * 8), yj, x + (i * 8) + 8, yj, iner)


class Boton:
 # Paletas de cajas y botones: indice -> (color_interior, color_borde)
 paletas = {
  0: (7, 6), 1: (2, 3), 2: (0, 1), 3: (11, 13), 4: (10, 8),
  5: (13, 15), 6: (15, 15), 7: (15, 13), 8: (13, 13),
 }

 def __init__(self, txt, col, x, y, w, h, active):
  # w y h en tiles de 8 px. 'col' es el indice en Boton.paletas.
  self.txt = txt
  self.x = x
  self.y = y
  self.w = w
  self.h = h
  self.active = active
  self.iner, self.bor = Boton.paletas.get(col, (7, 6))

 def pintar(self):
  # Dibuja el boton. Si esta pulsado o inactivo se pinta "hundido"
  # (1 px mas abajo y sin sombra). Devuelve si esta pulsado.
  set_col(6, self.bor)
  set_col(7, self.iner)
  clk = self.clicado()
  y = self.y
  hundido = clk or not self.active
  if hundido:
   y += 1
  dibujar_caja(self.x, y, self.w, self.h, self.iner, self.bor, not hundido)
  txt = self.txt
  draw_text(txt, int(self.w * 8 / 2 - (len(txt) / 2) * 3) + self.x, int(self.h * 8 / 2 - 4) + y, self.bor)
  reset_col()
  return clk

 def clicado(self):
  # True mientras el boton izquierdo este pulsado dentro del boton.
  # Para un clic unico usar boton_clic (o comprobar ademas clic_nuevo()).
  return mouse()[2] and raton_en(self.x, self.y, self.w * 8, self.h * 8)


def boton_clic(txt, col, x, y, w, h, active=True):
 # Pinta un Boton y devuelve True si se acaba de hacer clic en el.
 # OJO: un boton inactivo se pinta hundido pero el clic se detecta igual;
 # si en ese caso no debe pasar nada, quien lo llama lo comprueba.
 bt = Boton(txt, col, x, y, w, h, active)
 bt.pintar()
 return bt.clicado() and not gs["Clk0"]


def PrintBox(col, x, y, w, h, extra=0):
 # Caja decorativa (sin texto ni clic) de w x h tiles, 1 px mas abajo de y.
 # extra = px de mas de alto (ver dibujar_caja).
 iner, bor = Boton.paletas.get(col, (7, 6))
 set_col(6, bor)
 set_col(7, iner)
 dibujar_caja(x, y + 1, w, h, iner, bor, False, extra)
 reset_col()


def draw_diamond(cx, cy, w, h, col):
 # Rombo relleno centrado en (cx, cy): fondo de las particulas.
 hw = w // 2
 hh = h // 2
 if hw <= 0 or hh <= 0:
  return
 tri(cx - hw, cy, cx, cy - hh, cx + hw, cy, col)
 tri(cx - hw, cy, cx, cy + hh, cx + hw, cy, col)


# =============================================================================
#  10. MODELO: Carta, Joker, Planeta, Mazo
# =============================================================================
class Carta:
 def __init__(self, dt, suit, value, effect, stamp, edition):
  self.dt = dt          # baraja de la que viene
  self.su = suit        # palo 0-3
  self.va = value       # valor 1-13 (1 = As)
  self.ef = effect      # efecto (indice en EFFECTS)
  self.st = stamp       # sello (indice en SEAL_NAMES)
  self.ed = edition     # edicion: 0 nada, 1 foil, 2 holo (ver abajo)
  self.an = random.randint(0, 1000)  # desfase de flotacion
  # La edicion guarda directamente el fotograma de su animacion:
  # foil va de 1 a 5 y holo de 49 a 53. Empieza en uno al azar.
  if self.ed == 1:
   self.ed = random.randint(1, 5)
  elif self.ed == 2:
   self.ed = random.randint(49, 53)
  self.sel = False       # seleccionada por el jugador
  self.offset_eval = 0   # "bote" hacia arriba mientras puntua
  self.bc = 0            # fichas extra permanentes (Hiker)
  self.bk = 0            # 1 = Glass rota, se quita del mazo al acabar la mano


class Joker:
 # Ligero a proposito: lo fijo de cada joker esta en JDEFS[id]. La
 # instancia solo guarda lo que cambia durante la partida.
 def __init__(self, type_id):
  self.id = type_id   # indice en JDEFS
  self.st = 0         # estado acumulado (sticky, fichas/mult que bajan...)
  self.xm = 0.0       # multiplicador mutable (Ramen, Vampire, Lucky Cat)
  self.sv = 0         # valor de venta extra (Egg)
  d = JDEFS[type_id]
  if d[1] == F_RAMEN:
   self.xm = float(d[2])
  elif d[1] in (F_VAMP, F_LUCKY):
   self.xm = 1.0
  elif d[1] in (F_FCHP_DEC, F_FMUL_DEC):
   self.st = d[2]  # empiezan en d[2] y van bajando
  self.an = random.randint(0, 1000)  # desfase de flotacion
  self.ht = 0                        # fotogramas con el raton encima


class Planeta:
 # Consumible. No tiene atributo 'xm': asi se distingue de un Joker con
 # hasattr(x, "xm"), porque isinstance no es fiable en pocketpy.
 def __init__(self, pid):
  self.id = pid       # indice en PLANETS
  self.an = random.randint(0, 1000)
  self.ht = 0


def sort_hand():
 # Ordena la mano segun gs["sort_mode"]: 0 = por rango (A K Q ... 2),
 # 1 = por palo y dentro de cada palo por rango. El As cuenta como 14.
 h = gs["hand"]
 if gs["sort_mode"] == 0:
  h.sort(key=lambda c: 14 if c.va == 1 else c.va, reverse=True)
 else:
  h.sort(key=lambda c: (c.su, -(14 if c.va == 1 else c.va)))


class Mazo:
 def __init__(self, tipo_baraja):
  self.dt = tipo_baraja   # tipo de baraja (indice en DECK_INFO)
  self.cartas = []        # cartas que quedan por repartir
  self.total = []         # el mazo completo (visor y algunos jokers)

 def generar_mazo(self):
  # Crea las cartas segun el tipo de baraja.
  self.cartas = []
  dt = self.dt
  if dt in (BAR_ROJA, BAR_AZUL, BAR_VERDE, BAR_AMARILLA, BAR_NEGRA):
   # baraja normal de 52
   for suit in range(4):
    for value in range(1, 14):
     self.cartas.append(Carta(dt, suit, value, 0, 0, 0))
  elif dt == BAR_DAMERO:
   # solo picas y corazones, cada carta repetida
   for suit in range(2):
    for value in range(1, 14):
     for _ in range(2):
      self.cartas.append(Carta(dt, suit, value, 0, 0, 0))
  elif dt == BAR_ABANDONADA:
   # solo del 1 al 10
   for suit in range(4):
    for value in range(1, 11):
     self.cartas.append(Carta(dt, suit, value, 0, 0, 0))
  elif dt == BAR_ERRATICA:
   # 52 cartas con palo y valor al azar
   for i in range(52):
    suit = int(random.randint(0, 3))
    value = int(random.randint(1, 13))
    self.cartas.append(Carta(dt, suit, value, 0, 0, 0))
   self.ordenar()
  self.total = self.cartas.copy()

 def mostrar(self, x, y, scale, showtxt, txx, txy):
  # Dibuja el lomo de la baraja y, si showtxt, su descripcion en (txx, txy).
  dt = self.dt
  s = scale
  sp, c2, lns = DECK_INFO[dt]
  set_col(2, c2)
  spr(sp, x, y, 0, s, 0, 0, 1, 3)
  spr(sp, x + s * 8, y, 0, s, 0, 2, 1, 3)
  if showtxt:
   for k in range(len(lns)):
    t, c = lns[k]
    draw_text(t, txx, txy + k * 8, c)
  reset_col()

 def muestra(self, pal):
  # Cartas que ensena el visor: "total" o las que quedan.
  return self.total if pal == "total" else self.cartas

 def mezclar(self):
  random.shuffle(self.cartas)

 def ordenar(self):
  self.cartas.sort(key=lambda c: c.va)

 def repartir(self):
  # Rellena la mano hasta gs["hs"] cartas y la ordena.
  hand = gs["hand"]
  while len(hand) < gs["hs"] and len(self.cartas) > 0:
   hand.append(self.cartas.pop(0))
  sort_hand()
  # FIX: las cartas que quedan han cambiado, hay que recalcular el visor.
  # Su cache solo miraba cuantas cartas habia, y en otra ronda con el
  # mismo numero de cartas ensenaba las de antes.
  gs["vk"] = None


# =============================================================================
#  11. REGLAS DE MANO
# =============================================================================
def cartas_seleccionadas():
 # Cartas seleccionadas de la mano, en su orden.
 return [c for c in gs["hand"] if c.sel]


def chips_c(card):
 # Fichas que da una carta al puntuar: Stone 50, As 11, figuras 10, resto
 # su numero. Mas las fichas permanentes de Hiker (bc).
 if card.ef == EF_STONE:
  return 50 + card.bc
 if card.va == 1:
  return 11 + card.bc
 elif card.va >= 11:
  return 10 + card.bc
 return card.va + card.bc


def analizar_cartas(cartas):
 # Lo que comparten detectar_mano y calcular_mano_flags. Devuelve
 # (cv, g, ecol, eesc):
 #   cv    {valor: cuantas cartas}
 #   g     tamanos de los grupos de valor, de mayor a menor
 #   ecol  es color: 5 cartas de un palo (las Wild valen para cualquiera)
 #   eesc  es escalera: 5 valores seguidos (A-2-3-4-5 y 10-J-Q-K-A valen)
 cv = {}  # valor -> cuantas cartas
 cs = {}  # palo  -> cuantas cartas (sin contar Wild)
 for c in cartas:
  cv[c.va] = cv.get(c.va, 0) + 1
  if c.ef != EF_WILD:
   cs[c.su] = cs.get(c.su, 0) + 1
 g = sorted(cv.values(), reverse=True)
 vals = sorted(cv.keys())
 n = len(cartas)
 ecol = (len(cs) <= 1 and n == 5)
 eesc = False
 if n == 5 and len(cv) == 5:
  r = vals[-1] - vals[0]
  eesc = (r == 4) or vals == [1, 2, 3, 4, 5] or vals == [1, 10, 11, 12, 13]
 return cv, g, ecol, eesc


def detectar_mano(cartas):
 # Devuelve (tipo_de_mano, cartas_que_puntuan): la MEJOR mano que forman.
 # Para pareja / doble pareja / trio / poker solo puntua el grupo; para el
 # resto puntuan todas.
 if len(cartas) == 0:
  return (-1, [])
 cv, g, ecol, eesc = analizar_cartas(cartas)
 e5i = (len(cartas) == 5 and g[0] == 5)  # cinco iguales
 # de mejor a peor
 if e5i and ecol:
  return (H_5KF, cartas[:])
 if ecol and g[0] >= 3 and len(g) >= 2 and g[1] >= 2:
  return (H_FH, cartas[:])
 if e5i:
  return (H_5K, cartas[:])
 if eesc and ecol:
  return (H_SF, cartas[:])
 if g[0] == 4:
  sc = [c for c in cartas if cv[c.va] == 4]
  return (H_POK, sc)
 if g[0] == 3 and len(g) >= 2 and g[1] == 2:
  return (H_FUL, cartas[:])
 if ecol:
  return (H_COL, cartas[:])
 if eesc:
  return (H_ESC, cartas[:])
 if g[0] == 3:
  sc = [c for c in cartas if cv[c.va] == 3]
  return (H_TRI, sc)
 if len(g) >= 2 and g[0] == 2 and g[1] == 2:
  sc = [c for c in cartas if cv[c.va] == 2]
  return (H_DPA, sc)
 if g[0] == 2:
  sc = [c for c in cartas if cv[c.va] == 2]
  return (H_PAR, sc)
 # carta alta: solo puntua la mayor (As = 14)
 mejor = max(cartas, key=lambda c: 14 if c.va == 1 else c.va)
 return (H_HC, [mejor])


def calcular_mano_flags(cartas):
 # A diferencia de detectar_mano, marca TODOS los tipos de mano que contiene
 # la jugada (un full tambien "contiene" pareja y trio). Lo usan los jokers
 # tipo "si la mano contiene X". Devuelve 12 booleanos (indice H_*).
 f = [False] * 12
 if len(cartas) == 0:
  return f
 cv, g, ecol, eesc = analizar_cartas(cartas)
 f[H_PAR] = g[0] >= 2
 f[H_DPA] = len(g) >= 2 and g[0] >= 2 and g[1] >= 2
 f[H_TRI] = g[0] >= 3
 f[H_ESC] = eesc
 f[H_COL] = ecol
 f[H_FUL] = g[0] >= 3 and len(g) >= 2 and g[1] >= 2
 f[H_POK] = g[0] >= 4
 f[H_HC] = True
 f[H_SF] = eesc and ecol
 f[H_5K] = g[0] >= 5
 f[H_FH] = f[H_FUL] and ecol
 f[H_5KF] = f[H_5K] and ecol
 return f


def hand_score(hi):
 # (nombre, fichas, mult) del tipo de mano hi, con su nivel actual aplicado.
 if hi < 0:
  return ("", 0, 0)
 d = HAND_DEF[hi]
 lv = gs["hl"][hi]
 return d[0], d[1] + d[3] * (lv - 1), d[2] + d[4] * (lv - 1)


# =============================================================================
#  12. REGLAS DE PARTIDA (segun la baraja y los jokers)
# =============================================================================
def base_hands():
 # Manos por ronda: 4, +1 con la azul, -1 con la negra.
 dt = gs["baraja"].dt
 v = 4
 if dt == BAR_AZUL:
  v += 1
 elif dt == BAR_NEGRA:
  v -= 1
 return v


def base_discards():
 # Descartes por ronda: 4, +1 con la roja.
 dt = gs["baraja"].dt
 v = 4
 if dt == BAR_ROJA:
  v += 1
 return v


def start_money():
 # $4, y la amarilla $10 mas (como en Balatro: $14)
 if gs["baraja"].dt == BAR_AMARILLA:
  return 14
 return 4


def joker_slots():
 if gs["baraja"].dt == BAR_NEGRA:
  return 6
 return 5


def recalc_hs():
 # Tamano de mano: 8 + lo que sumen/resten los jokers (minimo 1).
 # Hay que llamarlo SIEMPRE que cambie la lista de jokers. De paso
 # recoloca la seleccion (sel_joker_sync).
 hs = 8
 for j in gs["jokers"]:
  d = JDEFS[j.id]
  if d[1] == F_HS_MOD:
   hs += d[3]
  elif d[1] == F_HAND_SIZE:
   hs += d[2]
 if hs < 1:
  hs = 1
 gs["hs"] = hs
 sel_joker_sync()


def sel_joker_pon(i):
 # Selecciona el joker i de la fila (-1 = ninguno). Guarda tambien el
 # objeto, para que la seleccion siga al joker aunque la lista cambie.
 if 0 <= i < len(gs["jokers"]):
  gs["sel_joker"] = i
  gs["sel_joker_obj"] = gs["jokers"][i]
 else:
  gs["sel_joker"] = -1
  gs["sel_joker_obj"] = None


def sel_joker_sync():
 # Tras cambiar la lista de jokers (vender, destruir, reordenar): el
 # indice vuelve a apuntar al joker seleccionado, o a ninguno si ya no
 # esta. Antes la seleccion saltaba al joker de al lado.
 j = gs["sel_joker_obj"]
 if j is not None and j in gs["jokers"]:
  gs["sel_joker"] = gs["jokers"].index(j)
 else:
  sel_joker_pon(-1)


def jokers_de(f):
 # Jokers equipados de la familia f (F_*), en el orden de la fila.
 r = []
 for j in gs["jokers"]:
  if JDEFS[j.id][1] == f:
   r.append(j)
 return r


def splash_active():
 return len(jokers_de(F_SPLASH)) > 0


def has_free_reroll():
 return len(jokers_de(F_FREE_REROLL)) > 0


def ante_base(a):
 # Fichas base del ante a. A partir del 9 (modo infinito) x1.6 por ante.
 if a <= 8:
  return ANTE_BASE[a - 1]
 v = ANTE_BASE[7]
 for _ in range(a - 8):
  v = int(v * 1.6)
 return v


def blind_req():
 # Puntos que pide la ciega actual.
 a = gs["ant"]
 return int(ante_base(a) * BLIND_MULT[gs["blind"]])


# =============================================================================
#  13. JOKERS: CUANDO ACTUAN
# =============================================================================
# Cada joker actua en un momento distinto de la puntuacion. Estas funciones
# deciden si un joker entra en la cola de eventos y en que punto.

def joker_fires_play(j):
 # Al jugar la mano, antes de puntuar cartas. Reservado: hoy ninguno.
 return False


def joker_fires_score(j, card):
 # Al puntuar una carta concreta (jokers por palo o por rango).
 d = JDEFS[j.id]
 f = d[1]
 if f == F_SMUL or f == F_SCHP or f == F_SMONEY:
  return card.su == d[3] or card.ef == EF_WILD
 if f == F_RMUL or f == F_RCHP:
  return card.va in d[3]
 if f == F_RCM:
  return card.va in d[4]
 if f == F_SXPROB:
  # la probabilidad se tira aqui: si falla, el evento ni se encola
  if card.su != d[4] and card.ef != EF_WILD:
   return False
  return random.randint(1, d[3]) == 1
 return False


def joker_fires_ind(j):
 # Independientes de carta: actuan una vez, despues de todas las cartas.
 # F_HELD_R y F_DUSK no estan aqui a proposito: tienen su propio camino
 # (eventos E_HELD y retriggers).
 d = JDEFS[j.id]
 f = d[1]
 # siempre
 if f in (F_FMUL, F_FCHP, F_XMUL, F_STENCIL, F_CHIP_DISC, F_RAMEN, F_NJOK_M,
          F_BULL, F_RAND_M, F_HS_MOD, F_DECK_C, F_XMUL_PER_EF):
  return True
 # si llevan algo acumulado
 if f in (F_STICKY_M, F_STICKY_C, F_FCHP_DEC, F_FMUL_DEC):
  return j.st > 0
 if f in (F_VAMP, F_LUCKY):
  return j.xm > 1.0
 # con condicion
 if f in (F_HMUL, F_HCHP, F_HXMUL):
  return gs["mano_flags"][d[3]]
 if f == F_SZMUL:
  return len(gs["b"]) <= d[3]
 if f == F_NODISC_M:
  return gs["ds"] == 0
 if f == F_HD_LAST_X:
  return gs["hd"] == 1
 if f == F_BOOTS:
  return gs["mn"] >= d[3]
 return False


def count_retriggers(card):
 # Cuantas veces EXTRA puntua una carta: +1 por cada F_RTRG que cubra su
 # rango y +1 por Dusk en la ultima mano. Se llama al montar la cola,
 # antes de restar la mano jugada, por eso la ultima mano es hd == 1.
 n = 0
 for j in gs["jokers"]:
  d = JDEFS[j.id]
  if d[1] == F_RTRG and card.va in d[2]:
   n += 1
  if d[1] == F_DUSK and gs["hd"] == 1:
   n += 1
 return n


def update_sticky(b, sc, flags):
 # Hace crecer (o resetea) los jokers acumulativos F_STICKY_M / F_STICKY_C.
 # Se llama una vez al jugar la mano, antes de montar la cola.
 #   b = cartas jugadas, sc = cartas que puntuan, flags = mano_flags
 face = (11, 12, 13)
 has_face = False
 for c in sc:
  if c.va in face:
   has_face = True
   break
 for j in gs["jokers"]:
  d = JDEFS[j.id]
  f = d[1]
  if f != F_STICKY_M and f != F_STICKY_C:
   continue
  cond = d[3]
  param = d[4]
  inc = d[2]
  if cond == SC_NO_FACE:
   if has_face:
    j.st = 0
   else:
    j.st += inc
  elif cond == SC_PLAYED:
   j.st += inc
  elif cond == SC_HAND_FLAG:
   if flags[param]:
    j.st += inc
  elif cond == SC_SIZE_EQ:
   if len(b) == param:
    j.st += inc
  elif cond == SC_RANK_SCORED:
   for c in sc:
    if c.va in param:
     j.st += inc


# =============================================================================
#  14. JOKERS Y CARTAS: QUE HACEN
# =============================================================================
def joker_aporte(j):
 # Lo que aporta el joker j ahora mismo, como lista de (tipo, valor):
 #   "chip" suma fichas, "mult" suma mult, "xmult" multiplica el mult,
 #   "money" da dinero. [] = no aporta un numero por si mismo.
 # Es la UNICA fuente de esos valores: la usan apply_joker_effect (para
 # aplicarlo), spawn_for_joker (particulas) y el tooltip (valor actual).
 # Misprint (F_RAND_M) no esta: es al azar, lo tira apply_joker_effect.
 # F_HELD_R tampoco: se aplica por carta en el evento E_HELD.
 d = JDEFS[j.id]
 f = d[1]
 if f in (F_FMUL, F_HMUL, F_SMUL, F_RMUL, F_SZMUL, F_NODISC_M):
  return [("mult", d[2])]
 if f in (F_FCHP, F_HCHP, F_SCHP, F_RCHP, F_HS_MOD):
  return [("chip", d[2])]
 if f in (F_XMUL, F_RXFIRST, F_HD_LAST_X, F_HXMUL, F_SXPROB):
  return [("xmult", d[2])]
 if f in (F_RAMEN, F_VAMP, F_LUCKY):
  return [("xmult", j.xm)]
 if f in (F_STICKY_M, F_FMUL_DEC):
  return [("mult", j.st)]
 if f in (F_STICKY_C, F_FCHP_DEC):
  return [("chip", j.st)]
 if f == F_STENCIL:
  return [("xmult", max(1, gs["jslots"] - len(gs["jokers"]) + 1))]
 if f == F_CHIP_DISC:
  return [("chip", d[2] * gs["ds"])]
 if f == F_NJOK_M:
  return [("mult", d[2] * len(gs["jokers"]))]
 if f == F_BULL:
  return [("chip", d[2] * gs["mn"])]
 if f == F_BOOTS:
  return [("mult", d[2] * (gs["mn"] // d[3]))]
 if f == F_RCM:
  return [("chip", d[2]), ("mult", d[3])]
 if f == F_SMONEY:
  return [("money", d[2])]
 if f == F_DECK_C:
  # cuenta las cartas que QUEDAN en el mazo, no el total
  return [("chip", d[2] * len(gs["baraja"].cartas))]
 if f == F_XMUL_PER_EF:
  ct = 0
  for c in gs["baraja"].total:
   if c.ef == d[3]:
    ct += 1
  return [("xmult", 1 + d[2] * ct)]
 return []


def apply_joker_effect(j):
 # Aplica lo que aporta el joker (joker_aporte) a tot_chips / tot_mult o
 # al dinero.
 d = JDEFS[j.id]
 if d[1] == F_RAND_M:
  gs["tot_mult"] += random.randint(0, d[2])
  return
 for tipo, v in joker_aporte(j):
  if tipo == "chip":
   gs["tot_chips"] += v
  elif tipo == "mult":
   gs["tot_mult"] += v
  elif tipo == "xmult":
   gs["tot_mult"] *= v
  elif tipo == "money":
   gs["mn"] += v


def apply_card_ef(c, cx, cy):
 # Efecto propio de una carta al puntuar (Bonus, Mult, Glass, Gold, Lucky)
 # y los jokers que reaccionan a esos efectos. (cx, cy) es el centro de la
 # carta, para lanzar las particulas encima.
 for jh in gs["jokers"]:
  f = JDEFS[jh.id][1]
  if f == F_MIDAS and c.va > 10:
   c.ef = EF_GOLD  # Midas Mask: la figura pasa a ser Gold
  elif f == F_VAMP and c.ef > 0:
   # Vampire se "come" el efecto y gana x0.1
   jh.xm += 0.1
   c.ef = 0
   spawn_particle(cx, cy - 6, round(jh.xm, 2), "xmult")
 ef = c.ef
 if ef == EF_BONUS:
  gs["tot_chips"] += 30
  spawn_particle(cx, cy - 6, 30, "chip")
 elif ef == EF_MULT:
  gs["tot_mult"] += 4
  spawn_particle(cx, cy - 6, 4, "mult")
 elif ef == EF_GLASS:
  # x2 y 1 entre 4 de romperse (se quita al acabar la mano)
  gs["tot_mult"] *= 2
  spawn_particle(cx, cy - 6, 2, "xmult")
  if random.randint(1, 4) == 1:
   c.bk = 1
 elif ef == EF_GOLD:
  # solo da dinero al puntuar si tienes Golden Ticket ($4 cada uno)
  for jh in jokers_de(F_GTICK):
   gs["mn"] += 4
   spawn_particle(cx, cy - 12, 4, "money")
 elif ef == EF_LUCKY:
  # 1/5 de +20 mult y 1/15 de +$20
  tr = False
  if random.randint(1, 5) == 1:
   gs["tot_mult"] += 20
   spawn_particle(cx, cy - 6, 20, "mult")
   tr = True
  if random.randint(1, 15) == 1:
   gs["mn"] += 20
   spawn_particle(cx, cy - 12, 20, "money")
   tr = True
  if tr:
   # Lucky Cat crece cada vez que una Lucky acierta
   for jh in jokers_de(F_LUCKY):
    jh.xm += 0.25


# =============================================================================
#  15. PARTICULAS
# =============================================================================
# Las posiciones repiten la formula de reparto horizontal de print_cards /
# print_jokers para que la particula salga justo encima de su carta o joker.

def card_center_xy(ci):
 # Centro de la carta jugada ci (indice en scoring_cards).
 c = gs["scoring_cards"][ci]
 b = gs["b"]
 if c not in b:
  return (128, JUG_Y)
 idx = b.index(c)
 n = len(b)
 sep = (n * 16 - 17) / (n - 1) if n > 1 else 0
 return (int(MANO_X0 + idx * sep) + 8, JUG_Y)


def joker_center_xy(ji):
 # Centro del joker ji en la fila de jokers (un joker solo va centrado).
 n = len(gs["jokers"])
 if n == 1:
  return (JOK_X0 + (JOK_XF - JOK_X0 - 16) // 2 + 8, FILA_Y + 12)
 sep = (JOK_XF - JOK_X0 - 16) / (n - 1)
 return (int(JOK_X0 + ji * sep) + 8, FILA_Y + 12)


def hand_card_center(hi):
 # Centro de la carta hi de la mano (las que no se juegan).
 cards = gs["hand"]
 if len(cards) == 0 or hi >= len(cards):
  return (128, MANO_Y - gs["up"])
 x = MANO_X0
 y = MANO_Y - gs["up"]
 xf = MANO_XF
 sep = 0 if len(cards) == 1 else (xf - x - 17) / (len(cards) - 1)
 xc = int(x + hi * sep)
 return (xc + 8, y + 10)


def spawn_particle(cx, cy, value, kind):
 # Crea una particula y hace temblar el contador del HUD que corresponda.
 gs["particles"].append({"x": cx, "y": cy, "life": 45, "max_life": 45, "value": value, "kind": kind})
 if kind == "chip":
  gs["shake_chips"] = 15
 elif kind in ("mult", "xmult"):
  gs["shake_mult"] = 15
 elif kind == "money":
  gs["shake_money"] = 15
 elif kind == "loss_m":
  gs["shake_mult"] = 15


def spawn_for_joker(ji):
 # Lanza sobre el joker ji las particulas de lo que acaba de aportar
 # (las mismas que aplico apply_joker_effect, ver joker_aporte). Si son
 # varias (Scholar: fichas y mult) van una encima de otra.
 j = gs["jokers"][ji]
 cx, cy = joker_center_xy(ji)
 if JDEFS[j.id][1] == F_RAND_M:
  spawn_particle(cx, cy, "?", "mult")
  return
 i = 0
 for tipo, v in joker_aporte(j):
  if type(v) is float:
   v = round(v, 2)
  spawn_particle(cx, cy - 6 * i, v, tipo)
  i += 1


def update_and_draw_particles():
 # Anima y dibuja todas las particulas y quita las que han acabado.
 # Cada una vive 45 fotogramas: crece (20%), se queda (50%) y encoge (30%)
 # mientras sube 6 px.
 alive = []
 for p in gs["particles"]:
  ml = p["max_life"]
  r = (ml - p["life"]) / ml  # progreso 0 -> 1
  if r < 0.2:
   s = r / 0.2
  elif r < 0.7:
   s = 1.0
  else:
   s = 1.0 - (r - 0.7) / 0.3
  cx = int(p["x"])
  cy = int(p["y"] - r * 6)
  col, prefix = PARTICLE_KINDS[p["kind"]]
  txt = prefix + str(p["value"])
  w = int(max(18, len(txt) * 4 + 6) * s)
  h = int(10 * s)
  draw_diamond(cx, cy, w, h, col)
  if s > 0.5:
   draw_text(txt, cx - len(txt) * 2 + 1, cy - 2, 15)
  p["life"] -= 1
  if p["life"] > 0:
   alive.append(p)
 gs["particles"] = alive


# =============================================================================
#  16. MOTOR DE PUNTUACION (cola de eventos)
# =============================================================================
# Recorrido de una mano:
#   handle_play -> build_event_queue -> (cada fotograma) step_queue
#   -> apply_event al empezar cada evento -> finalize_score al vaciarse.

def build_event_queue(scoring):
 # Monta la cola de eventos de la mano EN EL ORDEN en que se anima.
 # 'scoring' son las cartas que puntuan.
 q = [[E_RISE, None]]

 # 1) Precalculo: carta objetivo de Photograph y retriggers de Hanging Chad
 fm = {}
 first_rt = 0
 for ji, j in enumerate(gs["jokers"]):
  d = JDEFS[j.id]
  if d[1] == F_RXFIRST:
   for ci, c in enumerate(scoring):
    if c.va in d[3]:
     fm[ji] = ci
     break
  elif d[1] == F_FIRST_RTRG:
   first_rt += d[2]
 gs["first_match"] = fm

 # 2) Jokers "al jugar" (reservado, hoy no entra ninguno)
 for ji, j in enumerate(gs["jokers"]):
  if joker_fires_play(j):
   q.append([E_OPLAY, ji])

 # 3) Cada carta que puntua, repetida tantas veces como retriggers tenga.
 #    Detras de cada repeticion, los jokers que reaccionan a esa carta.
 for ci, c in enumerate(scoring):
  rt = count_retriggers(c)
  if ci == 0:
   rt += first_rt
  for r in range(1 + rt):
   q.append([E_CSCORE, ci, r > 0])
   for ji, j in enumerate(gs["jokers"]):
    if joker_fires_score(j, c) or fm.get(ji) == ci:
     q.append([E_OSCORE, (ji, ci)])

 # 4) Cartas que se quedan en la mano, de izquierda a derecha. Por cada una:
 #    primero su propio efecto (Steel x1.5) y despues los jokers de "carta
 #    en la mano" (Baron, Shoot the Moon...) que la cuentan.
 # FIX: como en Balatro, esta fase va ANTES de los jokers independientes.
 # Antes Baron & co. actuaban en su posicion de la fila de jokers y las Steel
 # al final del todo, multiplicando tambien el mult de los demas jokers.
 for hi, c in enumerate(gs["hand"]):
  if c in gs["b"]:
   continue
  if c.ef == EF_STEEL:
   q.append([E_HELD, (-1, hi)])
  for ji, j in enumerate(gs["jokers"]):
   d = JDEFS[j.id]
   if d[1] == F_HELD_R and c.va in d[3]:
    q.append([E_HELD, (ji, hi)])

 # 5) Jokers independientes, de izquierda a derecha (F_HELD_R nunca entra
 #    aqui: joker_fires_ind devuelve False para ellos)
 for ji, j in enumerate(gs["jokers"]):
  if joker_fires_ind(j):
   q.append([E_IND, ji])

 q.append([E_FINAL, None])
 return q


def apply_event(e):
 # Aplica el efecto de un evento. Se llama UNA vez, en el primer fotograma
 # del evento (el resto del tiempo solo se anima).
 et = e[0]
 if et == E_CSCORE:
  ci = e[1]
  c = gs["scoring_cards"][ci]
  # Hiker: la carta gana fichas permanentes antes de puntuar
  for jh in jokers_de(F_HIKER):
   c.bc += JDEFS[jh.id][2]
  chips = chips_c(c)
  gs["tot_chips"] += chips
  cx, cy = card_center_xy(ci)
  is_rt = len(e) > 2 and e[2]
  spawn_particle(cx, cy, chips, "chip")
  if is_rt:
   spawn_particle(cx, cy - 12, "TRIGER", "trigger")
  apply_card_ef(c, cx, cy)
 elif et == E_OPLAY:
  apply_joker_effect(gs["jokers"][e[1]])
  spawn_for_joker(e[1])
 elif et == E_OSCORE:
  ji, ci = e[1]
  apply_joker_effect(gs["jokers"][ji])
  spawn_for_joker(ji)
 elif et == E_IND:
  ji = e[1]
  apply_joker_effect(gs["jokers"][ji])
  spawn_for_joker(ji)
 elif et == E_HELD:
  ji, hi = e[1]
  if hi < len(gs["hand"]):
   cx, cy = hand_card_center(hi)
  else:
   cx, cy = (128, JUG_Y)
  if ji < 0:
   # carta Steel
   gs["tot_mult"] *= 1.5
   spawn_particle(cx, cy, 1.5, "xmult")
   return
  j = gs["jokers"][ji]
  d = JDEFS[j.id]
  if d[4] == 0:
   gs["tot_mult"] += d[2]
   spawn_particle(cx, cy, d[2], "mult")
  else:
   gs["tot_mult"] *= d[2]
   spawn_particle(cx, cy, d[2], "xmult")


def step_queue():
 # Avanza la cola un fotograma. Cuando se acaba, cierra la mano.
 q = gs["ev_queue"]
 if gs["ev_idx"] >= len(q):
  finalize_score()
  return
 e = q[gs["ev_idx"]]
 if gs["ev_timer"] == 0:
  apply_event(e)
 gs["ev_timer"] += 1
 if gs["ev_timer"] >= EDUR[e[0]]:
  gs["ev_idx"] += 1
  gs["ev_timer"] = 0


def update_event_visuals():
 # Cada fotograma decide que se resalta segun el evento en curso: la carta
 # que puntua "bota" (offset_eval) y el joker que actua sube un poco.
 for c in gs["b"]:
  c.offset_eval = 0
 for c in gs["hand"]:
  if c not in gs["b"]:
   c.offset_eval = 0
 gs["active_joker_idx"] = -1
 q = gs["ev_queue"]
 if gs["ev_idx"] >= len(q):
  return
 e = q[gs["ev_idx"]]
 et = e[0]
 prog = min(1.0, gs["ev_timer"] / EDUR[et]) if EDUR[et] > 0 else 1.0
 bounce = int(math.sin(prog * math.pi) * 6)
 if et == E_CSCORE:
  ci = e[1]
  if ci < len(gs["scoring_cards"]):
   gs["scoring_cards"][ci].offset_eval = bounce
  if len(e) > 2 and e[2]:
   # retrigger: resaltar el joker responsable. Aqui la mano ya se ha
   # restado, por eso Dusk mira hd == 0.
   c = gs["scoring_cards"][ci]
   for ji, j in enumerate(gs["jokers"]):
    d = JDEFS[j.id]
    if d[1] == F_RTRG and c.va in d[2]:
     gs["active_joker_idx"] = ji
     break
    elif d[1] == F_DUSK and gs["hd"] == 0:
     gs["active_joker_idx"] = ji
     break
 elif et == E_OSCORE:
  ji, ci = e[1]
  gs["active_joker_idx"] = ji
  if ci < len(gs["scoring_cards"]):
   gs["scoring_cards"][ci].offset_eval = bounce // 2
 elif et == E_OPLAY or et == E_IND:
  gs["active_joker_idx"] = e[1]
 elif et == E_HELD:
  ji, hi = e[1]
  if ji >= 0:
   gs["active_joker_idx"] = ji
  if hi < len(gs["hand"]):
   gs["hand"][hi].offset_eval = bounce


def finalize_score():
 # Cierre de la mano, cuando se acaba la cola de eventos.
 # 1) Jokers que bajan por mano jugada (Ice Cream...): se destruyen al limite
 new_j = []
 for j in gs["jokers"]:
  d = JDEFS[j.id]
  if d[1] == F_FCHP_DEC:
   j.st -= d[3]
   if j.st <= d[4]:
    continue
  new_j.append(j)
 gs["jokers"] = new_j
 recalc_hs()

 # 2) Sumar la mano a la ronda, quitar Glass rotas y cartas jugadas
 gs["rs"] += int(gs["tot_chips"] * gs["tot_mult"])
 gs["baraja"].total = [c for c in gs["baraja"].total if not c.bk]
 gs["hand"] = [c for c in gs["hand"] if c not in gs["b"]]
 gs["b"] = []
 gs["scoring_cards"] = []
 gs["ev_queue"] = []
 gs["ev_idx"] = 0
 gs["ev_timer"] = 0
 gs["active_joker_idx"] = -1

 # 3) Ganar, perder o seguir jugando
 if gs["rs"] >= blind_req():
  start_round_win()
 elif gs["hd"] <= 0:
  if try_mr_bones():
   start_round_win()
  else:
   gs["gm"] = GM_GAMEOVER
 else:
  gs["baraja"].repartir()
  gs["fase_puntos"] = FP_ELEGIR


# =============================================================================
#  17. FIN DE RONDA, CASH OUT Y PASO ENTRE PANTALLAS
# =============================================================================
# Flujo de una ronda:
#   GM_CIEGAS --start_blind--> GM_JUEGO --ganar--> cash out (FP_SUBIR, FP_COBRAR)
#   --collect_cash_out / enter_shop--> GM_TIENDA --shop_next_round--> GM_CIEGAS

def joker_round_money():
 # Dinero extra al final de ronda: jokers de fin de ronda + cartas Gold
 # que se quedaron en la mano ($3 cada una).
 m = 0
 for j in gs["jokers"]:
  d = JDEFS[j.id]
  f = d[1]
  if f == F_EOR_MONEY:
   m += d[2]
  elif f == F_EOR_DISC:
   # solo si no se ha usado ningun descarte
   if gs["ds"] == base_discards():
    m += d[2] * gs["ds"]
  elif f == F_EOR_DECK_RANK:
   c = 0
   for ca in gs["baraja"].total:
    if ca.va == d[3]:
     c += 1
   m += d[2] * c
 for c in gs["hand"]:
  if c.ef == EF_GOLD:
   m += 3
 return m


def cash_out_money():
 # Desglose del cobro: (recompensa, manos, interes, descartes, extra).
 dt = gs["baraja"].dt
 reward = BLIND_REWARD[gs["blind"]]
 if dt == BAR_VERDE:
  # sin interes, $2 por mano y $1 por descarte que quede
  hands = gs["hd"] * 2
  interest = 0
  disc = gs["ds"]
 else:
  hands = gs["hd"]
  itc = len(jokers_de(F_EOR_INT))  # To the Moon: cada uno suma otro interes
  interest = min(INTEREST_CAP, gs["mn"] // 5) * (1 + itc)
  disc = 0
 extra = joker_round_money()
 return reward, hands, interest, disc, extra


def try_mr_bones():
 # Si tienes Mr Bones y llegaste a 1/4 de la ciega: se sacrifica y ganas.
 for ji, j in enumerate(gs["jokers"]):
  if JDEFS[j.id][1] == F_BONES:
   if gs["rs"] >= blind_req() // 4:
    gs["jokers"].pop(ji)
    recalc_hs()
    gs["rs"] = blind_req()
    return True
   return False
 return False


def start_round_win():
 # Ronda ganada: efectos de fin de ronda de los jokers, calculo del cobro
 # y arranque de la subida de pantalla hacia el cash out (fase 2).
 new_j = []
 for j in gs["jokers"]:
  d = JDEFS[j.id]
  if j.id == J_GROS:
   if random.randint(1, 6) == 1:
    continue
  elif j.id == J_CAVE:
   if random.randint(1, 1000) == 1:
    continue
  elif d[1] == F_FMUL_DEC:
   j.st -= d[3]
   if j.st <= 0:
    continue
  elif d[1] == F_EOR_SV:
   j.sv += d[2]
  new_j.append(j)
 gs["jokers"] = new_j
 recalc_hs()
 r, h, it, dc, ex = cash_out_money()
 gs["co_reward"] = r
 gs["co_hands"] = h
 gs["co_interest"] = it
 gs["co_disc"] = dc
 gs["co_extra"] = ex
 gs["co_total"] = r + h + it + dc + ex
 gs["co_req"] = blind_req()
 gs["voff"] = 0
 gs["co_wait"] = CASH_WAIT
 gs["fase_puntos"] = FP_SUBIR


def reset_round():
 # Devuelve todas las cartas al mazo, baraja y limpia la mano y la
 # puntuacion. No reparte: eso lo hace quien la llama cuando toca.
 b = gs["baraja"]
 b.cartas = b.total.copy()
 for c in b.cartas:
  c.sel = False
  c.offset_eval = 0
 b.mezclar()
 gs["vk"] = None  # FIX: el mazo ha cambiado, recalcular el visor (ver Mazo.repartir)
 gs["hand"] = []
 gs["b"] = []
 gs["scoring_cards"] = []
 gs["nombre_mano"] = ""
 gs["hand_idx_play"] = -1
 gs["tot_chips"] = 0
 gs["tot_mult"] = 1
 gs["particles"] = []
 gs["ev_queue"] = []
 gs["ev_idx"] = 0
 gs["ev_timer"] = 0
 gs["active_joker_idx"] = -1


def collect_cash_out():
 # Clic en el panel del cash out: cobrar e ir a la tienda.
 gs["mn"] += gs["co_total"]
 enter_shop()


def enter_shop():
 gs["voff"] = 0
 gs["fase_puntos"] = FP_ELEGIR
 gs["pack"] = None
 gs["reroll"] = SHOP_BASE_REROLL
 gs["free_rr"] = 1 if has_free_reroll() else 0
 gs["rs"] = 0
 gs["hd"] = base_hands()
 gs["ds"] = base_discards()
 reset_round()
 roll_shop()
 gs["gm"] = GM_TIENDA


def shop_next_round():
 # Boton "next" de la tienda: siguiente ciega (tras el jefe, siguiente ante).
 gs["blind"] += 1
 if gs["blind"] > 2:
  gs["blind"] = 0
  gs["ant"] += 1
 gs["rd"] += 1
 gs["gm"] = GM_CIEGAS


def start_blind():
 # Boton "play" de la pantalla de ciegas: empezar la ronda.
 gs["voff"] = 0
 gs["fase_puntos"] = FP_ELEGIR
 reset_round()
 gs["baraja"].repartir()
 gs["gm"] = GM_JUEGO


# =============================================================================
#  18. TIENDA Y SOBRES
# =============================================================================
def roll_rarity():
 # 70% comun, 25% poco comun, 5% raro
 r = random.randint(1, 100)
 if r <= 70:
  return 0
 if r <= 95:
  return 1
 return 2


def roll_joker():
 # Id de joker al azar: primero la rareza, luego uno de esa rareza.
 rar = roll_rarity()
 pool = JPOOL[rar]
 if len(pool) == 0:
  pool = JPOOL[0]
 return pool[random.randint(0, len(pool) - 1)]


def roll_joker_unique(used):
 # Como roll_joker pero sin repetir: ni los de 'used' (otros huecos de la
 # misma tirada), ni los que ya tienes, ni los que dependen de un joker
 # que no tienes (JDEP). Tras 40 intentos se rinde y devuelve uno cualquiera.
 hj = [j.id for j in gs["jokers"]]
 for _ in range(40):
  jid = roll_joker()
  if jid in used:
   continue
  if jid in hj:
   continue
  dep = JDEP.get(jid)
  if dep is not None:
   hd = False
   for j in gs["jokers"]:
    if j.id == dep:
     hd = True
   if not hd:
    continue
  return jid
 return roll_joker()


def roll_planeta_unique(used):
 # Planeta al azar que no este en 'used' ni en tus consumibles. Los de
 # manos secretas (id >= 9) solo salen si ya has jugado esa mano.
 hu = []
 for c in gs["consu"]:
  if not hasattr(c, "xm"):
   hu.append(c.id)
 for _ in range(40):
  pid = random.randint(0, len(PLANETS) - 1)
  if pid in used:
   continue
  if pid in hu:
   continue
  if pid >= 9 and not gs["hp"][PLANETS[pid][1]]:
   continue
  return pid
 return random.randint(0, 8)


def joker_price(jid):
 return JCOST[JRAR.get(jid, 0)]


def roll_shop_items():
 # Rellena los 2 huecos principales de la tienda: cada uno es un planeta
 # ($3) con un 25% de probabilidad, si no un joker.
 gs["shop_j"] = []
 used_j = []
 used_p = []
 for _ in range(2):
  if random.randint(1, 4) == 1:
   pid = roll_planeta_unique(used_p)
   used_p.append(pid)
   gs["shop_j"].append([Planeta(pid), 3, False, 1])
  else:
   jid = roll_joker_unique(used_j)
   used_j.append(jid)
   gs["shop_j"].append([Joker(jid), joker_price(jid), False, 0])


def roll_shop():
 # Tienda nueva: los 2 huecos principales y los 2 sobres.
 roll_shop_items()
 gs["shop_p"] = []
 for _ in range(2):
  # probabilidad de cada sobre (indice en PACK_DEF):
  # 20% BUF, 10% JBF, 5% MGB, 45% CEL, 10% JCL, 10% MCL
  r = random.randint(1, 100)
  if r <= 20:
   k = 0
  elif r <= 30:
   k = 1
  elif r <= 35:
   k = 2
  elif r <= 80:
   k = 3
  elif r <= 90:
   k = 4
  else:
   k = 5
  gs["shop_p"].append([k, PACK_DEF[k][2], False])


def do_reroll():
 # Reroll de los huecos principales (los sobres no cambian). Primero se
 # gastan los gratis; si no, cuesta gs["reroll"] y el siguiente $1 mas.
 if gs["free_rr"] > 0:
  gs["free_rr"] -= 1
 elif gs["mn"] >= gs["reroll"]:
  gs["mn"] -= gs["reroll"]
  gs["reroll"] += 1
 else:
  return
 roll_shop_items()


def buy_joker(slot):
 if slot >= len(gs["shop_j"]):
  return
 e = gs["shop_j"][slot]
 if e[2]:
  return
 if len(gs["jokers"]) >= gs["jslots"]:
  return
 if gs["mn"] < e[1]:
  return
 gs["mn"] -= e[1]
 gs["jokers"].append(e[0])
 e[2] = True
 recalc_hs()


def buy_planeta(slot):
 if slot >= len(gs["shop_j"]):
  return
 e = gs["shop_j"][slot]
 if e[2]:
  return
 if len(gs["consu"]) >= MAX_CONSU:
  return
 if gs["mn"] < e[1]:
  return
 gs["mn"] -= e[1]
 gs["consu"].append(e[0])
 e[2] = True


def open_pack(slot):
 # Compra y abre el sobre 'slot': genera sus opciones y abre el selector
 # (draw_pack_picker).
 if slot >= len(gs["shop_p"]):
  return
 e = gs["shop_p"][slot]
 if e[2]:
  return
 if gs["mn"] < e[1]:
  return
 k = e[0]
 gs["mn"] -= e[1]
 e[2] = True
 ch = []
 pkd = PACK_DEF[k]
 if pkd[3] == 0:
  # sobre de jokers
  used = []
  for _ in range(pkd[0]):
   jid = roll_joker_unique(used)
   used.append(jid)
   ch.append(Joker(jid))
 else:
  # sobre de planetas: sin repetir los que tienes ni los de la tienda
  used = []
  for c in gs["consu"]:
   if not hasattr(c, "xm"):
    used.append(c.id)
  for sj in gs["shop_j"]:
   if not hasattr(sj[0], "xm") and not sj[2]:
    used.append(sj[0].id)
  used2 = used[:]
  for _ in range(pkd[0]):
   pid = roll_planeta_unique(used2)
   used2.append(pid)
   ch.append(Planeta(pid))
 gs["pack"] = {"k": k, "choices": ch, "picks": pkd[1]}
 gs["aviso_t"] = 0


def pack_pick(idx):
 # Elegir la opcion idx del sobre abierto. Si no tienes hueco para ella,
 # no se coge: sale un aviso y el sobre sigue abierto, para que puedas
 # vender (o usar) algo y volver a elegir.
 p = gs["pack"]
 if p is None:
  return
 if idx >= len(p["choices"]):
  return
 it = p["choices"][idx]
 if hasattr(it, "xm"):
  # es un Joker
  if len(gs["jokers"]) >= gs["jslots"]:
   gs["aviso"] = "SELL A JOKER FIRST"
   gs["aviso_t"] = AVISO_DUR
   return
  gs["jokers"].append(it)
  p["choices"].pop(idx)
  recalc_hs()
 else:
  # es un Planeta
  if len(gs["consu"]) >= MAX_CONSU:
   gs["aviso"] = "USE OR SELL FIRST"
   gs["aviso_t"] = AVISO_DUR
   return
  gs["consu"].append(it)
  p["choices"].pop(idx)
 p["picks"] -= 1
 if p["picks"] <= 0 or len(p["choices"]) == 0:
  gs["pack"] = None


def pack_skip():
 gs["pack"] = None


# =============================================================================
#  19. VENDER Y USAR
# =============================================================================
def use_planeta(idx):
 # Usar el planeta idx de los consumibles: +1 nivel a su mano.
 if idx >= len(gs["consu"]):
  return
 p = gs["consu"][idx]
 d = PLANETS[p.id]
 gs["hl"][d[1]] += 1
 gs["consu"].pop(idx)


def joker_sell_value(j):
 # Mitad del precio de compra (minimo $1) + lo que haya ganado (Egg).
 v = JCOST[JRAR.get(j.id, 0)] // 2 + j.sv
 if v < 1:
  v = 1
 return v


def sell_joker(idx):
 if idx >= len(gs["jokers"]):
  return
 j = gs["jokers"][idx]
 gs["mn"] += joker_sell_value(j)
 gs["jokers"].pop(idx)
 sel_joker_pon(-1)
 recalc_hs()


def sell_consu(idx):
 # Los consumibles se venden siempre por $1.
 if idx >= len(gs["consu"]):
  return
 gs["mn"] += 1
 gs["consu"].pop(idx)
 gs["sel_consu"] = -1


def joker_x_pos(ji, n):
 # X del joker ji si hay n en la fila (misma formula que print_jokers).
 if n == 1:
  return JOK_X0 + (JOK_XF - JOK_X0 - 16) // 2
 sep = (JOK_XF - JOK_X0 - 16) / (n - 1)
 dec = 0
 x = JOK_X0
 for i in range(n):
  if i == ji:
   return int(x + i * int(sep) + int(dec))
  dec += sep - int(sep)
 return JOK_X0


def draw_sell_use_buttons(raton):
 # Botones pequenos encima del objeto seleccionado:
 #   joker seleccionado      -> "$N" para venderlo
 #   consumible seleccionado -> "$1" para venderlo y "use" para usarlo
 # FIX: solo eligiendo cartas. Antes se podia vender un joker MIENTRAS se
 # puntuaba la mano: la cola de eventos seguia apuntando a su indice y el
 # juego petaba (IndexError en apply_event).
 if gs["fase_puntos"] != FP_ELEGIR:
  return
 sj = gs["sel_joker"]
 sc = gs["sel_consu"]
 if 0 <= sj < len(gs["jokers"]):
  n = len(gs["jokers"])
  xj = joker_x_pos(sj, n)
  j = gs["jokers"][sj]
  v = joker_sell_value(j)
  if boton_clic("$" + str(v), 4, xj + 18, 14, 2, 1):
   sell_joker(sj)
 if 0 <= sc < len(gs["consu"]):
  xp = CONSU_X0 + sc * CONSU_DX
  if boton_clic("$1", 4, xp + 18, 10, 2, 1):
   sell_consu(sc)
  if boton_clic("use", 0, xp + 18, 20, 2, 1):
   use_planeta(sc)
   gs["sel_consu"] = -1


# =============================================================================
#  20. TEXTOS DE JOKER (tooltip y caja de respaldo)
# =============================================================================
# El tooltip usa la descripcion de cada joker (JDESC, mas abajo). Para un
# joker que aun no la tenga, y para la caja de respaldo, cada familia tiene
# una plantilla corta en vez de un "switch" gigante.
#
# JVT (texto corto de respaldo): familia -> (texto1, modo1, texto2, modo2, texto3)
#   resultado = texto1 + valor(modo1) + texto2 + valor(modo2) + texto3
#   modos: 0 nada, 1 d[2], 2 d[3], 3 j.st, 4 j.xm redondeado
JVT = {
 F_FMUL: ("+", 1, " MULT", "", 0),
 F_FCHP: ("+", 1, " CHIPS", "", 0),
 F_XMUL: ("X", 1, " MULT", "", 0),
 F_HMUL: ("+", 1, " MULT", "", 0),
 F_HCHP: ("+", 1, " CHIPS", "", 0),
 F_HXMUL: ("X", 1, " MULT", "", 0),
 F_SMUL: ("+", 1, " MULT/SUIT", "", 0),
 F_RMUL: ("+", 1, " M/RANK", "", 0),
 F_SCHP: ("+", 1, " C/SUIT", "", 0),
 F_RCHP: ("+", 1, " C/RANK", "", 0),
 F_RCM: ("+", 1, "C +", 2, "M"),
 F_SMONEY: ("+$", 1, "/SUIT", "", 0),
 F_SXPROB: ("X", 1, " MULT", "", 0),
 F_RTRG: ("RETRIGGER", 0, "", "", 0),
 F_DUSK: ("RTRG END", 0, "", "", 0),
 F_RXFIRST: ("X", 1, " 1st CARD", "", 0),
 F_SZMUL: ("+", 1, " M IF<=", 2, ""),
 F_STENCIL: ("X(5-JOKERS)", 0, "", "", 0),
 F_CHIP_DISC: ("+", 1, " C/DISC", "", 0),
 F_NJOK_M: ("+", 1, " M/JOKER", "", 0),
 F_NODISC_M: ("+", 1, " IF 0 DISC", "", 0),
 F_HD_LAST_X: ("X", 1, " LAST HAND", "", 0),
 F_BULL: ("+", 1, " C/$", "", 0),
 F_BOOTS: ("+", 1, "M/", 2, "$"),
 F_RAND_M: ("+0-", 1, " MULT", "", 0),
 F_HIKER: ("+", 1, "C PERM", "", 0),
 F_STICKY_M: ("+", 3, " MULT", "", 0),
 F_STICKY_C: ("+", 3, " CHIPS", "", 0),
 F_RAMEN: ("X", 4, " MULT", "", 0),
 F_FCHP_DEC: ("+", 3, " CHIPS", "", 0),
 F_HS_MOD: ("+", 1, "C ", 2, "HAND"),
 F_DECK_C: ("+", 1, " C/CARD LEFT", "", 0),
 F_FMUL_DEC: ("+", 3, " MULT", "", 0),
 F_EOR_MONEY: ("+$", 1, " END RND", "", 0),
 F_EOR_DISC: ("+$", 1, "/UNUSED D", "", 0),
 F_EOR_INT: ("INTEREST X2", 0, "", "", 0),
 F_EOR_DECK_RANK: ("+$", 1, "/CARD ", 2, ""),
 F_SPLASH: ("ALL SCORE", 0, "", "", 0),
 F_FIRST_RTRG: ("+", 1, " RTRG 1st", "", 0),
 F_HAND_SIZE: ("+", 1, " HAND SIZE", "", 0),
 F_BONES: ("PREVENTS LOSS", 0, "", "", 0),
 F_FREE_REROLL: ("1 FREE REROLL", 0, "", "", 0),
 F_XMUL_PER_EF: ("X", 1, "/EFFECT", "", 0),
 F_EOR_SV: ("+$", 1, " VAL/RND", "", 0),
 F_MIDAS: ("FACE>GOLD", 0, "", "", 0),
 F_GTICK: ("$4/GOLD", 0, "", "", 0),
 F_VAMP: ("X", 4, " EAT EF", "", 0),
 F_LUCKY: ("X", 4, " MULT", "", 0),
}


def _jvt_v(j, d, m):
 # Valor de un "modo" de JVT
 if m == 1:
  return str(d[2])
 if m == 2:
  return str(d[3])
 if m == 3:
  return str(j.st)
 if m == 4:
  return str(round(j.xm, 2))
 return ""


def joker_value_text(j):
 # Descripcion corta del joker para su tooltip.
 d = JDEFS[j.id]
 f = d[1]
 if f == F_HELD_R:
  # caso aparte: el prefijo depende de d[4]
  p = "+" if d[4] == 0 else "X"
  return p + str(d[2]) + " M/RETEN"
 e = JVT.get(f)
 if not e:
  return ""
 p1, m1, p2, m2, p3 = e
 r = p1 + _jvt_v(j, d, m1) + p2 + _jvt_v(j, d, m2)
 if p3:
  r += p3
 return r


# JDESC: descripcion de cada joker para su tooltip, por id (igual que JDEFS).
# Cada entrada es una tupla de lineas (como mucho 24 caracteres visibles).
#   {1} {2} {3}  se cambian por d[2] d[3] d[4] de JDEFS: si se cambia un valor
#                alli, la descripcion lo sigue.
#   ~c ~m ~x ~$  color de fichas / mult / xmult / dinero,  ~o  palabra clave,
#   ~n           vuelve al color normal (ver TT_COL y draw_text_marcas).
# Texto en ingles, como Balatro. Los #M describen lo que hacen AQUI, no en
# Balatro: el tooltip nunca miente. Los jokers cuyo valor cambia durante la
# partida anaden solos la linea "(CURRENTLY ...)", ver joker_actual.
JDESC = {
 0: ("~m+{1} MULT",),                                                    # Joker
 1: ("~m+{1} MULT~n IF PLAYED HAND", "CONTAINS A ~oPAIR"),               # Jolly Joker
 2: ("~m+{1} MULT~n IF PLAYED HAND", "CONTAINS A", "~oTHREE OF A KIND"),  # Zany Joker
 3: ("~m+{1} MULT~n IF PLAYED HAND", "CONTAINS A ~oTWO PAIR"),           # Mad Joker
 4: ("~m+{1} MULT~n IF PLAYED HAND", "CONTAINS A ~oSTRAIGHT"),           # Crazy Joker
 5: ("~m+{1} MULT~n IF PLAYED HAND", "CONTAINS A ~oFLUSH"),              # Droll Joker
 6: ("~c+{1} CHIPS~n IF PLAYED HAND", "CONTAINS A ~oPAIR"),              # Sly Joker
 7: ("~c+{1} CHIPS~n IF PLAYED HAND", "CONTAINS A", "~oTHREE OF A KIND"),  # Wily Joker
 8: ("~c+{1} CHIPS~n IF PLAYED HAND", "CONTAINS A ~oTWO PAIR"),          # Clever Joker
 9: ("~c+{1} CHIPS~n IF PLAYED HAND", "CONTAINS A ~oSTRAIGHT"),          # Devious Joker
 10: ("~c+{1} CHIPS~n IF PLAYED HAND", "CONTAINS A ~oFLUSH"),            # Crafty Joker
 11: ("PLAYED CARDS WITH", "~oDIAMOND~n SUIT GIVE", "~m+{1} MULT~n WHEN SCORED"),   # Greedy Joker
 12: ("PLAYED CARDS WITH", "~oHEART~n SUIT GIVE", "~m+{1} MULT~n WHEN SCORED"),     # Lusty Joker
 13: ("PLAYED CARDS WITH", "~oSPADE~n SUIT GIVE", "~m+{1} MULT~n WHEN SCORED"),     # Wrathful Joker
 14: ("PLAYED CARDS WITH", "~oCLUB~n SUIT GIVE", "~m+{1} MULT~n WHEN SCORED"),      # Gluttonous Joker
 15: ("PLAYED ~oACES~n GIVE", "~c+{1} CHIPS~n AND ~m+{2} MULT", "WHEN SCORED"),     # Scholar
 16: ("PLAYED ~oFACE~n CARDS GIVE", "~m+{1} MULT~n WHEN SCORED"),                 # Smiley Face
 17: ("PLAYED CARDS WITH ~oEVEN", "~oRANK~n GIVE ~m+{1} MULT", "WHEN SCORED", "(10, 8, 6, 4, 2)"),  # Even Steven
 18: ("PLAYED CARDS WITH ~oODD", "~oRANK~n GIVE ~c+{1} CHIPS", "WHEN SCORED", "(A, 9, 7, 5, 3)"),  # Odd Todd
 19: ("~oRETRIGGER~n ALL PLAYED", "~oFACE~n CARDS"),                    # Sock and Buskin
 20: ("~m+{1} MULT", "1 IN 6 CHANCE THIS CARD", "IS DESTROYED AT THE", "END OF THE ROUND"),  # Gros Michel
 21: ("~m+{1} MULT~n IF PLAYED HAND", "HAS {2} OR FEWER CARDS"),          # Half Joker
 22: ("FIRST PLAYED ~oFACE~n CARD", "GIVES ~xX{1} MULT~n WHEN", "SCORED"),  # Photograph
 23: ("~xX1 MULT~n FOR EACH EMPTY", "~oJOKER~n SLOT", "(STENCIL COUNTS", "AS EMPTY)"),  # Joker Stencil
 24: ("EACH PLAYED ~oA, 2, 3, 5", "~nOR ~o8~n GIVES ~m+{1} MULT", "WHEN SCORED"),  # Fibonacci
 25: ("~oRETRIGGER~n EACH PLAYED", "~o2, 3, 4~n OR ~o5"),                 # Hack
 26: ("PLAYED CARDS WITH", "~oSPADE~n SUIT GIVE", "~c+{1} CHIPS~n WHEN SCORED"),   # Arrowhead
 27: ("1 IN {2} CHANCE FOR PLAYED", "CARDS WITH ~oHEART~n SUIT", "TO GIVE ~xX{1} MULT", "WHEN SCORED"),  # Bloodstone
 28: ("~c+{1} CHIPS~n FOR EACH", "REMAINING ~oDISCARD"),                 # Banner
 29: ("PLAYED ~oFACE~n CARDS GIVE", "~c+{1} CHIPS~n WHEN SCORED"),        # Scary Face
 30: ("~xX{1} MULT", "1 IN 1000 CHANCE THIS", "CARD IS DESTROYED AT", "THE END OF THE ROUND"),  # Cavendish
 31: ("GAINS ~c+{1} CHIPS~n WHEN", "EACH PLAYED ~o2~n IS SCORED"),        # Wee Joker
 32: ("PLAYED CARDS WITH", "~oCLUB~n SUIT GIVE", "~m+{1} MULT~n WHEN SCORED"),      # Onyx Agate
 33: ("~xX{1} MULT~n IF PLAYED HAND", "CONTAINS A ~oPAIR"),               # The Duo
 34: ("~xX{1} MULT~n IF PLAYED HAND", "CONTAINS A ~oFLUSH"),              # The Tribe
 35: ("~xX{1} MULT~n IF PLAYED HAND", "CONTAINS A ~oSTRAIGHT"),           # The Order
 36: ("~xX{1} MULT~n IF PLAYED HAND", "CONTAINS A", "~oTHREE OF A KIND"),  # The Trio
 37: ("~xX{1} MULT~n IF PLAYED HAND", "CONTAINS A", "~oFOUR OF A KIND"),  # The Family
 38: ("PLAYED CARDS WITH", "~oDIAMOND~n SUIT EARN ~$${1}", "WHEN SCORED"),  # Rough Gem
 39: ("~m+0~n TO ~m+{1} MULT", "(RANDOM)"),                              # Misprint
 40: ("~oRETRIGGER~n ALL PLAYED", "CARDS IN ~oFINAL HAND", "OF THE ROUND"),  # Dusk
 41: ("~m+{1} MULT~n FOR EVERY ~$${2}", "YOU HAVE"),                     # Bootstraps
 42: ("~c+{1} CHIPS", "{2} HAND SIZE"),                                  # Stuntman
 43: ("~c+{1} CHIPS", "~c-{2} CHIPS~n FOR EVERY", "HAND PLAYED"),         # Ice Cream
 44: ("~m+{1} MULT~n FOR EACH", "~oJOKER~n CARD"),                       # Abstract Joker
 45: ("~m+{1} MULT~n WHEN ~o0", "~oDISCARDS~n REMAINING"),                # Mystic Summit
 46: ("~xX{1} MULT~n ON ~oFINAL HAND", "OF THE ROUND"),                   # Acrobat
 47: ("~c+{1} CHIPS~n FOR EACH ~$$1", "YOU HAVE"),                       # Bull
 48: ("GAINS ~m+{1} MULT~n PER", "CONSECUTIVE HAND PLAYED", "WITHOUT A SCORING", "~oFACE~n CARD"),  # Ride the Bus
 49: ("~m+{1} MULT~n PER HAND PLAYED", "~m-1 MULT~n PER DISCARD"),       # Green Joker
 50: ("EVERY PLAYED CARD", "PERMANENTLY GAINS", "~c+{1} CHIPS~n WHEN SCORED"),  # Hiker
 51: ("~xX{1} MULT~n, LOSES ~xX0.01", "PER CARD DISCARDED"),              # Ramen
 52: ("GAINS ~c+{1} CHIPS~n IF", "PLAYED HAND CONTAINS", "A ~oSTRAIGHT"),  # Runner
 53: ("GAINS ~c+{1} CHIPS~n IF", "PLAYED HAND HAS", "EXACTLY ~o{3}~n CARDS"),  # Square Joker
 54: ("GAINS ~m+{1} MULT~n IF", "PLAYED HAND CONTAINS", "A ~oTWO PAIR"),  # Spare Trousers
 55: ("EACH ~oQUEEN~n HELD IN HAND", "GIVES ~m+{1} MULT"),               # Shoot the Moon
 56: ("EACH ~oKING~n HELD IN HAND", "GIVES ~xX{1} MULT"),                # Baron
 57: ("EACH PLAYED ~o10~n OR ~o4", "~nGIVES ~c+{1} CHIPS~n AND", "~m+{2} MULT~n WHEN SCORED"),  # Walkie Talkie
 58: ("~c+{1} CHIPS~n FOR EACH", "REMAINING CARD IN ~oDECK"),            # Blue Joker
 59: ("~o+{1} HAND SIZE",),                                              # Juggler
 60: ("~m+{1} MULT", "~m-{2} MULT~n PER ROUND", "PLAYED"),                # Popcorn
 61: ("EARN ~$${1}~n AT THE END", "OF THE ROUND"),                       # Golden Joker
 62: ("EARN ~$${1}~n PER DISCARD", "IF NO DISCARDS ARE USED", "BY THE END OF THE ROUND"),  # Delayed Gratification
 63: ("EARN AN EXTRA ~$$1~n OF", "INTEREST FOR EVERY ~$$5", "~nYOU HAVE AT THE END", "OF THE ROUND (MAX ~$$5~n)"),  # To the Moon
 64: ("EVERY ~oPLAYED~n CARD", "COUNTS IN SCORING"),                     # Splash
 65: ("~oRETRIGGER~n THE FIRST", "SCORING CARD {1} MORE", "TIMES"),        # Hanging Chad
 66: ("EARN ~$${1}~n FOR EACH ~o{2}~n IN", "YOUR FULL DECK AT THE", "END OF THE ROUND"),  # Cloud 9
 67: ("PREVENTS DEATH IF YOU", "SCORED AT LEAST ~o1/4~n OF", "THE REQUIRED CHIPS", "(SELF DESTRUCTS)"),  # Mr. Bones
 68: ("~o1 FREE REROLL~n IN", "EACH SHOP"),                              # Chaos the Clown
 69: ("~m+{1} MULT",),                                                   # Burglar #M (la condicion "carta alta" siempre se cumple)
 70: ("PLAYED ~oACES~n AND ~oFACE", "~nCARDS GIVE ~m+{1} MULT", "WHEN SCORED"),  # Pareidolia #M
 71: ("~c+{1} CHIPS",),                                                  # Stone Joker #M
 72: ("GIVES ~xX{1} MULT~n FOR EACH", "~oSTEEL~n CARD IN YOUR", "FULL DECK"),  # Steel Joker
 73: ("~c+{1} CHIPS",),                                                  # Showman #M
 74: ("~m+{1} MULT",),                                                   # Throwback #M
 75: ("~m+{1} MULT~n IF PLAYED HAND", "CONTAINS A ~oFLUSH HOUSE"),        # Hologram #M
 76: ("GAINS ~xX0.1 MULT~n PER", "SCORING ~oENHANCED~n CARD", "PLAYED, REMOVES ITS", "ENHANCEMENT"),  # Vampire
 77: ("GAINS ~c+{1} CHIPS~n PER", "HAND PLAYED"),                         # Castle #M
 78: ("GAINS ~$${1}~n OF SELL VALUE", "AT THE END OF THE ROUND"),         # Egg
 79: ("EARN ~$${1}~n AT THE END", "OF THE ROUND"),                       # Faceless Joker #M
 80: ("~c+{1} CHIPS~n IF PLAYED HAND", "CONTAINS A", "~oSTRAIGHT FLUSH"),  # Cartomancer #M
 81: ("~c+{1} CHIPS~n IF PLAYED HAND", "CONTAINS A ~oFLUSH FIVE"),        # Marble Joker #M
 82: ("~m+{1} MULT~n IF PLAYED HAND", "CONTAINS A ~oTWO PAIR"),           # Drunkard #M
 83: ("EACH ~oFACE~n CARD HELD IN", "HAND GIVES ~m+{1} MULT"),            # Reserved Parking #M
 84: ("~oRETRIGGER~n ALL", "PLAYED CARDS"),                              # Mime #M
 85: ("~xX{1} MULT~n IF PLAYED HAND", "CONTAINS", "~oFIVE OF A KIND"),     # Triboulet #M
 86: ("~xX{1} MULT~n IF PLAYED HAND", "CONTAINS A ~oFLUSH HOUSE"),        # Yorick #M
 87: ("~m+{1} MULT",),                                                   # Constellation #M
 88: ("~m+{1} MULT~n FOR EACH", "~oJOKER~n CARD"),                       # Madness #M
 89: ("~m+{1} MULT~n FOR EVERY ~$${2}", "YOU HAVE"),                     # Vagabond #M
 90: ("ALL PLAYED ~oFACE~n CARDS", "BECOME ~oGOLD~n CARDS", "WHEN SCORED"),  # Midas Mask
 91: ("PLAYED ~oGOLD~n CARDS EARN", "~$$4~n WHEN SCORED"),                # Golden Ticket
 92: ("GAINS ~xX0.25 MULT~n EACH", "TIME A ~oLUCKY~n CARD", "SUCCESSFULLY TRIGGERS"),  # Lucky Cat
}


# JBOX (caja de respaldo de los jokers sin sprite):
#   familia -> (prefijo, modo, color). Si modo es None solo se pinta el prefijo.
#   modos: 1 d[2], 2 j.xm, 3 d[2]*descartes, 4 d[2]*jokers, 5 d[2]*dinero,
#          6 j.st, 7 d[2]*(dinero//d[3]), 8 d[2]+"c", 9 d[3], 10 d[2]+"H"
JBOX = {
 F_FMUL: ("+", 1, 3),
 F_HMUL: ("+", 1, 3),
 F_SMUL: ("+", 1, 3),
 F_RMUL: ("+", 1, 3),
 F_SZMUL: ("+", 1, 3),
 F_FCHP: ("+", 1, 6),
 F_HCHP: ("+", 1, 6),
 F_SCHP: ("+", 1, 6),
 F_RCHP: ("+", 1, 6),
 F_XMUL: ("x", 1, 3),
 F_RXFIRST: ("x", 1, 3),
 F_HD_LAST_X: ("x", 1, 3),
 F_HXMUL: ("x", 1, 3),
 F_RAMEN: ("x", 2, 3),
 F_STENCIL: ("xN", None, 3),
 F_RTRG: ("RTG", None, 11),
 F_DUSK: ("RTG", None, 11),
 F_CHIP_DISC: ("+", 3, 6),
 F_NJOK_M: ("+", 4, 3),
 F_NODISC_M: ("+", 1, 3),
 F_BULL: ("+", 5, 6),
 F_STICKY_M: ("+", 6, 3),
 F_STICKY_C: ("+", 6, 6),
 F_RAND_M: ("+?", None, 3),
 F_BOOTS: ("+", 7, 3),
 F_HIKER: ("+", 1, 6),
 F_RCM: ("+", 8, 6),
 F_SXPROB: ("x", 1, 3),
 F_SMONEY: ("+$", 1, 9),
 F_HS_MOD: ("+", 1, 6),
 F_FCHP_DEC: ("+", 6, 6),
 F_DECK_C: ("+", 1, 6),
 F_FMUL_DEC: ("+", 6, 3),
 F_EOR_MONEY: ("$", 1, 9),
 F_EOR_DISC: ("$/D", None, 9),
 F_EOR_INT: ("INTx2", None, 9),
 F_EOR_DECK_RANK: ("$/", 9, 9),
 F_SPLASH: ("ALL", None, 11),
 F_FIRST_RTRG: ("RT1", None, 11),
 F_HAND_SIZE: ("+", 10, 15),
 F_BONES: ("REV", None, 11),
 F_FREE_REROLL: ("RR0", None, 9),
 F_EOR_SV: ("$", 1, 9),
}


def _jbox_val(j, d, m):
 # Valor de un "modo" de JBOX
 if m == 1:
  return str(d[2])
 if m == 2:
  return str(round(j.xm, 2))
 if m == 3:
  return str(d[2] * gs["ds"])
 if m == 4:
  return str(d[2] * len(gs["jokers"]))
 if m == 5:
  return str(d[2] * gs["mn"])
 if m == 6:
  return str(j.st)
 if m == 7:
  return str(d[2] * (gs["mn"] // d[3]))
 if m == 8:
  return str(d[2]) + "c"
 if m == 9:
  return str(d[3])
 if m == 10:
  return str(d[2]) + "H"
 return ""


# =============================================================================
#  21. DIBUJO DE CARTAS, JOKERS Y PLANETAS
# =============================================================================
# Sprites de una carta (16x24 = 2x3 tiles):
#   17 + ef        fondo de la carta segun su efecto (mitad izquierda,
#                  la derecha es la misma espejada)
#   su * 16        palo (centro)
#   va             numero (arriba izq.) y lo mismo girado (abajo der.)
#   59 + st        sello (arriba der.)
#   112 + ed       capa de la edicion foil/holo (animada)

def draw_card_at(i, xc, yc_base):
 # Pinta la carta i en (xc, yc_base) con todas sus capas. Esta separada de
 # print_cards para poder pintarla tambien siguiendo al raton al arrastrar.
 cs = i.su * 16
 cv = i.va
 ce = i.ef + 17
 cm = i.st + 59
 ced = int(i.ed) + 112
 spr(ce, xc, yc_base, 0, 1, 0, 0, 1, 3)
 spr(ce, xc + 8, yc_base, 0, 1, 0, 2, 1, 3)
 spr(cs, xc, yc_base + 8, 0)
 spr(cs, xc + 8, yc_base + 8, 0, 1, 1)
 if i.su % 2 == 1:
  set_col(14, 2)  # palos rojos: el numero en rojo
 spr(cv, xc, yc_base, 0)
 spr(cv, xc + 8, yc_base + 16, 0, 1, 0, 2)
 set_col(14, 14)
 spr(cm, xc + 8, yc_base, 0)
 if i.ed != 0:
  # avanza la animacion de la edicion (foil 1-5, holo 49-53, en bucle)
  if i.ed < 10:
   i.ed = counter(1, i.ed, 5, 0.125, True)
  else:
   i.ed = counter(49, i.ed, 53, 0.125, True)
  spr(ced, xc, yc_base, 0, 1, 0, 0, 1, 3)
  spr(ced, xc + 8, yc_base, 0, 1, 0, 2, 1, 3)


def print_cards(x, y, xf, cards, permite_seleccion):
 # Dibuja una fila de cartas repartidas entre x y xf.
 # Si es la mano (cards is gs["hand"]) y permite_seleccion, ademas gestiona
 # el raton: clic = seleccionar/deseleccionar, arrastrar = reordenar.
 # Se distingue por umbral: si al mantener pulsado el raton se mueve mas
 # de 3 px, es un arrastre.
 b = gs["b"]
 hand = gs["hand"]
 if len(cards) == 0:
  return
 tt = gs["gm"] == GM_VISOR  # en el visor se muestran tooltips de carta
 mx = mouse()[0]
 my = mouse()[1]
 mb = mouse()[2]
 draggable = permite_seleccion and (cards is hand)

 # Pulsado y se ha movido mas de 3 px: pasa a ser arrastre
 if draggable and mb and gs["drag_card"] is not None and not gs["drag_active"]:
  if abs(mx - gs["drag_px"]) > 3:
   gs["drag_active"] = True

 # Se suelta el raton: soltar la carta arrastrada o conmutar la seleccion
 if draggable and not mb and gs["Clk0"] and gs["drag_card"] is not None:
  dc = gs["drag_card"]
  if gs["drag_active"]:
   # la carta va al hueco mas cercano a donde se suelta
   n = len(hand)
   sp = 0 if n <= 1 else (xf - x - 17) / (n - 1)
   if sp > 0:
    ni = int(round((mx - x - 8) / sp))
   else:
    ni = 0
   if ni < 0:
    ni = 0
   if ni >= n:
    ni = n - 1
   if dc in hand:
    oi = hand.index(dc)
    if ni != oi:
     hand.pop(oi)
     hand.insert(ni, dc)
  else:
   # clic limpio: seleccionar (como mucho MAX_SEL) o deseleccionar
   if dc.sel or len(cartas_seleccionadas()) < MAX_SEL:
    dc.sel = not dc.sel
  gs["drag_card"] = None
  gs["drag_active"] = False

 # Dibujo de la fila. La separacion es decimal: 'dec' acumula los decimales
 # para que el reparto sea uniforme hasta xf.
 con = 0
 sep = 0 if len(cards) == 1 else (xf - x - 17) / (len(cards) - 1)
 dec = 0
 for i in cards:
  dec += sep - int(sep)
  xc = int(x + con * int(sep) + int(dec))
  # flotacion - bote al puntuar - 4 px si esta seleccionada
  yc_base = int(y + onda_y(i.an) - i.offset_eval + (-4 if (i.sel and permite_seleccion) else 0))
  con += 1
  # las cartas jugadas no se pintan en la mano (se pintan arriba)
  if i in b and cards is hand:
   continue
  hv = (permite_seleccion or tt) and raton_en(xc, yc_base, 16, 23)
  if draggable and hv and clic_nuevo():
   # clic nuevo sobre esta carta: candidata a clic o arrastre
   gs["drag_card"] = i
   gs["drag_active"] = False
   gs["drag_px"] = mx
   gs["drag_py"] = my
  if gs["drag_active"] and gs["drag_card"] is i:
   continue  # la arrastrada se pinta al final, en el raton
  draw_card_at(i, xc, yc_base)
  if tt and hv:
   gs["tt_target"] = ("card", i, xc, yc_base)

 # La carta arrastrada sigue al raton. Se pinta al final del fotograma
 # (TIC) para quedar por encima de todo.
 if draggable and gs["drag_active"] and gs["drag_card"] is not None:
  gs["arrastre"] = ("carta", gs["drag_card"], mx - 8, my - 12)


def dibujar_joker(x, y, j, sc=1):
 # Pinta el joker j segun JSPR. sc = escala (2 en el selector de sobres).
 # Devuelve False si no tiene sprite (el llamador pinta la caja de respaldo).
 if j.id not in JSPR:
  return False
 cfg = JSPR[j.id]
 modo = cfg[0]
 if modo == 3:
  # cambio de paleta y luego se dibuja con el modo base cfg[1]
  for slot, col in cfg[3]:
   set_col(slot, col)
  bm = cfg[1]
  sid = cfg[2]
 else:
  bm = modo
  sid = cfg[1]
 if bm == 2:
  # marco (sprite 17 en las 4 esquinas, espejado) + dibujo de 2x2
  spr(17, x, y, 0, sc)
  spr(17, x + 8 * sc, y, 0, sc, 1)
  spr(17, x, y + 16 * sc, 0, sc, 2)
  spr(17, x + 8 * sc, y + 16 * sc, 0, sc, 3)
  spr(sid, x, y + 4 * sc, 0, sc, 0, 0, 2, 2)
 elif bm == 1:
  spr(sid, x, y + 4 * sc, 0, sc, 0, 0, 2, 2)
 else:
  spr(sid, x, y, 0, sc, 0, 0, 2, 3)
 if modo == 3:
  for slot, _ in cfg[3]:
   set_col(slot, slot)
 return True


def draw_joker_box(xj, yj_base, j, sc=1):
 # Caja de respaldo para jokers sin sprite: 3 letras del nombre y su valor.
 d = JDEFS[j.id]
 rect(xj, yj_base, 16 * sc, 24 * sc, 1)
 rectb(xj, yj_base, 16 * sc, 24 * sc, 14)
 draw_text(d[0][:3].upper(), xj + 2, yj_base + 3, 15)
 f = d[1]
 e = JBOX.get(f)
 if e:
  prefix, m, col = e
  txt = prefix + _jbox_val(j, d, m) if m is not None else prefix
  draw_text(txt, xj + 2, yj_base + 14, col)
 elif f == F_HELD_R:
  pre = "+" if d[4] == 0 else "x"
  draw_text(pre + str(d[2]), xj + 2, yj_base + 14, 3)


def print_jokers(oy=0):
 # Dibuja la fila de jokers (x de JOK_X0 a JOK_XF). 'oy' desplaza la fila en
 # vertical: lo usa el scroll del cash out para pintar dos copias.
 # En juego y tienda con la fase 0, gestiona clic (seleccionar para vender)
 # y arrastre (reordenar), igual que print_cards.
 reset_col()
 bx = JOK_X0
 by = FILA_Y + oy
 xf = JOK_XF
 ai = gs["active_joker_idx"]
 n = len(gs["jokers"])
 if n == 0:
  # sin jokers: si se estaba arrastrando uno (p.ej. se vendio), soltarlo
  if not mouse()[2] and gs["Clk0"] and gs["drag_joker"] is not None:
   gs["drag_joker"] = None
   gs["drag_active"] = False
  return
 if n == 1:
  sep = 0
  bx = JOK_X0 + (xf - JOK_X0 - 16) // 2  # un joker solo va centrado
 else:
  sep = (xf - JOK_X0 - 16) / (n - 1)
 mx = mouse()[0]
 my = mouse()[1]
 mb = mouse()[2]
 # FIX: tambien en la pantalla de ciegas. Ahi ya se pintaba el boton
 # de vender, pero no habia forma de seleccionar un joker.
 draggable = (gs["gm"] in (GM_JUEGO, GM_TIENDA, GM_CIEGAS)) and gs["fase_puntos"] == FP_ELEGIR and oy == 0

 # ob = el raton esta encima del boton de vender: ese clic no es para el joker
 ob = False
 ssj = gs["sel_joker"]
 if 0 <= ssj < n:
  obx = joker_x_pos(ssj, n) + 18
  if raton_en(obx, 14, 16, 8):
   ob = True

 # Pulsado y se ha movido mas de 3 px: pasa a ser arrastre
 if draggable and mb and gs["drag_joker"] is not None and not gs["drag_active"]:
  if abs(mx - gs["drag_px"]) > 3 or abs(my - gs["drag_py"]) > 3:
   gs["drag_active"] = True

 # Se suelta el raton: recolocar el joker o conmutar su seleccion
 if draggable and not mb and gs["Clk0"] and gs["drag_joker"] is not None:
  dj = gs["drag_joker"]
  if dj in gs["jokers"]:
   oi = gs["jokers"].index(dj)
   if gs["drag_active"]:
    nj = len(gs["jokers"])
    sp = 0 if nj <= 1 else (xf - bx - 16) / (nj - 1)
    if sp > 0:
     ni = int(round((mx - bx - 8) / sp))
    else:
     ni = 0
    if ni < 0:
     ni = 0
    if ni >= nj:
     ni = nj - 1
    if ni != oi:
     gs["jokers"].pop(oi)
     gs["jokers"].insert(ni, dj)
     sel_joker_sync()  # la seleccion se va con su joker
   else:
    # clic limpio: solo puede haber un objeto seleccionado
    if gs["sel_joker"] == oi:
     sel_joker_pon(-1)
    else:
     sel_joker_pon(oi)
     gs["sel_consu"] = -1
  gs["drag_joker"] = None
  gs["drag_active"] = False

 # Dibujo de la fila
 con = 0
 dec = 0
 tt_target = None
 for j in gs["jokers"]:
  dec += sep - int(sep)
  xj = int(bx + con * int(sep) + int(dec))
  # flotacion - 4 px si esta actuando - 5 px si esta seleccionado
  yj_base = int(by + onda_y(j.an) * 1.2) - (4 if ai == con else 0) - (5 if gs["sel_joker"] == con else 0)
  hv = raton_en(xj, yj_base, 16, 24)
  # el tooltip sale tras 15 fotogramas con el raton encima
  if hv and not gs["drag_active"]:
   if j.ht < 30:
    j.ht += 1
  else:
   j.ht = 0
  if draggable and hv and clic_nuevo() and gs["drag_joker"] is None and not ob:
   gs["drag_joker"] = j
   gs["drag_active"] = False
   gs["drag_px"] = mx
   gs["drag_py"] = my
  con += 1
  d = JDEFS[j.id]
  if gs["drag_active"] and gs["drag_joker"] is j:
   continue  # el arrastrado se pinta al final, en el raton
  if not dibujar_joker(xj, yj_base, j):
   draw_joker_box(xj, yj_base, j)
   # Blue Joker y los de carta retenida muestran su valor actual
   f = d[1]
   if f == F_DECK_C or f == F_HELD_R:
    rect(xj + 1, yj_base + 13, 14, 7, 1)
    if f == F_DECK_C:
     draw_text("+" + str(d[2] * len(gs["baraja"].cartas)), xj + 2, yj_base + 14, 6)
    else:
     held = 0
     for c in gs["hand"]:
      if c not in gs["b"] and c.va in d[3]:
       held += 1
     if d[4] == 0:
      draw_text("+" + str(d[2] * held), xj + 2, yj_base + 14, 3)
     else:
      draw_text("x" + str(d[2]), xj + 2, yj_base + 14, 3)
  if hv and j.ht >= 15 and gs["fase_puntos"] < FP_SUBIR and not gs["drag_active"]:
   tt_target = (j, xj, yj_base)
 if tt_target:
  gs["tt_target"] = ("joker", tt_target[0], tt_target[1], tt_target[2])

 # El joker arrastrado sigue al raton. Se pinta al final del fotograma
 # (TIC) para quedar por encima de textos, ciegas, tienda y sobres.
 if draggable and gs["drag_active"] and gs["drag_joker"] is not None:
  gs["arrastre"] = ("joker", gs["drag_joker"], mx - 8, my - 12)


def dibujar_planeta(x, y, p, sc=1):
 # Halo (sprite 71 y su espejo) + el planeta concreto en medio.
 d = PLANETS[p.id]
 spr(71, x, y, 0, sc, 0, 0, 1, 3)
 spr(71, x + 8 * sc, y, 0, sc, 3, 0, 1, 3)
 spr(d[2], x + 4 * sc, y + 8 * sc, 0, sc)


def print_consumibles(oy=0):
 # Fila de consumibles (MAX_CONSU huecos desde x = CONSU_X0). Clic =
 # seleccionar para vender o usar. 'oy' como en print_jokers.
 reset_col()
 n = len(gs["consu"])
 if n == 0:
  return
 clickable = (gs["gm"] in (GM_JUEGO, GM_TIENDA, GM_CIEGAS)) and gs["fase_puntos"] == FP_ELEGIR and oy == 0
 # ob = el raton esta encima de los botones $1 / use
 ob = False
 ssc = gs["sel_consu"]
 if 0 <= ssc < n:
  bx = CONSU_X0 + ssc * CONSU_DX + 18
  if raton_en(bx, 10, 16, 8) or raton_en(bx, 20, 16, 8):
   ob = True
 clicked = -1
 for i in range(n):
  p = gs["consu"][i]
  xp = CONSU_X0 + i * CONSU_DX
  yp = int(FILA_Y + oy + onda_y(p.an) * 1.2) - (5 if gs["sel_consu"] == i else 0)
  dibujar_planeta(xp, yp, p)
  hv = raton_en(xp, yp, 16, 22)
  if hv:
   if p.ht < 30:
    p.ht += 1
   gs["tt_target"] = ("planeta", p, xp, yp)
   if clickable and clic_nuevo() and not ob:
    clicked = i
  else:
   p.ht = 0
 if clicked >= 0:
  if gs["sel_consu"] == clicked:
   gs["sel_consu"] = -1
  else:
   gs["sel_consu"] = clicked
   sel_joker_pon(-1)


def check_mazo_click(raton):
 # Clic en el lomo del mazo (abajo a la derecha): abrir el visor.
 if raton[0] > MAZO_X and raton[0] < MAZO_X + 16 and raton[1] > MAZO_Y and raton[1] < MAZO_Y + 24 and clic_nuevo():
  gs["visor_from"] = gs["gm"]
  gs["gm"] = GM_VISOR


# =============================================================================
#  22. TOOLTIPS
# =============================================================================
# Se pintan al final del fotograma (ver TIC()) para quedar encima de todo.
# Formato comun (dibujar_tooltip): caja exterior con el nombre y caja
# interior con las lineas. Las lineas admiten marcas de color: "~m+4 MULT~n"
# pinta "+4 MULT" en el color del mult y vuelve al normal.

# Color de cada marca: ~c fichas, ~m mult, ~x xmult, ~$ dinero, ~o palabra
# clave (palos, rangos, mejoras...). ~n vuelve al color de la linea.
# Elegidos para leerse sobre el gris de la caja interior (paleta 5).
TT_COL = {"c": 7, "m": 3, "x": 3, "$": 10, "o": 8}

# Rareza en el tooltip de joker (por JRAR): texto y color, como en Balatro
RAREZA_TXT = (("COMMON", 7), ("UNCOMMON", 0), ("RARE", 3))
TT_TXT = 11  # color normal del texto sobre la caja gris


def texto_largo(txt):
 # Caracteres que se ven de un texto con marcas (cada "~X" no ocupa).
 n = 0
 i = 0
 while i < len(txt):
  if txt[i] == "~":
   i += 2
  else:
   n += 1
   i += 1
 return n


def draw_text_marcas(txt, x, y, col):
 # Como draw_text, pero entendiendo las marcas ~X (ver TT_COL).
 c = col
 seg = ""
 i = 0
 while i < len(txt):
  if txt[i] == "~":
   if seg != "":
    draw_text(seg, x, y, c)
    x += len(seg) * 4
    seg = ""
   k = txt[i + 1]
   if k == "n":
    c = col
   else:
    c = TT_COL[k]
   i += 2
  else:
   seg += txt[i]
   i += 1
 if seg != "":
  draw_text(seg, x, y, c)


def dibujar_tooltip(titulo, lineas, xc, yc, centrar):
 # Tooltip bajo el objeto de 16 px de ancho en (xc, yc). lineas es una
 # lista de (texto, color). Si no cabe debajo va encima, y nunca se sale
 # de la pantalla. Caja exterior oscura con el nombre (paleta 7) y caja
 # interior gris con las lineas (paleta 5), igual para cartas, jokers y
 # planetas. La exterior lleva 1 px de mas de alto para que la interior no
 # toque su borde de abajo.
 ml = len(titulo)
 for ln in lineas:
  if texto_largo(ln[0]) > ml:
   ml = texto_largo(ln[0])
 # ancho en tiles. Las lineas centradas dejan 3 px de margen a cada lado
 # dentro de la caja interior; las de carta conservan su ancho de siempre.
 if centrar:
  ws = (ml * 4 + 12) // 8 + 1
 else:
  ws = (ml * 4 + 6) // 8 + 1
 hb = len(lineas)
 tx = xc + 8 - ws * 4
 ty = yc + 27
 th = (2 + hb) * 8 + 1
 if tx < 0:
  tx = 0
 if tx + ws * 8 > SCREEN_W:
  tx = SCREEN_W - ws * 8
 if ty + th > SCREEN_H:
  ty = yc - th - 2
 if ty < 0:
  ty = 0
 PrintBox(7, tx, ty, ws, 2 + hb, 1)
 draw_text(titulo, tx + (ws * 8 - len(titulo) * 4) // 2 + 3, ty + 2, 11)
 PrintBox(5, tx + 4, ty + 7, ws - 1, hb + 1)
 for k in range(hb):
  t, c = lineas[k]
  if centrar:
   x = tx + 4 + ((ws - 1) * 8 - texto_largo(t) * 4) // 2 + 1
  else:
   x = tx + 9
  draw_text_marcas(t, x, ty + 11 + k * 9, c)


def tt_card(c, xc, yc):
 # Tooltip de una carta (visor): nombre, fichas, efecto, sello y edicion.
 v = c.va
 a = str(c.va)
 if v == 1:
  a = "A"
 if v == 11:
  a = "J"
 if v == 12:
  a = "Q"
 if v == 13:
  a = "K"
 nm = a + " of " + SUITS[c.su]
 ls = [("+" + str(chips_c(c)) + " Chips", 7)]  # (texto, color) de cada linea
 if c.ef:
  en = EFFECTS[c.ef] if c.ef < len(EFFECTS) else "Effect"
  ls.append((en + " Card", 9))
 if c.st:
  sn = SEAL_NAMES[c.st] if c.st < len(SEAL_NAMES) else "Seal"
  ls.append((sn + " Seal", 4))
 if c.ed:
  ls.append(("Foil" if c.ed < 10 else "Holo", 12))
 dibujar_tooltip(nm, ls, xc, yc, False)


def num_txt(v):
 # Numero para un texto: 2.0 -> "2", 1.5 -> "1.5", 1.234 -> "1.23"
 if type(v) is float:
  v = round(v, 2)
  if v == int(v):
   v = int(v)
 return str(v)


def rellenar_desc(t, d):
 # Cambia {1} {2} {3} de una linea de JDESC por d[2] d[3] d[4].
 for k in range(1, 4):
  tok = "{" + str(k) + "}"
  if tok in t:
   t = t.replace(tok, num_txt(d[k + 1]))
 return t


# Familias cuyo valor cambia durante la partida: su tooltip dice cuanto
# aportan ahora (como el "Currently" de Balatro).
JOKER_VIVO = (F_STENCIL, F_CHIP_DISC, F_NJOK_M, F_BULL, F_BOOTS, F_DECK_C,
              F_XMUL_PER_EF, F_STICKY_M, F_STICKY_C, F_FCHP_DEC, F_FMUL_DEC,
              F_RAMEN, F_VAMP, F_LUCKY)


def joker_actual(j):
 # "(CURRENTLY +12 MULT)" con lo que aporta ahora (joker_aporte), o "".
 if JDEFS[j.id][1] not in JOKER_VIVO:
  return ""
 r = "(CURRENTLY"
 for tipo, v in joker_aporte(j):
  if tipo == "chip":
   r += " ~c+" + num_txt(v) + " CHIPS~n"
  elif tipo == "mult":
   r += " ~m+" + num_txt(v) + " MULT~n"
  elif tipo == "xmult":
   r += " ~xX" + num_txt(v) + " MULT~n"
 return r + ")"


def tt_joker(j, xj, yj):
 # Tooltip de un joker: nombre, descripcion (JDESC), lo que aporta ahora
 # si va cambiando, y rareza. Sin JDESC usa el texto corto de JVT.
 d = JDEFS[j.id]
 lineas = []
 desc = JDESC.get(j.id)
 if desc is None:
  desc = (joker_value_text(j),)
 for t in desc:
  lineas.append((rellenar_desc(t, d), TT_TXT))
 ahora = joker_actual(j)
 if ahora != "":
  lineas.append((ahora, TT_TXT))
 lineas.append(RAREZA_TXT[JRAR.get(j.id, 0)])
 dibujar_tooltip(d[0].upper(), lineas, xj, yj + 1, True)


def tt_planeta(p, xc, yc):
 # Tooltip de un planeta: que mano sube, cuanto, y como esta la mano
 # ahora (nivel, fichas x mult).
 d = PLANETS[p.id]
 hi = d[1]
 hd = HAND_DEF[hi]
 lv = gs["hl"][hi]
 sc = hand_score(hi)
 ch = sc[1]
 mu = sc[2]
 lineas = [
  ("LEVEL UP ~o" + hd[0], TT_TXT),
  ("~m+" + str(hd[4]) + " MULT~n AND ~c+" + str(hd[3]) + " CHIPS", TT_TXT),
  ("LVL " + str(lv) + ": ~c" + str(ch) + "~n X ~m" + str(mu), TT_TXT),
 ]
 dibujar_tooltip(d[0], lineas, xc, yc, True)


# =============================================================================
#  23. HUD
# =============================================================================
# Panel lateral izquierdo (x de 4 a 68): puntuacion de ronda, mano jugada con
# fichas x mult, manos/descartes, dinero, ante y ronda. Se queda fijo aunque
# la pantalla suba en el cash out.

def draw_money_box():
 # Contador de dinero, con temblor cuando cambia.
 ox, oy = shake_offset(gs["shake_money"], 15, 2, 1, 4)
 if gs["shake_money"] > 0:
  gs["shake_money"] -= 1
 PrintBox(8, 4, 95, 8, 2)
 # esquinas redondeadas a mano
 pix(5, 96, 15)
 line(4, 97, 4, 110, 15)
 pix(5, 111, 15)
 pix(66, 96, 15)
 line(67, 97, 67, 110, 15)
 pix(66, 111, 15)
 PrintBox(7, 8 + int(ox), 95 + int(oy), 7, 2)
 draw_text("$" + str(gs["mn"]), 31 + int(ox), 100 + int(oy), 9)


def draw_score_hud(permitir):
 # Bloque central del HUD: nombre de la mano, su nivel y las cajas de
 # fichas (azul) y mult (rojo).
 #   - Puntuando (fase > FP_ELEGIR): muestra los acumuladores tot_chips / tot_mult.
 #   - Eligiendo cartas (permitir): vista previa de la mano seleccionada.
 ox_c, oy_c = shake_offset(gs["shake_chips"], 15, 2, 1, 4)
 ox_m, oy_m = shake_offset(gs["shake_mult"], 15, 2, 1, 4)
 ox_n, oy_n = shake_offset(gs["shake_nombre"], 22, 3, 2, 3)
 if gs["shake_chips"] > 0:
  gs["shake_chips"] -= 1
 if gs["shake_mult"] > 0:
  gs["shake_mult"] -= 1
 if gs["shake_nombre"] > 0:
  gs["shake_nombre"] -= 1
 PrintBox(5, 4, 32, 8, 5)
 PrintBox(0, 8 + int(ox_c), 52 + int(oy_c), 3, 2)
 PrintBox(1, 41 + int(ox_m), 52 + int(oy_m), 3, 2)
 spr(242, 32, 57, 0)  # la "x" entre fichas y mult
 if gs["fase_puntos"] > FP_ELEGIR:
  tc = int(gs["tot_chips"])
  tm = int(gs["tot_mult"])
  PrintBox(0, 8 + int(ox_c), 52 + int(oy_c), 3, 2)
  draw_text(str(tc), int(12 - len(str(tc)) * 1.5) + 8 + int(ox_c), 57 + int(oy_c), 6)
  PrintBox(1, 41 + int(ox_m), 52 + int(oy_m), 3, 2)
  draw_text(str(tm), int(12 - len(str(tm)) * 1.5) + 41 + int(ox_m), 57 + int(oy_m), 3)
  if gs["nombre_mano"] != "":
   draw_text(gs["nombre_mano"], 36 - int(((len(gs["nombre_mano"]) / 2) * 4 - 2)) + int(ox_n), 36 + int(oy_n), 11)
   hi = gs["hand_idx_play"]
   if hi >= 0:
    lvtxt = "lvl " + str(gs["hl"][hi])
    draw_text(lvtxt, 36 - int(((len(lvtxt) / 2) * 4 - 2)), 44, 11)
 if permitir:
  sel = cartas_seleccionadas()
  if len(sel) > 0:
   hi, _ = detectar_mano(sel)
   nm, cb, mb = hand_score(hi)
   draw_text(nm, 36 - int(((len(nm) / 2) * 4 - 2)), 36, 11)
   if hi >= 0:
    lvtxt = "lvl " + str(gs["hl"][hi])
    draw_text(lvtxt, 36 - int(((len(lvtxt) / 2) * 4 - 2)), 44, 11)
   PrintBox(0, 8, 52, 3, 2)
   draw_text(str(cb), int(12 - len(str(cb)) * 1.5) + 8, 57, 6)
   PrintBox(1, 41, 52, 3, 2)
   draw_text(str(mb), int(12 - len(str(mb)) * 1.5) + 41, 57, 3)


def draw_side_hud(permitir):
 # Todo el panel lateral izquierdo.
 # puntuacion de la ronda
 PrintBox(5, 4, 17, 8, 2)
 PrintBox(6, 32, 21, 4, 1)
 spr(241, 32, 22, 0)
 draw_text(str(gs["rs"]), 42, 22, 11)
 draw_text("ROUND", 10, 20, 11)
 draw_text("SCORE", 10, 26, 11)
 # manos y descartes
 PrintBox(5, 4, 71, 4, 3)
 draw_text("HANDS", 13, 73, 11)
 PrintBox(7, 8, 78, 3, 2)
 draw_text(str(gs["hd"]), 21, 83, 7)
 PrintBox(5, 36, 71, 4, 3)
 draw_text("Discard", 41, 73, 11)
 PrintBox(7, 40, 78, 3, 2)
 draw_text(str(gs["ds"]), 53, 83, 2)
 # dinero
 draw_money_box()
 # ante y ronda
 PrintBox(5, 4, 111, 4, 3)
 draw_text("ANTE", 14, 113, 11)
 PrintBox(7, 8, 118, 3, 2)
 draw_text(str(gs["ant"]), 21, 123, 7)
 PrintBox(5, 36, 111, 4, 3)
 draw_text("ROUND", 45, 113, 11)
 PrintBox(7, 40, 118, 3, 2)
 draw_text(str(gs["rd"]), 53, 123, 2)
 # mano / fichas x mult
 draw_score_hud(permitir)


def draw_contadores(oy, con_mazo):
 # Contadores de huecos: jokers "n/5" (arriba izq.), consumibles "n/2"
 # (arriba der.) y, si con_mazo, cartas del mazo "n/52" (abajo der.).
 draw_text(str(len(gs["jokers"])) + "/" + str(gs["jslots"]), 82, 29 + oy, 11)
 draw_text(str(len(gs["consu"])) + "/" + str(MAX_CONSU), 223, 29 + oy, 11)
 if con_mazo:
  draw_text(str(len(gs["baraja"].cartas)) + "/52", MAZO_X + 1, MAZO_Y + 24 + oy, 11)


def draw_cash_out(oy):
 # Panel del cash out. 'oy' = SCREEN_H - voff: empieza fuera de la pantalla
 # por abajo y sube hasta su sitio (oy = 0).
 # Barra naranja con el total (es tambien la zona donde se hace clic)
 bx = 97
 bw = 96
 by = 53 + oy
 PrintBox(4, bx, by, int(bw / 8), 2)
 t = "CASH OUT: $" + str(gs["co_total"])
 draw_text(t, bx + (bw - len(t) * 4) // 2, by + 6, 11)
 # Desglose
 px = bx - 8
 py = by + 20
 pw = 112
 # ciega superada y su recompensa
 circ(px + 10, py + 12, 11, (6, 8, 3)[gs["blind"]])
 nb = BLIND_NAME[gs["blind"]]
 draw_text(nb, px + 13 - len(nb) * 2, py + 9, 11)
 draw_text("PUNTUA AL MENOS", px + 28, py + 5, 11)
 draw_text(str(gs["co_req"]), px + 28, py + 14, 2)
 draw_text("$" * gs["co_reward"], px + pw - gs["co_reward"] * 4 - 3, py + 10, 9)
 draw_text("." * 29, px - 1, py + 21, 11)
 # manos restantes (como mucho se pintan 10 "$")
 draw_text(str(gs["co_hands"]), px, py + 30, 6)
 draw_text("MANOS RESTANTES", px + 6, py + 30, 11)
 nh = gs["co_hands"]
 if nh > 10:
  nh = 10
 draw_text("$" * nh, px + pw - nh * 4 - 3, py + 30, 9)
 # descartes restantes (baraja verde) o interes (el resto)
 yl = py + 40
 if gs["co_disc"] > 0:
  draw_text(str(gs["co_disc"]), px, yl, 2)
  draw_text("DESCARTES REST.", px + 6, yl, 11)
  nd = gs["co_disc"]
  if nd > 10:
   nd = 10
  draw_text("$" * nd, px + pw - nd * 4 - 3, yl, 9)
 else:
  draw_text(str(gs["co_interest"]), px, yl, 8)
  draw_text("INTERES 1 POR 5", px + 6, yl, 11)
  draw_text("$" * gs["co_interest"], px + pw - gs["co_interest"] * 4 - 3, yl, 9)
 # extra de jokers y cartas Gold
 if gs["co_extra"] > 0:
  yl2 = py + 50
  draw_text("JOKER/BARAJA", px + 6, yl2, 11)
  ne = gs["co_extra"]
  if ne > 10:
   ne = 10
  draw_text("$" * ne, px + pw - ne * 4 - 3, yl2, 9)


# =============================================================================
#  24. PANTALLAS
# =============================================================================
# Una funcion por pantalla, elegida en TIC() segun gs["gm"] (GM_*). Cada pantalla
# dibuja y procesa el raton en la misma pasada: se pinta un boton y justo
# despues se mira si lo han pulsado.

# -----------------------------------------------------------------------------
#  GM_MENU
# -----------------------------------------------------------------------------
def nueva_partida():
 # Deja todo listo para empezar con la baraja elegida en el menu.
 gs["fase_puntos"] = FP_ELEGIR
 gs["rs"] = 0
 gs["ant"] = 1
 gs["rd"] = 1
 gs["vk"] = None
 gs["particles"] = []
 gs["shake_chips"] = 0
 gs["shake_mult"] = 0
 gs["shake_nombre"] = 0
 gs["shake_money"] = 0
 gs["hs"] = 8
 gs["blind"] = 0
 gs["voff"] = 0
 gs["co_wait"] = 0
 gs["hl"] = [1] * 12
 gs["hp"] = [False] * 12
 sel_joker_pon(-1)
 gs["sel_consu"] = -1
 gs["pack"] = None
 gs["baraja"].generar_mazo()
 gs["baraja"].mezclar()
 gs["mn"] = start_money()
 gs["jslots"] = joker_slots()
 gs["hd"] = base_hands()
 gs["ds"] = base_discards()
 gs["jokers"] = []
 gs["hand"] = []
 gs["b"] = []
 gs["consu"] = []
 recalc_hs()


def PantallaMenu(raton):
 cls()
 map(0, 0, 31, 18)
 # Logo: una carta con numero y palo al azar (num1 / num2) junto al titulo
 titx = 108
 tity = 12
 spr(77, titx + 28, tity, 0, 2, 0, 0, 3, 2)
 spr(gs["num1"], titx, tity - 9, 0, 2, 0, 0, 1, 3)
 spr(gs["num1"], titx + 16, tity - 9, 0, 2, 0, 2, 1, 3)
 spr(gs["num2"], titx, tity + 7, 0, 2)
 spr(gs["num2"], titx + 16, tity + 7, 0, 2, 1)
 if gs["num2"] in (16, 48):
  set_col(14, 2)  # palo rojo
 spr(1, titx, tity - 9, 0, 2)
 spr(1, titx + 16, tity + 23, 0, 2, 0, 2)
 set_col(14, 14)
 spr(73, titx - 52, tity, 0, 2, 0, 0, 4, 2)
 line(titx - 48, tity - 2, titx - 41, tity - 2, 15)
 line(titx - 48, tity - 1, titx - 41, tity - 1, 15)
 # Baraja elegida con su descripcion, y botones < play >
 gs["baraja"].mostrar(64, 64, 2, True, 102, 70)
 prev_DS = gs["DS"]
 nb = len(DECK_INFO)
 if boton_clic(" <", 1, 100, 95, 3, 2):
  gs["DS"] = (gs["DS"] + nb - 1) % nb
 if boton_clic(" >", 0, 150, 95, 3, 2):
  gs["DS"] = (gs["DS"] + 1) % nb
 if gs["DS"] != prev_DS:
  gs["baraja"] = Mazo(gs["DS"])
 if boton_clic("play", 4, 125, 95, 3, 2):
  nueva_partida()
  gs["gm"] = GM_CIEGAS  # primero se elige ciega


# -----------------------------------------------------------------------------
#  GM_JUEGO
# -----------------------------------------------------------------------------
# Botones de abajo. Se mueven con la zona de la mano ('up' al empezar y
# 'voff' al subir al cash out).

def handle_discard(up):
 # Boton "discard": tira las cartas seleccionadas y repone la mano.
 voff = gs["voff"]
 activo = gs["fase_puntos"] == FP_ELEGIR and gs["ds"] > 0
 if boton_clic("discard", 1, 145, BOT_Y - up - voff, 4, 2, activo) and activo and len(cartas_seleccionadas()) > 0:
  n_disc = len(cartas_seleccionadas())
  gs["hand"] = [c for c in gs["hand"] if not c.sel]
  gs["baraja"].repartir()
  gs["ds"] -= 1
  # Jokers que reaccionan al descarte. Las posiciones se guardan ANTES
  # de tocar la lista, para que las particulas salgan en su sitio.
  positions = [joker_center_xy(ji) for ji in range(len(gs["jokers"]))]
  new_j = []
  for ji, j in enumerate(gs["jokers"]):
   d = JDEFS[j.id]
   f = d[1]
   if f == F_RAMEN:
    # Ramen / Lava: -0.01 por carta descartada, se destruye en x1
    j.xm -= 0.01 * n_disc
    if j.xm <= 1.0:
     continue
   if f == F_STICKY_M and d[3] == SC_PLAYED:
    # Green Joker: -1 mult por descarte
    if j.st > 0:
     j.st -= 1
     if ji < len(positions):
      spawn_particle(positions[ji][0], positions[ji][1], 1, "loss_m")
   new_j.append(j)
  gs["jokers"] = new_j
  recalc_hs()


def handle_play(up):
 # Boton "play": detecta la mano, prepara la puntuacion y arranca la cola
 # de eventos (FP_PUNTUAR).
 voff = gs["voff"]
 activo = gs["fase_puntos"] == FP_ELEGIR and gs["hd"] > 0
 if boton_clic("play", 0, 95, BOT_Y - up - voff, 4, 2, activo) and activo:
  b = cartas_seleccionadas()
  if len(b) > 0:
   # las Stone no cuentan para formar la mano, pero siempre puntuan
   hi, sc = detectar_mano([c for c in b if c.ef != EF_STONE])
   if hi < 0:
    hi = H_HC
   sc = sc + [c for c in b if c.ef == EF_STONE]
   nm, cb, mb = hand_score(hi)
   gs["hp"][hi] = True  # mano descubierta (para los planetas secretos)
   if splash_active():
    sc = b[:]
   gs["b"] = b
   gs["nombre_mano"] = nm
   gs["hand_idx_play"] = hi
   gs["scoring_cards"] = sc
   gs["tot_chips"] = cb
   gs["tot_mult"] = mb
   # FIX: sin las Stone, igual que detectar_mano. Antes una Stone podia
   # "formar" pareja o color para los jokers de tipo de mano.
   gs["mano_flags"] = calcular_mano_flags([c for c in b if c.ef != EF_STONE])
   update_sticky(b, sc, gs["mano_flags"])
   gs["ev_queue"] = build_event_queue(sc)
   gs["ev_idx"] = 0
   gs["ev_timer"] = 0
   gs["active_joker_idx"] = -1
   gs["fase_puntos"] = FP_PUNTUAR
   gs["shake_nombre"] = 22
   gs["hd"] -= 1  # se resta DESPUES de montar la cola (ver count_retriggers)
   for c in b:
    c.offset_eval = 0


def handle_sort(up):
 # Boton "Rango" / "Palo": cambia el orden de la mano.
 voff = gs["voff"]
 lbl = "Rango" if gs["sort_mode"] == 0 else "Palo"
 act = gs["fase_puntos"] == FP_ELEGIR
 if boton_clic(lbl, 3, 180, BOT_Y - up - voff, 3, 2, act) and act:
  gs["sort_mode"] = 1 - gs["sort_mode"]
  sort_hand()


def draw_tapete(yt):
 # Tapete donde va la mano: 14 tiles de ancho x 3 de alto desde (MANO_X0, yt).
 spr(189, 80, yt)
 spr(190, 80, yt + 8)
 spr(206, 80, yt + 16)
 for i in range(12):
  spr(190, 88 + i * 8, yt)
  spr(190, 88 + i * 8, yt + 8)
  spr(190, 88 + i * 8, yt + 16)
 spr(191, 184, yt)
 spr(190, 184, yt + 8)
 spr(207, 184, yt + 16)


def PantallaJuego(raton):
 # Hay 3 tipos de elementos respecto al scroll del cash out (voff):
 #   - mundo de juego (y - voff): sube y se va por arriba al ganar
 #   - HUD lateral (sin voff): se queda fijo
 #   - pantalla del cash out (y + SCREEN_H - voff): entra desde abajo; ahi
 #     se vuelven a pintar jokers, consumibles y mazo para que se vean
 cls()
 voff = gs["voff"]
 fp = gs["fase_puntos"]
 map(60, 17, 30, 17, 0, -voff)
 if fp >= FP_SUBIR:
  map(60, 0, 30, 17, 0, SCREEN_H - voff)
 # la zona de la mano sube al empezar (up de 0 a 50)
 gs["up"] = counter(0, gs["up"], 50, 1, False)
 up = gs["up"]
 draw_tapete(MANO_Y - up - voff)
 permitir_interaccion = (fp == FP_ELEGIR)

 # contadores: cartas en mano / tamano de mano, y huecos
 draw_text(str(len(gs["hand"])) + "/" + str(gs["hs"]), MANO_X0 + 2, MANO_Y + 22 - up - voff, 11)
 draw_contadores(-voff, True)
 if fp >= FP_SUBIR:
  draw_contadores(SCREEN_H - voff, True)

 # jokers y consumibles (y su copia en la pantalla del cash out)
 print_jokers(-voff)
 print_consumibles(-voff)
 if fp >= FP_SUBIR:
  print_jokers(SCREEN_H - voff)
  print_consumibles(SCREEN_H - voff)

 draw_side_hud(permitir_interaccion)
 handle_discard(up)
 handle_play(up)
 handle_sort(up)

 # mazo (y su copia)
 gs["baraja"].mostrar(MAZO_X, MAZO_Y - voff, 1, False, 0, 0)
 if fp >= FP_SUBIR:
  gs["baraja"].mostrar(MAZO_X, MAZO_Y + SCREEN_H - voff, 1, False, 0, 0)
 if fp == FP_ELEGIR:
  check_mazo_click(raton)
 draw_sell_use_buttons(raton)

 # FP_PUNTUAR: animar la puntuacion. Las cartas jugadas suben de JUG_Y0
 # a JUG_Y durante E_RISE y se quedan en JUG_Y el resto de la cola.
 if fp == FP_PUNTUAR:
  update_event_visuals()
  q = gs["ev_queue"]
  if gs["ev_idx"] < len(q) and q[gs["ev_idx"]][0] == E_RISE:
   prog = gs["ev_timer"] / EDUR[E_RISE]
   y = int(JUG_Y0 - prog * (JUG_Y0 - JUG_Y))
  else:
   y = JUG_Y
  print_cards(MANO_X0, y, MANO_X0 + (len(gs["b"]) * 16), gs["b"], False)
  step_queue()

 # la mano va al final para que ninguna particula la tape
 print_cards(MANO_X0, MANO_Y - up - voff, MANO_XF, gs["hand"], permitir_interaccion)
 update_and_draw_particles()

 # FP_SUBIR y FP_COBRAR: subida al cash out y espera del clic para cobrar
 if fp >= FP_SUBIR:
  if fp == FP_SUBIR:
   if gs["co_wait"] > 0:
    gs["co_wait"] -= 1
   else:
    gs["voff"] += CASH_SPEED
    if gs["voff"] >= SCREEN_H:
     gs["voff"] = SCREEN_H
     gs["fase_puntos"] = FP_COBRAR
  draw_cash_out(SCREEN_H - gs["voff"])
  # clic en la barra naranja de draw_cash_out: cobrar
  if gs["fase_puntos"] == FP_COBRAR and clic_nuevo() and raton_en(97, 53, 96, 16):
   collect_cash_out()


# -----------------------------------------------------------------------------
#  GM_VISOR: VISOR DEL MAZO
# -----------------------------------------------------------------------------
def PantallaVisor(raton):
 # Estadisticas del mazo (por valor, por palo, ases/numeros/figuras) y las
 # cartas agrupadas por palo. Se puede ver el mazo "total" o lo que queda.
 cls()
 map(30, 18, 61, 35)
 if boton_clic(gs["pal"], 0, 80, 118, 4, 2):
  gs["pal"] = "total" if gs["pal"] == "actual" else "actual"
 gs["baraja"].mostrar(12, 12, 2, False, 30, 65)
 PrintBox(5, 59, 11, 21, 12)  # fondo del panel de cartas

 # Las estadisticas se calculan solo cuando cambia la clave (vista, n cartas)
 cm = gs["baraja"].muestra(gs["pal"])
 k = (gs["pal"], len(cm))
 if gs["vk"] != k:
  pi = []  # picas
  co = []  # corazones
  tr = []  # treboles
  ro = []  # rombos (diamantes)
  v = [0] * 14       # cuantas hay de cada valor
  s = [0, 0, 0, 0]   # cuantas hay de cada palo
  can = [0, 0, 0]    # ases, numeros, figuras
  bys = [pi, co, tr, ro]
  for i in cm:
   if i.va == 1:
    can[0] += 1
   elif i.va in (11, 12, 13):
    can[2] += 1
   else:
    can[1] += 1
   v[i.va] += 1
   bys[i.su].append(i)
   s[i.su] += 1
  for ly in bys:
   ly.sort(key=lambda c: c.va)
  gs["vc"] = (pi, co, tr, ro, v, s, can)
  gs["vk"] = k
 pi, co, tr, ro, v, s, can = gs["vc"]

 # columna de valores (A..K) con su recuento
 set_col(14, 15)
 for i in range(1, 14):
  spr(245, 50, 7 + (i * 7), 0)
  spr(i, 49, 6 + (i * 7), 0)
  draw_text(str(v[i]), 46, 8 + (i * 7), 11)
 set_col(14, 14)
 # recuento por palo (2x2)
 for k in range(4):
  sx = 11
  tx = 17
  sy = 77 if k < 2 else 92
  if k % 2:
   sx += 16
   tx += 16
  sid = k * 16
  spr(sid, sx, sy, 0)
  spr(sid, sx + 8, sy, 0, 1, 1)
  draw_text(str(s[k]), tx, sy + 8, 11)
 # ases / numeros / figuras
 for k in range(3):
  sids = (1, 14, 15)
  sxs = (11, 22, 33)
  txs = (16, 24, 35)
  spr(sids[k], sxs[k], 59 if k == 0 else 60, 0)
  draw_text(str(can[k]), txs[k], 68, 11)
 # una fila de cartas por palo
 print_cards(60, 14, 227, pi, False)
 print_cards(60, 37, 227, ro, False)
 print_cards(60, 60, 227, tr, False)
 print_cards(60, 83, 227, co, False)
 # clic en el mazo grande: volver
 if raton[0] > 12 and raton[0] < 44 and raton[1] > 20 and raton[1] < 68 and clic_nuevo():
  gs["gm"] = gs["visor_from"]


# -----------------------------------------------------------------------------
#  GM_TIENDA
# -----------------------------------------------------------------------------
def draw_shop_jslot(slot, x, y, raton):
 # Hueco principal de la tienda: precio arriba y el joker o planeta debajo.
 # Clic = comprar.
 if slot >= len(gs["shop_j"]):
  return
 e = gs["shop_j"][slot]
 if e[2]:
  return  # ya vendido: hueco vacio
 it = e[0]
 pr = e[1]
 tp = e[3] if len(e) > 3 else 0  # 0 joker, 1 planeta
 PrintBox(6, x, y - 9, 2, 1)
 draw_text("$" + str(pr), x + 4, y - 7, 9)
 yj = int(y + onda_y(it.an) * 1.2)
 if tp == 1:
  dibujar_planeta(x, yj, it)
 else:
  if not dibujar_joker(x, yj, it):
   draw_joker_box(x, yj, it)
 if raton_en(x, yj, 16, 24):
  if tp == 1:
   gs["tt_target"] = ("planeta", it, x, yj)
   if clic_nuevo():
    buy_planeta(slot)
  else:
   gs["tt_target"] = ("joker", it, x, yj)
   if clic_nuevo():
    buy_joker(slot)


def draw_shop_pslot(slot, x, y, raton):
 # Hueco de sobre: precio y caja con su nombre. Clic = comprar y abrir.
 if slot >= len(gs["shop_p"]):
  return
 e = gs["shop_p"][slot]
 if e[2]:
  return  # ya abierto
 k = e[0]
 pr = e[1]
 PrintBox(6, x, y - 9, 2, 1)
 draw_text("$" + str(pr), x + 4, y - 7, 9)
 PrintBox(PACK_COL[k], x, y, 2, 3)
 nm = PACK_NAME[k]
 draw_text(nm, x + 8 - len(nm) * 2, y + 4, 11)
 draw_text("PACK", x + 8 - 8, y + 12, 15)
 if raton_en(x, y, 16, 24) and clic_nuevo():
  open_pack(slot)


def draw_pack_picker(raton):
 # Selector del sobre abierto: opciones a tamano doble, clic = elegir,
 # boton "skip" = cerrar el sobre. Debajo de las opciones sale el aviso de
 # pack_pick si lo hay.
 p = gs["pack"]
 if p is None:
  return
 nm = PACK_NAME[p["k"]] + " PACK"
 draw_text(nm, 120 - len(nm) * 2, 16, 11)
 et = "Choose " + str(p["picks"])
 draw_text(et, 120 - len(et) * 2, 24, 15)
 if gs["aviso_t"] > 0:
  gs["aviso_t"] -= 1
  av = gs["aviso"]
  draw_text(av, 120 - len(av) * 2, 100, 8)
 ch = p["choices"]
 n = len(ch)
 if n > 0:
  bx = 120 - (n * 40) // 2 + 4  # opciones centradas, cada 40 px
  for i in range(n):
   it = ch[i]
   xj = bx + i * 40
   yj = int(40 + onda_y(it.an) * 1.2)
   isp = not hasattr(it, "xm")  # es planeta
   if isp:
    dibujar_planeta(xj, yj, it, 2)
    spr(106, xj + 8, yj + 8, 0, 2, 0, 0, 1, 2)  # adorno del planeta
   elif not dibujar_joker(xj, yj, it, 2):
    draw_joker_box(xj, yj, it, 2)
   if raton_en(xj, yj, 32, 48):
    gs["tt_target"] = ("planeta" if isp else "joker", it, xj, yj + 24)
    if clic_nuevo():
     pack_pick(i)
     return
 if boton_clic("skip", 1, 156, 116, 4, 2):
  pack_skip()


def PantallaTienda(raton):
 cls()
 map(90, 0, 30, 17)
 draw_side_hud(False)
 draw_contadores(0, True)
 print_jokers(0)
 print_consumibles(0)
 gs["baraja"].mostrar(MAZO_X, MAZO_Y, 1, False, 0, 0)
 check_mazo_click(raton)
 # con un sobre abierto solo se ve su selector (y los botones de vender y
 # usar, para poder hacer hueco antes de elegir)
 if gs["pack"] is not None:
  draw_pack_picker(raton)
  draw_sell_use_buttons(raton)
  return
 # fondos de los bloques
 PrintBox(5, 130, 46, 9, 5)
 PrintBox(5, 146, 88, 7, 5)
 PrintBox(5, 86, 88, 7, 5)
 PrintBox(5, 90, 92, 6, 4)
 # izquierda: "next" y "reroll"
 if boton_clic("next", 1, 87, 48, 5, 2):
  shop_next_round()
 if gs["free_rr"] > 0:
  rlbl = "free"
 else:
  rlbl = "$" + str(gs["reroll"])
 act = gs["free_rr"] > 0 or gs["mn"] >= gs["reroll"]
 if boton_clic(rlbl, 0, 87, 69, 5, 2, act) and act:
  do_reroll()
 draw_text("reroll", 98, 84, 11)
 # derecha: 2 huecos principales arriba y 2 sobres abajo
 draw_shop_jslot(0, 142, 59, raton)
 draw_shop_jslot(1, 173, 59, raton)
 draw_shop_pslot(0, 155, 101, raton)
 draw_shop_pslot(1, 178, 101, raton)
 draw_sell_use_buttons(raton)


# -----------------------------------------------------------------------------
#  GM_CIEGAS: SELECCION DE CIEGA
# -----------------------------------------------------------------------------
def blind_panel(bi, x, y, raton):
 # Panel de la ciega bi (0 pequena, 1 grande, 2 jefe): circulo de color,
 # puntos que pide y, si es la que toca, boton "play" (si no, su premio).
 sel = (bi == gs["blind"])
 circ(x + 24, y + 18, 11, (6, 8, 2)[bi])
 nb = BLIND_NAME[bi]
 draw_text(nb, x + 27 - len(nb) * 2, y + 15, 11)
 req = int(ante_base(gs["ant"]) * BLIND_MULT[bi])
 draw_text("score", x + 18, y + 40, 11)
 draw_text(str(req), x + 27 - len(str(req)) * 2, y + 48, 2)
 rw = BLIND_REWARD[bi]
 if sel:
  if boton_clic("play", 4, x + 9, y + 58, 4, 2):
   start_blind()
 else:
  draw_text("$" * rw, x + 27 - rw * 2, y + 62, 8)


def PantallaBlind(raton):
 cls()
 map(90, 17, 30, 17)
 draw_side_hud(False)
 draw_contadores(0, False)
 print_jokers(0)
 print_consumibles(0)
 blind_panel(0, 79, 52, raton)
 blind_panel(1, 136, 52, raton)
 blind_panel(2, 192, 52, raton)
 draw_sell_use_buttons(raton)


# -----------------------------------------------------------------------------
#  GM_GAMEOVER
# -----------------------------------------------------------------------------
def PantallaGameOver(raton):
 cls(0)
 draw_text("GAME OVER", 106, 40, 2)
 draw_text("ANTE " + str(gs["ant"]) + " RONDA " + str(gs["rd"]), 100, 56, 11)
 draw_text("$" + str(gs["mn"]), 114, 68, 9)
 if boton_clic("menu", 4, 102, 90, 4, 2):
  gs["gm"] = GM_MENU
  gs["hand"] = []
  gs["b"] = []
  gs["jokers"] = []
  gs["consu"] = []
  gs["pack"] = None
  gs["baraja"] = Mazo(gs["DS"])


# =============================================================================
#  25. ARRANQUE Y BUCLE PRINCIPAL
# =============================================================================
gs["baraja"] = Mazo(gs["DS"])


def TIC():
 # TIC-80 llama a esta funcion 60 veces por segundo.
 gs["tt_target"] = None  # las pantallas lo rellenan si hay que pintar un tooltip
 gs["arrastre"] = None   # y este si se esta arrastrando una carta o un joker
 raton = mouse()         # (x, y, boton_izquierdo, ...)
 gm = gs["gm"]
 if gm == GM_MENU:
  PantallaMenu(raton)
 elif gm == GM_JUEGO:
  PantallaJuego(raton)
 elif gm == GM_VISOR:
  PantallaVisor(raton)
 elif gm == GM_TIENDA:
  PantallaTienda(raton)
 elif gm == GM_CIEGAS:
  PantallaBlind(raton)
 elif gm == GM_GAMEOVER:
  PantallaGameOver(raton)
 # lo arrastrado y el tooltip se pintan al final para quedar por encima
 # de todo
 ar = gs["arrastre"]
 if ar:
  if ar[0] == "carta":
   draw_card_at(ar[1], ar[2], ar[3])
  elif not dibujar_joker(ar[2], ar[3], ar[1]):
   draw_joker_box(ar[2], ar[3], ar[1])
 tt = gs["tt_target"]
 if tt:
  if tt[0] == "card":
   tt_card(tt[1], tt[2], tt[3])
  elif tt[0] == "joker":
   tt_joker(tt[1], tt[2], tt[3])
  elif tt[0] == "planeta":
   tt_planeta(tt[1], tt[2], tt[3])
 # guardar el estado del raton para detectar clics nuevos el proximo fotograma
 gs["Clk0"] = raton[2]
