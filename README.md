# Bitlatro

> A compact, faithful demake of **Balatro** for the [TIC-80](https://tic80.com) fantasy console, written in Python.

*Read this in other languages: [Español](README.es.md).*

## What is it?

Bitlatro is a poker roguelike that squeezes the core loop of Balatro into the
240×136 screen of TIC-80. You build a poker hand, play it for chips × mult,
stack synergistic **jokers**, level your hands with **planets** and beat
escalating **blinds** across antes, all rendered with a hand-made pixel font,
custom UI widgets and an animated, step-by-step scoring sequence.

All the pixel art and music are original.

## Features

- **8 decks**, each with its own rule twist (extra discard, extra hand,
  no-interest economy deck, $10 start, +1 joker slot / −1 hand, two-suit deck,
  ranks 1–10 only, fully randomized ranks).
- **93 jokers**, all from the real game (75 faithful, 18 still with a
  placeholder effect), across common / uncommon / rare rarities: flat and
  ×mult, per-suit, per-rank, per-hand-type, retriggers, scaling jokers,
  held-in-hand bonuses, economy jokers and destruction mechanics
  (Gros Michel → Cavendish).
- **12 poker hands**, including the secret **Five of a Kind**, **Flush House**
  and **Flush Five**, each leveled independently with **12 planets**.
- **Card modifiers**: 8 enhancements (Bonus, Mult, Wild, Glass, Steel, Stone,
  Gold, Lucky), foil/holo editions and 4 seals.
- **Shop** with rerolls, free rerolls and **booster packs** (normal / jumbo /
  mega).
- **Blinds** (Small / Big / Boss) with score targets and rewards, **antes**
  that scale beyond the base 8, and a full cash-out with interest.
- **Juicy presentation**: event-queue scoring animation, floating
  chip/mult/×mult/money particles, damped shake, drag-and-drop for cards and
  jokers, and a deck viewer with live suit/rank stats.

## How to play

1. **Select** up to 5 cards from your hand (click or drag).
2. **Play** the hand to score `chips × mult`, or **Discard** to swap cards.
3. Beat the **blind's required score** before you run out of hands.
4. **Cash out** and spend in the **shop**: buy jokers, planets and packs,
   reroll the offer, then pick your next blind.
5. Survive the rising antes for as long as you can.

## Running it

1. Install [TIC-80](https://tic80.com/create) (a version with Python support).
2. Download [`bitlatro.tic`](bitlatro.tic) and drag it onto the TIC-80 window,
   or type `load bitlatro.tic` and then `run` in the console.

The cartridge holds the code, sprites, map and music. The same code lives in
[`python/bitlatro.py`](python/bitlatro.py) so it can be read and diffed here.

## Code structure

Everything lives in one script (`python/bitlatro.py`), split into 25 commented
sections with an index at the top:

| Area | Key pieces |
|------|------------|
| Text & color | `mini_font`, `draw_text`, `set_col` / `reset_col` |
| State & data | `gs` global state, `SUITS`, `HAND_DEF`, `PLANETS`, `ANTE_BASE`, `BLIND_*` |
| Jokers | `JDEFS` definitions, `F_*` effect families, `JRAR` / `JPOOL` rarities, `JSPR` sprites |
| Entities | `Carta` (card), `Joker`, `Planeta`, `Mazo` (deck) |
| Rendering | `draw_card_at`, `print_cards`, `dibujar_joker`, `dibujar_planeta`, tooltips, `PrintBox` / `Boton`, particles |
| Hand logic | `detectar_mano`, `hand_score`, `calcular_mano_flags` |
| Scoring pipeline | `build_event_queue`, `step_queue`, `apply_event`, `apply_joker_effect`, `apply_card_ef` |
| Economy / shop | `roll_shop`, `buy_joker`, `buy_planeta`, `open_pack`, `pack_pick`, `cash_out_money` |
| Screens (`gm`) | `PantallaMenu` (0), `PantallaJuego` (1), `PantallaVisor` (2), `PantallaTienda` (3), `PantallaBlind` (4), `PantallaGameOver` (5) |
| Entry point | `TIC()` |

For a function-by-function walkthrough of the engine, see the
[technical documentation](docs/TECHNICAL.es.md) (Spanish).

## How it got here

Bitlatro started in **June 2025** as a small Lua proof of concept ("Balaro",
kept in [`prototype/`](prototype/)): a keyboard-driven hand that could only
detect poker hands. In **April 2026** I started over from scratch in Python and
grew it version by version: first the scoring engine, then the full run loop,
then planets and a much bigger joker roster.

Up to **v0.4.1** I was using the free version of TIC-80, where all the code has
to fit in a single 64 KB bank. Space was the priority: short names, 1-space
indentation, no comments and constant trimming. **v0.5.0** is the first version
made with **TIC-80 PRO**, so the 64 KB limit no longer applies, and the whole
code was rewritten to be readable and commented.

The history before October 2026 was rebuilt from saved copies. Several
versions had lost their numbers or shared the same one, so they were put back
in order by their content and renumbered. Each version has its tag and the
full log is in the [CHANGELOG](CHANGELOG.md).

| Version | Date | Highlights |
|---------|------|------------|
| `v0.0.0` | Jun 2025 | Lua proof of concept: hand of 8 cards and poker hand detection |
| `v0.0.1` | Dec 2025 | Prototype tweaks |
| `v0.1.0` | Apr 2026 | Fresh start in Python: deck menu, hand and deck viewer |
| `v0.1.1` | May 2026 | Bug fixes |
| `v0.2.0` | May 2026 | Event-queue scoring engine and the first 24 jokers |
| `v0.2.1` | May 2026 | Particles, shake and 29 jokers |
| `v0.2.2` | May 2026 | 57 jokers (scaling ones included) and tooltips |
| `v0.2.3` | May 2026 | Reworked HUD, money and hand-size effects |
| `v0.3.0` | Jun 2026 | Full run: blinds, cash out, shop, packs and game over |
| `v0.4.0` | Jun 2026 | Planets, hand levels, 12 hands and selling jokers |
| `v0.4.1` | Jun 2026 | Card enhancements in scoring and 123 jokers |
| `v0.5.0` | Oct 2026 | TIC-80 PRO rewrite: readable code, only real jokers (93) |

## Roadmap

- [ ] Faithful effects for the 18 placeholder jokers
- [ ] Boss blind variants
- [ ] Vouchers, tarot and spectral cards
- [ ] Skipping blinds and tags
- [ ] Animated Balatro-style background
- [ ] Save / continue

## Credits & license

Made by **LaCroquetona**, pixel art and music included.

Bitlatro is a non-commercial fan project inspired by *Balatro* by LocalThunk
(published by Playstack). It is not affiliated with or endorsed by them, and
all rights to Balatro belong to their owners. The MIT [license](LICENSE)
covers this project's own code and assets only.
