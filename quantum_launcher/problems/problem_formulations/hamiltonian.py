# from .launcher import QiskitProblem
from quantum_launcher.base import formatter
import quantum_launcher.hampy as hampy
import numpy as np
from qiskit.quantum_info import SparsePauliOp
from qiskit import QuantumCircuit
import quantum_launcher.problems.problem_initialization as problems


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


@formatter(problems.EC, 'hamiltonian')
class ECQiskit:
    def __call__(self, problem: problems.EC) -> SparsePauliOp:
        """ generating hamiltonian"""
        elements = set().union(*problem.instance)
        onehots = []
        for ele in elements:
            ohs = set()
            for i, subset in enumerate(problem.instance):
                if ele in subset:
                    ohs.add(i)
            onehots.append(ohs)
        hamiltonian = None
        for ohs in onehots:
            if problem.onehot == 'exact':
                part = hampy.Ham_not(hampy.H_one_in_n(
                    list(ohs), size=len(problem.instance)))
            elif problem.onehot == 'quadratic':
                part = hampy.quadratic_onehot(list(ohs), len(problem.instance))

            if hamiltonian is None:
                hamiltonian = part
            else:
                hamiltonian += part
        return hamiltonian.simplify()

    def get_mixer_hamiltonian(self, problem: problems.EC, amount_of_rings=None):
        """ generates mixer hamiltonian """
        def get_main_set():
            main_set = []
            for element_set in problem.instance:
                for elem in element_set:
                    if elem not in main_set:
                        main_set.append(elem)
            return main_set

        def get_constraints():
            constraints, main_set = [], get_main_set()
            for element in main_set:
                element_set = set()
                for index, _ in enumerate(problem.instance):
                    if element in problem.instance[index]:
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
                sp = SparsePauliOp.from_sparse_list(
                    sparse_list, len(problem.instance))
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
                raise ValueError(
                    f"Too many rings. Maximum amount is {max_amount_of_rings}")
            elif amount_of_rings == 0:
                ring_qubits = []
            else:
                current_qubits = ring[0]
                for index in range(amount_of_rings):
                    user_rings.append(ring[index])
                    current_qubits = current_qubits.union(ring[index])
                ring_qubits = current_qubits
        x_gate.extend(id for id, _ in enumerate(
            problem.instance) if id not in ring_qubits)

        # connecting all parts of mixer hamiltonian together
        mix_ham = None
        for set_ in ring:
            if mix_ham is None:
                mix_ham = ring_ham(set_, len(problem.instance))
            else:
                mix_ham += ring_ham(set_, len(problem.instance))

        if mix_ham is None:
            mix_ham = x_gate_ham(x_gate)
        else:
            mix_ham += x_gate_ham(x_gate)

        return mix_ham


@formatter(problems.JSSP, 'hamiltonian')
def get_qiskit_hamiltonian(problem: problems.JSSP) -> SparsePauliOp:
    if problem.optimization_problem:
        return problem.h_o
    else:
        return problem.h_d


@formatter(problems.MaxCut, 'hamiltonian')
def get_qiskit_hamiltonian(problem: problems.MaxCut):
    ham = None
    n = problem.instance.number_of_nodes()
    for edge in problem.instance.edges():
        if ham is None:
            ham = hampy.Ham_not(hampy.H_one_in_n(edge, n))
        else:
            ham += hampy.Ham_not(hampy.H_one_in_n(edge, n))
    return ham.simplify()


@formatter(problems.QATM, 'hamiltonian')
class QATMQiskit:
    def __call__(self, problem: problems.QATM) -> SparsePauliOp:
        cm = problem.instance['cm']
        aircrafts = problem.instance['aircrafts']

        onehot_hamiltonian = None
        for plane, manouvers in aircrafts.groupby(by='aircraft'):
            if problem.onehot == 'exact':
                h = hampy.Ham_not(hampy.H_one_in_n(
                    manouvers.index.values.tolist(), len(cm)))
            elif problem.onehot == 'quadratic':
                h = hampy.quadratic_onehot(
                    manouvers.index.values.tolist(), len(cm))
            elif problem.onehot == 'xor':
                h = hampy.Ham_not(hampy.H_xor(
                    manouvers.index.values.tolist(), len(cm)))
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

        if problem.optimization_problem:
            goal_hamiltonian = None
            for i, (maneuver, ac) in problem.instance['aircrafts'].iterrows():
                if maneuver != ac:
                    h = hampy.H_x(i, len(aircrafts))
                    if goal_hamiltonian is None:
                        goal_hamiltonian = h
                    else:
                        goal_hamiltonian += h
            goal_hamiltonian /= sum(sum(cm))
            hamiltonian += goal_hamiltonian

        return hamiltonian.simplify()

    def get_mixer_hamiltonian(self, problem: problems.QATM) -> SparsePauliOp:
        cm = problem.instance['cm']
        aircrafts = problem.instance['aircrafts']

        mixer_hamiltonian = None
        for plane, manouvers in aircrafts.groupby(by='aircraft'):
            h = ring_ham(manouvers.index.values.tolist(), len(cm))
            if mixer_hamiltonian is None:
                mixer_hamiltonian = h
            else:
                mixer_hamiltonian += h
        return mixer_hamiltonian

    def get_QAOAAnsatz_initial_state(self, problem: problems.QATM) -> QuantumCircuit:
        aircrafts = problem.instance['aircrafts']
        qc = QuantumCircuit(len(aircrafts))
        for plane, manouvers in aircrafts.groupby(by='aircraft'):
            qc.x(manouvers.index.values.tolist()[0])
        return qc


@formatter(problems.Raw, 'hamiltonian')
def get_qiskit_hamiltonian(self) -> SparsePauliOp:
    return self.instance
