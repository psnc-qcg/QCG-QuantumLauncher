""" File with problem sub-classes """
import ast
import os
from collections import defaultdict

import hampy
import networkx as nx
import numpy as np
import pandas as pd
from qat.core import Observable, Term
from qiskit.quantum_info import SparsePauliOp

from jssp.qiskit_scheduler import get_jss_hamiltonian
from templates import Problem
from utils import ham_from_qiskit_to_atos


class QATM(Problem):
    """ class for QATM problem """

    def __init__(self, onehot: str, instance_name: str, instance_path: str = None) -> None:
        super().__init__()
        self.name = 'qatm'
        self.onehot = onehot

        self.instance_name = instance_name.split('.')[0]
        self.instance = self.read_instance(instance_name, instance_path)
        self._set_path()

    def _set_path(self) -> None:
        self.path = f'{self.name}/{self.instance_name}'

    def read_instance(self, instance_name: str, instance_path: str):
        """ reads instance of the problem """
        cm_path = os.path.join(instance_path, 'CM_' + instance_name)
        aircrafts_path = os.path.join(instance_path, 'aircrafts_' + instance_name)

        return np.loadtxt(cm_path), pd.read_csv(aircrafts_path, delimiter=' ', header=None)

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

    def get_atos_hamiltonian(self):
        return ham_from_qiskit_to_atos(self.get_qiskit_hamiltonian())


class EC(Problem):
    """ Class for exact cover problem """

    def __init__(self, onehot: str, instance_name: str, instance_path: str = None) -> None:
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
                self.instance = self.read_instance(instance_name,
                                                   instance_path)
                self.instance_name = instance_name.split('.')[0]
        self.onehot = onehot
        self._set_path()

    def _set_path(self) -> None:
        self.path = f'{self.name}/{self.instance_name}@{self.onehot}'

    def read_instance(self, instance_name: str, instance_path: str):
        path = os.path.join(instance_path, instance_name)
        with open(path, 'r', encoding='utf-8') as file:
            read_file = file.read()
        instance = ast.literal_eval(read_file)
        return instance

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
        self._set_path()

    def _set_path(self) -> None:
        self.path = f'{self.name}/{self.instance_name}@{self.max_time}@{self.opt}@{self.onehot}'

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


class MaxCut(Problem):
    """ MacCut for Orca """

    def _set_path(self) -> None:
        self.path = f'{self.name}/{self.instance_name}'

    def __init__(self, instance_name: str = '', instance_path: str = '') -> None:
        super().__init__()
        self.name = 'maxcut'
        self.G = nx.Graph()
        match instance_name:
            case 'default':
                self.instance_name = instance_name
                edge_list = [(0, 1), (0, 2), (0, 5), (1, 3), (1, 4), (2, 4), (2, 5), (3, 4), (3, 5)]
                self.G.add_edges_from(edge_list)

            case _:
                self.instance_name = instance_name.split('.')[0]
                raw_instance = self.read_instance(os.path.join(instance_path, instance_name))
        self._set_path()
        
    def read_instance(self, path: str):
        """ Reads the instance of the problem from path file """
        return None

    def get_qubo_fn(self, Q):
        def qubo_fn(bin_vec):
            return np.dot(bin_vec, np.dot(Q, bin_vec))

        return qubo_fn

    def get_orca_qubo(self):
        """ Returns Qubo function """
        Q = np.zeros((6, 6))
        for (i, j) in self.G.edges:
            Q[i, i] += -1
            Q[j, j] += -1
            Q[i, j] += 1
            Q[j, i] += 1

        return self.get_qubo_fn, Q

    def get_qiskit_hamiltonian(self):
        ham = None
        n = self.G.number_of_nodes()
        for edge in self.G.edges():
            if ham is None:
                ham = hampy.Ham_not(hampy.H_one_in_n(edge, n))
            else:
                ham += hampy.Ham_not(hampy.H_one_in_n(edge, n))
        return ham.simplify()

    def get_atos_hamiltonian(self):
        return ham_from_qiskit_to_atos(self.get_qiskit_hamiltonian())
