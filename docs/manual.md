# SEA-App User Manual

## 1. Theoretical Background

Statistical Energy Analysis (SEA) is a vibratory energy-flow technique which provides prediction procedures that are suitable for high frequencies. The system is divided into a set of coupled subsystems, each representing a group of resonant modes. Parameters such as coupling loss factors and modal densities represent ensemble average quantities.

### 1.1 Assumptions and Validity
SEA makes several key assumptions regarding the modeled system:
*   The primary response is resonant.
*   The subsystems have high Modal Overlap ($M > 1$), implying sufficient damping or high modal density.
*   Subsystem modes in each band are assumed to be uncoupled or have equal energies.
*   Traditionally assumes steady-state, incoherent broadband random excitation.

### 1.2 Power Flow Equations

#### Basic Power Flow (Two Subsystems)
For a system consisting of two connected subsystems, power flows in both directions. The total energy $E_i$ in subsystem $i$ is calculated using the power balance matrix equation:

$$
\omega
\begin{bmatrix}
\eta_1 + \eta_{12} & -\eta_{21} \\
-\eta_{12} & \eta_2 + \eta_{21}
\end{bmatrix}
\begin{bmatrix}
E_1 \\
E_2
\end{bmatrix}
=
\begin{bmatrix}
\Pi_{in,1} \\
\Pi_{in,2}
\end{bmatrix}
$$

**Where:**
*   $\omega$ = Band center angular frequency ($\text{rad/sec}$)
*   $\eta_i$ = Internal dissipation loss factor of subsystem $i$
*   $\eta_{ij}$ = Coupling loss factor from subsystem $i$ to $j$
*   $E_i$ = Total kinetic energy in subsystem $i$ ($\text{Joules}$)
*   $\Pi_{in,i}$ = Input power to subsystem $i$ ($\text{Watts}$)

```mermaid
block-beta
  columns 3
  
  space In1(("Pi_in,1")) space
  Sub1["Subsystem 1\nDissipation: Pi_diss,1"] right<"Pi_12"> Sub2["Subsystem 2\nDissipation: Pi_diss,2"]
  space In2(("Pi_in,2")) space
  
  In1 --> Sub1
  In2 --> Sub2
```

#### N-Subsystem Power Balance
The `sea_app` generalizes this to an arbitrary $N \times N$ matrix size, constructing the matrix $[N]$ such that:
*   **Diagonal terms**: $N_{ii} = \eta_i + \sum_{j \neq i} \eta_{ij}$
*   **Off-Diagonal terms**: $N_{ij} = -\eta_{ji}$

---

## 2. Core Physics Formulas

The architecture calculates required physical parameters dynamically based on the subsystem geometry and material properties.

### 2.1 Wave Speeds (Appendix A)
For a homogeneous thin plate, the bending phase speed ($C_B$) depends on the frequency $\omega$:

$$
C_B = \sqrt{\omega} \left( \frac{B}{m^{\prime\prime}} \right)^{1/4}
$$
where $B = \frac{E \cdot h^3}{12 (1 - \nu^2)}$ is the flexural rigidity, and $m^{\prime\prime}$ is the mass per unit area.

### 2.2 Critical Frequency (Appendix B)
The critical frequency ($f_c$) is where the structural bending wave speed equals the acoustic wave speed in the surrounding medium ($C_0$).

$$
f_c = \frac{C_0^2}{2\pi h} \sqrt{ \frac{12 \rho (1-\nu^2)}{E} }
$$

### 2.3 Coupling Loss Factor (Appendix C)
The coupling from a vibrating structure to an acoustic cavity is calculated via radiation resistance ($R_{rad}$):

$$ \eta_{struct \rightarrow cavity} = \frac{\rho_0 C_0 A \sigma_{rad}}{M \omega} $$

The reverse coupling from the cavity back to the structure relies on the SEA consistency relationship:
$$ \eta_{cavity \rightarrow struct} = \eta_{struct \rightarrow cavity} \frac{n_{struct}}{n_{cavity}} $$
where $n_i$ is the modal density.

---

## 3. Application Usage

The `sea_app` is designed as a modular Python package, allowing you to script complex SEA models by connecting objects together.

### 3.1 Setup and Materials
Import the core modules and define the basic materials your system will use. The package provides common engineering materials, or you can define your own.

