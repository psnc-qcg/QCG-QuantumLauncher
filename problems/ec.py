""" Exact Cover Problem """
import ast
import hampy
from qat.core import Observable, Term
from qiskit.quantum_info import SparsePauliOp
from templates import Problem

class EC(Problem):
    """ Class for exact cover problem """

    def __init__(self, onehot: str) -> None:
        super().__init__()
        self.name = 'ec'
        self.onehot = onehot
        self._set_path()

    def set_instance(self, instance:list[set[int]] | None = None,
                    instance_name:str | None=None) -> None:
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

