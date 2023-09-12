''' file with qiskit algorithms subclasses '''
from abc import abstractmethod

import numpy as np
from qiskit.circuit import ParameterVector
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.opflow import H
from qiskit.quantum_info import SparsePauliOp
from qiskit_algorithms import QAOA

from qiskit_stuff.backend import QiskitBackend
from templates import Problem, Algorithm


class HamiltonianAlgorithm(Algorithm):

    @abstractmethod
    def run(self, problem: Problem, backend: QiskitBackend):
        ''' Runs the hamiltonian on current algorithm '''

    def check_problem(self, problem: Problem) -> bool:
        ''' Check if the problem implements get_hamiltonian method'''
        return callable(getattr(problem, 'get_hamiltonian', False))

    def get_problem_data(self, problem: Problem):
        if self.check_problem(problem):
            return problem.get_hamiltonian()
        else:
            raise NotImplementedError('The problem does not have hamiltonian getter implemented')


def commutator(op_a: SparsePauliOp, op_b: SparsePauliOp) -> SparsePauliOp:
    ''' Commutator '''
    return op_a @ op_b - op_b @ op_a


class QAOA2(HamiltonianAlgorithm):
    ''' Algorithm class with QAOA '''

    def __init__(self, p: int = 1, aux=None):
        self.name = 'qaoa'
        self.path_name = f'{self.name}@{p}'
        self.aux = aux
        self.p: int = p
        self.parameters = ['p']

    def run(self, problem: Problem, backend: QiskitBackend) -> dict:
        ''' Runs the QAOA algorithm '''
        hamiltonian = self.get_problem_data(problem)
        energies = []

        def qaoa_callback(evaluation_count, params, mean, std):
            energies.append(mean)

        sampler = backend.get_primitive_strategy().get_sampler()
        optimizer = backend.get_primitive_strategy().get_optimizer()

        qaoa = QAOA(sampler, optimizer, reps=self.p, callback=qaoa_callback)
        qaoa_result = qaoa.compute_minimum_eigenvalue(hamiltonian, self.aux)
        depth = qaoa.ansatz.decompose(reps=10).depth()
        if 'cx' in qaoa.ansatz.decompose(reps=10).count_ops():
            cx_count = qaoa.ansatz.decompose(reps=10).count_ops()['cx']
        else:
            cx_count = 0
        result = {'qaoa_res': qaoa_result,
                  'energy': qaoa_result.eigenvalue,
                  'depth': depth,
                  'cx_count': cx_count,
                  'energies': energies}
        return result


class FALQON(HamiltonianAlgorithm):
    ''' Algorithm class with FALQON '''

    def __init__(self, driver_h=None, delta_t=0, beta_0=0, n=1):

        self.name = 'falqon'
        self.path_name = f'{self.name}@{n}@{delta_t}@{beta_0}'
        self.driver_h = driver_h
        self.delta_t = delta_t
        self.beta_0 = beta_0
        self.n = n
        self.cost_h = None
        self.n_qubits: int = 0
        self.parameters = ['n', 'delta_t', 'beta_0']

    def run(self, problem: Problem, backend: QiskitBackend):
        ''' run falqon '''
        # TODO implement aux operator
        hamiltonian = self.get_problem_data(problem)
        self.cost_h = hamiltonian
        self.n_qubits = hamiltonian.num_qubits
        if self.driver_h is None:
            self.driver_h = SparsePauliOp.from_sparse_list(
                [("X", [i], 1) for i in range(self.n_qubits)], num_qubits=self.n_qubits)

        betas = [self.beta_0]
        energies = []
        circuit_depths = []
        cxs = []

        estimator = backend.get_primitive_strategy().get_estimator()
        sampler = backend.get_primitive_strategy().get_sampler()

        best_sample, last_sample = self.falqon_subroutine(estimator,
                                                          sampler, energies, betas, circuit_depths, cxs)

        result = {'betas': betas,
                  'energies': energies,
                  'depths': circuit_depths,
                  'cxs': cxs,
                  'best_sample': best_sample,
                  'last_sample': last_sample,
                  'n': self.n,
                  'delta_t': self.delta_t,
                  'beta_0': self.beta_0,
                  'energy': min(energies)}

        return result

    def build_ansatz(self, betas):
        ''' building ansatz circuit '''
        circ = (H ^ self.cost_h.num_qubits).to_circuit()
        params = ParameterVector("beta", length=len(betas))
        for param in params:
            circ.append(PauliEvolutionGate(self.cost_h, time=self.delta_t), circ.qubits)
            circ.append(PauliEvolutionGate(self.driver_h, time=self.delta_t * param), circ.qubits)
        return circ

    def falqon_subroutine(self, estimator,
                          sampler, energies, betas, circuit_depths, cxs):
        ''' subroutine for falqon '''
        for i in range(self.n):
            betas, energy, depth, cx_count = self.run_falqon(betas, estimator)
            print(i, energy)
            energies.append(energy)
            circuit_depths.append(depth)
            cxs.append(cx_count)
        argmin = np.argmin(np.asarray(energies))
        best_sample = self.sample_at(betas[:argmin], sampler)
        last_sample = self.sample_at(betas, sampler)
        return best_sample, last_sample

    def run_falqon(self, betas, estimator):
        ''' Method to run FALQON algorithm '''
        ansatz = self.build_ansatz(betas)
        comm_h = complex(0, 1) * commutator(self.driver_h, self.cost_h)
        beta = -1 * estimator.run(ansatz, comm_h, betas).result().values[0]
        betas.append(beta)

        ansatz = self.build_ansatz(betas)
        energy = estimator.run(ansatz, self.cost_h, betas).result().values[0]

        depth = ansatz.decompose(reps=10).depth()
        if 'cx' in ansatz.decompose(reps=10).count_ops():
            cx_count = ansatz.decompose(reps=10).count_ops()['cx']
        else:
            cx_count = 0

        return betas, energy, depth, cx_count

    def sample_at(self, betas, sampler):
        ''' Not sure yet '''
        ansatz = self.build_ansatz(betas)
        ansatz.measure_all()
        res = sampler.run(ansatz, betas).result()
        return res
