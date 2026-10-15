# Changelog

*Read this in other languages: [Español](CHANGELOG.es.md).*

Versioning: the middle number goes up when a new game system arrives
(`0.X.0`); the last one is for more content, polish and fixes (`0.X.Y`). The
game stays below 1.0 until it is complete.

> **About this history.** It was rebuilt in October 2026 from saved copies of
> the code and the cartridges. Several versions had lost their number or shared
> the same one (0.1, 0.5, 0.8, 0.9…), so they were put back in order by their
> content (each one contains the previous one plus something new) and
> renumbered. Dates come from the development chats and from the save date of
> the cartridges; the one marked `~` is approximate. Another attempt existed
> between the prototype and v0.1.0, but it was lost.
>
> **About space.** Up to v0.4.1 the game was made with the free version of
> TIC-80, where all the code has to fit in one 64 KB bank. That is why the old
> versions use short names, 1-space indentation and almost no comments. v0.5.0
> is the first one made with TIC-80 PRO.

## v0.5.1 — 2026-10-15 — Descriptions, cleanup and fixes

- **New tooltips**: each of the 93 jokers has a Balatro-style description,
  with colors for chips, mult, money and keywords, its rarity and, for jokers
  that change over the run, what they give right now ("CURRENTLY"). The
  planet tooltip shows which hand it levels up, by how much, and the hand's
  current level. Cards, jokers and planets share the same look and never go
  off-screen.
- Cards and jokers being dragged are always drawn on top (they used to end up
  behind text, blinds and the shop).
- Packs with full slots: the picked joker or planet used to be lost. Now a
  warning shows up and the pack stays open, so you can sell jokers or
  use/sell planets to make room.
- Bug fixes: when a joker was destroyed or moved, the selection jumped to the
  one next to it; the Yellow Deck gave $10 in total instead of $10 extra
  ($14); every run started with a test Ice Cream.
- Cleaner code with the same gameplay: named constants (`EF_*`, `BAR_*`,
  `GM_*`, `FP_*` and the UI coordinates), helpers for buttons and clicks
  (`boton_clic`, `raton_en`, `clic_nuevo`, `jokers_de`), a single function
  for what each joker gives (`joker_aporte`) and a single hand analysis
  (`analizar_cartas`).
- Tested in the TIC-80 emulator and with a bot playing full runs on the
  pocketpy builds of TIC-80 1.1 and 1.3.

## v0.5.0 — 2026-10-08 — Readable rewrite with TIC-80 PRO

- First version made with **TIC-80 PRO**: the code no longer has to fit in one
  64 KB bank, so the whole file was reorganized into 25 commented sections with
  an index and a glossary. Same names as always; new helpers to remove repeated
  code (`dibujar_caja`, `roll_shop_items`, `nueva_partida`, `draw_tapete`,
  `draw_contadores`).
- Scoring order faithful to Balatro: played cards → cards held in hand (Steel,
  Baron…) → jokers.
- Jokers audited against the wiki: the 30 invented ones are gone, leaving
  **93 real jokers** (75 faithful, 18 marked `#M` with their real effect noted).
  16 rarities and 3 names fixed.
- `JSPR` checked against the cartridge sprites: the mapping was right.
- Bugs fixed: selling a joker during scoring crashed the game; the deck viewer
  showed cards from the previous round; a Stone card could make a pair or a
  flush for hand-type jokers; jokers could not be selected for selling on the
  blind screen.
- Tested in the TIC-80 emulator.

## v0.4.1 — 2026-06-11 — Card enhancements and 123 jokers

- Card enhancements now apply when scoring (`apply_card_ef`): Bonus, Mult,
  Wild, Glass, Steel, Stone, Gold and Lucky.
- Jokers with a sell value that grows (Egg) and that eat enhancements
  (Vampire).
- New jokers: Midas Mask, Golden Ticket and Lucky Cat (**123** in total).

## v0.4.0 — ~2026-06-09 — Planets and hand levels

