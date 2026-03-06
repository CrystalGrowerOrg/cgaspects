# Planes & Slicing Tutorial

This tutorial shows how to add crystallographic planes to the 3D viewport and use them to reveal interior cross-sections of a crystal.

---

## Prerequisites

- CGAspects is open with an XYZ crystal loaded
- Lattice parameters are set (if using Miller indices)

---

## Part 1 — Adding a Plane by Miller Indices

1. Open **Crystallography → Set Lattice Parameters** and enter your unit cell parameters if not already set
2. Open **Crystallography → Add Planes** (`Ctrl+Shift+L`)
3. In the dialog, select the **Miller** coordinate mode (top selector)
4. Enter h=1, k=0, l=0 in the index fields
5. Set **Size** to 1.5× for a plane slightly larger than the crystal
6. Leave **Opacity** at 180 (semi-transparent)
7. Click **Add Plane**

The (100) plane appears in the viewport as a semi-transparent coloured quad.

!!! tip
    Use the **Reduce** button to simplify indices. For example, entering `2 0 0` and clicking Reduce gives `1 0 0`.

---

## Part 2 — Finding a Plane from Selected Points

You can fit a plane to three or more points that you Shift+Click in the viewport:

1. In the Planes dialog, click **Find Plane**
2. The dialog closes temporarily. `Shift+Click` on 3 or more points in the viewport that you know lie on the same crystallographic plane
3. A small toolbar appears — click **Confirm**
4. The fitted plane is added to the plane list

This is useful for identifying unknown planes or verifying that features lie on the expected crystallographic face.

---

## Part 3 — Slicing the Crystal

Now enable slicing to reveal an interior cross-section:

1. In the Planes dialog, select the (100) plane you added in Part 1
2. In the **Slicing** section at the bottom, check **Enable slice**
3. Make sure **Two-sided slab** is checked
4. Set **Thickness** to 10 (Å or whatever unit your crystal uses)

The point cloud clips to a slab 10 units wide around the (100) plane, revealing the crystal interior.

---

## Part 4 — Moving the Slice Through the Crystal

1. With the (100) plane selected, click **Move Along Normal…**
2. A slider dialog opens
3. Drag the slider left and right — the plane (and its slice) moves through the crystal in real time
4. Pause at any cross-section that reveals interesting interior structure

---

## Part 5 — Half-Space Mode

To show only one side of the crystal (instead of a slab):

1. Select the plane in the list
2. Uncheck **Two-sided slab**
3. Increase **Thickness** to a large value (e.g., 1000) to see everything on one side

The crystal is now clipped at the plane, showing only the positive-normal half.

---

## Part 6 — Hiding the Plane Quad

If the plane polygon obscures the view of the slice:

1. Select the plane in the list
2. Click **Hide Plane**

The coloured quad disappears, but the slice remains active. Click **Show Plane** to restore it.

---

## Part 7 — Multiple Simultaneous Slices

Add a second plane perpendicular to the first:

1. In the Planes dialog, add a new plane with h=0, k=1, l=0 (the (010) plane)
2. Enable slice on this plane too
3. Set Thickness to 10

Now only points that are within 10 units of both planes are shown — a box-shaped cross-section at the intersection.

---

## Summary

| Action | Result |
|--------|--------|
| Add plane (Miller) | Semi-transparent quad at that crystallographic face |
| Enable slice | Clips point cloud to plane region |
| Two-sided slab | Shows ±thickness/2 around the plane |
| Half-space | Shows only one side of the plane |
| Move Along Normal | Sweep the slice through the crystal |
| Hide Plane | Invisible plane, active slice |
| Multiple slices | All slices applied simultaneously (AND logic) |
