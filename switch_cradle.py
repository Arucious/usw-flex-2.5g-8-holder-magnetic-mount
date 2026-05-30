"""
Parametric under-desk magnetic cradle for a Ubiquiti USW-Flex-2.5G-8-PoE switch.

Mounts UPSIDE-DOWN under a steel desk: press-fit disc magnets in the solid TOP
plate grab the steel. The switch slides in from the FRONT (where its RJ45 ports
and cables are); chamfered bottom rails capture it so it can't drop. The fit is
deliberately looser than the sibling brick cradle -- that one was hard to insert
and bowed its walls -- so the rails, not friction, do the retaining.

Geometry (printed magnet-plate-down):
  - Solid TOP PLATE      (+Z, holds magnets, contacts the desk steel)
  - OPEN BOTTOM          (-Z, faces the floor) with two chamfered RETENTION RAILS
  - OPEN FRONT           (-Y, ports / cables / insertion)
  - Honeycomb REAR WALL  (+Y, also the insertion stop)
  - Honeycomb SIDE WALLS (+/-X, grip the switch's short ends)
  - 3x2 grid of press-fit magnet pockets cut into the top from the desk side

Coordinate convention:
  X = length (212.9)  -- switch long axis; side walls grip the short ends
  Y = depth  (99.4)   -- insertion direction; front open at -Y, rear wall at +Y
  Z = height (33.5)   -- 0 at the open bottom (floor side), up to the top plate

All tunable values live in the PARAMETERS block. Everything downstream is derived.
Shares its honeycomb generator, magnet grid, per-axis clearance and 45deg chamfer
conventions with ../g80sd-brick-holder-magnetic-mount.
"""

import math

from build123d import (
    Box,
    Cylinder,
    Plane,
    Polygon,
    Pos,
    RegularPolygon,
    Sketch,
    export_step,
    export_stl,
    extrude,
)

# ---------------------------------------------------------------------------
# PARAMETERS  (millimetres)
# ---------------------------------------------------------------------------

# --- The switch being held (Ubiquiti USW-Flex-2.5G-8-PoE, official dims) ---
SWITCH_L = 212.9   # length  (X)
SWITCH_W = 99.4    # depth   (Y, insertion direction)
SWITCH_H = 33.5    # height  (Z)

# --- Fit (looser than the brick, which was hard to insert at 0.5 mm width) ---
CLEARANCE_L = 0.8  # X (the ends gripped by the side walls)
CLEARANCE_W = 1.0  # Y (slide-in direction -- generous, no effect on hold)
CLEARANCE_H = 0.6  # Z

WALL = 2.5         # side + rear wall thickness
TOP_THICK = 6.0    # top (magnet) plate thickness; pockets cut from the desk side

# --- Disc magnets / pockets (proven press-fit from the brick project) ---
MAGNET_DIA = 20.0       # nominal magnet diameter (reference)
MAGNET_THICK = 3.0      # magnet disc thickness (reference)
POCKET_DIA = 20.1       # pocket diameter -- tested press-fit, keep exactly
POCKET_DEPTH = 3.0      # pocket depth, cut from the OUTER (desk-facing) side
MAG_COLS = 3            # magnets along the length (X)
MAG_ROWS = 2            # magnets across the depth (Y)
MAG_INSET_END = 30.0    # inset of outer magnet centres from each short end (X)
MAG_INSET_SIDE = 24.0   # inset of magnet centres from front/rear edges (Y)

# --- Bottom retention rails (capture the switch + act as the slide-in chamfer) --
# The chamfer is exactly 45deg (self-supporting, magnet-plate-down) when
# RAIL_THICK == RAIL_OVERHANG.
RAIL_THICK = 5.0    # how far each rail stands proud of the bottom edge (Z)
RAIL_OVERHANG = 5.0 # how far each rail reaches inward over the switch (X)

# --- Honeycomb venting (rear wall + both side walls) ---
HEX_CIRCUMRADIUS = 7.0  # hexagon size: centre -> vertex (the hole radius)
HEX_GAP = 2.0           # solid wall remaining between adjacent hexes
HEX_BORDER = 5.0        # solid, un-perforated border around each vented region

# --- Output ---
STL_PATH = "switch_cradle.stl"
STEP_PATH = "switch_cradle.step"


