# RESEARCH — How mangaka actually make manga

Sources (fetched 2026-11-02):
- SketchFlix, "The 10-Step Workflow: How to Make a Manga Step-by-Step"
- Art Rocket / Clip Studio, "How to Draw Anime Eyes Like A Pro"
- Clip Studio Tips, "My Style of Basic Manga Creation Methods"
- Search digest of anime-eye tutorials (Gvaat et al.)
- Too Corporation, "Inking" — frame lines typically 0.5–0.8 mm
- Clip Studio TIPS 3170, "Tips for Inking / Line Art" — G-pen weight guidelines
- z's Guide + Japan House (Kubo Kiriko) + r/ArtisanVideos — screentone: press
  with the tonehera, carve highlights with the tone knife (backing is flimsy;
  light pressure)

## The production pipeline (10 steps), mapped to our toolchain

| Step | Industry term | Our equivalent |
|---|---|---|
| 1. Core concept ("Want" + "Pressure") | the engine | session `prepare` + `reflection` notes |
| 2. Script by page/panel (beats) | the roadmap | composition notes before strokes |
| 3. "Name" storyboard | the skeleton | red construction guides (occlusion-clipped) |
| 4. Manuscript prep (B4, safe zones, bleed) | the paper | `prepare_session` 176×250, panel borders |
| 5. Pencils (roughs: anatomy, perspective) | the building | light-pressure construction strokes |
| 6. Inking — **line weight: thick for weight/shadow, thin for light/detail** | the finality | **G-pen hierarchy we lack: outline vs detail pressures** |
| 7. Backgrounds & perspective grids | the world | `world.py` camera, occlusion-clipped guides |
| 8. Screentones ("less is more") | the grays | `tone()` halftone grids — sparser, not denser |
| 9. Lettering — **"breathing room" so text isn't cramped** | the voice | `stamp_text` — must fit INSIDE balloons with margin |
| 10. Finish — **white-out corrections** | the fixes | **`whiteout` tool (this round)** |

## Eye construction (per Art Rocket), mapped

1. Anime eyes dominate the face — bigger than real. *Our eyes were timid arcs: go 2-3× larger.*
2. Outline shape → pupil center → highlights PLANNED first (use sketch lines as guides).
3. Iris: solid dark region; **pupil darker than the rest of the eye**.
4. **Upper eyelid casts a shadow over the top of the iris** (dark band under the lid).
5. **Two highlights**: large primary (light source) + small secondary, consistent across both eyes — leave them as paper.
6. Lower lid: faint, thin.
7. Expression = iris size + brow shape + shadows; constricted iris + blank eye = shock.

→ Implementation: `dot_fill` (overlapping dabs, highlight disks skipped = paper),
thick upper-lid pass, lid-shadow dabs on the iris top, two reserved highlights.

## Craft rules confirmed

- Line-weight hierarchy is THE inking skill (G-pen pressure): silhouettes
  thick, fabric/detail thin, backgrounds thinnest.
- Tones: less is more; let black/white contrast talk.
- Lettering needs breathing room: text smaller than the balloon, never
  touching the rim (fix: `whiteout` interior + margin check before stamping).
- White-out is a named finishing step for corrections — a real medium, not a
  cheat. Opaque: it fully covers, so no ghost floor (unlike the eraser).
- Backgrounds support emotion, don't compete: thin, sparse, occluded (we
  already occlusion-clip construction).

## Reference-page analysis (user-provided One Piece pages, 2026-11-02)

Finished pages (Alabasta reverie chapter; Wano/Onigashima battle) + one PENCIL
NAME/manuscript sheet — the construction-order evidence:

1. **Busts crop at the chest.** Emotional panels are head-and-chest, and the
   panel BORDER crops the body deliberately — intimacy via cropping. A
   floating head with no shoulders reads as an error (our page 2/3 P2/P3).
2. **Grounding = drawn contact.** In the name page's deck panel, figures stand
   with feet ON drawn plank lines that converge in perspective; contact is
   explicit. Ship decks read because rail + deck floor + planks are three
   separate drawn lines (rail above, floor below, figures BETWEEN them,
   legs occluded by the rail drawn afterward — occlusion order, not hope).
3. **Hair is a solid black mass**, not an outline — Zoro's and Luffy's hair
   are filled silhouettes with a few white accent cuts.
4. **Speed lines radiate from the action focus** and fill ACTION panels; they
   do not cross faces in calm talking panels.
5. **White space is structural** — big empty sky/sea areas make the black
   masses pop. Not everything needs tone.
6. **Figures overlap panel borders** (heads/shoulders breaking the frame) —
   a depth cue that makes characters inhabit the page.
7. **OP shonen eyes are SMALL and BOLD**: heavy upper lid, solid dark pupil,
   one white spec. Not huge irises — placement and contrast do the work.
8. The pencil name shows bodies ALWAYS present even in rough: vest, shorts,
   limbs — construction never reduces people to heads-on-sticks.

## Deltas for page 3

1. `whiteout` engine tool (opaque, no ghost, no damage) — balloon interiors
   whitened before stamping; tone collisions removed.
2. Eyes rebuilt per the tutorial: dot_fill iris, lid shadow, two highlights.
3. Line-weight hierarchy on every stroke choice.
4. Crew feet ON the deck (contact), deck drawn as a floor band; cabin present
   in BOTH ship views (consistency check between panels).
