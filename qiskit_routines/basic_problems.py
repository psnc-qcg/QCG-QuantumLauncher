# from .launcher import QiskitProblem
import hampy
import numpy as np
from qiskit.quantum_info import SparsePauliOp
from qiskit import QuantumCircuit

import problems
from .qiskit_template import QiskitRoutine



def ring_ham(ring: set, n):
    total = None
    ring = list(ring)
    for index in range(len(ring) - 1):
        sparse_list = []
        sparse_list.append((("XX", [ring[index], ring[index + 1]], 1)))
        sparse_list.append((("YY", [ring[index], ring[index + 1]], 1)))
        sp = SparsePauliOp.from_sparse_list(sparse_list, n)
        if total is None:
            total = sp
        else:
            total += sp
    sparse_list = []
    sparse_list.append((("XX", [ring[-1], ring[0]], 1)))
    sparse_list.append((("YY", [ring[-1], ring[0]], 1)))
    sp = SparsePauliOp.from_sparse_list(sparse_list, n)
    total += sp
    return SparsePauliOp(total)

class ECQiskit(problems.EC, QiskitRoutine):
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

    def get_mixer_hamiltonian(self, amount_of_rings = None):
        """ generates mixer hamiltonian """
        def get_main_set():
            main_set = []
            for element_set in self.instance:
                for elem in element_set:
                    if elem not in main_set:
                        main_set.append(elem)
            return main_set

        def get_constraints():
            constraints, main_set = [], get_main_set()
            for element in main_set:
                element_set = set()
                for index, _ in enumerate(self.instance):
                    if element in self.instance[index]:
                        element_set.add(index)
                if len(element_set) > 0 and element_set not in constraints:
                    constraints.append(element_set)

            return constraints

        # creating mixer hamiltonians for all qubits that aren't in rings (in other words applying X gate to them)
        def x_gate_ham(x_gate: list):
            total = None
            for elem in x_gate:
                sparse_list = []
                sparse_list.append((("X", [elem], 1)))
                sp = SparsePauliOp.from_sparse_list(sparse_list, len(self.instance))
                if total is None:
                    total = sp
                else:
                    total += sp
            return SparsePauliOp(total)

        # looking for all rings in a data and creating a list with them
        ring, x_gate, constraints = [], [], get_constraints()
        
        ring.append(max(constraints, key=len))

        ring_qubits = set.union(*ring)

        for set_ in constraints:
            if len(set_.intersection(ring_qubits)) == 0:
                ring.append(set_)
                ring_qubits.update(set_)

        if amount_of_rings is not None:
            max_amount_of_rings, user_rings = len(ring), []
            if amount_of_rings > max_amount_of_rings:
                raise ValueError(f"Too many rings. Maximum amount is {max_amount_of_rings}")
            elif amount_of_rings == 0:
                ring_qubits = []
            else:
                current_qubits = ring[0]
                for index in range(amount_of_rings):
                    user_rings.append(ring[index])
                    current_qubits = current_qubits.union(ring[index])
                ring_qubits = current_qubits
        x_gate.extend(id for id, _ in enumerate(self.instance) if id not in ring_qubits)

        # connecting all parts of mixer hamiltonian together
        mix_ham = None
        for set_ in ring:
            if mix_ham is None:
                mix_ham = ring_ham(set_, len(self.instance))
            else:
                mix_ham += ring_ham(set_, len(self.instance))

        if mix_ham is None:
            mix_ham = x_gate_ham(x_gate)
        else:
            mix_ham += x_gate_ham(x_gate)

        return mix_ham


class JSSPQiskit(problems.JSSP, QiskitRoutine):
    def get_qiskit_hamiltonian(self) -> SparsePauliOp:
        if self.optimization_problem:
            return self.h_o
        else:
            return self.h_d


class MaxCutQiskit(problems.MaxCut, QiskitRoutine):
    def get_qiskit_hamiltonian(self):
        ham = None
        n = self.instance.number_of_nodes()
        for edge in self.instance.edges():
            if ham is None:
                ham = hampy.Ham_not(hampy.H_one_in_n(edge, n))
            else:
                ham += hampy.Ham_not(hampy.H_one_in_n(edge, n))
        return ham.simplify()


class QATMQiskit(problems.QATM, QiskitRoutine):
    def get_qiskit_hamiltonian(self) -> SparsePauliOp:
        cm = self.instance['cm']
        aircrafts = self.instance['aircrafts']

        onehot_hamiltonian = None
        for plane, manouvers in aircrafts.groupby(by='aircraft'):
            if self.onehot == 'exact':
                h = hampy.Ham_not(hampy.H_one_in_n(manouvers.index.values.tolist(), len(cm)))
            elif self.onehot == 'quadratic':
                h = hampy.quadratic_onehot(manouvers.index.values.tolist(), len(cm))
            elif self.onehot == 'xor':
                h = hampy.Ham_not(hampy.H_xor(manouvers.index.values.tolist(), len(cm)))
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

        if self.optimization_problem:
            goal_hamiltonian = None
            for i, (maneuver, ac) in self.instance['aircrafts'].iterrows():
                if maneuver != ac:
                    h = hampy.H_x(i, len(aircrafts))
                    if goal_hamiltonian is None:
                        goal_hamiltonian = h
                    else:
                        goal_hamiltonian += h
            goal_hamiltonian /= sum(sum(cm))
            hamiltonian += goal_hamiltonian

        return hamiltonian.simplify()

    def get_mixer_hamiltonian(self) -> SparsePauliOp:
        cm = self.instance['cm']
        aircrafts = self.instance['aircrafts']

        mixer_hamiltonian = None
        for plane, manouvers in aircrafts.groupby(by='aircraft'):
            h = ring_ham(manouvers.index.values.tolist(), len(cm))
            if mixer_hamiltonian is None:
                mixer_hamiltonian = h
            else:
                mixer_hamiltonian += h
        return mixer_hamiltonian

    def get_QAOAAnsatz_initial_state(self) -> QuantumCircuit:
        aircrafts = self.instance['aircrafts']
        qc = QuantumCircuit(len(aircrafts))
        for plane, manouvers in aircrafts.groupby(by='aircraft'):
            qc.x(manouvers.index.values.tolist()[0])
        return qc

