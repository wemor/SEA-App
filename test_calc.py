import os
import json
import math
import subprocess
import sys

# 1. Install PyMuPDF if not present
try:
    import fitz
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymupdf"])
    import fitz

def load_app_logic():
    # Load JSON
    json_path = r"C:\Users\WernerMoretti\OneDrive - wemo\Antigravity_WS\SEA-App\Examples\SEA_Example_C1_L1221_W1_L2332_C2.json"
    with open(json_path) as f:
        data = json.load(f)
    return data

def calc_sea(data):
    # Mimic app.py logic
    freq = data["global"]["freq"]
    rho0 = data["global"]["rho0"]
    c0 = data["global"]["c0"]
    
    # We will simulate the same math code as app.py
    # But since we just want the output, let's just use the exact logic from app.py
    
    import sys
    sys.path.append(r"C:\Users\WernerMoretti\OneDrive - wemo\Antigravity_WS\SEA-App")
    from sea_app.core.system import SEASystem

    sea = SEASystem()
    sys_indices = {}
    
    print("--- SEA App JSON Calculation ---")
    print(f"Freq: {freq} Hz")
    
    class DummySub:
        def __init__(self, name, eta):
            self.name = name
            self.loss_factor = eta

    # Register
    for el in data["elements"]:
        eta_internal = 0.0
        if el["type"] == "Cavity":
            t60 = float(el["t60"])
            eta_internal = 2.2 / (t60 * freq) if t60 > 0 else 0.0
        elif el["type"] == "Wall":
            eta_internal = float(el["eta"])
            
        sub = DummySub(el["name"], eta_internal)
        idx = sea.add_subsystem(sub)
        sys_indices[el["id"]] = idx
        
        power_val = 0.0
        if el["type"] == "Cavity" and el.get("power", 0.0) > 0:
            power_val = float(el["power"])
            sea.set_power_input(idx, power_val)
            
        print(f"Subsystem {el['id']} ({el['name']}): eta_i={eta_internal:.4e}, power={power_val:.4e}")

    # Junctions
    for j in data["junctions"]:
        src = next((e for e in data["elements"] if e["id"] == j["from"]), None)
        recv = next((e for e in data["elements"] if e["id"] == j["to"]), None)
        
        if src and recv:
            src_idx = sys_indices[src["id"]]
            recv_idx = sys_indices[recv["id"]]
            
            eta_ij = 0.0
            eta_ji = 0.0
            
            if src["type"] == "Cavity" and recv["type"] == "Wall":
                S2 = float(recv["surface"])
                fc_2 = float(recv["fc"])
                sigma2 = float(recv["sigma"])
                V1 = float(src["volume"])
                m_2 = float(recv["density"])
                
                if m_2 > 0 and V1 > 0:
                    eta_ij = (rho0 * c0**2 * S2 * fc_2 * sigma2) / (8 * math.pi * V1 * m_2 * freq**3)
                if m_2 > 0:
                    eta_ji = (rho0 * c0 * sigma2) / (2 * math.pi * freq * m_2)
                    
            elif src["type"] == "Wall" and recv["type"] == "Cavity":
                S2 = float(src["surface"])
                fc_2 = float(src["fc"])
                sigma2 = float(src["sigma"])
                V3 = float(recv["volume"])
                m_2 = float(src["density"])
                
                if m_2 > 0:
                    eta_ij = (rho0 * c0 * sigma2) / (2 * math.pi * freq * m_2)
                if m_2 > 0 and V3 > 0:
                    eta_ji = (rho0 * c0**2 * S2 * fc_2 * sigma2) / (8 * math.pi * V3 * m_2 * freq**3)
                    
            elif src["type"] == "Cavity" and recv["type"] == "Cavity":
                V1 = float(src["volume"])
                V3 = float(recv["volume"])
                S_c = float(src.get("surface", 10.0)) 
                tau = 0.01
                
                if V1 > 0:
                    eta_ij = (c0 * S_c * tau) / (8 * math.pi * freq * V1)
                if V3 > 0:
                    eta_ji = (c0 * S_c * tau) / (8 * math.pi * freq * V3)
                    
            sea.set_coupling_loss_factor(src_idx, recv_idx, eta_ij)
            sea.set_coupling_loss_factor(recv_idx, src_idx, eta_ji)
            print(f"Coupling {src['name']} -> {recv['name']}: CLF={eta_ij:.4e}, Rev CLF={eta_ji:.4e}")

    energies = sea.solve(freq)
    
    print("\n--- RESULTS ---")
    for i, el in enumerate(data["elements"]):
        E = energies[i]
        
        if el["type"] == "Cavity":
            V = float(el.get("volume", 50.0))
            p = math.sqrt(max(E * rho0 * c0**2 / V, 1e-24))
            Lp = 20 * math.log10(max(p / 20e-6, 1e-12))
            print(f"{el['name']}: E = {E:.4e} J, Lp = {Lp:.1f} dB")
        elif el["type"] == "Wall":
            M = float(el.get("density", 100.0)) * float(el.get("surface", 10.0))
            v = math.sqrt(max(E / M, 1e-24))
            Lv = 20 * math.log10(max(v / 5e-8, 1e-12))
            print(f"{el['name']}: E = {E:.4e} J, Lv = {Lv:.1f} dB")
            
def extract_pdf():
    pdf_path = r"C:\Users\WernerMoretti\OneDrive - wemo\Antigravity_WS\SEA-App\SEA_equationssolved_nopath13.pdf"
    doc = fitz.open(pdf_path)
    print("\n--- EXTRACTING PDF ---")
    for i, page in enumerate(doc):
        text = page.get_text("text")
        lines = [line for line in text.split('\n') if line.strip()]
        for line in lines:
            if 'dB' in line or 'Cavity 2' in line or 'Lp' in line or 'E' in line or 'p' in line or '=' in line:
                line_safe = line.strip().encode('ascii', 'replace').decode('ascii')
                print(f"Page {i+1}: {line_safe}")

if __name__ == '__main__':
    data = load_app_logic()
    calc_sea(data)
    extract_pdf()
