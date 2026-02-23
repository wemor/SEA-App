import math
import numpy as np
from typing import List, Dict, Tuple
from sea_app.core.subsystem import Subsystem

class SEASystem:
    """
    Manages a collection of subsystems and solves for their energy levels (E_i)
    using the Statistical Energy Analysis power balance equations.
    """
    def __init__(self):
        self.subsystems: List[Subsystem] = []
        # Store coupling loss factors: clf_matrix[i][j] = eta_ij
        self.clf_matrix: Dict[Tuple[int, int], float] = {}
        # External power inputs: inputs[i] = Pi_in_i
        self.power_inputs: Dict[int, float] = {}
        
    def add_subsystem(self, subsystem: Subsystem) -> int:
        """
        Add a subsystem to the model.
        :return: The index of the added subsystem.
        """
        self.subsystems.append(subsystem)
        index = len(self.subsystems) - 1
        self.power_inputs[index] = 0.0 # Default to 0 input
        return index

    def set_coupling_loss_factor(self, i: int, j: int, clf: float):
        """
        Set the Coupling Loss Factor (eta_ij) from subsystem i to j.
        """
        self.clf_matrix[(i, j)] = clf

    def set_power_input(self, i: int, power: float):
        """
        Set the external power input (Pi_in_i) to subsystem i in Watts.
        """
        self.power_inputs[i] = power

    def solve(self, frequency: float) -> np.ndarray:
        """
        Solve the power balance equations for a given center frequency (Hz).
        Returns an array of energy levels (E_i) for each subsystem in Joules.
        
        The SEA linear system for energy E is:
        omega * [N] * {E} = {Pi_in}
        where [N] is the coupling matrix such that:
        N_ii = eta_i + sum(eta_ij for j != i)
        N_ij = -eta_ji   (note the index reversal)
        """
        omega = 2.0 * math.pi * frequency
        num_sys = len(self.subsystems)
        
        if num_sys == 0:
            return np.array([])
            
        N = np.zeros((num_sys, num_sys))
        P = np.zeros(num_sys)
        
        for i in range(num_sys):
            eta_i = self.subsystems[i].loss_factor
            
            # Diagonal term N_ii
            sum_eta_ij = 0.0
            for j in range(num_sys):
                if i != j:
                    sum_eta_ij += self.clf_matrix.get((i, j), 0.0)
            
            N[i, i] = eta_i + sum_eta_ij
            
            # Off-diagonal terms N_ij
            for j in range(num_sys):
                if i != j:
                    # Note from Eq 3 and 5 in PDF: N_ij element is -eta_ji
                    # Because moving E_j term to the left side makes it negative
                    eta_ji = self.clf_matrix.get((j, i), 0.0)
                    N[i, j] = -eta_ji
                    
            P[i] = self.power_inputs[i] / omega
            
        # Solve the linear system [N] * {E} = {P}
        # Using numpy's linear algebra solver
        try:
            E = np.linalg.solve(N, P)
        except np.linalg.LinAlgError as e:
            print(f"Error solving SEA matrix: {e}")
            E = np.zeros(num_sys)
            
        return E
