"""Dataclasses for crystallographic plane and direction items.

These are the canonical data objects shared between the dialogs and renderers.
Both absolute (world-space) and relative (UI multiplier) sizes are stored so
that items round-trip correctly when cross-converted between planes and directions.
"""

from dataclasses import dataclass
from typing import Literal, Tuple


@dataclass
class PlaneData:
    """A crystallographic plane to be rendered as a semi-transparent quad.

    Attributes:
        normal:        Miller indices (h, k, l) if fractional=True, else
                       Cartesian normal vector (nx, ny, nz).
        origin:        World-space origin of the plane (x, y, z).
        fractional:    True → normal is Miller indices; False → Cartesian.
        size:          Absolute half-extent of the quad in world units.
        size_relative: UI multiplier stored alongside size so the spinbox
                       value survives cross-conversion to a DirectionData.
                       size = size_relative * max_extent at creation time.
        color:         RGB tuple, each component in [0, 1].
        alpha:         Opacity in [0, 1].
    """

    normal: Tuple[float, float, float]
    origin: Tuple[float, float, float]
    fractional: bool
    size: float
    size_relative: float
    color: Tuple[float, float, float]
    alpha: float
    visible: bool = True
    slice_enabled: bool = False
    slice_two_sided: bool = True
    slice_thickness: float = 5.0


@dataclass
class DirectionData:
    """A crystallographic direction to be rendered as a line/arrow/cylinder.

    Attributes:
        vector:          Fractional indices [u, v, w] if fractional=True,
                         else Cartesian direction (dx, dy, dz).
        origin:          World-space start of the direction (x, y, z).
        fractional:      True → vector is fractional; False → Cartesian.
        style:           Rendering style: "line", "arrow", or "cylinder".
        thickness:       Line/cylinder thickness in pixels.
        length:          Absolute length in world units.
        length_relative: UI multiplier stored alongside length so the spinbox
                         value survives cross-conversion to a PlaneData.
                         length = length_relative * max_extent at creation time.
        color:           RGB tuple, each component in [0, 1].
        alpha:           Opacity in [0, 1].
    """

    vector: Tuple[float, float, float]
    origin: Tuple[float, float, float]
    fractional: bool
    style: Literal["line", "arrow", "cylinder"]
    thickness: float
    length: float
    length_relative: float
    color: Tuple[float, float, float]
    alpha: float
