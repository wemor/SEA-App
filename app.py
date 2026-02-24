import streamlit as st
import numpy as np
import math
import graphviz
import json

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
    """,
    unsafe_allow_html=True
)

# Initialize Session State Defaults
defaults = {
    "project_name": "Project xxxxxxxx",
    "freq": 500.0, "rho0": 1.204, "c0": 343.0,
    "v1": 60.0, "s1": 12.0, "t60_1": 0.6, "p1": 0.005,
    "s2": 12.0, "m2": 200.0, "fc2": 150.0, "sig2": 1.0, "eta2": 0.05,
    "v3": 72.0, "s3": 12.0, "t60_3": 0.7
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Load Project Callback
def load_project_callback():
    uploaded_file = st.session_state.get("uploaded_project_file")
    if uploaded_file is not None:
        try:
            uploaded_file.seek(0)
            loaded_data = json.load(uploaded_file)
            for section, params in loaded_data.items():
                for k, v in params.items():
                    # Apply to global variables
                    if k in st.session_state:
                         st.session_state[k] = float(v) if isinstance(v, (int, float)) else str(v)
                         
            st.session_state.load_success = True
            st.session_state.load_error = None
        except Exception as e:
            st.session_state.load_success = False
            st.session_state.load_error = str(e)

if "current_view" not in st.session_state:
    st.session_state.current_view = "Visualization"

# Native Streamlit Toolbar
t_col1, t_col2, t_col3, t_col4, t_col5, t_spacer, t_col6 = st.columns([1, 1, 1, 1, 1, 3, 1])

with t_col1:
    if st.button("File", use_container_width=True): st.session_state.current_view = "File"
with t_col2:
    if st.button("Visualization", use_container_width=True): st.session_state.current_view = "Visualization"
with t_col3:
    if st.button("Calculation", use_container_width=True): st.session_state.current_view = "Calculation"
with t_col4:
    if st.button("Results", use_container_width=True): st.session_state.current_view = "Results"
with t_col5:
    if st.button("Materials", use_container_width=True): pass
with t_col6:
    if st.button("Help", use_container_width=True): st.session_state.current_view = "Help"

st.markdown("---")


# --- 2. Left Sidebar (Project Tree) ---

st.sidebar.markdown(f"### 🌲 {st.session_state.project_name}")
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

if st.session_state.selected_element == "🌍 Global Setup":
    with st.sidebar:
        pname = st.text_input("Project Name", value=st.session_state.project_name)
        freq = st.number_input("Center Frequency $f$ (Hz)", min_value=10.0, max_value=20000.0, value=float(st.session_state.freq), step=100.0)
        rho0 = st.number_input("Air Density $\\rho_0$ (kg/m³)", value=float(st.session_state.rho0), format="%.3f")
        c0 = st.number_input("Speed of Sound $c_0$ (m/s)", value=float(st.session_state.c0), format="%.1f")
    
    # Sync visual inputs with backend state
    st.session_state.project_name = pname
    st.session_state.freq = freq
    st.session_state.rho0 = rho0
    st.session_state.c0 = c0

elif st.session_state.selected_element == "Room 1 (Source)":
    with st.sidebar:
        st.markdown("**Geometric Properties**")
        st.number_input("Volume (m³)", key="v1_ui")
        st.number_input("Coupling Surface (m²)", key="s1_ui")
        st.markdown("**Acoustic Properties**")
        st.number_input("Rev Time (s)", key="t60_1_ui")
        st.markdown("**Excitation**")
        st.number_input("Input Power P1 (W)", format="%.4f", key="p1_ui")
    
    st.session_state.v1 = st.session_state.v1_ui
    st.session_state.s1 = st.session_state.s1_ui
    st.session_state.t60_1 = st.session_state.t60_1_ui
    st.session_state.p1 = st.session_state.p1_ui

elif st.session_state.selected_element == "Wall 2 (Division)":
    with st.sidebar:
        st.markdown("**Geometric Properties**")
        S2 = st.number_input("Surface (m²)", value=float(st.session_state.s2))
        m_2 = st.number_input("Area Density (kg/m²)", value=float(st.session_state.m2))
        st.markdown("**Structural Properties**")
        fc_2 = st.number_input("Critical Freq (Hz)", value=float(st.session_state.fc2))
        sigma2 = st.number_input("Radiation Efficiency", value=float(st.session_state.sig2))
        eta2 = st.number_input("Internal Damping", value=float(st.session_state.eta2))
    
    st.session_state.s2 = S2
    st.session_state.m2 = m_2
    st.session_state.fc2 = fc_2
    st.session_state.sig2 = sigma2
    st.session_state.eta2 = eta2

elif st.session_state.selected_element == "Room 3 (Receiving)":
    with st.sidebar:
        st.markdown("**Geometric Properties**")
        st.number_input("Volume (m³)", key="v3_ui")
        st.number_input("Coupling Surface (m²)", key="s3_ui")
        st.markdown("**Acoustic Properties**")
        st.number_input("Rev Time (s)", key="t60_3_ui")
    
    st.session_state.v3 = st.session_state.v3_ui
    st.session_state.s3 = st.session_state.s3_ui
    st.session_state.t60_3 = st.session_state.t60_3_ui


# Re-assign local variables for the calculation engine
project_name = st.session_state.project_name
freq, rho0, c0 = float(st.session_state.freq), float(st.session_state.rho0), float(st.session_state.c0)
V1, S1, T60_1, P1 = float(st.session_state.v1), float(st.session_state.s1), float(st.session_state.t60_1), float(st.session_state.p1)
S2, m_2, fc_2, sigma2, eta2 = float(st.session_state.s2), float(st.session_state.m2), float(st.session_state.fc2), float(st.session_state.sig2), float(st.session_state.eta2)
V3, S3, T60_3 = float(st.session_state.v3), float(st.session_state.s3), float(st.session_state.t60_3)

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
    
    if st.session_state.current_view == "File":
        st.markdown("### 💾 Project File Management")
        
        f_col1, f_col2 = st.columns(2)
        
        with f_col1:
            st.markdown("#### Save Project")
            current_state_dict = {
                "global": {"project_name": project_name, "freq": freq, "rho0": rho0, "c0": c0},
                "room_1": {"v1": V1, "s1": S1, "t60_1": T60_1, "p1": P1},
                "wall_2": {"s2": S2, "m2": m_2, "fc2": fc_2, "sig2": sigma2, "eta2": eta2},
                "room_3": {"v3": V3, "s3": S3, "t60_3": T60_3}
            }
            json_string = json.dumps(current_state_dict, indent=2)
            
            p_name_clean = project_name.replace(" ", "_")
            st.download_button(
                label=f"⬇️ Download `{p_name_clean}.json`",
                data=json_string,
                file_name=f"{p_name_clean}.json",
                mime="application/json"
            )
            
        with f_col2:
            st.markdown("#### Load Project")
            st.file_uploader("Upload a saved `.json` project file", type="json", key="uploaded_project_file", on_change=load_project_callback)
            
            # Display status after callback execution
            if st.session_state.get("load_success"):
                st.success("Project loaded successfully!")
                st.info("Check the Model Elements tree to verify properties.")
            elif st.session_state.get("load_error"):
                st.error(f"Failed to load file. Error: {st.session_state.load_error}")

    elif st.session_state.current_view == "Visualization":
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

    elif st.session_state.current_view == "Results":
        st.markdown("### 📈 Calculation Results")
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("Room 1 Lp", f"{Lp1:.1f} dB", f"{E1:.2e} J")
        res_col2.metric("Wall 2 Lv", f"{Lv2:.1f} dB", f"{E2:.2e} J")
        res_col3.metric("Room 3 Lp", f"{Lp3:.1f} dB", f"{E3:.2e} J")

    elif st.session_state.current_view == "Calculation":
        st.success("Calculation complete!")
        st.info(f"SEA Energy matrix solved for f = {int(freq)} Hz.")
        st.markdown("Navigate to **Results** to see detailed acoustic metrics, or **Visualization** to see updated graph edge weights.")

    elif st.session_state.current_view == "Help":
        try:
            with open("docs/manual.md", "r", encoding="utf-8") as f:
                st.markdown(f.read())
        except FileNotFoundError:
            st.warning("Help manual not found at `docs/manual.md`.")

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

