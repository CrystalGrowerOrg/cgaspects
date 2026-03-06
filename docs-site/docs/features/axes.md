# Axes Settings

Open the Axes Settings dialog with **View → Axes Settings** (`Ctrl+Shift+A`).

The coordinate axes are displayed as an overlay in the 3D viewport showing the current orientation of the coordinate system.

---

## Cartesian vs Fractional Axes

Toggle between coordinate systems with **Crystallography → Switch to Fractional Axes** (`Shift+A`):

| Mode | Axes Shown | Labels |
|------|-----------|--------|
| Cartesian | X, Y, Z | x, y, z (or custom) |
| Fractional | a, b, c | a, b, c (or custom) |

Fractional mode requires [lattice parameters](lattice-parameters.md) to be set so the a/b/c vectors can be computed.

---

## Rendering Style

| Style | Description |
|-------|-------------|
| Line | Simple flat lines |
| Arrow | Lines with 2D arrowheads |
| Cylinder | 3D cylinders with cone tips |

Default colours are: X/a = red, Y/b = green, Z/c = blue.

---

## Settings

| Setting | Range | Description |
|---------|-------|-------------|
| Thickness | 1.0–10.0 | Line or cylinder pixel width |
| Length Multiplier | 0.1–10.0× | Scale the axis length |
| Show Labels | On/Off | Display axis name labels |
| Label Colour | RGB | Custom label colour, or match axis colour |
| Origin X/Y/Z | −10.0–10.0 | Reposition the axes origin in world space |

### Live Preview

Click **Apply** in the dialog to preview changes without closing. Changes take effect immediately in the viewport.

---

## Axis Alignment

Use these keyboard shortcuts to instantly align the camera view along an axis:

| Key | View Direction |
|-----|---------------|
| `X` | Along the X (or a) axis |
| `Y` | Along the Y (or b) axis |
| `Z` | Along the Z (or c) axis |

These shortcuts work whether axes are shown or hidden.
