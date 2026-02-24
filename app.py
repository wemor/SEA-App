import streamlit as st
import numpy as np
import math
import graphviz
import json
import time

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

# Initialize Session State Defaults (Phase 2 Dynamic Elements)
if "project_name" not in st.session_state:
    st.session_state.project_name = "Project xxxxxxxx"
    st.session_state.freq = 500.0
    st.session_state.rho0 = 1.204
    st.session_state.c0 = 343.0

if "elements" not in st.session_state:
    st.session_state.elements = []

if "junctions" not in st.session_state:
    st.session_state.junctions = []

# Load Project Callback
def load_project_callback():
    uploaded_file = st.session_state.get("uploaded_project_file")
    if uploaded_file is not None:
        try:
            uploaded_file.seek(0)
            loaded_data = json.load(uploaded_file)
            
            # Load Global parameters
            if "global" in loaded_data:
                for k, v in loaded_data["global"].items():
                    if k in st.session_state:
                         st.session_state[k] = float(v) if isinstance(v, (int, float)) else str(v)
            
            # Load elements array
            if "elements" in loaded_data:
                st.session_state.elements = loaded_data["elements"]
                
                # Make sure the current selected element still exists, otherwise reset
                valid_names = [el["name"] for el in st.session_state.elements]
                if st.session_state.get("selected_element") not in valid_names and st.session_state.get("selected_element") != "🌍 Global Setup":
                     st.session_state.selected_element = "🌍 Global Setup"

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
    # Dynamic tree generation
    tree_options = ["🌍 Global Setup"]
    for i, el in enumerate(st.session_state.elements):
        prefix = "└─ " if i == len(st.session_state.elements) - 1 else "├─ "
        tree_options.append(f"{prefix}{el['name']}")
    
    selected_option = st.radio("Select Element to Edit:", tree_options, label_visibility="collapsed")

    # Map visual tree options back to logical IDs
    st.session_state.selected_element = "🌍 Global Setup"
    for el in st.session_state.elements:
        if el['name'] in selected_option:
            st.session_state.selected_element = el['name']
            break


st.sidebar.markdown("---")
st.sidebar.markdown(f"#### Edit: {st.session_state.selected_element}")

# Input Parameters - Conditionally Displayed based on Selection
# We still need to keep the values in session state or default variables to calculate the graph!
# In a real app we'd load this from a project dict, here we use Streamlit keys and defaults.

# DYNAMIC PROPERTIES EDITOR
# Find the currently selected element dictionary
active_el = None
active_el_idx = None
for i, el in enumerate(st.session_state.elements):
    if el['name'] == st.session_state.selected_element:
        active_el = el
        active_el_idx = i
        break

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

elif active_el is not None:
    with st.sidebar:
        # Edit Name
        st.markdown("**General Properties**")
        new_name = st.text_input("Element Name", value=active_el["name"])
        st.session_state.elements[active_el_idx]["name"] = new_name
        
        if active_el["type"] == "Cavity":
            st.markdown("**Geometric Properties**")
            st.session_state.elements[active_el_idx]["volume"] = st.number_input("Volume (m³)", value=float(active_el["volume"]))
            st.session_state.elements[active_el_idx]["surface"] = st.number_input("Coupling Surface (m²)", value=float(active_el["surface"]))
            st.markdown("**Acoustic Properties**")
            st.session_state.elements[active_el_idx]["t60"] = st.number_input("Rev Time (s)", value=float(active_el["t60"]))
            st.markdown("**Excitation**")
            st.session_state.elements[active_el_idx]["power"] = st.number_input("Input Power P (W)", value=float(active_el["power"]), format="%.4f")
            
        elif active_el["type"] == "Wall":
            st.markdown("**Geometric Properties**")
            st.session_state.elements[active_el_idx]["surface"] = st.number_input("Surface (m²)", value=float(active_el["surface"]))
            st.session_state.elements[active_el_idx]["density"] = st.number_input("Area Density (kg/m²)", value=float(active_el["density"]))
            st.markdown("**Structural Properties**")
            st.session_state.elements[active_el_idx]["fc"] = st.number_input("Critical Freq (Hz)", value=float(active_el["fc"]))
            st.session_state.elements[active_el_idx]["sigma"] = st.number_input("Radiation Efficiency", value=float(active_el["sigma"]))
            st.session_state.elements[active_el_idx]["eta"] = st.number_input("Internal Damping", value=float(active_el["eta"]))



# Re-assign local variables for the calculation engine
# Legacy Calculation Engine Adapter
# Map dynamic elements array back to legacy variables until SEA engine is rebuilt
project_name = st.session_state.project_name
freq, rho0, c0 = float(st.session_state.freq), float(st.session_state.rho0), float(st.session_state.c0)

