import streamlit as st
import numpy as np
import math
import graphviz

# Import sea_app core functions
from sea_app.core.system import SEASystem

st.set_page_config(page_title="SEA App", page_icon="🌊", layout="wide")
st.title("🌊 Statistical Energy Analysis (SEA) App")
st.markdown("Configure your subsystems in the sidebar to dynamically calculate the power balance matrix and energy flows.")

# --- Sidebar Configuration (Tree Structure) ---
st.sidebar.header("⚙️ System Configuration")

with st.sidebar.expander("🌍 Global Environment", expanded=True):
    freq = st.number_input("Center Frequency $f$ (Hz)", min_value=10.0, max_value=20000.0, value=500.0, step=100.0)
    rho0 = st.number_input("Air Density $\\rho_0$ (kg/m³)", value=1.204, format="%.3f")
    c0 = st.number_input("Speed of Sound $c_0$ (m/s)", value=343.0, format="%.1f")
    omega = 2 * math.pi * freq

st.sidebar.markdown("### 🧱 Subsystems")

with st.sidebar.expander("Room 1 (Source Cavity)", expanded=False):
    st.markdown("**Geometric Properties**")
    V1 = st.number_input("Volume R1 (m³)", value=60.0, key="v1")
    S1 = st.number_input("Coupling Surface R1 (m²)", value=12.0, key="s1")
    st.markdown("**Acoustic Properties**")
    T60_1 = st.number_input("Rev Time T60_1 (s)", value=0.6, key="t60_1")
    eta1 = 2.2 / (T60_1 * freq)
    st.markdown("**Excitation**")
    P1 = st.number_input("Input Power P1 (W)", value=0.005, format="%.4f", key="p1")

with st.sidebar.expander("Wall 2 (Structural Division)", expanded=False):
    st.markdown("**Geometric Properties**")
    S2 = st.number_input("Surface W2 (m²)", value=12.0, key="s2")
    m_2 = st.number_input("Area Density m'' (kg/m²)", value=200.0, key="m2")
    st.markdown("**Structural Properties**")
    fc_2 = st.number_input("Critical Freq fc_2 (Hz)", value=150.0, key="fc2")
    sigma2 = st.number_input("Radiation Efficiency σ2", value=1.0, key="sig2")
    eta2 = st.number_input("Internal Damping η2", value=0.05, key="eta2")

with st.sidebar.expander("Room 3 (Receiving Cavity)", expanded=False):
    st.markdown("**Geometric Properties**")
    V3 = st.number_input("Volume R3 (m³)", value=72.0, key="v3")
    S3 = st.number_input("Coupling Surface R3 (m²)", value=12.0, key="s3")
    st.markdown("**Acoustic Properties**")
    T60_3 = st.number_input("Rev Time T60_3 (s)", value=0.7, key="t60_3")
    eta3 = 2.2 / (T60_3 * freq)

# --- Calculation ---
M2 = m_2 * S2
eta12 = (rho0 * c0**2 * S2 * fc_2 * sigma2) / (8 * math.pi * V1 * m_2 * freq**3)
eta21 = (rho0 * c0 * sigma2) / (2 * math.pi * freq * m_2)
eta23 = eta21 
tau13 = 0.01
eta13 = (c0 * S1 * tau13) / (8 * math.pi * freq * V1)
eta31 = (c0 * S3 * tau13) / (8 * math.pi * freq * V3)

# Build System
sea = SEASystem()

class DummySub:
    """A lightweight struct for the UI solver bypassing the generic complex components."""
    def __init__(self, name, eta):
        self.name = name
        self.loss_factor = eta

idx1 = sea.add_subsystem(DummySub("Room 1", eta1))
idx2 = sea.add_subsystem(DummySub("Wall 2", eta2))
idx3 = sea.add_subsystem(DummySub("Room 3", eta3))

sea.set_coupling_loss_factor(idx1, idx2, eta12)
sea.set_coupling_loss_factor(idx2, idx1, eta21)
sea.set_coupling_loss_factor(idx2, idx3, eta23)
sea.set_coupling_loss_factor(idx3, idx2, eta21) # symmetry
sea.set_coupling_loss_factor(idx1, idx3, eta13)
sea.set_coupling_loss_factor(idx3, idx1, eta31)

sea.set_power_input(idx1, P1)

# Run matrix calculation
energies = sea.solve(freq)
E1, E2, E3 = energies

# Post-processing Results
# Room 1
p1 = math.sqrt(E1 * rho0 * c0**2 / V1)
Lp1 = 20 * math.log10(p1 / 20e-6)

# Wall 2
v2 = math.sqrt(E2 / M2)
Lv2 = 20 * math.log10(v2 / 5e-8)

# Room 3
p3 = math.sqrt(E3 * rho0 * c0**2 / V3)
Lp3 = 20 * math.log10(p3 / 20e-6)


# --- Sidebar: Calculation Results ---
st.sidebar.markdown("---")
with st.sidebar.expander("📊 Calculation Results", expanded=True):
    st.markdown("##### Subsystem Outputs")
    
    with st.container(border=True):
        st.markdown("**Room 1 (Source)**")
        st.markdown(f"Kinetic Energy $E_1$: **{E1:.2e} J**")
        st.markdown(f"Sound Pressure $L_{{p1}}$: **{Lp1:.1f} dB**")
        
    with st.container(border=True):
        st.markdown("**Wall 2 (Division)**")
        st.markdown(f"Kinetic Energy $E_2$: **{E2:.2e} J**")
        st.markdown(f"Velocity Level $L_{{v2}}$: **{Lv2:.1f} dB**")
        
    with st.container(border=True):
        st.markdown("**Room 3 (Receiving)**")
        st.markdown(f"Kinetic Energy $E_3$: **{E3:.2e} J**")
        st.markdown(f"Sound Pressure $L_{{p3}}$: **{Lp3:.1f} dB**")


# --- Main Layout ---
st.subheader("System Architecture")
graph = graphviz.Digraph()
graph.attr(rankdir='LR')
# Nodes
graph.node('R1', f'Room 1\\nLp = {Lp1:.1f} dB', style='filled', fillcolor='#cce5ff', shape='box')
graph.node('W2', f'Wall 2\\nLv = {Lv2:.1f} dB', style='filled', fillcolor='#e2e3e5', shape='box')
graph.node('R3', f'Room 3\\nLp = {Lp3:.1f} dB', style='filled', fillcolor='#d4edda', shape='box')

# Edges
graph.edge('R1', 'W2', label=f'η={eta12:.1e}')
graph.edge('W2', 'R1', label=f'η={eta21:.1e}')
graph.edge('W2', 'R3', label=f'η={eta23:.1e}')
graph.edge('R3', 'W2', label=f'η={eta21:.1e}')
graph.edge('R1', 'R3', label=f'η={eta13:.1e}')

st.graphviz_chart(graph, use_container_width=True)

