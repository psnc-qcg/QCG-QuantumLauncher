""" Qiskit Launcher """

from templates import QuantumLauncher


class QiskitLauncher(QuantumLauncher):
    """ Quantum Launcher for Qiskit """

    def run(self) -> dict:
        return self.algorithm.run(self.problem, self.backend)
