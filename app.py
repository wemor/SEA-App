import streamlit as st
import numpy as np
import math
import graphviz

# Import sea_app core functions
from sea_app.core.system import SEASystem

st.set_page_config(page_title="SEA App", page_icon="🌊", layout="wide")

# --- 1. Top Toolbar (Simulated) & Global Theming ---
st.markdown(
    """
    <style>
    /* Global Streamlit Background Overrides */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
        font-family: 'Inter', system-ui, sans-serif;
    }
    
    /* Sidebar Overrides */
    [data-testid="stSidebar"] {
        background-color: #21262d;
        border-right: 1px solid #30363d;
    }
    [data-testid="stSidebar"] * {
        color: #e6edf3 !important;
    }
    
    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #e6edf3 !important;
    }

    /* Cards/Containers in Streamlit */
    [data-testid="stVerticalBlock"] > div[style*="border"] {
        background-color: #161b22;
        border-color: #30363d !important;
        border-radius: 12px;
    }

    /* Buttons */
    .stButton > button {
        background-color: #161b22;
        color: #e6edf3;
        border: 1px solid #30363d;
        border-radius: 6px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        border-color: #58a6ff;
        color: #58a6ff;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #161b22;
        border-radius: 6px;
    }

    /* Inputs */
    .stNumberInput input {
        background-color: rgba(255, 255, 255, 0.03) !important;
        color: #e6edf3 !important;
        border: 1px solid #30363d !important;
    }
    .stNumberInput input:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 0 1px #58a6ff !important;
    }

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
        <div class="toolbar-button">Calculation</div>
        <div class="toolbar-button">Results</div>
        <div class="toolbar-button">Materials</div>
        <div class="toolbar-title">Querschnittberechnung_I - SEA App</div>
        <div class="toolbar-button">Help</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🌊 Statistical Energy Analysis (SEA) App")


# --- 2. Left Sidebar (Project Tree) ---
st.sidebar.markdown("### 🌲 Project Tree")
st.sidebar.markdown("---")

# Expandable Tree Structure representation
with st.sidebar.expander("[-] Model Elements", expanded=True):
    # Tree nodes for the existing model
    st.markdown("├─ **Room 1 (Source)**")
    st.markdown("├─ **Wall 2 (Partition)**")
    st.markdown("└─ **Room 3 (Receiving)**")

st.sidebar.markdown("---")
st.sidebar.markdown("#### Input Parameters")

with st.sidebar.expander("🌍 Global Setup", expanded=True):
    freq = st.number_input("Center Frequency $f$ (Hz)", min_value=10.0, max_value=20000.0, value=500.0, step=100.0)
    rho0 = st.number_input("Air Density $\\rho_0$ (kg/m³)", value=1.204, format="%.3f")
    c0 = st.number_input("Speed of Sound $c_0$ (m/s)", value=343.0, format="%.1f")
    omega = 2 * math.pi * freq

with st.sidebar.expander("Room 1 (Source)", expanded=False):
    V1 = st.number_input("Volume (m³)", value=60.0, key="v1")
    S1 = st.number_input("Coupling Surface (m²)", value=12.0, key="s1")
    T60_1 = st.number_input("Rev Time (s)", value=0.6, key="t60_1")
    P1 = st.number_input("Input Power P1 (W)", value=0.005, format="%.4f", key="p1")
    eta1 = 2.2 / (T60_1 * freq)

with st.sidebar.expander("Wall 2 (Division)", expanded=False):
    S2 = st.number_input("Surface (m²)", value=12.0, key="s2")
    m_2 = st.number_input("Area Density (kg/m²)", value=200.0, key="m2")
    fc_2 = st.number_input("Critical Freq (Hz)", value=150.0, key="fc2")
    sigma2 = st.number_input("Radiation Efficiency", value=1.0, key="sig2")
    eta2 = st.number_input("Internal Damping", value=0.05, key="eta2")

with st.sidebar.expander("Room 3 (Receiving)", expanded=False):
    V3 = st.number_input("Volume (m³)", value=72.0, key="v3")
    S3 = st.number_input("Coupling Surface (m²)", value=12.0, key="s3")
    T60_3 = st.number_input("Rev Time (s)", value=0.7, key="t60_3")
    eta3 = 2.2 / (T60_3 * freq)

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
    st.subheader("📊 SEA Model Visualization")
    
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

