"""
Physical constants used in Statistical Energy Analysis.
Values extracted from typical engineering references unless specified otherwise.
"""

# Acoustic properties of air at standard conditions (approx 20 C, 1 atm)
SPEED_OF_SOUND_AIR   = 343.0  # m/s (Co in the PDF)
DENSITY_AIR          = 1.21   # kg/m^3 (rho_0 in some texts)
CHARACTERISTIC_IMPEDANCE_AIR = SPEED_OF_SOUND_AIR * DENSITY_AIR # Rayls (Pa*s/m)
