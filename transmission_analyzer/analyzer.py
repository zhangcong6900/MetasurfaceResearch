"""Utilities for analyzing two-column COMSOL transmission spectra."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class AnalysisResult:
    """Summary values computed from a transmission spectrum."""

    resonance_wavelength_nm: float
    minimum_transmission: float
    fwhm_nm: float | None
    q_factor: float | None


def load_comsol_txt(path: str | Path) -> tuple[list[float], list[float]]:
    """Load wavelength and transmission columns from a COMSOL TXT export.

    COMSOL TXT exports commonly include header lines beginning with ``%``.
    This parser also ignores ``#`` comments, accepts whitespace or comma
    separators, and reads the first two numeric columns from each data row.
    """

    rows: list[tuple[float, float]] = []
    with Path(path).open("r", encoding="utf-8") as input_file:
        for line_number, raw_line in enumerate(input_file, start=1):
            line = raw_line.strip()
            if not line or line.startswith(("%", "#")):
                continue

            parts = line.replace(",", " ").split()
            if len(parts) < 2:
                continue

            try:
                rows.append((float(parts[0]), float(parts[1])))
            except ValueError as exc:
                raise ValueError(
                    f"Line {line_number} does not start with two numeric columns."
                ) from exc

    if len(rows) < 3:
        raise ValueError("At least three valid data points are required.")

    rows.sort(key=lambda row: row[0])
    wavelengths = [row[0] for row in rows]
    transmissions = [row[1] for row in rows]
    return wavelengths, transmissions


def analyze_transmission(
    wavelength_nm: Iterable[float], transmission: Iterable[float]
) -> AnalysisResult:
    """Find resonance wavelength and estimate FWHM/Q for a transmission dip.

    The resonance is defined as the wavelength where transmission is minimum.
    For a dip, the FWHM level is halfway between the minimum transmission and a
    baseline estimated from the larger of the two edge transmissions. The FWHM
    is measured between interpolated left and right crossings of that level.
    """

    pairs = sorted(zip(wavelength_nm, transmission), key=lambda pair: pair[0])
    if len(pairs) < 3:
        raise ValueError("At least three data points are required for analysis.")

    wavelengths = [float(pair[0]) for pair in pairs]
    transmissions = [float(pair[1]) for pair in pairs]

    resonance_index = min(range(len(transmissions)), key=transmissions.__getitem__)
    resonance_wavelength = wavelengths[resonance_index]
    minimum_transmission = transmissions[resonance_index]

    fwhm = _calculate_dip_fwhm(wavelengths, transmissions, resonance_index)
    q_factor = resonance_wavelength / fwhm if fwhm and fwhm > 0 else None

    return AnalysisResult(
        resonance_wavelength_nm=resonance_wavelength,
        minimum_transmission=minimum_transmission,
        fwhm_nm=fwhm,
        q_factor=q_factor,
    )


def _calculate_dip_fwhm(
    wavelengths: list[float], transmissions: list[float], resonance_index: int
) -> float | None:
    """Return the full width at half minimum for a resonance dip, if possible."""

    baseline = max(transmissions[0], transmissions[-1])
    minimum = transmissions[resonance_index]

    if baseline <= minimum:
        return None

    half_level = minimum + (baseline - minimum) / 2.0
    left = _find_crossing(wavelengths, transmissions, resonance_index, half_level, -1)
    right = _find_crossing(wavelengths, transmissions, resonance_index, half_level, 1)

    if left is None or right is None or right <= left:
        return None
    return right - left


def _find_crossing(
    wavelengths: list[float],
    transmissions: list[float],
    start: int,
    level: float,
    direction: int,
) -> float | None:
    """Find an interpolated crossing of ``level`` moving away from ``start``."""

    index = start
    next_index = index + direction

    while 0 <= next_index < len(transmissions):
        y1 = transmissions[index]
        y2 = transmissions[next_index]
        if (y1 - level) * (y2 - level) <= 0 and y1 != y2:
            x1 = wavelengths[index]
            x2 = wavelengths[next_index]
            fraction = (level - y1) / (y2 - y1)
            return x1 + fraction * (x2 - x1)
        index = next_index
        next_index = index + direction

    return None


def plot_transmission(
    wavelength_nm: Iterable[float],
    transmission: Iterable[float],
    result: AnalysisResult,
    output_path: str | Path,
) -> None:
    """Save a PNG plot of the transmission spectrum and resonance marker."""

    import matplotlib.pyplot as plt

    wavelengths = list(wavelength_nm)
    transmissions = list(transmission)

    plt.figure(figsize=(8, 5))
    plt.plot(wavelengths, transmissions, label="Transmission", linewidth=2)
    plt.axvline(
        result.resonance_wavelength_nm,
        color="crimson",
        linestyle="--",
        label=f"Resonance: {result.resonance_wavelength_nm:.3f} nm",
    )
    plt.scatter(
        [result.resonance_wavelength_nm],
        [result.minimum_transmission],
        color="crimson",
        zorder=3,
    )

    title = "Transmission Spectrum"
    if result.q_factor is not None:
        title += f" (Q = {result.q_factor:.2f})"

    plt.title(title)
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Transmission")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
