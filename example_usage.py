import numpy as np

from sea_app.core.material import Aluminum
from sea_app.core.subsystem import HomogeneousPlate, AcousticCavity
from sea_app.core.system import SEASystem
from sea_app.core.coupling import clf_plate_to_acoustic, clf_acoustic_to_plate

def run_example():
    """
    A simple example mimicking a vibrating aluminum plate radiating into a room.
    """
    print("--- Statistical Energy Analysis (SEA) Example ---")
    
    # 1. Define Subsystems
    # A generic aluminum plate, 1m x 1m, 2mm thick
    plate = HomogeneousPlate(
        name="Aluminum Panel", 
        material=Aluminum, 
        length=1.0, 
        width=1.0, 
        thickness=0.002, 
        loss_factor=0.01 # 1% internal damping
    )
    
    # A small room/cavity, 3m x 3m x 3m = 27 m^3
    room = AcousticCavity(
        name="Receiving Room",
        volume=27.0,
        loss_factor=0.05 # Typical room absorption
    )
    
    # 2. Build the System
    sea = SEASystem()
    idx_plate = sea.add_subsystem(plate)
    idx_room = sea.add_subsystem(room)
    
    # 3. Define the Frequency of Interest (e.g. 1000 Hz, 1/3 octave band center)
    freq = 1000.0
    print(f"Solving for Center Frequency: {freq} Hz")
    
    # 4. Calculate and Set Coupling Loss Factors
    eta_plate_room = clf_plate_to_acoustic(plate, room, freq)
    eta_room_plate = clf_acoustic_to_plate(room, plate, freq)
    
    print(f"CLF Plate -> Room: {eta_plate_room:.2e}")
    # Note: room -> plate CLF is usually tiny because modal density of room >> plate
    print(f"CLF Room -> Plate: {eta_room_plate:.2e}") 

    sea.set_coupling_loss_factor(idx_plate, idx_room, eta_plate_room)
    sea.set_coupling_loss_factor(idx_room, idx_plate, eta_room_plate)
    
    # 5. Apply External Power
    # Inject 1 Watt into the plate (e.g. mechanically driven)
    power_in = 1.0
    sea.set_power_input(idx_plate, power_in)
    
    # 6. Solve the system
    energies = sea.solve(freq)
    
    # 7. Output Results
    print("\n--- Results ---")
    for i, subsystem in enumerate(sea.subsystems):
        E = energies[i]
        print(f"System {i} [{subsystem.name}]: Energy = {E:.2e} Joules")
        
        # We can calculate secondary variables from Energy
        if isinstance(subsystem, HomogeneousPlate):
            mass = subsystem.get_mass()
            v_squared = E / mass # E = M * <v^2>
            v_rms = np.sqrt(v_squared)
            print(f"   -> RMS Velocity: {v_rms:.4f} m/s")
            
        elif isinstance(subsystem, AcousticCavity):
            # Energy E = (p_rms^2 * V) / (rho0 * c0^2)
            # p_rms = sqrt(E * rho0 * c0^2 / V)
            p_rms = np.sqrt(E * room.density * (room.speed_of_sound**2) / room.volume)
            # Sound Pressure Level in dB (ref 20 uPa)
            p_ref = 20e-6
            spl = 20 * np.log10(p_rms / p_ref)
            print(f"   -> SPL: {spl:.1f} dB")

if __name__ == "__main__":
    run_example()