# Default fallbacks (in case user hasn't created elements yet)
V1, S1, T60_1, P1 = 60.0, 12.0, 0.6, 0.005
S2, m_2, fc_2, sigma2, eta2 = 12.0, 200.0, 150.0, 1.0, 0.05
V3, S3, T60_3 = 72.0, 12.0, 0.7

# Find the first Cavity for Room 1, the first Wall for Wall 2, second Cavity for Room 3
cavity_count, wall_count = 0, 0
for el in st.session_state.elements:
    if el["type"] == "Cavity":
        cavity_count += 1
        if cavity_count == 1:
            V1, S1, T60_1, P1 = el["volume"], el["surface"], el["t60"], el.get("power", 0.0)
        elif cavity_count == 2:
            V3, S3, T60_3 = el["volume"], el["surface"], el["t60"]
    elif el["type"] == "Wall":
        wall_count += 1
        if wall_count == 1:
            S2, m_2, fc_2, sigma2, eta2 = el["surface"], el["density"], el["fc"], el["sigma"], el["eta"]

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
                "elements": st.session_state.elements,
                "junctions": st.session_state.junctions
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
        
        # Draw Nodes
        for el in st.session_state.elements:
            short_id = el["id"][-4:] # Use last 4 chars of ID for node name
            if el["type"] == "Cavity":
                graph.node(short_id, f"{el['name']}\\n(Cavity)", style='filled', fillcolor='#cce5ff', shape='box')
            elif el["type"] == "Wall":
                graph.node(short_id, f"{el['name']}\\n(Wall)", style='filled', fillcolor='#e2e3e5', shape='box')
            else:
                graph.node(short_id, el['name'], style='filled', fillcolor='#f8d7da', shape='box')
                
        # Draw Edges
        for j in st.session_state.junctions:
            src_short = j["from"][-4:]
            recv_short = j["to"][-4:]
            graph.edge(src_short, recv_short, label="linked")
            
        if len(st.session_state.elements) == 0:
            graph.node('Empty', 'No elements created yet.\\nAdd them from the right sidebar.', style='dashed', shape='box')
            
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
    
    if st.button("Cavity", use_container_width=True):
        new_id = f"c_{int(time.time() * 1000)}"
        new_name = f"Cavity {sum(1 for el in st.session_state.elements if el['type'] == 'Cavity') + 1}"
        st.session_state.elements.append({
            "id": new_id, "type": "Cavity", "name": new_name, 
            "volume": 50.0, "surface": 10.0, "t60": 1.0, "power": 0.0
        })
        st.session_state.selected_element = new_name
        st.rerun()
        
    if st.button("Wall", use_container_width=True):
        new_id = f"w_{int(time.time() * 1000)}"
        new_name = f"Wall {sum(1 for el in st.session_state.elements if el['type'] == 'Wall') + 1}"
        st.session_state.elements.append({
            "id": new_id, "type": "Wall", "name": new_name, 
            "surface": 10.0, "density": 100.0, "fc": 250.0, "sigma": 1.0, "eta": 0.02
        })
        st.session_state.selected_element = new_name
        st.rerun()
        
    st.button("Plate", use_container_width=True, disabled=True)
    st.button("Beam", use_container_width=True, disabled=True)
    
    st.markdown("---")
    st.markdown("### 🔗 Connections")
    with st.expander("Add Junction", expanded=False):
        if len(st.session_state.elements) >= 2:
            el_names = [el["name"] for el in st.session_state.elements]
            source_el = st.selectbox("From (Source)", el_names, key="j_src")
            recv_el = st.selectbox("To (Receiving)", el_names, key="j_recv")
            
            if st.button("Create Link", use_container_width=True):
                if source_el != recv_el:
                    src_id = next(el["id"] for el in st.session_state.elements if el["name"] == source_el)
                    recv_id = next(el["id"] for el in st.session_state.elements if el["name"] == recv_el)
                    
                    # Avoid duplicates
                    if not any(j["from"] == src_id and j["to"] == recv_id for j in st.session_state.junctions):
                        st.session_state.junctions.append({
                            "id": f"j_{int(time.time() * 1000)}",
                            "from": src_id,
                            "to": recv_id
                        })
                        st.rerun()
        else:
            st.info("Create at least two elements to link.")


# --- 5. Bottom Tool Messages (Fixed Footer) ---
st.markdown(
    '<div class="footer-msg">Ready. Calculation updated for f = {} Hz.</div>'.format(int(freq)),
    unsafe_allow_html=True
)

# Trigger Streamlit Rebuild
