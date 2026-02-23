import math

class Material:
    """
    Represents a material and its physical properties required for SEA calculations.
    Calculates derived properties like shear modulus upon initialization.
    """
    def __init__(self, name: str, density: float, elastic_modulus: float, poisson_ratio: float, loss_factor: float = 0.0):
        """
        :param name: Identifier for the material (e.g., 'Aluminum 6061-T6')
        :param density: Mass density (rho) in kg/m^3
        :param elastic_modulus: Young's Modulus (E) in Pa (N/m^2)
        :param poisson_ratio: Poisson's ratio (v), dimensionless
        :param loss_factor: Internal dissipation loss factor (eta) of the material
        """
        self.name = name
        self.density = density
        self.elastic_modulus = elastic_modulus
        self.poisson_ratio = poisson_ratio
        self.loss_factor = loss_factor

    @property
    def shear_modulus(self) -> float:
        """
        Calculate Shear Modulus (G).
        Eq: G = E / (2 * (1 + v))
        Note: The PDF Appendix A lists G = E / (2+2v) which is mathematically identical.
        :return: Shear modulus in Pa
        """
        return self.elastic_modulus / (2.0 * (1.0 + self.poisson_ratio))

    @property
    def comp_wave_speed_plate(self) -> float:
        """
        Calculate Longitudinal (Compression) Wave Speed for a plate (C_L).
        Eq (A-2) from PDF: c_L = sqrt(E / (rho * (1 - v^2)))
        :return: Wave speed in m/s
        """
        return math.sqrt(self.elastic_modulus / (self.density * (1.0 - self.poisson_ratio**2)))

    @property
    def comp_wave_speed_beam(self) -> float:
        """
        Calculate Longitudinal Wave Speed for a beam (C_L).
        Eq (A-1) from PDF: c_L = sqrt(E / rho)
        :return: Wave speed in m/s
        """
        return math.sqrt(self.elastic_modulus / self.density)

    @property
    def shear_wave_speed(self) -> float:
        """
        Calculate Shear Wave Speed (C_S).
        Eq (A-3) from PDF: c_S = sqrt(G / rho)
        :return: Wave speed in m/s
        """
        return math.sqrt(self.shear_modulus / self.density)

    def __repr__(self):
        return f"Material(name='{self.name}', density={self.density})"

# Common engineering materials
Aluminum = Material(
    name="Aluminum",
    density=2700.0,
    elastic_modulus=70e9, # 70 GPa
    poisson_ratio=0.33,
    loss_factor=0.001
)

Steel = Material(
    name="Steel",
    density=7850.0,
    elastic_modulus=210e9, # 210 GPa
    poisson_ratio=0.30,
    loss_factor=0.001
)
