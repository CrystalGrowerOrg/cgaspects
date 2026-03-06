# 3D Viewport

The central 3D viewport renders the crystal as an interactive OpenGL scene. It supports millions of points and multiple crystallographic overlays.

---

## Camera Controls

| Input | Action |
|-------|--------|
| Left-click + drag | Orbit camera around the crystal |
| Right-click + drag | Translate the crystal (camera axes stay fixed) |
| Scroll wheel | Zoom in / out |
| `R` | Reset camera to default position |
| `Shift+S` | Store current camera orientation |
| `X` / `Y` / `Z` | Align view along X / Y / Z axis |
| `1` / `2` / `3` | Lock rotation to X / Y / Z axis only |

### Projection Mode

Toggle between **perspective** (foreshortening) and **orthographic** (no foreshortening) projection with `Ctrl+Shift+P` or **View → Switch Projection**.

Orthographic is often preferred for crystallographic alignment since it preserves parallel lines and true relative sizes.

---

## Point Selection

**Shift+Click** on any point to select it. The [Point Info Panel](panels.md#point-info-panel) shows the selected point's data.

Multiple points can be selected with repeated Shift+Click. Selected points are highlighted in cyan.

### Actions on Selected Points

From the Point Info Panel:
- **Delete selected** — remove from the visualisation (does not modify the source file)
- **Export selected** — save selected points to a new XYZ file

---

## Rendering Styles

The rendering style controls how each point is drawn:

| Style | Description |
|-------|-------------|
| Points | Fast GL_POINTS rasterization. Best for very large datasets. |
| Spheres | GPU-instanced icosphere per point. Realistic but slower. |
| Convex Hull | Renders the outer boundary surface of the crystal. |
| Mesh | Loads and renders a 3D mesh (OBJ/STL/PLY/GLB). |

---

## Coloring

Points can be coloured by any column in the XYZ data:

| Colour Mode | Description |
|------------|-------------|
| Type | Colour by atom/molecule type |
| Number | Colour by atom number |
| Layer | Colour by growth layer |
| Site | Colour by site number |
| Energy | Colour by particle energy |
| Single Colour | Uniform colour for all points |

A **colourmap** is applied to numerical columns. Available colourmaps include Viridis, Cividis, Plasma, Inferno, and others. The colourmap and colour column are set in the visualisation settings.

---

## Overlays

The following elements are rendered over the point cloud:

- **Crystallographic planes** — semi-transparent quads (from the [Planes dialog](../features/planes.md))
- **Crystallographic directions** — lines, arrows, or cylinders (from the [Directions dialog](../features/directions.md))
- **Coordinate axes** — Cartesian (X/Y/Z) or fractional (a/b/c) (from [Axes Settings](../features/axes.md))

---

## Render / Export

**File → Render** (`Ctrl+R`) saves the current viewport as an image. Available options:

- Format: PNG
- Resolution multiplier: 1×, 2×, 4×

The 3D geometry can also be exported as a mesh:
- **OBJ** (with normals)
- **STL** (binary)
- **PLY**
- **GLB** (glTF binary)

---

## Point Size

Adjust the displayed point size using:
- **View → Increase Point Size** (`Ctrl+=`)
- **View → Decrease Point Size** (`Ctrl+-`)

This only affects the GL_POINTS or sphere radius and does not modify underlying data.
