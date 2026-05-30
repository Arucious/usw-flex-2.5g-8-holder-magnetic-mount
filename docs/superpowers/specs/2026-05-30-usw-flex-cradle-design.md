# USW-Flex-2.5G-8-PoE Under-Desk Magnetic Cradle — Design

**Date:** 2026-05-30
**Status:** Approved pending review

## Purpose

A 3D-printable cradle that holds a Ubiquiti UniFi Switch Flex 2.5G 8-port **PoE**
switch upside-down under a steel desk. Press-fit disc magnets in the solid top
plate grab the desk steel; the switch inserts from the front (where its RJ45 ports
and cables are), and chamfered bottom rails capture it so it can't drop. Built as a
parametric build123d script, exporting STL + STEP, following the conventions of the
sibling `g80sd-brick-holder-magnetic-mount` project.

## Target device

Ubiquiti **USW-Flex-2.5G-8-PoE**, official dimensions **212.9 × 99.4 × 33.5 mm**.
(The non-PoE base model is only 76 mm deep; the user's ~4 in / 101.6 mm measured
depth confirms the PoE variant. Building to the published PoE spec.)

## Coordinate convention

- **X** = length (212.9 mm) — the switch's long axis; the two short ends are gripped
  by the side walls.
- **Y** = depth (99.4 mm) — the insertion/slide direction. Front opening at −Y.
- **Z** = height (33.5 mm) — 0 at the open bottom (floor-facing when mounted),
  increasing up to the solid magnet plate (against the desk steel).

## Faces / structure

| Face | Treatment | Why |
|------|-----------|-----|
| **Top** (+Z, to desk) | Solid plate, magnet pockets | Needs material behind magnets; contacts steel |
| **Bottom** (−Z, to floor) | Open, with chamfered retention rails | Lightweight; rails catch the switch & guide insertion |
| **Front** (−Y) | Fully open | Ports face here; insertion; cable exit |
| **Rear** (+Y) | Honeycomb wall + insertion stop | Vented; sets insertion depth |
| **Sides** (±X) | Honeycomb walls | Vented; grip the switch's short ends |

## Key parameters (initial values)

```
SWITCH_L = 212.9   # X
SWITCH_W = 99.4    # Y (depth / insertion)
SWITCH_H = 33.5    # Z

# Looser than the brick (which was still hard to insert at 0.5 mm width):
CLEARANCE_L = 0.8  # X (ends gripped by side walls)
CLEARANCE_W = 1.0  # Y (slide direction — generous, no effect on hold)
CLEARANCE_H = 0.6  # Z

WALL = 2.5         # side + rear wall thickness
TOP_THICK = 6.0    # magnet plate thickness (pockets cut from the desk side)

# Magnets: 6 (3×2), proven press-fit from the brick project
MAGNET_DIA = 20.0 ; MAGNET_THICK = 3.0
POCKET_DIA = 20.1 ; POCKET_DEPTH = 3.0   # keep 20.1 — tested press-fit
MAG_COLS = 3 ; MAG_ROWS = 2

# Bottom retention rails (the "chamfer to slide it in" + catch)
RAIL_THICK = 5.0     # how far the rail stands proud (Z), 45° underside
RAIL_OVERHANG = 5.0  # how far it reaches inward over the switch (X)

# Honeycomb (reused generator)
HEX_CIRCUMRADIUS = 7.0 ; HEX_GAP = 2.0 ; HEX_BORDER = 5.0

# Rear insertion stop
END_STOP = True ; END_STOP_THICK = 2.5 ; END_STOP_HEIGHT = 12.0
```

## Retention strategy

- **Insertion:** friction kept deliberately loose (clearances above) so the switch
  slides in easily — the brick at 0.5 mm was too tight and bowed its walls.
- **Hold (upside-down):** chamfered bottom rails along the bottom edges of the two
  side walls. The 45° underside doubles as the slide-in lead-in and prints
  support-free in the chosen orientation. The rails physically catch the switch so
  the loose friction never has to bear the ~700 g load.
- **Depth:** rear honeycomb wall acts as the stop; front stays fully open.

## Print orientation

**Magnet-plate-down** (solid plate on the bed): magnet pockets open to the bed for
flush, support-free magnets. The open bottom + honeycomb faces print as the upper
structure; the bottom rails' 45° chamfers are self-supporting. Per the user: the
bottom is intentionally open (not a solid floor) with just the chamfered rails.

## Reuse from `g80sd-brick-holder-magnetic-mount`

- Parametric honeycomb centre generator (`hex_centers`) + `honeycomb_cutter`
- Per-axis clearance pattern
- Magnet-pocket grid (`grid_positions`)
- 45° chamfered-rail profile (was the brick's lips)
- Report printout + `export_stl`/`export_step` + guarded `ocp_vscode` `show()`

## Out of scope (YAGNI)

- No cable notch (front is fully open — ports/cables already clear).
- No PoE-vs-non-PoE auto-switching; build to the PoE spec, dimensions are params.
- MakerWorld generator port remains a future aspiration, not this build.

## Success criteria

1. Script runs clean, exports a valid (watertight, single-solid) STL + STEP.
2. Switch inserts easily (looser than the brick) and is captured by the rails.
3. Honeycomb on both sides + rear; solid top with 6 magnet pockets (⌀20.1×3).
4. Reported dimensions + hex counts printed for sanity-check.
