# SEA App - UI Architecture

This document describes the design and implementation of the graphical User Interface (GUI) for the Statistical Energy Analysis (SEA) application.

## 1. Technology Stack
*   **Framework**: [Streamlit](https://streamlit.io/)
*   **Graphing**: [Graphviz](https://graphviz.org/)
*   **Execution**: Deployed via `uv` package manager

## 2. Layout Strategy

The interface was designed with an "Engineering-First" mindset, prioritizing screen real-estate for the visualization of the complex models while keeping all data inputs neatly organized and accessible.

### 2.1 The Sidebar (Control & Results Center)
The left-hand sidebar acts as the main control center. It uses an expandable "Tree View" structure (`st.expander`) to prevent visual clutter:

*   **Global Environment**: Contains $f$ (Hz), $\rho_0$, and $c_0$.
*   **Subsystem Inputs**: Organized by component (e.g., Room 1, Wall 2, Room 3). Opening an expander reveals neatly categorized geometric and acoustic/structural properties.
*   **Calculation Results**: Appended at the bottom of the sidebar. When the user tweaks an input above, the application re-runs top-down instantly, and the resulting physical levels ($E_i$, $L_{pi}$, $L_{vi}$) update immediately within their respective bordered containers.

### 2.2 The Main View (Visualization)
The central working area is deliberately kept clean and is 100% dedicated to displaying the **System Architecture**.
*   Using `graphviz.Digraph(rankdir='LR')`, a dynamic block diagram is rendered.
*   **Nodes** represent the active subsystems and display their calculated primary response (e.g., $L_{p1} = 69.6 \text{ dB}$).
*   **Edges** represent the power flow paths between subsystems, labeled dynamically with their calculated Coupling Loss Factors ($\eta_{ij}$).

## 3. Data Integration (`sea_app.core`)

The user interface `app.py` acts purely as a presentation layer. It remains decoupled from the heavy mathematics. 

**Workflow:**
1.  **Input Gathering**: Streamlit captures user parameters from the sidebar widgets.
2.  **Pre-processing**: The script calculates intermediate properties (like mass $M_2$, or modal overlap $\eta_{ij}$) using standard acoustic equations based on those inputs.
3.  **Core Instantiation**: The `SEASystem` object from `sea_app.core.system` is instantiated.
4.  **Model Building**: Subsystems and coupling factors are added to the `SEASystem`. Input power is applied.
5.  **Solving**: `sea.solve(freq)` executes the power balance matrix inversion using `numpy`.
6.  **Post-processing**: Kinetic energies ($E_i$, Joules) are converted back into engineering units like Sound Pressure Level ($L_p$, dB) or Velocity Level ($L_v$, dB) and rendered back into the UI.

## 4. Running the App

To ensure all UI dependencies are present without permanently altering the system Python environment, the app is launched via:

```bash
uv run --with graphviz --with streamlit streamlit run app.py
```
