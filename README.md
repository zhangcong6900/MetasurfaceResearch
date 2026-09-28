# Transmission Analyzer

Transmission Analyzer is a small Python command-line program for analyzing TXT files exported from COMSOL. It expects two numeric columns:

1. Wavelength in nanometers (`nm`)
2. Transmission

The program plots the transmission spectrum, finds the resonance wavelength as the minimum transmission point, estimates the full width at half maximum (FWHM) for a transmission dip when possible, calculates the Q factor, and saves the plot as a PNG image.

## Installation

Create and activate a virtual environment, then install the project:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Input file format

Use a whitespace-delimited two-column TXT file. COMSOL header/comment lines that begin with `%` or `#` are ignored.

Example:

```text
% wavelength_nm transmission
1500 0.91
1510 0.72
1520 0.35
1530 0.71
1540 0.90
```

## Usage

Run the analyzer with an input TXT file and choose an output PNG path:

```bash
transmission-analyzer path/to/comsol_export.txt --output spectrum.png
```

You can also run it as a Python module:

```bash
python -m transmission_analyzer.cli path/to/comsol_export.txt -o spectrum.png
```

The terminal output includes:

- Resonance wavelength in nm
- Minimum transmission
- FWHM in nm, if the half-depth crossings are inside the sampled wavelength range
- Q factor, calculated as `resonance wavelength / FWHM` when FWHM is available
- Path to the saved PNG plot

## Notes on Q factor

For a transmission dip, Transmission Analyzer estimates the FWHM level halfway between the minimum transmission and a baseline estimated from the larger of the two edge transmissions. If the data does not cross that half-depth level on both sides of the resonance, FWHM and Q factor are reported as unavailable.