# ---------------------------------------------------------------------------
# DERIVED DIMENSIONS
# ---------------------------------------------------------------------------
# Cavity = switch + per-axis clearance.
CAVITY_L = SWITCH_L + CLEARANCE_L
CAVITY_W = SWITCH_W + CLEARANCE_W
CAVITY_H = SWITCH_H + CLEARANCE_H

# Outer envelope.
#   X: a side wall on each end          -> CAVITY_L + 2*WALL
#   Y: front open (no wall), rear wall  -> CAVITY_W + WALL
#   Z: rails below + cavity + top plate -> RAIL_THICK + CAVITY_H + TOP_THICK
OUTER_L = CAVITY_L + 2 * WALL
OUTER_W = CAVITY_W + WALL
OUTER_H = RAIL_THICK + CAVITY_H + TOP_THICK

CAVITY_FLOOR_Z = RAIL_THICK              # rail tops / where the switch bottom sits
CAVITY_CEIL_Z = RAIL_THICK + CAVITY_H    # underside of the top plate

# Front opening left between the two rails (sanity check this stays > 0).
RAIL_OPENING_L = CAVITY_L - 2 * RAIL_OVERHANG

# A small overshoot so subtractive cuts break cleanly through faces.
EPS = 1.0


# ---------------------------------------------------------------------------
# HONEYCOMB CENTRE GENERATION  (shared approach with the brick cradle)
# ---------------------------------------------------------------------------
def hex_centers(u_min, u_max, v_min, v_max, circumradius, gap):
    """Offset (tessellated) hex packing -- the HexLocations equivalent.

    Returns (u, v) centres for POINTY-TOP hexagons whose full extent fits inside
    the rectangle [u_min, u_max] x [v_min, v_max]. A single centre-to-centre
    pitch D gives a uniform `gap` between all six neighbours:

        D = sqrt(3) * circumradius + gap
    """
    D = math.sqrt(3) * circumradius + gap
    col_pitch = D                       # horizontal spacing within a row
    row_pitch = D * math.sqrt(3) / 2.0  # vertical spacing between rows
    half_w = math.sqrt(3) / 2.0 * circumradius  # apothem (horizontal)
    half_h = circumradius                       # centre -> top vertex (vertical)

    u_c = (u_min + u_max) / 2.0
    v_c = (v_min + v_max) / 2.0
    usable_u = (u_max - u_min) - 2 * half_w
    usable_v = (v_max - v_min) - 2 * half_h
    if usable_u < 0 or usable_v < 0:
        return []  # region too small for even one hex inside the border

    # Maximal count of fully-inside rows/cols, then centre the whole block.
    n_rows = int(usable_v / row_pitch) + 1
    n_cols = int(usable_u / col_pitch) + 1
    v_start = v_c - (n_rows - 1) * row_pitch / 2.0

    centers = []
    for j in range(n_rows):
        v = v_start + j * row_pitch
        u_off = (col_pitch / 2.0) if (j % 2) else 0.0  # offset alternate rows
        cols = n_cols if u_off == 0.0 else max(1, n_cols - 1)
        u_start = u_c - (cols - 1) * col_pitch / 2.0
        for i in range(cols):
            u = u_start + i * col_pitch
            if (u - half_w >= u_min and u + half_w <= u_max
                    and v - half_h >= v_min and v + half_h <= v_max):
                centers.append((u, v))
    return centers


def honeycomb_cutter(u_min, u_max, v_min, v_max, plane, thickness):
    """Both-directions extruded honeycomb cutter on `plane` (u -> plane x,
    v -> plane y). Returns (solid_or_None, count)."""
    centers = hex_centers(u_min, u_max, v_min, v_max, HEX_CIRCUMRADIUS, HEX_GAP)
    if not centers:
        return None, 0
    sketch = Sketch()
    for (u, v) in centers:
        sketch += Pos(u, v) * RegularPolygon(
            HEX_CIRCUMRADIUS, 6, major_radius=True, rotation=90
        )
    cutter = extrude(plane * sketch, amount=thickness / 2.0, both=True)
    return cutter, len(centers)


def grid_positions(span, count, inset):
    """`count` centres evenly spread along `span`, `inset` from each edge."""
    lo = -span / 2.0 + inset
    hi = span / 2.0 - inset
    if count == 1:
        return [0.0]
    return [lo + (hi - lo) * k / (count - 1) for k in range(count)]