```python
from sea_app.core.material import Material, Aluminum
from sea_app.core.subsystem import HomogeneousPlate, AcousticCavity
from sea_app.core.system import SEASystem
from sea_app.core.coupling import clf_plate_to_acoustic, clf_acoustic_to_plate

# Define a custom material if needed
Titanium = Material(name="Titanium", density=4500.0, elastic_modulus=116e9, poisson_ratio=0.32)
```

### 3.2 Defining Subsystems
Create your structural and acoustic elements.

```python
# A 2mm thick structural panel
panel = HomogeneousPlate(
    name="Equipment Panel", 
    material=Aluminum, 
    length=1.5, 
    width=0.8, 
    thickness=0.002, 
    loss_factor=0.02 # internal structural damping
)

# An interior acoustic volume
cabin = AcousticCavity(
    name="Vehicle Cabin",
    volume=5.0, # m^3
    loss_factor=0.08 # acoustic absorption
)
```

### 3.3 Building the System Matrix
Add subsystems to the `SEASystem` object. *Keep track of the returned indices*, as they are used to define power inputs and read outputs.

```python
sea = SEASystem()
idx_panel = sea.add_subsystem(panel)
idx_cabin = sea.add_subsystem(cabin)

freq = 1000.0 # Define analytical center frequency in Hz

# Calculate the coupling between the panel and the cabin
eta_panel_cabin = clf_plate_to_acoustic(panel, cabin, freq)
eta_cabin_panel = clf_acoustic_to_plate(cabin, panel, freq)

sea.set_coupling_loss_factor(idx_panel, idx_cabin, eta_panel_cabin)
sea.set_coupling_loss_factor(idx_cabin, idx_panel, eta_cabin_panel)
```

### 3.4 Solving the Model
Apply external power (e.g., from an engine or a speaker) to a specific subsystem, and order the system to solve for the energies.

```python
# Apply 10 Watts of vibratory power directly to the panel
sea.set_power_input(idx_panel, 10.0)

# Solve the Power Balance Matrix
energy_results = sea.solve(freq)

print(f"Panel Energy: {energy_results[idx_panel]} Joules")
print(f"Cabin Energy: {energy_results[idx_cabin]} Joules")
The resulting energies can be post-processed to find physical velocities (for plates) or sound pressure levels (for cavities) using the methods demonstrated in `example_usage.py`.

---

## 4. Example: Room-Wall-Room Transmission (`myExample`)

To demonstrate the power of the matrix solver vs. simplified analytical solutions, the repository includes `myExample.py`. This script models a classic layout: **Room 1 $\rightarrow$ Wall 2 $\rightarrow$ Room 3**.

Crucially, this script does not just re-calculate hand-formulas; it directly imports and utilizes the core `sea_app` architecture we developed:

```python
from sea_app.core.subsystem import AcousticCavity
from sea_app.core.system import SEASystem

# 1. Initialize the Core Solver
sea = SEASystem()

# 2. Add subsystems using the built-in classes
R1 = AcousticCavity("Raum 1", volume=60.0, loss_factor=eta1, ...)
i_R1 = sea.add_subsystem(R1)
# ...

# 3. Solve the full NxN Energy Matrix
energies = sea.solve(frequency=500.0)
```

### 4.1 The Problem
*   **Room 1**: Source room ($V=60 m^3$), injected with $0.005\text{ W}$ of acoustic power at $500\text{ Hz}$.
*   **Wall 2**: A heavy concrete division ($m^{\prime\prime} = 200 \text{ kg/m}^2$, $S=12 m^2$).
*   **Room 3**: Receiving room ($V=72 m^3$).

### 4.2 The Solution Approach
The script sets up the 3x3 SEA matrix representing these three coupled subsystems. The user's original `MathCAD` calculation solved this using a simplified cascade approach (ignoring back-coupling, i.e., energy flowing from Room 3 back to the Wall, or Wall back to Room 1). 

By executing the `sea_app` matrix solver on this system, we prove that the full, mathematically rigorous matrix solution yields the exact same pressure and velocity levels as the simplified hand-calculations:

*   **Sound Pressure Level (Room 3)**: $69.6 \text{ dB}$
*   **Wall Velocity**: $3.4 \cdot 10^{-6} \text{ m/s}$

You can view the setup and execute this specific comparison by running:
```bash
uv run myExample.py
```
