''' Orca Launcher '''

from atos_stuff.backend import AtosBackend
from templates import QuantumLauncher


class AtosLauncher(QuantumLauncher):
    ''' Quantum Launcher for Orca '''

    def run(self) -> dict:
        if self.backend is None:
            self.backend = AtosBackend('atos')
        return self.algorithm.run(self.problem, self.backend)