# ---------------------------------------------------------------------------
# BUILD THE CRADLE
# ---------------------------------------------------------------------------
# 1) Outer block: bottom face on Z=0, centred in X and Y.
cradle = Pos(0, 0, OUTER_H / 2.0) * Box(OUTER_L, OUTER_W, OUTER_H)

# 2) Hollow out the switch space -- one cut that also opens the BOTTOM (-Z) and
#    the FRONT (-Y). Keeps: side walls (+/-X), rear wall (+Y), top plate (+Z).
#    Y spans from beyond the front face to the rear wall's inner face.
cut_y_front = -OUTER_W / 2.0 - EPS               # overshoot the open front
cut_y_rear = OUTER_W / 2.0 - WALL                 # leave the rear wall
cut_y_len = cut_y_rear - cut_y_front
cut_z_lo = -EPS                                   # overshoot the open bottom
cut_z_hi = CAVITY_CEIL_Z                          # leave the top plate
cut_z_len = cut_z_hi - cut_z_lo
cradle -= Pos(
    0, (cut_y_front + cut_y_rear) / 2.0, (cut_z_lo + cut_z_hi) / 2.0
) * Box(CAVITY_L, cut_y_len, cut_z_len)

# 3) Magnet pockets: cut into the top plate from the OUTER (desk-facing) side.
#    Pockets occupy Z in [OUTER_H - POCKET_DEPTH, OUTER_H]; the remaining
#    (TOP_THICK - POCKET_DEPTH) mm backs each magnet toward the cavity.
mag_xs = grid_positions(OUTER_L, MAG_COLS, MAG_INSET_END)
mag_ys = grid_positions(OUTER_W, MAG_ROWS, MAG_INSET_SIDE)
for mx in mag_xs:
    for my in mag_ys:
        cradle -= Pos(mx, my, OUTER_H - POCKET_DEPTH / 2.0) * Cylinder(
            POCKET_DIA / 2.0, POCKET_DEPTH
        )

# 4) Honeycomb venting.
hex_v_min = CAVITY_FLOOR_Z + HEX_BORDER          # above the rails
hex_v_max = CAVITY_CEIL_Z - HEX_BORDER           # below the top plate

# 4a) Side walls (+/-X), in the Y-Z plane. Build one cutter on Plane.YZ (at X=0)
#     then shift it out to each wall's midplane.
side_u_min = -OUTER_W / 2.0 + HEX_BORDER
side_u_max = OUTER_W / 2.0 - HEX_BORDER
side_wall_x = OUTER_L / 2.0 - WALL / 2.0
hexes_side = {}
for sign in (+1, -1):
    cutter, n = honeycomb_cutter(
        side_u_min, side_u_max, hex_v_min, hex_v_max, Plane.YZ, WALL + 2 * EPS
    )
    hexes_side[sign] = n
    if cutter is not None:
        cradle -= Pos(sign * side_wall_x, 0, 0) * cutter

# 4b) Rear wall (+Y), in the X-Z plane.
rear_u_min = -OUTER_L / 2.0 + HEX_BORDER
rear_u_max = OUTER_L / 2.0 - HEX_BORDER
rear_wall_y = OUTER_W / 2.0 - WALL / 2.0
rear_cutter, hexes_rear = honeycomb_cutter(
    rear_u_min, rear_u_max, hex_v_min, hex_v_max, Plane.XZ, WALL + 2 * EPS
)
if rear_cutter is not None:
    cradle -= Pos(0, rear_wall_y, 0) * rear_cutter

