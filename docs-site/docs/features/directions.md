# Directions

Open the Directions dialog with **Crystallography → Add Directions** (`Ctrl+Shift+D`).

Crystallographic direction vectors are rendered as lines, arrows, or cylinders overlaid on the crystal. They can represent growth directions, slip directions, or any other vectors of interest.

---

## Coordinate Modes

| Mode | Input | Requires |
|------|-------|---------|
| Fractional [u v w] | Integer direction indices | Lattice parameters set |
| Cartesian | Float vector (x, y, z) | Nothing |

Switch modes with the **Fractional / Cartesian** selector. If lattice parameters have not been set and you select Fractional mode, a warning is shown. See [Lattice Parameters](lattice-parameters.md).

---

## Adding a Direction

1. Select the coordinate mode
2. Enter the [u v w] or (x, y, z) components
3. Optionally set an **Origin** (start position offset)
4. Choose a **Rendering Style** (Line, Arrow, or Cylinder)
5. Set **Thickness** (1.0–100.0)
6. Set **Length** (0.1–5.0× crystal extent)
7. Choose a **Colour** (auto-assigned by indices)
8. Adjust **Opacity**
9. Click **Add Direction**

---

## Rendering Styles

| Style | Description |
|-------|-------------|
| Line | Flat 2D line. Fastest, always visible. |
| Arrow | 2D arrow with arrowhead at the endpoint. |
| Cylinder | 3D cylinder with a cone arrowhead. Lighting-shaded. |

**Arrow** and **Cylinder** styles make direction clearer in 3D but are slower to render than **Line**.

---

## Direction List

All added directions appear in the direction list. Select a direction to edit its properties, or use:

- **Remove Selected** — delete the selected direction
- **Clear All** — remove all directions

---

## Converting a Direction to a Plane

Select a direction in the list and click **Add as Plane**. This creates a new plane in the [Planes dialog](planes.md) with a normal equal to the selected direction vector.

---

## Appearance Settings

| Setting | Range | Description |
|---------|-------|-------------|
| Thickness | 1.0–100.0 | Line/cylinder pixel width |
| Length | 0.1–5.0× | Length relative to crystal extent |
| Colour | RGB picker | Auto-assigned by indices |
| Opacity | 0–255 | Transparency |

---

## Colour Auto-Assignment

Directions are automatically assigned distinct colours based on their index values, making it easy to visually distinguish multiple directions. Colours can be overridden with the colour picker.
