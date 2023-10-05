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

from job_shop_scheduler import get_jss_hamiltonian
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


class EC(Problem):
    """ Class for exact cover problem """

    def __init__(self, onehot: str) -> None:
        super().__init__()
        self.name = 'ec'
        self.onehot = onehot
        self._set_path()

    def set_instance(self, instance:list[set[int]], instance_name:str | None=None) -> None:
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

    def read_instance(self, instance_path:str) -> None:
        self.instance_name = instance_path.rsplit('/', 1)[1].split('.')[0]
        with open(instance_path, 'r', encoding='utf-8') as file:
            read_file = file.read()
        self.instance = ast.literal_eval(read_file)

    def _set_path(self) -> None:
        self.path = f'{self.name}/{self.instance_name}@{self.onehot}'

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
        line_obs = Observable(len(self.instance))
        elements = set().union(*self.instance)
        onehots = []
        for ele in elements:
            ohs = set()
            for i, subset in enumerate(self.instance):
                if ele in subset:
                    ohs.add(i)
            onehots.append(ohs)

        for ohs in onehots:
            if self.onehot == 'exact':
                oneh = None
                for elem1 in ohs:
                    obs1 = Observable(len(self.instance), pauli_terms=[Term(0.5, "I", [0]), Term(-0.5, "Z", [elem1])])
                    c = ohs.copy()
                    c.remove(elem1)
                    for elem2 in c: 
                        obs1 *= Observable(len(self.instance), pauli_terms=[Term(0.5, "I", [elem2]), Term(0.5, "Z", [elem2])])
                    oneh = obs1 if oneh is None else oneh + obs1
                obs3 = Observable(len(self.instance), pauli_terms=[Term(1, "I", [0])])
                part = obs3 - oneh
            elif self.onehot == 'quadratic':
                # part = hampy.quadratic_onehot(list(ohs), len(self.instance))
                part = None
                for elem in ohs:
                    if part is None:
                        part = Observable(len(self.instance), pauli_terms=[Term(0.5, "I", [0]), Term(-0.5, "Z", [elem])])
                    else:
                        part += Observable(len(self.instance), pauli_terms=[Term(0.5, "I", [0]), Term(-0.5, "Z", [elem])])
                part = Observable(len(self.instance), pauli_terms=[Term(1, "I", [0])]) - part
                part *= part
            line_obs += part
        return line_obs

class JSSP(Problem):
    """ Class for Job Shop Shedueling Problem """

    def __init__(self, max_time: int, onehot: str, optimization_problem: bool = False) -> None:
        super().__init__()
        self.name = 'jssp'
        self.max_time = max_time
        self.onehot = onehot
        self.optimization_problem = optimization_problem
        self.h_d, self.h_o, self.h_pos_by_label, self.h_label_by_pos = get_jss_hamiltonian(self.instance, max_time,
                                                                                           onehot)

        self.results = {'instance_name': self.instance_name,
                        'max_time': max_time,
                        'onehot': onehot,
                        'H_pos_by_label': self.h_pos_by_label,
                        'H_label_by_pos': self.h_label_by_pos}
        opt = 'optimization' if optimization_problem else 'decision'
        self.variant = opt
        self.opt = opt
        self._set_path()

    def set_instance(self, instance:dict[str, list[tuple[str, int]]],
                      instance_name:str | None= None) -> None:
        super().set_instance(instance, instance_name)
        self.results['instance_name'] = instance_name
        if instance is None:
            match instance_name:
                case 'toy':
                    self.instance = {"cupcakes": [("mixer", 2), ("oven", 1)],
                                    "smoothie": [("mixer", 1)],
                                    "lasagna": [("oven", 2)]}

    def read_instance(self, instance_path:str) -> None:
        self.instance_name = instance_path.rsplit('/',1)[1].split('.', 1)[0]     
        raw_instance = defaultdict(list)
        with open(instance_path, 'r', encoding='utf-8') as file_:
            file_.readline()
            for i, line in enumerate(file_):
                lint = list(map(int, line.split()))
                raw_instance[i + 1] = [x for x in
                                   zip(lint[::2],  # machines
                                       lint[1::2]  # operation lengths
                                       )]
        self.instance={k:[(m,1) if t<6 else (m,2) for m, t in v] for k, v in raw_instance.items()}

    def _set_path(self) -> None:
        self.path = f'{self.name}/{self.instance_name}@{self.max_time}@{self.opt}@{self.onehot}'

    def get_qiskit_hamiltonian(self, optimization_problem: bool = None) -> SparsePauliOp:
        if optimization_problem is None:
            optimization_problem = self.optimization_problem

        if optimization_problem:
            return self.h_o
        else:
            return self.h_d

class MaxCut(Problem):
    """ MacCut for Orca """

    def __init__(self) -> None:
        super().__init__()
        self.name = 'maxcut'
        self._set_path()

    def set_instance(self, instance:nx.Graph | None = None, instance_name:str | None=None) -> None:
        super().set_instance(instance, instance_name)
        if instance is None:
            match instance_name:
                case 'default':
                    self.instance = nx.Graph()
                    edge_list = [(0, 1), (0, 2), (0, 5), (1, 3), (1, 4), (2, 4), (2, 5), (3, 4), (3, 5)]
                    self.instance.add_edges_from(edge_list)

    def _set_path(self) -> None:
        self.path = f'{self.name}/{self.instance_name}'

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
        line_obs = Observable(self.instance.number_of_nodes())
        for i, j in self.instance.edges():
            # print(i,j)
            line_obs.add_term(Term(0.5, "ZZ", [i, j]))
        line_obs.add_term(Term(-0.5, 'I', [0]))
        return line_obs
