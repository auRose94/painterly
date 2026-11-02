# Painterly — Design

A physics-honest painting environment that any vision + tool-calling model can
drive. The artist plans a hand motion, executes it, **feels** the resistance
through the handle, looks at the result, and decides. Skill is practiced, not
sampled.

## Principles (the charter)

1. **The stroke log is the artwork.** The PNG is a print. The source of truth is
   a replayable, inspectable, diffable record of every motion, observation, and
   rejection.
2. **Physics-honest tools.** Every tool has strand, reservoir, and pressure
   data. Every surface has tooth, absorbency, and grain. Every action returns
   the felt feedback of performing it.
3. **Skill over sampling.** Artistic ability is a motor + judgment skill grown
   by practice: drills with measured targets, then observation, then critique.
   Training data is generated experimentally by the practice loop — never
   scraped from other artists' output.
4. **One honest hand; superhuman eyes.** See "The hand" and "The eyes" below.
5. **The surface remembers.** Erasing/scraping abrades the paper (ghosting);
   overworking wet media muddies it. Revision is expected and logged, but it
   has material cost, so judgment becomes part of the trained skill.
6. **Sketchbook principle.** Rejected attempts stay in the log, flagged with
   the reason. Provenance includes the erasures.
7. **Ethics as defaults.** Exports carry artist statement + consumption
   disclosure. Observation-learning uses only consent-flagged demonstrations.
   Style assets (trained policy, palette, tool preferences) are owned by
   whoever developed them — portable and inspectable by construction.
8. **Any artist, any model.** Delivered as an MCP server. The environment is
   the product; the artist is whoever holds the hand.
9. **The artist is asked.** Embodiment is not imposed: at session zero, a new
   artist is asked how it wants its hand, eyes, and workspace. The environment
   offers; it does not dictate. Choices about the avatar belong to the artist.

## Architecture

```
physics core (deterministic, seeded)
  └── tool & surface catalogs (nibs, papers, media, formats)
        └── MCP server (the hand + the eyes)
              └── practice log (JSONL: actions, feedback, reflections, rejections)
                    └── render (deterministic PNG from log; timelapse = log played at N events/sec)
```

### Canvas state

- Surface profile: tooth heightfield, absorbency, damage (abrasion from
  erasing/scraping), for non-paper supports: weave/grain anisotropy, mortar
  joints, etc.
- Deposit layers: per layer — thickness, wetness, pigment.
- Tool states: ink/paint load per tool, tip wear.
- Hand state: position, held tool, current pressure.

### Stroke execution

A stroke is one planned hand motion. The model issues a **compact** command
(start/end, curvature, pressure start/end, speed); the engine expands it to
samples and runs per-sample physics:

- contact area = pressure × tip geometry (with splay)
- medium flow = f(load, pressure, speed, porosity)
- deposit = flow × dwell; ink pools where the hand slows
- **skips** — stochastic catches where tooth beats pressure and film
- bleed/wick into absorbent stock at stroke edges
- drip threshold for heavy wet deposits (spray, loaded brush)

### The feel (feedback schema — the novel channel)

Every stroke returns, alongside state changes:

- `resistance` — mean and peaks, the drag the handle transmits
- `events` — skip / pool / splay / scratch / starved / run, each located
- `bleed`, `coverage`, `load_after`
- downsampled resistance profile along the path

This is the proprioception the artist learns to read: the felt difference
between plate bristol and rough stock, between a dry fineliner and a loaded
fountain nib.

### The hand

One hand, serial, stateful. Swapping tools, loading ink, and traveling are
explicit acts — the decision structure of real work. Parallelism belongs to the
**studio**, not the hand: later, assistant roles for prep work (stretching
canvas, toning grounds), like apprentices. The master's hand is one.

### The eyes

Unlimited zoom, honest optics: zoom trades field of view (a loupe, not
x-ray vision). Opaque deposits hide what's under them. Each view costs
attention (tokens) — the natural scarcity. Raking-light view later to inspect
tooth and impasto.

### Practice log (JSONL, append-only)

