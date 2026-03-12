"""Structured axis label for cgaspects plots.

A :class:`PlotAxisLabel` holds a human-readable *name* and an optional *unit*
string.  It knows how to derive sensible defaults from raw DataFrame column
names, and it carries optional state for user customisation and active unit
conversion.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cgaspects.utils.units import UnitConversion

logger = logging.getLogger("CA:PlotAxisLabel")


def format_label(label: str) -> str:
    """Convert a column name to title case, replacing underscores with spaces.

    Examples
    --------
    >>> format_label("surface_area")
    'Surface Area'
    """
    if not label:
        return label
    return label.replace("_", " ").title()


@dataclass
class PlotAxisLabel:
    """A structured plot-axis label composed of a *name* and optional *unit*.

    Parameters
    ----------
    name:
        Human-readable label text (may contain LaTeX, e.g. ``r"$\\Delta G$"``).
    unit:
        Unit string, e.g. ``"kcal/mol"`` or ``"nm"``.  Empty string means
        no unit.
    is_user_set:
        When *True*, ``_set_labels()`` in :class:`PlottingDialog` skips
        overwriting this label so that user customisations survive replots.
    conversion:
        Active :class:`~cgaspects.utils.units.UnitConversion` that is applied
        to the corresponding data array each time a plot is triggered.

    Examples
    --------
    >>> label = PlotAxisLabel.from_column("starting_delmu_0")
    >>> str(label)
    '$\\Delta\\mu$ (kcal/mol)'
    >>> label = PlotAxisLabel("Energy", "kJ/mol")
    >>> repr(label)
    "PlotAxisLabel(name='Energy', unit='kJ/mol')"
    """

    name: str = ""
    unit: str = ""
    is_user_set: bool = field(default=False, repr=False, compare=False)
    conversion: "UnitConversion | None" = field(default=None, repr=False, compare=False)

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_column(cls, col: str) -> "PlotAxisLabel":
        """Return a :class:`PlotAxisLabel` derived from a DataFrame column name.

        Maps well-known column name patterns to structured labels with units.
        Falls back to simple title-casing for unrecognised names.
        """
        if not col or col == "None":
            return cls()

        if col == "Supersaturation" or col.startswith("starting_delmu"):
            return cls(r"$\Delta\mu$", "kcal/mol")

        if col.startswith("temperature"):
            return cls("Temperature", "°C")

        if col.startswith(("interaction", "Int_", "int_", "excess", "tile")):
            return cls(r"$\Delta G_{Cryst}$", "kcal/mol")

        if "energy" in col.lower():
            return cls(r"$\Delta G$", "kcal/mol")

        return cls(format_label(col), "")

    @classmethod
    def from_string(cls, s: str) -> "PlotAxisLabel":
        """Parse a label string of the form ``"Name (unit)"`` into its parts.

        If the string does not contain parentheses the entire string is treated
        as the name with an empty unit.
        """
        if s and "(" in s and s.endswith(")"):
            name, _, rest = s.rpartition("(")
            return cls(name.strip(), rest.rstrip(")").strip())
        return cls(s.strip(), "")

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        if self.unit:
            return f"{self.name} ({self.unit})"
        return self.name

    def __repr__(self) -> str:
        return f"PlotAxisLabel(name={self.name!r}, unit={self.unit!r})"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def is_empty(self) -> bool:
        """Return *True* if both *name* and *unit* are blank."""
        return not self.name and not self.unit
