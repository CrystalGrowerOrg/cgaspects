# Panels

## Left Panel

The left panel is always visible and provides the primary data import and analysis controls.

### Batch Folder Import

The folder path field and **Import XYZ Files** button at the top of the left panel let you select a folder containing XYZ simulation output files. CGAspects scans the folder for:

- XYZ crystal shape files
- Size files (`size.csv`)
- Simulation parameters file
- Crystallization event files
- Site population and occupation files
- Structure file (lattice parameters)

Once loaded, the available analysis buttons become active based on which files were found.

### Analysis Buttons

| Button | Enabled When | Opens |
|--------|-------------|-------|
| Calculate Aspect Ratio | XYZ files present | [Aspect Ratio dialog](../analysis/aspect-ratios.md) |
| Calculate Growth Rates | Size files present | [Growth Rates dialog](../analysis/growth-rates.md) |
| Calculate Site Analysis | Crystallization event files present | [Site Analysis dialog](../analysis/site-analysis.md) |

### Results Directory

The **Results Directory** button opens the output folder (`aspects_output/` inside the data folder) in the system file manager. All CSV exports, plots, and rendered images are saved here.

---

## Right Panel — Crystal Info

The right panel displays computed properties for the currently displayed crystal frame.

| Field | Value |
|-------|-------|
| Primary Aspect Ratio | S:M (short-to-middle dimension ratio, 0–1) |
| Secondary Aspect Ratio | M:L (middle-to-long dimension ratio, 0–1) |
| Shape | Zingg class: Block, Plate, Lath, or Needle |
| Volume | Convex hull volume in Å³ |
| Surface Area | Convex hull surface area in Å² |
| SA:Vol Ratio | Surface area to volume ratio in Å⁻¹ |

Values update automatically when you move between frames in a trajectory.

See [Zingg Classification](../science/zingg-classification.md) and [Shape Metrics](../science/shape-metrics.md) for the science behind these values.

---

## Point Info Panel

Toggle with **View → Toggle Point Info Panel** or `Ctrl+B`.

When visible, this panel appears as a sidebar and shows:

- **Hovered point data** — all column values for the point under the cursor
- **Selected point count** — number of currently selected points
- **Delete selected** button — remove selected points from the visualisation
- **Export selected** button — save selected points to a new XYZ file

---

## Movie Controls

The movie controls are shown at the bottom of the window when a multi-frame XYZ trajectory is loaded (i.e., a folder containing multiple XYZ files representing time steps).

| Control | Description |
|---------|-------------|
| Frame slider | Drag to navigate to any frame |
| Frame spinbox | Type a frame number directly |
| Play / Pause | Animate the crystal growth trajectory |
| FPS spinbox | Set playback speed (frames per second) |

The current frame number is shown next to the slider. The Crystal Info panel updates to show properties for the displayed frame.

---

## Status Bar

The status bar at the bottom of the window provides feedback on the current state:

- **Status messages** — Describe what the application is doing (loading, computing, ready)
- **Progress bar** — Shown during long-running operations (analysis, file loading)
- **Warnings** — Shown in yellow when data is missing or parameters are invalid
