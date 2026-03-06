# Planes

Open the Planes dialog with **Crystallography → Add Planes** (`Ctrl+Shift+L`).

Crystallographic planes are displayed as semi-transparent quads overlaid on the crystal. They can also be used to [slice the point cloud](slicing.md).

---

## Coordinate Modes

| Mode | Input | Requires |
|------|-------|---------|
| Miller (h k l) | Integer Miller indices | Lattice parameters set |
| Cartesian Normal | Float vector (nx, ny, nz) | Nothing |

Switch modes with the **Miller / Cartesian** selector in the dialog. If lattice parameters have not been set and you select Miller mode, a warning is shown. See [Lattice Parameters](lattice-parameters.md).

---

## Adding a Plane Manually

1. Select the coordinate mode (Miller or Cartesian)
2. Enter the h/k/l or nx/ny/nz values
3. Optionally set an **Origin** (X, Y, Z offset in world space)
4. Set **Size** (relative to crystal extent, 0.1–5.0×)
5. Choose a **Colour** (auto-assigned by indices, or pick manually)
6. Adjust **Opacity** (0 = transparent, 255 = opaque)
7. Click **Add Plane**

The plane appears in the viewport and is added to the plane list.

### Reduce Button

Click **Reduce** to simplify Miller indices by their GCD (e.g., `2 4 2` → `1 2 1`). This has no effect on the Cartesian normal.

---

## Finding a Plane from Points

You can fit a plane to three or more selected points in the viewport:

1. Click **Find Plane** in the dialog
2. The dialog hides. `Shift+Click` to select 3 or more points in the viewport
3. Click **Confirm** (in the Find Plane toolbar that appears)
4. The fitted plane is added to the list

This is useful when you want to identify the plane through specific crystallographic sites.

---

## Plane List

All added planes are shown in the plane list. Select a plane to:

- Edit its properties (origin, size, colour, opacity)
- Enable slicing (see [Slicing](slicing.md))
- Remove it with **Remove Selected**

**Clear All** removes every plane.

---

## Converting a Plane to a Direction

Select a plane in the list and click **Add as Direction**. This creates a new direction vector with the same normal vector as the selected plane in the [Directions dialog](directions.md).

---

## Plane Appearance

| Setting | Range | Description |
|---------|-------|-------------|
| Size | 0.1–5.0× | Size relative to crystal extent |
| Colour | RGB picker | Auto-assigned by indices; can be overridden |
| Opacity | 0–255 | Transparency of the quad |

---

## Cell Parameters Display

The current lattice parameters (a, b, c, α, β, γ) are shown at the top of the dialog for reference. They can be changed in [Lattice Parameters](lattice-parameters.md).
