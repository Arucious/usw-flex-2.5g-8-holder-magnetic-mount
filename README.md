# USW-Flex-2.5G-8-PoE Holder — Magnetic Mount

A parametric, 3D-printable cradle for the **Ubiquiti UniFi Switch Flex 2.5G (8-port,
PoE)** that **mounts upside-down under a steel desk** using press-fit disc magnets.
The switch **slides in from the front** (where its RJ45 ports and cables are) and is
captured by chamfered bottom rails so it can't drop.

Modeled in [build123d](https://github.com/gumyr/build123d) (Python). Every dimension is
a named parameter at the top of [`switch_cradle.py`](switch_cradle.py). Sibling project
to [`g80sd-brick-holder-magnetic-mount`](../g80sd-brick-holder-magnetic-mount), reusing
its honeycomb generator, magnet grid, per-axis clearance and 45° chamfer conventions.

## Design

- **Solid top plate** (6 mm) holds six press-fit magnets and contacts the desk steel.
- **Open front** — the switch's RJ45 ports face here; cables exit here; the switch
  inserts here.
- **Honeycomb rear wall** vents the back and acts as the insertion stop.
- **Honeycomb side walls** vent the sides and locate the switch's short ends.
- **Open bottom** with two **chamfered retention rails** along the bottom edges. The
  45° underside doubles as the slide-in lead-in and prints support-free; the rails
  catch the switch so the (deliberately loose) fit never has to hold it by friction.

### Target device

Ubiquiti **USW-Flex-2.5G-8-PoE**, **212.9 × 99.4 × 33.5 mm** ([datasheet](https://download.axilogi.com/Ubiquiti/Datasheet/USW-Flex-2_5G-8-PoE.pdf)).
The base (non-PoE) USW-Flex-2.5G-8 is only 76 mm deep — if that's your unit, set
`SWITCH_W = 76`.

### As built (default parameters)

| | |
|---|---|
| Switch (held) | 212.9 × 99.4 × 33.5 mm (PoE) |
| Cavity clearance | 0.8 / 1.0 / 0.6 mm (L / W / H) — looser than the brick cradle |
| Overall size | 218.7 × 102.9 × 45.1 mm |
| Walls / top plate | 2.5 mm / 6.0 mm |
| Retention rails | 5 mm tall, 5 mm overhang, 45° underside (open bottom) |
| Magnets | 6 × ⌀20 × 3 mm discs, pockets ⌀20.1 × 3 mm, 3×2 grid |
| Honeycomb | ⌀7 mm hexes, 2 mm gap, 5 mm border — 26 holes (6 + 6 sides, 14 rear) |

## Printing

- Orient **magnet-plate-down** (solid plate on the bed): magnet pockets open to the
  bed for flush, support-free magnets; the rail chamfers are self-supporting.
- Press ⌀20 × 3 mm discs into the pockets flush so they contact the desk steel.
- The fit relies on small per-axis clearances (`CLEARANCE_L/W/H`); the rails do the
  retaining, not friction. Adjust the clearances if your printer runs tight or loose.

Ready-to-print [`switch_cradle.stl`](switch_cradle.stl) and a
[`switch_cradle.step`](switch_cradle.step) are included.

## Regenerating / customizing

Requires Python 3.10+ (3.13 recommended).

```bash
python3 -m venv .venv
.venv/bin/pip install build123d
.venv/bin/python switch_cradle.py        # writes switch_cradle.stl + .step
```

Edit the `PARAMETERS` block at the top of `switch_cradle.py` to change switch size,
clearance, wall/top thickness, magnet count/size, honeycomb hex size, or the rail
dimensions — everything downstream is derived.

### Live preview (optional)

```bash
.venv/bin/pip install ocp_vscode
.venv/bin/python -m ocp_vscode --port 3939      # open http://127.0.0.1:3939/viewer
.venv/bin/python switch_cradle.py               # pushes the model into the viewer
```

The `show()` call in the script is guarded, so it's a no-op when no viewer is running.

## License

MIT — see [LICENSE](LICENSE).
