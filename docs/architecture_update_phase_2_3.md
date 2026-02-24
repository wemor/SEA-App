# Architecture Update: Phase 2 & Phase 3 (Dynamic Elements & Calculation Core)

## Overview
This document summarizes the architectural shift in the SEA-App from a hardcoded, static room layout to a completely dynamic modeling environment where users can create, configure, and connect acoustic elements modularly.

## 1. Data Structure Transition
Previously, the app relied on flat, hardcoded variables (`V1`, `S2`, `m_2`, `T60_3`) distributed across `app.py`.
This has been replaced by two primary state arrays in `st.session_state`:
- **`elements`**: A generic list of object dictionaries. Each dictionary stores an element's `id`, `type`, `name`, and component-specific acoustic properties (e.g., `volume`, `surface`, `density`).
- **`junctions`**: A list of connection dictionaries tracking which `id` connects to which `id`.

## 2. Dynamic UI
- **Project Tree**: The left sidebar tree is now iteratively generated from `st.session_state.elements`.
- **Property Editor**: The input property window dynamically checks the `type` of the selected element (e.g., `Cavity` vs. `Wall`) and renders the appropriate Streamlit `number_input` widgets. Changes are instantly serialized back into the dictionary.
- **Graphic Visualization**: The Graphviz pipeline loops through `elements` to draw nodes and loops through `junctions` to draw edges, giving users immediate visual feedback on their acoustic network.

## 3. SEASystem Calculation Engine Rewrite
The mathematical matrix solver was completely refactored.
- **Node Initialization**: Loop through all user-created elements. `SEASystem` internal loss factors ($\eta_i$) are calculated mathematically per-item (e.g., for Cavities $\eta = \frac{2.2}{T_{60} \cdot f}$).
- **Power Injection**: Any Cavity with $P > 0$ automatically registers as an excitation source.
- **Dynamic Array Construction**: The `junctions` array is traversed. The code checks the `type` of the source and receiver (e.g., `Cavity -> Wall`) and runs the appropriate physical formulas to determine the Coupling Loss Factor ($\eta_{ij}$).
- **Loop Restrictions**: Explicit direct transmission (e.g., `Wall -> Wall`) is intentionally blocked in the UI logic as a restriction per design requirements.

## 4. Save/Load Serialization
The JSON file format was upgraded to save the entire nested arrays of `elements` and `junctions`. Older legacy JSON files (`room_1`, `wall_2` schema) will still attempt to populate global fallbacks, but new schemas use the `elements` array.

## Outstanding Items
- Structure-borne transmission (`Plate`, `Beam`) elements are currently disabled in the UI. When implemented, the `eta_ij` matrix logic handling `Plate->Plate` scenarios will need to be written.
