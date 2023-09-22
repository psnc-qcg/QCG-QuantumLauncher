""" Orca Launcher """

from orca_stuff.backend import OrcaBackend
from templates import QuantumLauncher


class OrcaLauncher(QuantumLauncher):
    """ Quantum Launcher for Orca """

    def run(self) -> dict:
        if self.backend is None:
            self.backend = OrcaBackend('orca')
        return self.algorithm.run(self.problem, self.backend)
