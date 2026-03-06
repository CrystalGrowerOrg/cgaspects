# Visualisation

CGAspects renders crystal structures as interactive 3D point clouds using OpenGL 3.3. This page covers all options that control how the point cloud is displayed.

---

## Rendering Styles

| Style | Description | Best For |
|-------|-------------|----------|
| Points | Fast GL_POINTS rasterization | Very large datasets (millions of points) |
| Spheres | GPU-instanced icospheres per point | Publication figures, small–medium crystals |
| Convex Hull | Solid surface enclosing all points | Morphology overview |
| Mesh | External 3D mesh file (OBJ/STL/PLY/GLB) | Custom geometry |

Switch between styles in the **Visualisation Settings** area.

---

## Coloring Points

Points can be coloured by any numerical column in the XYZ data:

| Colour Mode | Source Column |
|------------|--------------|
| Type | Molecule/atom type identifier |
| Number | Atom number |
| Layer | Growth layer index |
| Site | Site number |
| Energy | Particle energy |
| Single Colour | Fixed colour (no data mapping) |

### Colourmaps

When a numerical column is selected, a colourmap maps values to colours. Available colourmaps:

- Viridis (default)
- Cividis
- Plasma
- Inferno
- Magma
- Cool–Warm
- Grayscale

The colourmap range is set automatically to the min/max of the selected column for the current frame.

---

## Point Size

Adjust point size interactively:
- **Increase**: `Ctrl+=` or **View → Increase Point Size**
- **Decrease**: `Ctrl+-` or **View → Decrease Point Size**

For the **Spheres** style, the point size directly controls the sphere radius.

---

## Site Highlighting

You can highlight specific lattice sites using **View → Highlight Sites** (`Ctrl+Shift+S`). This lets you colour-code individual sites or ranges while showing the rest of the crystal in a background colour.

See [Site Highlighting](site-highlighting.md) for full details.

---

## Background Colour

The background colour of the viewport can be changed from the Visualisation Settings. Black and white are common choices for publication figures.

---

## Export

### Render to Image
**File → Render** (`Ctrl+R`) saves the current viewport as a PNG image. Resolution multiplier options (1×, 2×, 4×) allow high-DPI export.

### Export 3D Mesh
The crystal geometry can be exported as a 3D mesh file:
- **OBJ** — Wavefront OBJ with surface normals
- **STL** — Binary STL for 3D printing
- **PLY** — Stanford PLY format
- **GLB** — glTF binary for web/game engines

### Export Point Cloud
**File → Export XYZ** (`Ctrl+Shift+E`) saves the current point cloud (including any deletions) as an XYZ file.
