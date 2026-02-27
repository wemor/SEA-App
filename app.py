import streamlit as st
import numpy as np
import math
import graphviz
import json
import time
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
@st.cache_resource
def get_firestore_client():
    if not firebase_admin._apps:
        try:
            # We assume a dict in st.secrets["firebase"] matching the service account format
            cred = credentials.Certificate(dict(st.secrets["firebase"]))
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.warning(f"Firebase not initialized. Ensure st.secrets['firebase'] is set. Error: {e}")
            return None
    try:
        return firestore.client()
    except Exception:
        return None

db = get_firestore_client()

# Import sea_app core functions
from sea_app.core.system import SEASystem

st.set_page_config(page_title="SEA App", page_icon="🌊", layout="wide")

st.markdown("<h3>🌊 Statistical Energy Analysis (SEA) App</h3>", unsafe_allow_html=True)

# --- 1. Top Toolbar (Native Streamlit Tabs) ---
st.markdown(
    """
    <style>
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
    
    /* Graphviz Background Overrides */
    [data-testid="stGraphVizChart"] {
        background-color: #d0d4dc;
        padding: 1rem;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize Session State Defaults (Phase 2 Dynamic Elements)
if "project_name" not in st.session_state:
    st.session_state.project_name = "Project Name"
    st.session_state.variant_name = "Variant 1"
    st.session_state.freq = 500.0
    st.session_state.rho0 = 1.204
    st.session_state.c0 = 343.0

if "elements" not in st.session_state:
    st.session_state.elements = []

if "junctions" not in st.session_state:
    st.session_state.junctions = []

if "cavity_id_counter" not in st.session_state:
    st.session_state.cavity_id_counter = 1

if "wall_id_counter" not in st.session_state:
    st.session_state.wall_id_counter = 1

if "junction_id_counter" not in st.session_state:
    st.session_state.junction_id_counter = 1

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

            if "junctions" in loaded_data:
                st.session_state.junctions = loaded_data["junctions"]
                
            # Update ID counters based on loaded data to prevent collisions
            max_c_id = 0
            max_w_id = 0
            for el in st.session_state.elements:
                if el["id"].startswith("c_"):
                    try: max_c_id = max(max_c_id, int(el["id"].split("_")[1]))
                    except (ValueError, IndexError): pass
                elif el["id"].startswith("w_"):
                    try: max_w_id = max(max_w_id, int(el["id"].split("_")[1]))
                    except (ValueError, IndexError): pass
                    
            max_j_id = 0
            for j in st.session_state.junctions:
                if j["id"].startswith("j_"):
                    try: max_j_id = max(max_j_id, int(j["id"].split("_")[1]))
                    except (ValueError, IndexError): pass
                    
            st.session_state.cavity_id_counter = max_c_id + 1
            st.session_state.wall_id_counter = max_w_id + 1
            st.session_state.junction_id_counter = max_j_id + 1

            st.session_state.load_success = True
            st.session_state.load_error = None
        except Exception as e:
            st.session_state.load_success = False
            st.session_state.load_error = str(e)

# Create Native Streamlit Tabs
tab_model, tab_file, tab_calc, tab_res, tab_help = st.tabs(["📊 Model", "💾 File", "🧮 Calc", "📈 Results", "❓ Help"])

# --- 2. Left Sidebar (Project Tree & Tools) ---

st.sidebar.markdown(f"### 🌲 {st.session_state.project_name}")
st.sidebar.markdown("---")

st.sidebar.markdown("### ⚙️ System Setup")

# Initialize Session State for Selection
if "selected_element" not in st.session_state:
    st.session_state.selected_element = "🌍 Global Setup"

with st.sidebar.expander("🌲 System Tree", expanded=True):
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

# DYNAMIC PROPERTIES EDITOR
with st.sidebar.expander(f"✎ Edit: {st.session_state.selected_element}", expanded=False):
    # Find the currently selected element dictionary
    active_el = None
    active_el_idx = None
    for i, el in enumerate(st.session_state.elements):
        if el['name'] == st.session_state.selected_element:
            active_el = el
            active_el_idx = i
            break

    if st.session_state.selected_element == "🌍 Global Setup":
        pname = st.text_input("Project Name", value=st.session_state.project_name)
        vname = st.text_input("Variant Name", value=st.session_state.get("variant_name", "Variant 1"))
        freq = st.number_input("Center Frequency $f$ (Hz)", min_value=10.0, max_value=20000.0, value=float(st.session_state.freq), step=100.0)
        rho0 = st.number_input("Air Density $\\rho_0$ (kg/m³)", value=float(st.session_state.rho0), format="%.3f")
        c0 = st.number_input("Speed of Sound $c_0$ (m/s)", value=float(st.session_state.c0), format="%.1f")
        
        # Sync visual inputs with backend state
        st.session_state.project_name = pname
        st.session_state.variant_name = vname
        st.session_state.freq = freq
        st.session_state.rho0 = rho0
        st.session_state.c0 = c0

    elif active_el is not None:
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
            st.session_state.elements[active_el_idx]["power"] = st.number_input("Input Power P (W)", value=float(active_el["power"]), format="%.4e")
            
        elif active_el["type"] == "Wall":
            st.markdown("**Geometric Properties**")
            st.session_state.elements[active_el_idx]["surface"] = st.number_input("Surface (m²)", value=float(active_el["surface"]))
            st.session_state.elements[active_el_idx]["density"] = st.number_input("Area Density (kg/m²)", value=float(active_el["density"]))
            st.markdown("**Structural Properties**")
            st.session_state.elements[active_el_idx]["fc"] = st.number_input("Critical Freq (Hz)", value=float(active_el["fc"]))
            st.session_state.elements[active_el_idx]["sigma"] = st.number_input("Radiation Efficiency", value=float(active_el["sigma"]))
            st.session_state.elements[active_el_idx]["eta"] = st.number_input("Internal Damping", value=float(active_el["eta"]))

st.sidebar.markdown("---")
st.sidebar.markdown("### ➕ Add Elements")
with st.sidebar.expander("Create New Element", expanded=False):
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        if st.button("Cavity", use_container_width=True):
            new_id = f"c_{st.session_state.cavity_id_counter}"
            st.session_state.cavity_id_counter += 1
            new_name = f"Cavity {sum(1 for el in st.session_state.elements if el['type'] == 'Cavity') + 1}"
            st.session_state.elements.append({
                "id": new_id, "type": "Cavity", "name": new_name, 
                "volume": 50.0, "surface": 10.0, "t60": 1.0, "power": 0.005
            })
            st.session_state.selected_element = new_name
            st.rerun()
    with f_col2:
        if st.button("Wall", use_container_width=True):
            new_id = f"w_{st.session_state.wall_id_counter}"
            st.session_state.wall_id_counter += 1
            new_name = f"Wall {sum(1 for el in st.session_state.elements if el['type'] == 'Wall') + 1}"
            st.session_state.elements.append({
                "id": new_id, "type": "Wall", "name": new_name, 
                "surface": 10.0, "density": 100.0, "fc": 250.0, "sigma": 1.0, "eta": 0.02
            })
            st.session_state.selected_element = new_name
            st.rerun()
            
    f_col3, f_col4 = st.columns(2)
    with f_col3:
        st.button("Plate", use_container_width=True, disabled=True)
    with f_col4:
        st.button("Beam", use_container_width=True, disabled=True)

st.sidebar.markdown("### 🔗 Add Connections")
with st.sidebar.expander("Add Junction", expanded=False):
    if len(st.session_state.elements) >= 2:
        el_names = [el["name"] for el in st.session_state.elements]
        source_el = st.selectbox("From (Source)", el_names, key="j_src")
        recv_el = st.selectbox("To (Receiving)", el_names, key="j_recv")
        
        if st.button("Create Link", use_container_width=True):
            if source_el != recv_el:
                src_id = next(el["id"] for el in st.session_state.elements if el["name"] == source_el)
                recv_id = next(el["id"] for el in st.session_state.elements if el["name"] == recv_el)
                
                # Block Wall to Wall Structural transmission as per user logic
                # We still allow the user to click the button but we throw an error label
                src_obj = next((e for e in st.session_state.elements if e["name"] == source_el), None)
                recv_obj = next((e for e in st.session_state.elements if e["name"] == recv_el), None)
                
                if src_obj and recv_obj and src_obj["type"] == "Wall" and recv_obj["type"] == "Wall":
                    st.error("Direct Wall-to-Wall structural transmission is not yet permitted in this model.")
                else:
                    # Avoid duplicates
                    if not any(j["from"] == src_id and j["to"] == recv_id for j in st.session_state.junctions):
                        new_j_id = f"j_{st.session_state.junction_id_counter}"
                        st.session_state.junction_id_counter += 1
                        st.session_state.junctions.append({
                            "id": new_j_id,
                            "from": src_id,
                            "to": recv_id
                        })
                        st.rerun()
    else:
        st.info("Create at least two elements to link.")



# --- DYNAMIC CALCULATION ENGINE ---

# Initialize intermediate results dictionary to hold DFLs, CLFs, Power, etc.
if "intermediate_results" not in st.session_state:
    st.session_state.intermediate_results = {
        "dfl_data": [],
        "clf_data": []
    }

# Reset before each run
st.session_state.intermediate_results["dfl_data"] = []
st.session_state.intermediate_results["clf_data"] = []

project_name = st.session_state.project_name
freq, rho0, c0 = float(st.session_state.freq), float(st.session_state.rho0), float(st.session_state.c0)
omega = 2 * math.pi * freq

sea = SEASystem()

class DummySub:
    """A lightweight struct for the UI solver bypassing the generic complex components."""
    def __init__(self, name, eta):
        self.name = name
        self.loss_factor = eta

# 1. Register Subsystems & Internal Loss Factors
sys_indices = {} # Map our element string ID to SEASystem internal integer ID

for el in st.session_state.elements:
    eta_internal = 0.0
    if el["type"] == "Cavity":
        t60 = float(el["t60"])
        eta_internal = 2.2 / (t60 * freq) if t60 > 0 else 0.0
    elif el["type"] == "Wall":
        eta_internal = float(el["eta"])
        
    sub = DummySub(el["name"], eta_internal)
    idx = sea.add_subsystem(sub)
    sys_indices[el["id"]] = idx
    
    # Store intermediate DFL
    power_val = 0.0
    # Register Power
    if el["type"] == "Cavity" and el.get("power", 0.0) > 0:
        power_val = float(el["power"])
        sea.set_power_input(idx, power_val)
        
    st.session_state.intermediate_results["dfl_data"].append({
        "ID": el["id"],
        "Name": el["name"],
        "Type": el["type"],
        "DFL (eta_i)": f"{eta_internal:.4e}",
        "Power (W)": f"{power_val:.4e}"
    })

# 2. Process Junctions (Coupling Loss Factors)
for j in st.session_state.junctions:
    src = next((e for e in st.session_state.elements if e["id"] == j["from"]), None)
    recv = next((e for e in st.session_state.elements if e["id"] == j["to"]), None)
    
    if src and recv:
        src_idx = sys_indices[src["id"]]
        recv_idx = sys_indices[recv["id"]]
        
        eta_ij = 0.0
        eta_ji = 0.0
        
        # Scenario A: Cavity to Wall
        if src["type"] == "Cavity" and recv["type"] == "Wall":
            S2 = float(recv["surface"])
            fc_2 = float(recv["fc"])
            sigma2 = float(recv["sigma"])
            V1 = float(src["volume"])
            m_2 = float(recv["density"])
            
            # Cavity -> Wall
            if m_2 > 0 and V1 > 0:
                eta_ij = (rho0 * c0**2 * S2 * fc_2 * sigma2) / (8 * math.pi * V1 * m_2 * freq**3)
            # Wall -> Cavity (Reversible coupling)
            if m_2 > 0:
                eta_ji = (rho0 * c0 * sigma2) / (2 * math.pi * freq * m_2)
                
            sea.set_coupling_loss_factor(src_idx, recv_idx, eta_ij)
            sea.set_coupling_loss_factor(recv_idx, src_idx, eta_ji)
            
            # Store CLFs
            st.session_state.intermediate_results["clf_data"].append({
                "From": src["name"],
                "To": recv["name"],
                "CLF (eta_ij)": f"{eta_ij:.4e}",
                "CLF (eta_ji)": f"{eta_ji:.4e}"
            })
            
        # Scenario B: Wall to Cavity
        elif src["type"] == "Wall" and recv["type"] == "Cavity":
            S2 = float(src["surface"])
            fc_2 = float(src["fc"])
            sigma2 = float(src["sigma"])
            V3 = float(recv["volume"])
            m_2 = float(src["density"])
            
            # Wall -> Cavity
            if m_2 > 0:
                eta_ij = (rho0 * c0 * sigma2) / (2 * math.pi * freq * m_2)
            # Cavity -> Wall (Reversible coupling)
            if m_2 > 0 and V3 > 0:
                eta_ji = (rho0 * c0**2 * S2 * fc_2 * sigma2) / (8 * math.pi * V3 * m_2 * freq**3)
                
            sea.set_coupling_loss_factor(src_idx, recv_idx, eta_ij)
            sea.set_coupling_loss_factor(recv_idx, src_idx, eta_ji)

            # Store CLFs
            st.session_state.intermediate_results["clf_data"].append({
                "From": src["name"],
                "To": recv["name"],
                "CLF (eta_ij)": f"{eta_ij:.4e}",
                "CLF (eta_ji)": f"{eta_ji:.4e}"
            })
            
        # Scenario C: Cavity to Cavity
        elif src["type"] == "Cavity" and recv["type"] == "Cavity":
            V1 = float(src["volume"])
            V3 = float(recv["volume"])
            # Assuming coupling surface S is tracked on the source cavity for now, or default
            S_c = float(src.get("surface", 10.0)) 
            tau = 0.01 # Hardcoded small opening for now
            
            if V1 > 0:
                eta_ij = (c0 * S_c * tau) / (8 * math.pi * freq * V1)
            if V3 > 0:
                eta_ji = (c0 * S_c * tau) / (8 * math.pi * freq * V3)
                
            sea.set_coupling_loss_factor(src_idx, recv_idx, eta_ij)
            sea.set_coupling_loss_factor(recv_idx, src_idx, eta_ji)

            # Store CLFs
            st.session_state.intermediate_results["clf_data"].append({
                "From": src["name"],
                "To": recv["name"],
                "CLF (eta_ij)": f"{eta_ij:.4e}",
                "CLF (eta_ji)": f"{eta_ji:.4e}"
            })
            
        # Scenario D: Wall to Wall
        elif src["type"] == "Wall" and recv["type"] == "Wall":
            pass # Explicitly blocked structure-borne transmission per user instruction

# 3. Solve SEA Matrix
energies = []
if len(sys_indices) > 0:
    energies = sea.solve(freq)

# 4. Map Results back to UI State
st.session_state.results = {}
for i, el in enumerate(st.session_state.elements):
    E = energies[i] if i < len(energies) else 0.0
    
    if el["type"] == "Cavity":
        V = float(el.get("volume", 50.0))
        p = math.sqrt(max(E * rho0 * c0**2 / V, 1e-24))
        Lp = 20 * math.log10(max(p / 20e-6, 1e-12))
        st.session_state.results[el["id"]] = {"E": E, "L": Lp, "unit": "Lp (dB)"}
    elif el["type"] == "Wall":
        M = float(el.get("density", 100.0)) * float(el.get("surface", 10.0))
        v = math.sqrt(max(E / M, 1e-24))
        Lv = 20 * math.log10(max(v / 5e-8, 1e-12))
        st.session_state.results[el["id"]] = {"E": E, "L": Lv, "unit": "Lv (dB)"}


# --- 3. Main View (Tabs Content) ---

with tab_model:
    # Graph Visualization
    graph = graphviz.Digraph()
    graph.attr(bgcolor='transparent', rankdir='LR')
    
    # Draw Nodes dynamically
    for el in st.session_state.elements:
        short_id = el["id"][-4:]
        
        # Retrieve node result if available
        res_str = ""
        if "results" in st.session_state and el["id"] in st.session_state.results:
            res = st.session_state.results[el["id"]]
            res_str = f"\\n{res['unit'][:2]} = {res['L']:.1f} dB"
        
        if el["type"] == "Cavity":
            graph.node(short_id, f"{el['name']}{res_str}", style='filled', fillcolor='#cce5ff', shape='box')
        elif el["type"] == "Wall":
            graph.node(short_id, f"{el['name']}{res_str}", style='filled', fillcolor='#e2e3e5', shape='box')
        else:
            graph.node(short_id, el['name'], style='filled', fillcolor='#f8d7da', shape='box')
            
    # Draw Edges dynamically
    for j in st.session_state.junctions:
        src_short = j["from"][-4:]
        recv_short = j["to"][-4:]
        graph.edge(src_short, recv_short, label="linked")
        
    if len(st.session_state.elements) == 0:
        graph.node('Empty', 'No elements created yet.\\nAdd them from the left sidebar.', style='dashed', shape='box')
        
    st.graphviz_chart(graph, use_container_width=True)

with tab_file:
    st.markdown("### 💾 Project File Management")
    
    st.markdown("#### 💻 Local PC")
    f_col1, f_col2 = st.columns(2)
    
    with f_col1:
        st.markdown("**Save Project locally**")
        current_state_dict = {
            "global": {"project_name": project_name, "variant_name": st.session_state.get("variant_name", "Variant 1"), "freq": freq, "rho0": rho0, "c0": c0},
            "elements": st.session_state.elements,
            "junctions": st.session_state.junctions
        }
        json_string = json.dumps(current_state_dict, indent=2)
        
        p_name_clean = f"{project_name.replace(' ', '_')}_{st.session_state.get('variant_name', 'Variant 1').replace(' ', '_')}"
        st.download_button(
            label=f"⬇️ Download `{p_name_clean}.json`",
            data=json_string,
            file_name=f"{p_name_clean}.json",
            mime="application/json"
        )
        
    with f_col2:
        st.markdown("**Load Project from PC**")
        st.file_uploader("Upload a saved `.json` project file", type="json", key="uploaded_project_file", on_change=load_project_callback)
        
        # Display status after callback execution
        if st.session_state.get("load_success"):
            st.success("Local Project loaded successfully!")
            st.info("Check the Model Elements tree to verify properties.")
        elif st.session_state.get("load_error"):
            st.error(f"Failed to load file. Error: {st.session_state.load_error}")
            
    st.markdown("---")
    st.markdown("#### ☁️ Cloud (Firebase)")
    if db is None:
        st.warning("Firebase is not connected. Please add Firebase service account credentials to `.streamlit/secrets.toml`.")
    else:
        fc_col1, fc_col2 = st.columns(2)
        
        with fc_col1:
            st.markdown("**Save Project to Cloud**")
            cloud_save_name = st.text_input("Cloud Project Name", value=project_name)
            variant_save_name = st.text_input("Cloud Variant Name", value=st.session_state.get("variant_name", "Variant 1"))
            if st.button("☁️ Save to Firebase", use_container_width=True):
                with st.spinner("Saving to Firestore..."):
                    try:
                        project_ref = db.collection("sea_projects").document(cloud_save_name)
                        project_ref.set({"exists": True}, merge=True)
                        doc_ref = project_ref.collection("variants").document(variant_save_name)
                        doc_ref.set(current_state_dict)
                        st.success(f"Variant '{variant_save_name}' saved to Project '{cloud_save_name}'!")
                    except Exception as e:
                        st.error(f"Failed to save to Firebase: {e}")
                        
        with fc_col2:
            st.markdown("**Manage Cloud Projects**")
            with st.spinner("Fetching available projects..."):
                try:
                    docs = db.collection("sea_projects").stream()
                    project_ids = [doc.id for doc in docs]
                except Exception as e:
                    project_ids = []
                    st.error(f"Failed to fetch Firebase projects: {e}")
            
            if project_ids:
                selected_cloud_project = st.selectbox("Select Project", project_ids)
                
                try:
                    variant_docs = db.collection("sea_projects").document(selected_cloud_project).collection("variants").stream()
                    variant_ids = [doc.id for doc in variant_docs]
                except Exception as e:
                    variant_ids = []
                    
                if variant_ids:
                    selected_variant = st.selectbox("Select Variant", variant_ids)
                    
                    cl_load, cl_del = st.columns(2)
                    
                    with cl_load:
                        if st.button("☁️ Load from Firebase", use_container_width=True):
                            with st.spinner("Loading from Firestore..."):
                                try:
                                    doc_ref = db.collection("sea_projects").document(selected_cloud_project).collection("variants").document(selected_variant)
                                    doc = doc_ref.get()
                                    if doc.exists:
                                        loaded_data = doc.to_dict()
                                        # Load Global parameters
                                        if "global" in loaded_data:
                                            for k, v in loaded_data["global"].items():
                                                if k in st.session_state:
                                                     st.session_state[k] = float(v) if isinstance(v, (int, float)) else str(v)
                                        
                                        # Load elements array
                                        if "elements" in loaded_data:
                                            st.session_state.elements = loaded_data["elements"]
                                            
                                            valid_names = [el["name"] for el in st.session_state.elements]
                                            if st.session_state.get("selected_element") not in valid_names and st.session_state.get("selected_element") != "🌍 Global Setup":
                                                 st.session_state.selected_element = "🌍 Global Setup"

                                        if "junctions" in loaded_data:
                                            st.session_state.junctions = loaded_data["junctions"]
                                            
                                        # Update counters
                                        max_c_id, max_w_id, max_j_id = 0, 0, 0
                                        for el in st.session_state.elements:
                                            if el["id"].startswith("c_"):
                                                try: max_c_id = max(max_c_id, int(el["id"].split("_")[1]))
                                                except: pass
                                            elif el["id"].startswith("w_"):
                                                try: max_w_id = max(max_w_id, int(el["id"].split("_")[1]))
                                                except: pass
                                                
                                        for j in st.session_state.junctions:
                                            if j["id"].startswith("j_"):
                                                try: max_j_id = max(max_j_id, int(j["id"].split("_")[1]))
                                                except: pass
                                                
                                        st.session_state.cavity_id_counter = max_c_id + 1
                                        st.session_state.wall_id_counter = max_w_id + 1
                                        st.session_state.junction_id_counter = max_j_id + 1
                                        
                                        st.success(f"Variant '{selected_variant}' loaded via Firebase!")
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("Variant not found in DB.")
                                except Exception as e:
                                    st.error(f"Error loading from Firebase: {e}")
                    
                    with cl_del:
                        if st.button("🗑️ Delete Variant", type="primary", use_container_width=True):
                            with st.spinner("Deleting from Firestore..."):
                                try:
                                    db.collection("sea_projects").document(selected_cloud_project).collection("variants").document(selected_variant).delete()
                                    st.success(f"Variant '{selected_variant}' deleted successfully from Cloud!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting variant from Firebase: {e}")
                else:
                    st.info("No variants found in this project.")
            else:
                st.info("No projects found in Firebase Database.")

with tab_res:
    import pandas as pd
    st.markdown("### 📈 Calculation Results")
    
    if not st.session_state.elements:
        st.info("No elements to display. Add elements and connections first.")
    else:
        
        # --- 1. Element Parameters (DFL / Power) ---
        st.markdown("#### 1. Subsystem Parameters")
        if st.session_state.intermediate_results["dfl_data"]:
            df_dfl = pd.DataFrame(st.session_state.intermediate_results["dfl_data"])
            st.dataframe(df_dfl, use_container_width=True, hide_index=True)
        else:
            st.caption("No subsystems calculated.")

        # --- 2. Coupling Parameters (CLF) ---
        st.markdown("#### 2. Coupling Loss Factors (CLF)")
        if st.session_state.intermediate_results["clf_data"]:
            df_clf = pd.DataFrame(st.session_state.intermediate_results["clf_data"])
            st.dataframe(df_clf, use_container_width=True, hide_index=True)
        else:
            st.caption("No junctions calculated.")

        st.markdown("---")
        
        # --- 3. Final Energies and Levels ---
        st.markdown("#### 3. Energy and Acoustic Levels")
        
        # Dynamically create columns based on number of elements
        cols = st.columns(min(len(st.session_state.elements), 4))
        
        for i, el in enumerate(st.session_state.elements):
            col = cols[i % len(cols)]
            res = st.session_state.results.get(el["id"], {"E": 0.0, "L": 0.0, "unit": "-"})
            col.metric(el["name"], f"{res['L']:.1f} {res['unit'][-3:]}", f"E: {res['E']:.2e} J")
            
        st.markdown("---")
        
        # --- 4. Markdown Export ---
        md_content = f"# SEA Calculation Results: {project_name}\n"
        md_content += f"**Frequency:** {freq} Hz | **Air Density:** {rho0} kg/m³ | **Speed of Sound:** {c0} m/s\n\n"
        
        md_content += "## 1. Subsystem Parameters\n\n"
        if st.session_state.intermediate_results["dfl_data"]:
            md_content += df_dfl.to_markdown(index=False) + "\n\n"
        else:
            md_content += "No subsystems calculated.\n\n"

        md_content += "## 2. Coupling Loss Factors (CLF)\n\n"
        if st.session_state.intermediate_results["clf_data"]:
            md_content += df_clf.to_markdown(index=False) + "\n\n"
        else:
            md_content += "No junctions calculated.\n\n"
            
        md_content += "## 3. Energy and Acoustic Levels\n\n"
        if st.session_state.elements:
            final_res = []
            for el in st.session_state.elements:
                res = st.session_state.results.get(el["id"], {"E": 0.0, "L": 0.0, "unit": "-"})
                final_res.append({
                    "Element": el["name"],
                    "Energy (J)": f"{res['E']:.4e}",
                    "Level": f"{res['L']:.1f} {res['unit'][-3:]}"
                })
            df_final = pd.DataFrame(final_res)
            md_content += df_final.to_markdown(index=False) + "\n\n"
        
        st.download_button(
            label="📄 Download Results as Markdown",
            data=md_content,
            file_name=f"{project_name.replace(' ', '_')}_Results.md",
            mime="text/markdown"
        )

with tab_calc:
    st.success("Calculation complete!")
    st.info(f"SEA Energy matrix solved for f = {int(freq)} Hz.")
    st.markdown("Navigate to **Results** to see detailed acoustic metrics, or **Model** to see updated graph edge weights.")

with tab_help:
    try:
        with open("docs/manual.md", "r", encoding="utf-8") as f:
            st.markdown(f.read())
    except FileNotFoundError:
        st.warning("Help manual not found at `docs/manual.md`.")

# --- 4. Bottom Tool Messages (Fixed Footer) ---
st.markdown(
    '<div class="footer-msg">Ready. Calculation updated for f = {} Hz.</div>'.format(int(freq)),
    unsafe_allow_html=True
)

# Trigger Streamlit Rebuild
