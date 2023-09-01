''' File with problem sub-classes '''
import os
from collections import defaultdict
import hampy
from qiskit.quantum_info import SparsePauliOp

from templates import Problem
from job_shop_scheduler import get_jss_hamiltonian

class EC(Problem):
    ''' Class for exact cover problem '''
    def __init__(self, onehot:str, instance_name:str, instance_path:str=None) -> None:
        super().__init__()
        self.name = 'ec'
        self.onehot = onehot
        match instance_name:
            case 'micro':
                self.instance = [{1, 2},
                        {1}]
                self.instance_name = instance_name
            case 'toy':
                self.instance = [{1, 4, 7},
                        {1, 4},
                        {4, 5, 7},
                        {3, 5, 6},
                        {2, 3, 6, 7},
                        {2, 7}]
                self.instance_name = instance_name
            case _:
                raise ValueError('Instance_name not found, path not supported yet')
                self.instance_name = instance_path.split('.')[0]
        self.path_name = f'{self.name}/{instance_name}-{onehot}'

    def get_hamiltonian(self) -> SparsePauliOp:
        ''' generating hamiltonian'''
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
                part = hampy.H_one_in_n(list(ohs), size=len(self.instance))
            elif self.onehot == 'quadratic':
                part = hampy.H_one_in_n(list(ohs), size=len(self.instance))

            if hamiltonian is None:
                hamiltonian = part
            else:
                hamiltonian = hamiltonian.compose(part)
        return hampy.Ham_not(hamiltonian).simplify()

class JSSP(Problem):
    ''' Ckass for Job Shop Shedueling Problem '''
    def __init__(self, max_time:int, onehot:str, instance_name:str='', instance_path:str='',
                optimization_problem:bool = False) -> None:
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
                self.instance_name = instance_path.split('.')[0]
                raw_instance = self.read_instance(os.path.join(instance_path, instance_name))
                self.instance = {k: [(m, 1) if t < 6 else (m, 2) for m, t in v] for k, v in raw_instance.items()}

        self.h_d, self.h_o, self.h_pos_by_label, self.h_label_by_pos = get_jss_hamiltonian(self.instance, max_time, onehot)

        self.results = {'instance_name': instance_name,
            'max_time': max_time,
            'onehot': onehot,
            'H_pos_by_label': self.h_pos_by_label,
            'H_label_by_pos': self.h_label_by_pos}
        opt = 'optimization' if optimization_problem else 'decision'
        self.variant = opt
        self.path_name = f'{self.name}/{self.instance_name}-{max_time}-{opt}-{onehot}-'

    def get_hamiltonian(self, optimization_problem:bool = None) -> SparsePauliOp:
        if optimization_problem is None:
            optimization_problem = self.optimization_problem

        if optimization_problem:
            return self.h_o
        else:
            return self.h_d

    def read_instance(self, path:str):
        ''' Sth '''
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
