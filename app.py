import streamlit as st
import numpy as np
import math
import graphviz

# Import sea_app core functions
from sea_app.core.system import SEASystem

st.set_page_config(page_title="SEA App", page_icon="🌊", layout="wide")

st.markdown("<h3>🌊 Statistical Energy Analysis (SEA) App</h3>", unsafe_allow_html=True)

# --- 1. Top Toolbar (Simulated) & Global Theming ---
st.markdown(
    """
    <style>
    /* Simulated Toolbar */
    .toolbar-container {
        display: flex;
        gap: 10px;
        padding-bottom: 20px;
        border-bottom: 1px solid #30363d;
        margin-bottom: 20px;
    }
    .toolbar-button {
        padding: 8px 16px;
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 4px;
        cursor: pointer;
        text-align: center;
        flex: 1;
        font-weight: 500;
        color: #e6edf3;
        transition: all 0.2s;
    }
    .toolbar-button:hover {
        border-color: #58a6ff;
        color: #58a6ff;
    }
    .toolbar-title {
        flex: 2;
        text-align: center;
        font-weight: bold;
        align-self: center;
        color: #e6edf3;
    }

    /* Fixed Footer Messaging */
    .footer-msg {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #161b22;
        color: #8b949e;
        text-align: left;
        padding: 8px 20px;
        font-size: 14px;
        border-top: 1px solid #30363d;
        z-index: 1000;
    }
    </style>
    <div class="toolbar-container">
        <div class="toolbar-button">File</div>
        <div class="toolbar-button">Visualization</div>
        <div class="toolbar-button">Calculation</div>
        <div class="toolbar-button">Results</div>
        <div class="toolbar-button">Materials</div>
        <div class="toolbar-title"></div>
        <div class="toolbar-button">Help</div>
    </div>
    """,
    unsafe_allow_html=True
)


# --- 2. Left Sidebar (Project Tree) ---
st.sidebar.markdown("### 🌲 Project Tree")
st.sidebar.markdown("---")

# Initialize Session State for Selection
if "selected_element" not in st.session_state:
    st.session_state.selected_element = "🌍 Global Setup"

with st.sidebar.expander("[-] Model Elements", expanded=True):
    # Interactive tree using a styling hack for a radio button
    tree_options = [
        "🌍 Global Setup",
        "├─ Room 1 (Source)",
        "├─ Wall 2 (Partition)",
        "└─ Room 3 (Receiving)"
    ]
    
    selected_option = st.radio(
        "Select Element to Edit:", 
        tree_options, 
        label_visibility="collapsed"
    )

    # Map visual tree options back to logical IDs
    if "Global Setup" in selected_option:
        st.session_state.selected_element = "🌍 Global Setup"
    elif "Room 1" in selected_option:
        st.session_state.selected_element = "Room 1 (Source)"
    elif "Wall 2" in selected_option:
        st.session_state.selected_element = "Wall 2 (Division)"
    elif "Room 3" in selected_option:
        st.session_state.selected_element = "Room 3 (Receiving)"


st.sidebar.markdown("---")
st.sidebar.markdown(f"#### Edit: {st.session_state.selected_element}")

# Input Parameters - Conditionally Displayed based on Selection
# We still need to keep the values in session state or default variables to calculate the graph!
# In a real app we'd load this from a project dict, here we use Streamlit keys and defaults.

