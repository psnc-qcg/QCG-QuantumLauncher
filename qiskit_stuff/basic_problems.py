# from .launcher import QiskitProblem
import hampy
import numpy as np
from qiskit.quantum_info import SparsePauliOp

import problems
from .qiskit_template import QiskitStuff


class ECQiskit(problems.EC, QiskitStuff):
    def get_qiskit_hamiltonian(self) -> SparsePauliOp:
        """ generating hamiltonian"""
        elements = set().union(*self.instance)
        onehots = []
        for ele in elements:
            ohs = set()
            for i, subset in enumerate(self.instance):
                if ele in subset:
                    ohs.add(i)
            onehots.append(ohs)
        hamiltonian = None
        for ohs in onehots:
            if self.onehot == 'exact':
                part = hampy.Ham_not(hampy.H_one_in_n(list(ohs), size=len(self.instance)))
            elif self.onehot == 'quadratic':
                part = hampy.quadratic_onehot(list(ohs), len(self.instance))

            if hamiltonian is None:
                hamiltonian = part
            else:
                hamiltonian += part
        return hamiltonian.simplify()


class JSSPQiskit(problems.JSSP, QiskitStuff):
    def get_qiskit_hamiltonian(self, optimization_problem: bool = None) -> SparsePauliOp:
        if optimization_problem is None:
            optimization_problem = self.optimization_problem

        if optimization_problem:
            return self.h_o
        else:
            return self.h_d


class MaxCutQiskit(problems.MaxCut, QiskitStuff):
    def get_qiskit_hamiltonian(self):
        ham = None
        n = self.instance.number_of_nodes()
        for edge in self.instance.edges():
            if ham is None:
                ham = hampy.Ham_not(hampy.H_one_in_n(edge, n))
            else:
                ham += hampy.Ham_not(hampy.H_one_in_n(edge, n))
        return ham.simplify()


class QATMQiskit(problems.QATM, QiskitStuff):
    def get_qiskit_hamiltonian(self) -> SparsePauliOp:
        cm, planes = self.instance

        onehot_hamiltonian = None
        for plane, manouvers in planes.groupby(by=1):
            if self.onehot == 'exact':
                h = hampy.Ham_not(hampy.H_one_in_n(manouvers.index.values.tolist(), len(cm)))
            elif self.onehot == 'quadratic':
                h = hampy.quadratic_onehot(manouvers.index.values.tolist(), len(cm))
            if onehot_hamiltonian is not None:
                onehot_hamiltonian += h
            else:
                onehot_hamiltonian = h

        triu = np.triu(cm, k=1)
        conflict_hamiltonian = None
        for p1, p2 in zip(*np.where(triu == 1)):
            if conflict_hamiltonian is not None:
                conflict_hamiltonian += hampy.H_and([p1, p2], len(cm))
            else:
                conflict_hamiltonian = hampy.H_and([p1, p2], len(cm))

        hamiltonian = onehot_hamiltonian + conflict_hamiltonian
        return hamiltonian.simplify()
