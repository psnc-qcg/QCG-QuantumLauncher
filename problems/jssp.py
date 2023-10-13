""" Job Shop Sheduling Problem """
from collections import defaultdict
import os
from qiskit.quantum_info import SparsePauliOp
from jssp.qiskit_scheduler import get_jss_hamiltonian
from templates import Problem
from utils import ham_from_qiskit_to_atos

class JSSP(Problem):
    """ Ckass for Job Shop Shedueling Problem """

    def __init__(self, max_time: int, onehot: str, instance_name: str = '', instance_path: str = '',
                 optimization_problem: bool = False) -> None:
        super().__init__()
        self.name = 'jssp'
        self.max_time = max_time
        self.onehot = onehot
        self.optimization_problem = optimization_problem
        match instance_name:
            case 'toy':
                self.instance_name = instance_name
                self.instance = {"cupcakes": [("mixer", 2), ("oven", 1)],
                                 "smoothie": [("mixer", 1)],
                                 "lasagna": [("oven", 2)]}
            case _:
                self.instance_name = instance_name.split('.')[0]
                raw_instance = self.read_instance(os.path.join(instance_path, instance_name))
                self.instance = {k: [(m, 1) if t < 6 else (m, 2) for m, t in v] for k, v in raw_instance.items()}

        self.h_d, self.h_o, self.h_pos_by_label, self.h_label_by_pos = get_jss_hamiltonian(self.instance, max_time,
                                                                                           onehot)

        self.results = {'instance_name': instance_name,
                        'max_time': max_time,
                        'onehot': onehot,
                        'H_pos_by_label': self.h_pos_by_label,
                        'H_label_by_pos': self.h_label_by_pos}
        opt = 'optimization' if optimization_problem else 'decision'
        self.variant = opt
        self.opt = opt

    def _get_path(self) -> str:
        return f'{self.name}/{self.instance_name}@{self.max_time}@{self.opt}@{self.onehot}'

    def get_qiskit_hamiltonian(self, optimization_problem: bool = None) -> SparsePauliOp:
        if optimization_problem is None:
            optimization_problem = self.optimization_problem

        if optimization_problem:
            return self.h_o
        else:
            return self.h_d
        

    def get_atos_hamiltonian(self):
        return ham_from_qiskit_to_atos(self.get_qiskit_hamiltonian())

    def read_instance(self, path: str):
        """ Sth """
        job_dict = defaultdict(list)
        with open(path, 'r', encoding='utf-8') as file_:
            file_.readline()
            for i, line in enumerate(file_):
                lint = list(map(int, line.split()))
                job_dict[i + 1] = [x for x in
                                   zip(lint[::2],  # machines
                                       lint[1::2]  # operation lengths
                                       )]
        return job_dict