# Initialize default values if not present
defaults = {
    "freq": 500.0, "rho0": 1.204, "c0": 343.0,
    "v1": 60.0, "s1": 12.0, "t60_1": 0.6, "p1": 0.005,
    "s2": 12.0, "m2": 200.0, "fc2": 150.0, "sig2": 1.0, "eta2": 0.05,
    "v3": 72.0, "s3": 12.0, "t60_3": 0.7
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if st.session_state.selected_element == "🌍 Global Setup":
    with st.sidebar:
        freq = st.number_input("Center Frequency $f$ (Hz)", min_value=10.0, max_value=20000.0, value=st.session_state.freq, step=100.0, key="freq_ui")
        rho0 = st.number_input("Air Density $\\rho_0$ (kg/m³)", value=st.session_state.rho0, format="%.3f", key="rho0_ui")
        c0 = st.number_input("Speed of Sound $c_0$ (m/s)", value=st.session_state.c0, format="%.1f", key="c0_ui")
    
    # Sync visual inputs with backend state
    st.session_state.freq, st.session_state.rho0, st.session_state.c0 = freq, rho0, c0

elif st.session_state.selected_element == "Room 1 (Source)":
    with st.sidebar:
        st.markdown("**Geometric Properties**")
        V1 = st.number_input("Volume (m³)", value=st.session_state.v1, key="v1_ui")
        S1 = st.number_input("Coupling Surface (m²)", value=st.session_state.s1, key="s1_ui")
        st.markdown("**Acoustic Properties**")
        T60_1 = st.number_input("Rev Time (s)", value=st.session_state.t60_1, key="t60_1_ui")
        st.markdown("**Excitation**")
        P1 = st.number_input("Input Power P1 (W)", value=st.session_state.p1, format="%.4f", key="p1_ui")
    
    st.session_state.v1, st.session_state.s1, st.session_state.t60_1, st.session_state.p1 = V1, S1, T60_1, P1

elif st.session_state.selected_element == "Wall 2 (Division)":
    with st.sidebar:
        st.markdown("**Geometric Properties**")
        S2 = st.number_input("Surface (m²)", value=st.session_state.s2, key="s2_ui")
        m_2 = st.number_input("Area Density (kg/m²)", value=st.session_state.m2, key="m2_ui")
        st.markdown("**Structural Properties**")
        fc_2 = st.number_input("Critical Freq (Hz)", value=st.session_state.fc2, key="fc2_ui")
        sigma2 = st.number_input("Radiation Efficiency", value=st.session_state.sig2, key="sig2_ui")
        eta2 = st.number_input("Internal Damping", value=st.session_state.eta2, key="eta2_ui")
    
    st.session_state.s2, st.session_state.m2, st.session_state.fc2, st.session_state.sig2, st.session_state.eta2 = S2, m_2, fc_2, sigma2, eta2

elif st.session_state.selected_element == "Room 3 (Receiving)":
    with st.sidebar:
        st.markdown("**Geometric Properties**")
        V3 = st.number_input("Volume (m³)", value=st.session_state.v3, key="v3_ui")
        S3 = st.number_input("Coupling Surface (m²)", value=st.session_state.s3, key="s3_ui")
        st.markdown("**Acoustic Properties**")
        T60_3 = st.number_input("Rev Time (s)", value=st.session_state.t60_3, key="t60_3_ui")
    
    st.session_state.v3, st.session_state.s3, st.session_state.t60_3 = V3, S3, T60_3


# Re-assign local variables for the calculation engine so it doesn't break
freq, rho0, c0 = st.session_state.freq, st.session_state.rho0, st.session_state.c0
V1, S1, T60_1, P1 = st.session_state.v1, st.session_state.s1, st.session_state.t60_1, st.session_state.p1
S2, m_2, fc_2, sigma2, eta2 = st.session_state.s2, st.session_state.m2, st.session_state.fc2, st.session_state.sig2, st.session_state.eta2
V3, S3, T60_3 = st.session_state.v3, st.session_state.s3, st.session_state.t60_3

omega = 2 * math.pi * freq
eta1 = 2.2 / (T60_1 * freq) if T60_1 > 0 else 0
eta3 = 2.2 / (T60_3 * freq) if T60_3 > 0 else 0

# --- Calculation Engine (same as before) ---
M2 = m_2 * S2
eta12 = (rho0 * c0**2 * S2 * fc_2 * sigma2) / (8 * math.pi * V1 * m_2 * freq**3)
eta21 = (rho0 * c0 * sigma2) / (2 * math.pi * freq * m_2)
eta23 = eta21 
tau13 = 0.01
eta13 = (c0 * S1 * tau13) / (8 * math.pi * freq * V1)
eta31 = (c0 * S3 * tau13) / (8 * math.pi * freq * V3)

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
sea.set_coupling_loss_factor(idx3, idx2, eta21)
sea.set_coupling_loss_factor(idx1, idx3, eta13)
sea.set_coupling_loss_factor(idx3, idx1, eta31)
sea.set_power_input(idx1, P1)

energies = sea.solve(freq)
E1, E2, E3 = energies

p1 = math.sqrt(E1 * rho0 * c0**2 / V1)
Lp1 = 20 * math.log10(p1 / 20e-6)
v2 = math.sqrt(E2 / M2)
Lv2 = 20 * math.log10(v2 / 5e-8)
p3 = math.sqrt(E3 * rho0 * c0**2 / V3)
Lp3 = 20 * math.log10(p3 / 20e-6)


# --- 3. Main View & 4. Right Sidebar Area (Using Columns) ---
# Create a 5:1 ratio layout to make the right side much narrower
col_main, col_right = st.columns([5, 1])

with col_main:
    
    # Graph Visualization
    graph = graphviz.Digraph()
    graph.attr(rankdir='LR')
    graph.node('R1', f'Room 1\\nLp = {Lp1:.1f} dB', style='filled', fillcolor='#cce5ff', shape='box')
    graph.node('W2', f'Wall 2\\nLv = {Lv2:.1f} dB', style='filled', fillcolor='#e2e3e5', shape='box')
    graph.node('R3', f'Room 3\\nLp = {Lp3:.1f} dB', style='filled', fillcolor='#d4edda', shape='box')
    graph.edge('R1', 'W2', label=f'η={eta12:.1e}')
    graph.edge('W2', 'R1', label=f'η={eta21:.1e}')
    graph.edge('W2', 'R3', label=f'η={eta23:.1e}')
    graph.edge('R3', 'W2', label=f'η={eta21:.1e}')
    graph.edge('R1', 'R3', label=f'η={eta13:.1e}')
    
    st.graphviz_chart(graph, use_container_width=True)
    
    # Calculation Results inline
    with st.expander("📈 Calculation Results", expanded=True):
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("Room 1 Lp", f"{Lp1:.1f} dB", f"{E1:.2e} J")
        res_col2.metric("Wall 2 Lv", f"{Lv2:.1f} dB", f"{E2:.2e} J")
        res_col3.metric("Room 3 Lp", f"{Lp3:.1f} dB", f"{E3:.2e} J")

with col_right:
    st.markdown("### 🧱 SEA Elements")
    st.button("Cavity", use_container_width=True)
    st.button("Wall", use_container_width=True)
    st.button("Plate", use_container_width=True)
    st.button("Beam", use_container_width=True)
    st.button("Junction", use_container_width=True)


# --- 5. Bottom Tool Messages (Fixed Footer) ---
st.markdown(
    '<div class="footer-msg">Ready. Calculation updated for f = {} Hz.</div>'.format(int(freq)),
    unsafe_allow_html=True
)

