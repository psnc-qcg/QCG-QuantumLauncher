''' Quantum Launcher '''
import pickle
from templates import QuantumLauncher

class QiskitLauncher(QuantumLauncher):
    ''' Global Launcher problem'''

    def run(self) -> dict:
        return self.algorithm.run(self.problem.get_hamiltonian(), self.backend)

def from_pickle(path_:str) -> dict:
    ''' reades pickle and returns as a dict '''
    with open(path_, 'rb') as file_:
        return pickle.load(file_)