- **12 poker hands**, including the secret Five of a Kind, Flush House and
  Flush Five, each with its own level.
- **12 planets** to level them up: bought in the shop and used from the
  consumable slots.
- Sell jokers and consumables, with sell/use buttons and a variable price.
- In-game text in English.
- **120 jokers**.

## v0.3.0 — 2026-06-01 — A full run

- **Blind select** screen (Small / Big / Boss) with the required score for
  each ante; antes keep scaling past ante 8.
- **Cash out** at the end of the round: blind reward, interest, money for
  remaining hands and from jokers.
- **Shop**: jokers by rarity (70 / 25 / 5 %), reroll that gets more expensive,
  free rerolls and Buffoon packs (normal, jumbo, mega).
- **Game over** screen, and Mr. Bones to save you once.
- Sort the hand by rank or suit, drag cards to reorder, two-line joker tooltips.
- **70 jokers** (Walkie Talkie, Blue Joker, Juggler, Popcorn, Golden Joker, To
  the Moon, Splash, Cloud 9, Chaos the Clown…).

## v0.2.3 — 2026-05-28 — HUD and money

- HUD split into its own functions (`draw_score_hud`, `draw_money_box`,
  `handle_play`, `handle_discard`).
- Hand size can change during the run.
- Scholar, Bloodstone, Rough Gem, Stuntman and Ice Cream get their real
  effects (5 new effect families).

## v0.2.2 — 2026-05-28 — 57 jokers and tooltips

- **57 jokers**: the ×mult family (The Duo, Trio, Family, Order, Tribe),
  scaling jokers (Ride the Bus, Green Joker, Runner, Square Joker, Spare
  Trousers), held-in-hand jokers (Baron, Shoot the Moon), Hiker, Ramen, Bull,
  Bootstraps, Misprint, Dusk, Abstract Joker, Mystic Summit, Acrobat…
- Tooltips for cards and jokers.
- Some of them still had known bugs, noted in the code comments.

## v0.2.1 — 2026-05-24 — Particles and shake

- Diamond-shaped particles for chips, mult, ×mult and retriggers.
- Damped shake on the chips and mult boxes and on the hand name.
- 5 new jokers: Fibonacci, Hack, Arrowhead, Bloodstone and Banner (**29**).
- Jimbo recolors to reuse one sprite for several jokers; jokers float gently.

## v0.2.0 — 2026-05-23 — Scoring engine

- All the game state lives in one dictionary (`gs`) and each screen is its own
  function.
- `detectar_mano`: high card to straight flush, with base chips and mult, and
  only the scoring cards count.
- **Event queue**: every card and every joker scores in turn with its own
  animation, like in Balatro.
- **24 jokers** in `JDEFS`, grouped into effect families (`F_*`).
- HUD with round score, hands, discards, money, ante and round; up to 5 cards
  selected.
- Debug mode to step through the queue with Z.

## v0.1.1 — 2026-05-08 — Bug fixes

- `repartir` could read outside the deck; it now draws from the top of the
  shuffled deck and stops when it is empty.
- `print_cards` no longer divides by zero with 0 or 1 cards.
- `eval_hand` used a variable that did not exist.
- The deck selector wraps around and only rebuilds the deck when it changes.
- Click debounce on the deck pile and in the deck viewer.

## v0.1.0 — 2026-04-21 — Fresh start in Python

- Started from scratch in Python (pocketpy).
- Main menu with the animated title and **8 decks**, each with its own rule.
- Hand of 8 cards with an idle wave, click to select, play and discard.
- Deck viewer with counts by suit and rank.
- Own 3×5 pixel font and sprite buttons with palette swaps.

## v0.0.1 — 2025-12-18 — Prototype tweaks

- Two extra UI boxes and small cleanups in the Lua prototype.

## v0.0.0 — 2025-06-20 — Lua proof of concept

- "Balaro": a hand of 8 cards from a shuffled deck, picked with a keyboard
  cursor (up to 5).
- Detects poker hands from high card to royal flush and shows their base chips
  and mult.