# 5) Bottom retention rails: a chamfered bar along the bottom inner edge of each
#    side wall, reaching inward over the switch. The 45deg chamfer (when
#    RAIL_THICK == RAIL_OVERHANG) faces the cavity, so it both captures the
#    switch's bottom edge and prints support-free magnet-plate-down. The rails
#    run the full cavity depth (front opening to the rear wall) and are extruded
#    along Y. Cross-section in (X, Z), built on Plane.XZ:
#
#        chamfer base (CAVITY_L/2, RAIL_THICK) ___ outer-top (OUTER_L/2, RAIL_THICK)
#                                              ╲  |
#                          45deg chamfer over   ╲ |
#                          the cavity            ╲|
#        inner tip (CAVITY_L/2-RAIL_OVERHANG, 0)__|___ outer-bottom (OUTER_L/2, 0)
rail_y_front = -OUTER_W / 2.0                     # rails reach the front edge
rail_y_rear = OUTER_W / 2.0 - WALL                # ... and tie into the rear wall
rail_y_len = rail_y_rear - rail_y_front
for side in (+1, -1):
    pts = [
        (side * OUTER_L / 2.0, RAIL_THICK),                    # outer-top
        (side * OUTER_L / 2.0, 0.0),                           # outer-bottom
        (side * (CAVITY_L / 2.0 - RAIL_OVERHANG), 0.0),        # inner tip (bottom)
        (side * CAVITY_L / 2.0, RAIL_THICK),                   # chamfer base (top)
    ]
    profile = Plane.XZ * Polygon(*pts, align=None)
    rail = extrude(profile, amount=rail_y_len / 2.0, both=True)
    cradle += Pos(0, (rail_y_front + rail_y_rear) / 2.0, 0) * rail


# ---------------------------------------------------------------------------
# EXPORT
# ---------------------------------------------------------------------------
export_stl(cradle, STL_PATH)
export_step(cradle, STEP_PATH)

bbox = cradle.bounding_box()


def _report():
    print("=" * 60)
    print("USW-FLEX-2.5G-8-PoE CRADLE -- build summary")
    print("=" * 60)
    print(f"Switch (held item)  : {SWITCH_L} x {SWITCH_W} x {SWITCH_H} mm")
    print(f"Clearance L/W/H     : {CLEARANCE_L} / {CLEARANCE_W} / {CLEARANCE_H} mm")
    print(f"Cavity (inside)     : {CAVITY_L} x {CAVITY_W} x {CAVITY_H} mm")
    print(f"Wall / top plate    : {WALL} mm walls, {TOP_THICK} mm top")
    print(f"Outer envelope      : {OUTER_L} x {OUTER_W} x {OUTER_H} mm")
    print(f"Bounding box (real) : "
          f"{bbox.size.X:.2f} x {bbox.size.Y:.2f} x {bbox.size.Z:.2f} mm")
    print("-" * 60)
    print(f"Retention rails     : {RAIL_THICK} mm tall, {RAIL_OVERHANG} mm "
          f"overhang each side, 45deg underside")
    print(f"  bottom opening    : {RAIL_OPENING_L:.1f} mm between rails "
          f"(switch {SWITCH_L} mm -> caught by "
          f"{(SWITCH_L - RAIL_OPENING_L) / 2:.1f} mm per side)")
    print(f"  insertion         : slide in from the open FRONT; rear wall = stop")
    print("-" * 60)
    print(f"Magnet pockets      : {MAG_COLS}x{MAG_ROWS} grid = "
          f"{MAG_COLS * MAG_ROWS} pockets, "
          f"dia {POCKET_DIA} mm x {POCKET_DEPTH} mm deep")
    print(f"  magnet (nominal)  : dia {MAGNET_DIA} x {MAGNET_THICK} mm")
    print(f"  backing behind    : {TOP_THICK - POCKET_DEPTH} mm")
    print(f"  X centres         : {[round(x, 1) for x in mag_xs]}")
    print(f"  Y centres         : {[round(y, 1) for y in mag_ys]}")
    print("-" * 60)
    print(f"Honeycomb           : circumradius {HEX_CIRCUMRADIUS} mm, "
          f"gap {HEX_GAP} mm, border {HEX_BORDER} mm")
    print(f"  hexes  +X wall    : {hexes_side[+1]}")
    print(f"  hexes  -X wall    : {hexes_side[-1]}")
    print(f"  hexes  rear wall  : {hexes_rear}")
    total = hexes_side[+1] + hexes_side[-1] + hexes_rear
    print(f"  TOTAL hex holes   : {total}")
    print("-" * 60)
    print(f"Exported            : {STL_PATH}, {STEP_PATH}")
    print("=" * 60)


_report()

# Optional live viewer -- guarded so headless / CI runs don't fail.
try:
    from ocp_vscode import show
    show(cradle)
    print("[ocp_vscode] viewer updated.")
except Exception as exc:
    print(f"[ocp_vscode] skipped live view ({type(exc).__name__}).")
