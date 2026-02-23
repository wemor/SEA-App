import math
from sea_app.core.subsystem import HomogeneousPlate, AcousticCavity
from sea_app.core import constants

def clf_plate_to_acoustic(plate: HomogeneousPlate, cavity: AcousticCavity, frequency: float) -> float:
    """
    Calculate Coupling Loss Factor (CLF or eta_ij) from a Plate to an Acoustic Cavity.
    Uses Eq (C-10) and (C-11) from PDF.
    eta_plate_to_air = R_rad / (M * omega)
    R_rad = rho0 * c0 * Area * sigma_rad
    """
    omega = 2.0 * math.pi * frequency
    M = plate.get_mass()
    A = plate.area
    rho0 = cavity.density
    c0 = cavity.speed_of_sound
    
    sigma_rad = plate.radiation_efficiency(frequency)
    
    # Radiation Resistance (R)
    R_rad = rho0 * c0 * A * sigma_rad
    
    # Coupling Loss Factor (eta_ij)
    clf = R_rad / (M * omega)
    return clf

def clf_acoustic_to_plate(cavity: AcousticCavity, plate: HomogeneousPlate, frequency: float) -> float:
    """
    Calculate Coupling Loss Factor from Acoustic Cavity to Plate.
    Uses the Consistency Relationship in SEA:
    n_i * eta_ij = n_j * eta_ji
    Thus: eta_ji = (n_i / n_j) * eta_ij
    """
    eta_ij = clf_plate_to_acoustic(plate, cavity, frequency)
    n_i = plate.get_modal_density(frequency)
    n_j = cavity.get_modal_density(frequency)
    
    # Avoid division by zero if modal density is somehow zero
    if n_j <= 0.0:
        return 0.0
        
    clf = (n_i / n_j) * eta_ij
    return clf
