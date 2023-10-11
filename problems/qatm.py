""" QATM Problem """
import os
import hampy
import numpy as np
import pandas as pd
from qiskit.quantum_info import SparsePauliOp
from templates import Problem

class QATM(Problem):
    """ class for QATM problem """

    def __init__(self, onehot: str, instance_name: str) -> None:
        super().__init__()
        self.name = 'qatm'
        self.onehot = onehot

        self.instance_name = instance_name.split('.')[0]
        self._set_path()

    def _set_path(self) -> None:
        self.path = f'{self.name}/{self.instance_name}'

    def read_instance(self, instance_path: str, instance_name: str) -> None:
        self.instance_name = instance_name.split('.', 1)[0]
        cm_path = os.path.join(instance_path, 'CM_' + instance_name)
        aircrafts_path = os.path.join(instance_path, 'aircrafts_' + instance_name)

        self.instance = np.loadtxt(cm_path), pd.read_csv(aircrafts_path, delimiter=' ', header=None)

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
