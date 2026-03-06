# Interface Overview

The CGAspects main window is divided into five regions:

```
┌─────────────────────────────────────────────────────────────┐
│  Menu Bar: File | View | Crystallography | Help             │
├──────────────┬──────────────────────────────┬───────────────┤
│              │                              │               │
│  Left Panel  │    3D Viewport               │  Right Panel  │
│  (Import &   │    (OpenGL crystal view)     │  (Crystal     │
│   Analysis)  │                              │   Info)       │
│              │                              │               │
├──────────────┴──────────────────────────────┴───────────────┤
│  Movie Controls (frame slider, play/pause, FPS)             │
├─────────────────────────────────────────────────────────────┤
│  Status Bar                                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Menu Bar

Four menus provide access to all application features:

- **File** — Import data, export results, open the plotting dialog
- **View** — Control visualisation appearance, align the camera, toggle panels
- **Crystallography** — Add planes and directions, set lattice parameters
- **Help** — Keyboard shortcuts reference, About dialog

See [Menus & Actions](menus.md) for a complete reference.

---

## Left Panel

The left panel is the main control area for loading data and running analyses.

**Import Controls**
- **Folder path field** — Shows the currently loaded data folder
- **Import XYZ Files** button — Browse for a folder containing XYZ simulation output
- **Import CSV for Plotting** — Load a CSV file directly into the plotting dialog

**Analysis Buttons** (enabled when the relevant data files are present)
- **Calculate Aspect Ratio** — Shape analysis and Zingg classification
- **Calculate Growth Rates** — Time-series growth rate computation
- **Calculate Site Analysis** — Crystallization event and site property analysis

**Results Directory** button — Opens the output folder where analysis results are saved

---

## 3D Viewport

The central viewport shows the crystal as an interactive 3D point cloud. You can:

- **Orbit** the camera (left-click drag)
- **Translate** the crystal (right-click drag)
- **Zoom** (scroll wheel)
- **Select** individual points (Shift+Click)

Crystallographic planes, directions, and coordinate axes are overlaid on the point cloud.

See [3D Viewport](viewport.md) for full details.

---

## Right Panel — Crystal Info

When a crystal is loaded, the right panel shows computed properties for the current frame:

| Property | Description |
|----------|-------------|
| Primary Aspect Ratio | Short / Middle dimension ratio (S:M) |
| Secondary Aspect Ratio | Middle / Long dimension ratio (M:L) |
| Shape | Zingg morphological class (Block, Plate, Lath, Needle) |
| Volume | Convex hull volume |
| Surface Area | Convex hull surface area |
| SA:Vol Ratio | Surface area to volume ratio |

An optional **Point Info Panel** (toggle with **Ctrl+B** or **View → Toggle Point Info Panel**) shows information about the currently hovered or selected point.

---

## Movie Controls

Displayed at the bottom of the window when a multi-frame XYZ trajectory is loaded:

- **Frame slider** — Drag to jump to any frame
- **Frame spinbox** — Type a frame number directly
- **Play / Pause** button — Animate the crystal growth trajectory
- **FPS control** — Set playback speed in frames per second

---

## Status Bar

The status bar at the bottom of the window shows:
- Current operation or status message
- Progress bar during long-running analyses
- Warnings and informational notices
