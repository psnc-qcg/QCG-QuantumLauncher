""" Exact Cover Problem """
import ast
import os
import hampy
from qiskit.quantum_info import SparsePauliOp
from templates import Problem
from utils import ham_from_qiskit_to_atos

class EC(Problem):
    """ Class for exact cover problem """

    def __init__(self, onehot: str, instance:any = None,
                 instance_name: str|None = None, instance_path: str = None) -> None:
        super().__init__(instance=instance, instance_name=instance_name,
                         instance_path=instance_path)
        self.name = 'ec'
        self.onehot = onehot

    def _get_path(self) -> str:
        return f'{self.name}/{self.instance_name}@{self.onehot}'

    def set_instance(self, instance: any, instance_name: str | None = None):
        super().set_instance(instance, instance_name)
        if instance is None:
            match instance_name:
                case 'micro':
                    self.instance = [{1, 2},
                                    {1}]
                case 'toy':
                    self.instance = [{1, 4, 7},
                                    {1, 4},
                                    {4, 5, 7},
                                    {3, 5, 6},
                                    {2, 3, 6, 7},
                                    {2, 7}]


    def read_instance(self, instance_path: str):
        with open(instance_path, 'r', encoding='utf-8') as file:
            read_file = file.read()
        self.instance = ast.literal_eval(read_file)

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
    

    def get_atos_hamiltonian(self):
        return ham_from_qiskit_to_atos(self.get_qiskit_hamiltonian())

