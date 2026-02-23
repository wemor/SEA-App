import math
from abc import ABC, abstractmethod
from typing import Optional
from sea_app.core.material import Material
from sea_app.core import constants

class Subsystem(ABC):
    """
    Abstract base class for all SEA subsystems.
    """
    def __init__(self, name: str, loss_factor: float = 0.0):
        self.name = name
        # Total internal dissipation loss factor override, defaults to 0
        self.loss_factor = loss_factor

    @abstractmethod
    def get_mass(self) -> float:
        pass

    @abstractmethod
    def get_modal_density(self, frequency: float) -> float:
        """
        Calculate modal density (n) at a given center frequency (Hz).
        Typically given in modes/rad/sec or modes/Hz. We will standardize on modes/Hz.
        """
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"


class AcousticCavity(Subsystem):
    """
    Represents an acoustic volume (e.g., a room or a rocket fairing interior).
    """
    def __init__(self, name: str, volume: float, speed_of_sound: float = constants.SPEED_OF_SOUND_AIR, density: float = constants.DENSITY_AIR, loss_factor: float = 0.0):
        super().__init__(name, loss_factor)
        self.volume = volume # Volume V (m^3)
        self.speed_of_sound = speed_of_sound # c0 (m/s)
        self.density = density # rho0 (kg/m^3)
        self.surface_area = 0.0 # Approximate surface area for better modal density if given
        self.perimeter = 0.0 # Approximate total perimeter sum of all edges

    def get_mass(self) -> float:
        return self.volume * self.density

    def get_modal_density(self, frequency: float) -> float:
        """
        Calculates Acoustic Cavity Modal Density.
        From traditional acoustics (and assuming PDF Appendix H follows standard Weyl's formula):
        n(f) = (4 * pi * V * f^2) / c^3 + (pi * A * f) / (2 * c^2) + L / (8 * c)
        where f is frequency in Hz, V is volume, A is surface area, L is total edge length.
        For high frequencies, only the first term dominates:
        n(f) ~ (4 * pi * V * f^2) / c^3   (Modes/Hz)
        """
        c = self.speed_of_sound
        f = frequency
        # Simplified dominant term for High Frequency SEA
        n_f = (4.0 * math.pi * self.volume * f**2) / (c**3)
        
        # Add boundary corrections if area/perimeter are provided
        if self.surface_area > 0:
             n_f += (math.pi * self.surface_area * f) / (2.0 * c**2)
        if self.perimeter > 0:
             n_f += self.perimeter / (8.0 * c)
             
        return n_f

class HomogeneousPlate(Subsystem):
    """
    Represents a flat, thin, homogeneous rectangular plate.
    """
    def __init__(self, name: str, material: Material, length: float, width: float, thickness: float, loss_factor: Optional[float] = None):
        if loss_factor is None:
            loss_factor = material.loss_factor
        super().__init__(name, loss_factor)
        self.material = material
        self.length = length # L1 (m)
        self.width = width   # L2 (m)
        self.thickness = thickness # h (m)

    @property
    def area(self) -> float:
        return self.length * self.width

    @property
    def perimeter(self) -> float:
        return 2.0 * (self.length + self.width)

    def get_mass(self) -> float:
        return self.area * self.thickness * self.material.density

    @property
    def mass_per_area(self) -> float:
        """ m'' (kg/m^2) """
        return self.thickness * self.material.density

    @property
    def flexural_rigidity(self) -> float:
        """
        Calculate Flexural Rigidity (B).
        Eq (A-6) from PDF: B = (E * h^3) / (12 * (1 - v^2))
        """
        E = self.material.elastic_modulus
        h = self.thickness
        v = self.material.poisson_ratio
        return (E * h**3) / (12.0 * (1.0 - v**2))
        
    def bending_wave_speed(self, frequency: float) -> float:
        """
        Calculate Bending Wave Phase Speed (C_B).
        Eq (A-5) adapted to frequency. C_B depends on frequency!
        omega = 2 * pi * f
        C_B = sqrt(omega) * (B / m'')^(1/4)
        """
        omega = 2.0 * math.pi * frequency
        B = self.flexural_rigidity
        m_double_prime = self.mass_per_area
        return math.sqrt(omega) * ((B / m_double_prime)**0.25)

    @property
    def critical_frequency(self) -> float:
        """
        Calculate Critical Frequency (f_c).
        Eq (B-1) from PDF: f_c = (c0^2 / (2 * pi * h)) * sqrt( (12 * rho * (1 - v^2)) / E )
        (This is where bending wave speed equals speed of sound in air)
        """
        c0 = constants.SPEED_OF_SOUND_AIR
        rho = self.material.density
        v = self.material.poisson_ratio
        E = self.material.elastic_modulus
        h = self.thickness
        
        term1 = (c0**2) / (2.0 * math.pi * h)
        term2 = math.sqrt( (12.0 * rho * (1.0 - v**2)) / E )
        return term1 * term2

    def get_modal_density(self, frequency: float) -> float:
        """
        Calculate Structural Modal Density for a Homogeneous Plate (n).
        Often mode counts for thin plates are independent of frequency.
        From standard texts (approximating Appendix I):
        n(f) = (A / 2) * sqrt(m'' / B)   (Modes/Hz)
        Note: The actual equation from PDF Appendix I should be verified, but this is the standard thin plate formula.
        """
        A = self.area
        m_double_prime = self.mass_per_area
        B = self.flexural_rigidity
        return (A / 2.0) * math.sqrt(m_double_prime / B)

    def radiation_efficiency(self, frequency: float) -> float:
        """
        Calculate Radiation Efficiency (sigma_rad) for a Baffled Plate.
        Implements Eq (C-3) through (C-7) from PDF loosely (a simplified model for now).
        To do exact implementation of (C-2) to (C-7), we need more detailed conditional logic.
        """
        f_c = self.critical_frequency
        f = frequency
        
        # Simplified radiation efficiency model
        if f < f_c:
            # Below critical frequency, radiates poorly (monopole/dipole edge cancellation)
            # A rough high-frequency approximation for f < fc:
            ratio = f / f_c
            return (self.perimeter * constants.SPEED_OF_SOUND_AIR) / (math.pi**2 * self.area * f_c) * math.sqrt(ratio) / (1 - ratio)
        elif abs(f - f_c) < 0.1 * f_c:
             # At or near critical frequency, radiates very efficiently (coincidence)
             # Usually limits around 1.0 to 2.0 or higher depending on damping
             return 1.5 
        else:
            # Above critical frequency, radiates like a rigid piston
            return 1.0 / math.sqrt(1 - f_c / f)