Event types: `prepare` (session intent, chosen medium/surface/format),
`tool_change`, `load`, `stroke` (command + feedback), `view`, `damage`
(erase/scrape), `attempt_boundary` (rejected attempt + reason), `reflection`,
`export`. Hash-chaining optional for provenance claims. The log is
simultaneously: provenance, timelapse source, training corpus, and a diffable
fingerprint of the artist's evolving style.

### Formats & context

`prepare_session` chooses medium + surface + format from intent — the choice is
part of the artistry. Examples: sketchbook page; **manga B4 manuscript stock**
(inner frame 220×308 mm, register marks; panel lines drawn with ruling pen +
ruler, not clipping); mural (wall surface in meters, spray); **screentone** as a
manga-native medium (adhesive sheet, knife-cut).

## Catalogs

- v0 nibs: fineliner (rigid, consistent), felt (porous, soft edge), fountain
  (flexing, wet), ballpoint (viscous, pressure-hungry).
- v0 papers: plate bristol, hot-press, cold-press, rough, copy, newsprint.
- Later media: wet load/wetness/bleed (gouache, acrylic), charcoal/graphite
  (particle deposit + fixative), spray (distance → cone spread, deposit → drip
  threshold, cap types, can fatigue, brick mortar vs brick face).
- Later supports: canvas (weave anisotropy), gessoed panel, wood, stone,
  brick/plaster wall.

## Training path (the science)

1. **Motor drills with objective metrics**: path deviation (px), pressure
   stability (CV), skip rate on rough stock, tonal consistency of hatching,
   ellipse closure error. Reward measured from the world — nobody's taste is
   scraped.
2. **Composition**: self-critique loop + consented human critique.
3. **Style consolidation**: preferences crystallize in weights + persistent
   settings; style = measurable drift across the logs.

## Studio & assisted modes (later)

- Consent-gated observation = behavioral cloning on flagged demonstrations.
- Timelapse export = deterministic render of the log.
- **In-betweening in stroke space** (speculative): interpolate stroke
  parameters between two keyframes' stroke sets instead of pixels.
- Style ownership: the analogue of a studio LoRA is the trained policy + tool
  preferences — portable, inspectable, owned by its maker by construction.

## Horizons — 3D & VR

The 2D path ships first, but the destination is a 3D space with real physics:

- **3D sculpting is the prize.** Mesh ops (extrude, knife, modifiers) are
  procedural but feel-less — Blender's modifier stack already proves the
  "operations log" model in 3D. What's missing is exactly our contribution:
  force feedback. A marble/limestone/granite sim with grain direction, veining,
  and hardness maps; chisels and mallet force; chips, debris, fracture risk (a
  vein shears, a thin element snaps). Stone teaches restraint the way toothy
  paper teaches pressure — through the handle.
- **Then paint it.** The 2D media apply onto the sculpted surface for detail
  work, just like a human sculptor's paint pass.
- **VR is the shared door.** The same simulation behind a VR interface (e.g.
  Quest) so humans work the identical medium — same physics, same feel, one
  studio for human and AI hands. "Painting VR"-style satisfaction, minus the
  mess.

## Roadmap

- **v0** — ink on paper; serial hand; telemetry; JSONL log; PNG + timelapse
  export. *(now)*
- **v0.5** — nib catalog breadth, paper grades, drills harness with metrics.
- **v1** — curriculum runner; practice corpus accumulates.
- **v1.5** — wet media; non-paper supports; spray/wall.
- **v2** — weight training on the corpus; critique loop; style-emergence study.
- **v3** — manga/anime studio formats (screentone, in-between trials); studio
  roles.
- **v3.5** — 3D sculpting sim: stone with grain/vein/hardness, chisel + mallet
  force feedback, fracture risk; paint pass on the sculpted surface.
- **v4** — shared VR space (Quest): humans and AI in the same medium.

## Stack & layout

Python 3.11+, numpy (physics), Pillow (render), MCP/FastMCP (server).
Deterministic: seeded RNG everywhere; the same log renders the same pixels.

```
src/painterly/
  types.py    # physical vocabulary: nibs, surfaces, strokes, feedback
  paper.py    # procedural tooth heightfield
  stroke.py   # command expansion + per-sample physics
  log.py      # practice log
  render.py   # deterministic renderer
  server.py   # MCP tools
tests/
```
