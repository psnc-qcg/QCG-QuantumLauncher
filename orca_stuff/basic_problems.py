""" Basic problems for Orca """
import numpy as np
from .orca_templates import OrcaStuff
from problems import MaxCut

class MaxCutOrca(MaxCut, OrcaStuff):
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
