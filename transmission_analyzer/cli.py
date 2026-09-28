"""Command-line interface for Transmission Analyzer."""

from __future__ import annotations

import argparse
from pathlib import Path

from .analyzer import analyze_transmission, load_comsol_txt, plot_transmission


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""

    parser = argparse.ArgumentParser(
        prog="transmission-analyzer",
        description="Analyze a two-column COMSOL transmission spectrum TXT file.",
    )
    parser.add_argument("input", type=Path, help="Path to COMSOL TXT export.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("transmission_spectrum.png"),
        help="PNG file path for the saved plot.",
    )
    return parser


def main() -> None:
    """Run the Transmission Analyzer command-line workflow."""

    args = build_parser().parse_args()
    wavelengths, transmissions = load_comsol_txt(args.input)
    result = analyze_transmission(wavelengths, transmissions)
    plot_transmission(wavelengths, transmissions, result, args.output)

    print(f"Resonance wavelength: {result.resonance_wavelength_nm:.6g} nm")
    print(f"Minimum transmission: {result.minimum_transmission:.6g}")
    if result.fwhm_nm is None or result.q_factor is None:
        print("FWHM/Q factor: could not be determined from the data range")
    else:
        print(f"FWHM: {result.fwhm_nm:.6g} nm")
        print(f"Q factor: {result.q_factor:.6g}")
    print(f"Plot saved to: {args.output}")


if __name__ == "__main__":
    main()
