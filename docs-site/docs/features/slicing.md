# Slicing

Plane slicing clips the displayed point cloud to reveal an interior cross-section. Any plane added in the [Planes dialog](planes.md) can be used as a slice.

---

## Enabling a Slice

1. Open **Crystallography → Add Planes** (`Ctrl+Shift+L`)
2. Select a plane in the plane list
3. In the **Slicing** section at the bottom of the dialog, check **Enable slice**

The point cloud immediately clips to one side of the plane. Multiple planes can have slicing enabled simultaneously; points must be inside all active slices.

---

## Slab vs Half-Space

| Mode | Behaviour |
|------|---------|
| **Two-sided slab** (default) | Show only points within ±thickness/2 of the plane. Reveals a slab cross-section. |
| **Half-space** | Show only points on one side of the plane (0 to +thickness from the plane). |

Toggle **Two-sided slab** in the Slicing section to switch modes.

---

## Thickness

The **Thickness** spinbox (0.1–10000 units) controls how much of the crystal is visible around the plane:

- In **two-sided slab** mode: points within ±thickness/2 of the plane are shown
- In **half-space** mode: points from 0 to +thickness from the plane are shown

Larger values show more of the crystal; smaller values reveal thinner cross-sections.

---

## Moving the Plane Along Its Normal

Click **Move Along Normal…** to open a slider dialog. Drag the slider to translate the plane along its normal direction, sweeping the slice through the crystal in real time.

The slider range is set automatically to cover the crystal's extent along the normal direction.

---

## Hiding the Plane Polygon While Slicing

You can hide the plane's visible quad while keeping its slice active:

- Click **Hide Plane** in the Slicing section (or the plane list context menu)
- The plane quad is no longer rendered, but the slice remains in effect

Click **Show Plane** to make it visible again.

This is useful when you want to see the slice cross-section without the plane quad obscuring the view.

---

## Multiple Simultaneous Slices

All planes with **Enable slice** checked are applied at the same time. Points are only visible if they pass through all active slice regions (AND logic). This lets you create box-shaped or slab-intersection cross-sections with two or more planes.

---

## Example: Revealing a (010) Cross-Section

1. Set lattice parameters (**Crystallography → Set Lattice Parameters**)
2. Add a plane with h=0, k=1, l=0
3. Enable slice on that plane
4. Set two-sided slab, thickness ≈ 5 Å
5. Use **Move Along Normal…** to position the slab through the crystal interior
