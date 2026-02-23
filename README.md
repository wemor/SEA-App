# SEA-App (Statistical Energy Analysis)

Welcome to the **SEA-App** repository! 

This repository contains a Python-based implementation of a Statistical Energy Analysis (SEA) framework, designed for high-frequency acoustic and structural vibration energy-flow predictions.

## Documentation & Manuals

A comprehensive user manual has been created that explains the core physics (derived from the original SEA parameters PDF) and shows exactly how these formulas translate into the Python matrix solver.

*   📖 **[SEA-App User Manual](docs/manual.md)**: Includes all theoretical background, equations (critical frequencies, wave speeds, coupling loss factors), and an overview of the Python classes.

## Features

The `sea_app/core` package includes:
*   **Material Definitions**: Built-in physical property calculation (e.g., density, elastic modulus).
*   **Subsystems**: Classes representing structural elements like `HomogeneousPlate` and acoustic volumes like `AcousticCavity`.
*   **Couplings**: Logic for computing Coupling Loss Factors ($\eta_{ij}$) between plates and cavities.
*   **Matrix Solver**: An generalized $N \times N$ matrix solver that strictly balances vibratory energy input against internal dissipation and coupling losses.

## Testing & Examples

To see the system in action and verify the math, check out the provided example scripts:

### 1. The "myExample" Reference (`myExample.py`)
This script demonstrates the exact 3-subsystem arrangement (Room 1 -> Wall 2 -> Room 3) from the original `myExample` MathCAD documents. It proves that the simplified analytical calculation perfectly matches the full `sea_app` matrix solution.
```bash
uv run myExample.py
```

### 2. Basic Example (`example_usage.py`)
A generalized, simpler example showing a 1x1m aluminum plate radiating sound into a 27 m³ receiving room.
```bash
uv run example_usage.py
```

## Setup & Execution

This project uses `uv` for lightning-fast Python dependency management.
Make sure you have `uv` installed.

Run any script by simply prefixing with `uv run`:
```bash
uv run <script_name>.py
```
*(Dependencies like numpy and PyMuPDF will be managed automatically over the virtual environment)*
