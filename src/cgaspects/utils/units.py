"""Unit conversion utilities for cgaspects plots.

Supported conversions
---------------------
Length  : Å  ↔  pm / nm / µm / mm / cm / m
Energy  : kcal/mol  ↔  kJ/mol / eV
Special : kcal/mol  ↔  σ  (non-linear, uses chemical-potential relation)

All conversions are bidirectional — reverse conversions are registered automatically.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable, Literal

import numpy as np

logger = logging.getLogger("CA:units")

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------
R: float = 8.314       # J / (mol·K)
T: float = 298.15      # K
J_to_kcal: float = 1 / 4184  # J → kcal conversion factor


# ---------------------------------------------------------------------------
# Raw thermodynamic conversion functions
# ---------------------------------------------------------------------------

def supersaturation_to_dmu(
    S: np.ndarray,
    R: float = R,
    T: float = T,
    unit: Literal["kcal", "kJ", "J"] = "kJ",
) -> np.ndarray:
    """Convert supersaturation *S* to chemical potential difference Δμ."""
    dmu_joule = R * T * np.log(S)
    if unit == "J":
        return dmu_joule
    if unit == "kJ":
        return dmu_joule / 1000
    # kcal
    return dmu_joule * J_to_kcal


def dmu_to_supersaturation(
    dmu: np.ndarray,
    R: float = R,
    T: float = T,
    unit: Literal["kcal", "kJ", "J"] = "kJ",
) -> np.ndarray:
    """Convert chemical potential difference Δμ to supersaturation *S*."""
    if unit == "J":
        dmu_joule = dmu
    elif unit == "kJ":
        dmu_joule = dmu * 1000
    elif unit == "kcal":
        dmu_joule = dmu / J_to_kcal
    else:
        raise ValueError(
            "Units for dmu should be 'J', 'kJ', or 'kcal'."
        )
    return np.exp(dmu_joule / (R * T))


# ---------------------------------------------------------------------------
# UnitConversion dataclass
# ---------------------------------------------------------------------------

# Internal registry: (from_unit, to_unit) → UnitConversion
_REGISTRY: dict[tuple[str, str], "UnitConversion"] = {}


@dataclass
class UnitConversion:
    """Encapsulates a conversion between two units.

    Use :meth:`get` to look up a registered conversion and :meth:`available_for`
    to list all conversions from a given unit.

    Example
    -------
    >>> conv = UnitConversion.get("kcal/mol", "kJ/mol")
    >>> conv.apply(np.array([1.0]))
    array([4.184])
    """

    from_unit: str
    to_unit: str
    _fn: Callable[[np.ndarray], np.ndarray] = field(repr=False, compare=False)

    def apply(self, values: np.ndarray) -> np.ndarray:
        """Apply the conversion to *values* and return the result."""
        return self._fn(np.asarray(values, dtype=float))

    def __str__(self) -> str:
        return f"{self.from_unit} → {self.to_unit}"

    def __repr__(self) -> str:
        return f"UnitConversion(from_unit={self.from_unit!r}, to_unit={self.to_unit!r})"

    # ------------------------------------------------------------------
    # Registry helpers
    # ------------------------------------------------------------------

    @classmethod
    def get(cls, from_unit: str, to_unit: str) -> "UnitConversion":
        """Return the registered conversion for the given unit pair.

        Raises
        ------
        KeyError
            If no conversion is registered for *(from_unit, to_unit)*.
        """
        key = (from_unit, to_unit)
        if key not in _REGISTRY:
            raise KeyError(
                f"No conversion registered for {from_unit!r} → {to_unit!r}. "
                f"Available: {[str(c) for c in _REGISTRY.values()]}"
            )
        return _REGISTRY[key]

    @classmethod
    def available_for(cls, unit: str) -> list["UnitConversion"]:
        """Return all registered conversions whose *from_unit* matches *unit*."""
        return [c for (f, _), c in _REGISTRY.items() if f == unit]

    @classmethod
    def known_units(cls) -> list[str]:
        """Return a sorted list of all units that appear in the registry."""
        units: set[str] = set()
        for from_u, to_u in _REGISTRY:
            units.add(from_u)
            units.add(to_u)
        return sorted(units)


# ---------------------------------------------------------------------------
# Registration helpers
# ---------------------------------------------------------------------------

def _register(
    from_unit: str,
    to_unit: str,
    fn: Callable[[np.ndarray], np.ndarray],
    reverse_fn: Callable[[np.ndarray], np.ndarray] | None = None,
    *,
    factor: float | None = None,
) -> None:
    """Register a forward conversion and optionally its reverse.

    Parameters
    ----------
    from_unit, to_unit:
        Unit strings.
    fn:
        Forward conversion function ``fn(values) -> values``.
    reverse_fn:
        Explicit reverse function.  If *None* and *factor* is given the
        reverse is derived as ``lambda x: x / factor``.  If neither is
        given, no reverse is registered.
    factor:
        Linear scale factor used to auto-derive the reverse when
        *reverse_fn* is not provided.
    """
    _REGISTRY[(from_unit, to_unit)] = UnitConversion(from_unit, to_unit, fn)

    if reverse_fn is not None:
        _REGISTRY[(to_unit, from_unit)] = UnitConversion(to_unit, from_unit, reverse_fn)
    elif factor is not None:
        _f = factor  # capture for closure
        _REGISTRY[(to_unit, from_unit)] = UnitConversion(
            to_unit, from_unit, lambda x, f=_f: x / f
        )


# ---------------------------------------------------------------------------
# Build the registry
# ---------------------------------------------------------------------------

# --- Length: Angstrom ↔ other metric lengths ---
_ANGSTROM_FACTORS: dict[str, float] = {
    "pm": 100.0,
    "nm": 0.1,
    "µm": 1e-4,
    "mm": 1e-7,
    "cm": 1e-8,
    "m":  1e-10,
}
for _to_unit, _factor in _ANGSTROM_FACTORS.items():
    _f = _factor  # capture
    _register("Å", _to_unit, lambda x, f=_f: x * f, factor=_f)

# --- Energy: kcal/mol → kJ/mol ---
_register(
    "kcal/mol", "kJ/mol",
    fn=lambda x: x * 4.184,
    factor=4.184,
)

# --- Energy: kcal/mol → eV ---
_EV_FACTOR = 4.184 / 96.485  # ≈ 0.04336 eV per kcal/mol
_register(
    "kcal/mol", "eV",
    fn=lambda x: x * _EV_FACTOR,
    factor=_EV_FACTOR,
)

# --- Special: kcal/mol ↔ σ (non-linear) ---
_register(
    "kcal/mol", "σ",
    fn=lambda x: dmu_to_supersaturation(x, unit="kcal"),
    reverse_fn=lambda x: supersaturation_to_dmu(x, unit="kcal"),
)
