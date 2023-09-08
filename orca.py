''' Quantum Launcher for Orca '''
from ptseries.algorithms.binary_solvers import BinaryBosonicSolver
from qiskit.quantum_info import SparsePauliOp
import numpy as np
import networkx as nx
from templates import QuantumLauncher, Algorithm, Backend, Problem


class OrcaLauncher(QuantumLauncher):
    ''' Quantum Launcher for Orca '''
    def run(self) -> dict:
        return self.algorithm.run(self.problem.get_qubo, self.problem.Q)

class MaxCut(Problem):
    ''' MacCut for Orca '''
    def __init__(self) -> None:
        super().__init__()
        G = nx.Graph()

        edge_list = [(0,1), (0,2), (0,5), (1,3), (1,4), (2,4), (2,5), (3,4), (3, 5)]

        G.add_edges_from(edge_list)
        self.Q = np.zeros((6,6))
        for (i,j) in G.edges:
            self.Q[i,i] += -1
            self.Q[j,j] += -1
            self.Q[i,j] += 1
            self.Q[j,i] += 1

    def get_qubo(self, Q):
        ''' Returns Qubo function '''
        def qubo_fn(bin_vec):
            return np.dot(bin_vec, np.dot(Q, bin_vec))
        return qubo_fn

    def get_hamiltonian(self) -> SparsePauliOp:
        ...

class BinaryBosonic(Algorithm):
    ''' Orca Algorithm '''
    def __init__(self) -> None:
        super().__init__()
        self.bbs = None

    def run(self, qubo_fn_fact, Q, backend: Backend=None):
        self.bbs = BinaryBosonicSolver(6,
            qubo_fn_fact(Q)
        )
        self.bbs.train(
            learning_rate=1e-1,
            updates=80,
            print_frequency=20
            )

        return self.bbs.return_solution()

def main():
    ''' main '''
    pr = MaxCut()
    alg = BinaryBosonic()
    launcher = OrcaLauncher(pr, alg, None)
    print(launcher.run())


if __name__ == '__main__':
    main()
