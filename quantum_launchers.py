''' Quantum Launcher '''
import pickle

from backends import LocalBackend
from templates import QuantumLauncher, Backend


class QiskitLauncher(QuantumLauncher):
    ''' Global Launcher problem'''

    def run(self) -> dict:
        if self.backend is None:
            self.backend = LocalBackend()
        return self.algorithm.run(self.problem.get_hamiltonian(), self.backend)

    def set_backend(self, backend: Backend) -> None:
        self.backend = backend


class OrcaLauncher(QuantumLauncher):
    ''' Quantum Launcher for Orca '''

    def run(self) -> dict:
        return self.algorithm.run(self.problem.get_qubo())


def from_pickle(path_: str) -> dict:
    ''' reades pickle and returns as a dict '''
    with open(path_, 'rb') as file_:
        return pickle.load(file_)
