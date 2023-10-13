""" Max Cut Problem """
import hampy
import numpy as np
import networkx as nx
from templates import Problem
from utils import ham_from_qiskit_to_atos

class MaxCut(Problem):
    """ MacCut for Orca """

    def __init__(self) -> None:
        super().__init__()
        self.name = 'maxcut'

    def set_instance(self, instance:nx.Graph | None = None, instance_name:str | None=None) -> None:
        super().set_instance(instance, instance_name)
        if instance is None:
            match instance_name:
                case 'default':
                    self.instance = nx.Graph()
                    edge_list = [(0, 1), (0, 2), (0, 5), (1, 3), (1, 4),
                                 (2, 4), (2, 5), (3, 4), (3, 5)]
                    self.instance.add_edges_from(edge_list)

    def _get_path(self) -> str:
        return f'{self.name}/{self.instance_name}'

    def get_qubo_fn(self, Q):
        def qubo_fn(bin_vec):
            return np.dot(bin_vec, np.dot(Q, bin_vec))

        return qubo_fn

    def get_orca_qubo(self):
        """ Returns Qubo function """
        Q = np.zeros((6, 6))
        for (i, j) in self.instance.edges:
            Q[i, i] += -1
            Q[j, j] += -1
            Q[i, j] += 1
            Q[j, i] += 1

        return self.get_qubo_fn, Q

    def get_qiskit_hamiltonian(self):
        ham = None
        n = self.instance.number_of_nodes()
        for edge in self.instance.edges():
            if ham is None:
                ham = hampy.Ham_not(hampy.H_one_in_n(edge, n))
            else:
                ham += hampy.Ham_not(hampy.H_one_in_n(edge, n))
        return ham.simplify()

    def get_atos_hamiltonian(self):
        return ham_from_qiskit_to_atos(self.get_qiskit_hamiltonian())
