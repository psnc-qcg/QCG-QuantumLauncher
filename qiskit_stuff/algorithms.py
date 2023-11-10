""" file with qiskit algorithms subclasses """
import json
from abc import abstractmethod

import numpy as np
from qiskit import qpy
from qiskit.circuit import ParameterVector
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.opflow import H
from qiskit.quantum_info import SparsePauliOp
from qiskit_algorithms import QAOA
from qiskit_algorithms.minimum_eigensolvers import SamplingVQEResult
from qiskit_algorithms.optimizers import SciPyOptimizer

from templates import Problem, Algorithm
from .backend import QiskitBackend
from .qiskit_template import QiskitStuff


class QiskitHamiltonianAlgorithm(Algorithm, QiskitStuff):
    """ Abstract class for algorithms using Qiskit Hamiltonian (SparsePauliOp) objects """

    @abstractmethod
    def run(self, problem: Problem, backend: QiskitBackend):
        """ Runs the hamiltonian on current algorithm """


def commutator(op_a: SparsePauliOp, op_b: SparsePauliOp) -> SparsePauliOp:
    """ Commutator """
    return op_a @ op_b - op_b @ op_a


class QAOA2(QiskitHamiltonianAlgorithm):
    """ Algorithm class with QAOA """

    def __init__(self, p: int = 1, aux=None, **alg_kwargs):
        super().__init__(**alg_kwargs)
        self.name = 'qaoa'
        self.aux = aux
        self.p: int = p
        self.parameters = ['p']
        self.optimizer = None

    @property
    def setup(self) -> dict:
        return {
            'aux': self.aux,
            'p': self.p,
            'parameters': self.parameters,
            'arg_kwargs': self.alg_kwargs
        }

    def _get_path(self) -> str:
        return f'{self.name}@{self.p}'

    @property
    def optimizer(self) -> SciPyOptimizer:
        return self._optimizer

    @optimizer.setter
    def optimizer(self, optimizer: SciPyOptimizer) -> None:
        self._optimizer = optimizer

    def parse_samplingVQEResult(self, res: SamplingVQEResult, res_path) -> dict:
        res_dict = {}
        for k, v in vars(res).items():
            if k[0] == "_":
                key = k[1:]
            else:
                key = k
            try:
                res_dict = {**res_dict, **json.loads(json.dumps({key: v}))}
            except TypeError as ex:
                if str(ex) == 'Object of type complex128 is not JSON serializable':
                    res_dict = {**res_dict, **json.loads(json.dumps({key: v}, default=repr))}
                elif str(ex) == 'Object of type ndarray is not JSON serializable':
                    res_dict = {**res_dict, **json.loads(json.dumps({key: v}, default=repr))}
                elif str(ex) == 'keys must be str, int, float, bool or None, not ParameterVectorElement':
                    res_dict = {**res_dict, **json.loads(json.dumps({key: repr(v)}))}
                elif str(ex) == 'Object of type OptimizerResult is not JSON serializable':
                    # recursion ftw
                    new_v = self.parse_samplingVQEResult(v, res_path)
                    res_dict = {**res_dict, **json.loads(json.dumps({key: new_v}))}
                elif str(ex) == 'Object of type QuantumCircuit is not JSON serializable':
                    path = res_path + '.qpy'
                    with open(path, 'wb') as f:
                        qpy.dump(v, f)
                    res_dict = {**res_dict, **{key: path}}
        return res_dict

    def run(self, problem: Problem, backend: QiskitBackend) -> dict:
        """ Runs the QAOA algorithm """
        hamiltonian = problem.get_qiskit_hamiltonian()
        energies = []

        def qaoa_callback(evaluation_count, params, mean, std):
            energies.append(mean)

        sampler = backend.get_primitive_strategy().sampler
        if self.optimizer is None:
            self.optimizer = backend.get_primitive_strategy().optimizer

        qaoa = QAOA(sampler, self.optimizer, reps=self.p, callback=qaoa_callback, **self.alg_kwargs)
        qaoa_result = qaoa.compute_minimum_eigenvalue(hamiltonian, self.aux)
        depth = qaoa.ansatz.decompose(reps=10).depth()
        if 'cx' in qaoa.ansatz.decompose(reps=10).count_ops():
            cx_count = qaoa.ansatz.decompose(reps=10).count_ops()['cx']
        else:
            cx_count = 0
        result = {'SamplingVQEResult': qaoa_result,
                  'energy': qaoa_result.eigenvalue,
                  'depth': depth,
                  'cx_count': cx_count,
                  'energies': energies}
        return result


class FALQON(QiskitHamiltonianAlgorithm):
    """ Algorithm class with FALQON """

    def __init__(self, driver_h=None, delta_t=0, beta_0=0, n=1):
        super().__init__()
        self.driver_h = driver_h
        self.delta_t = delta_t
        self.beta_0 = beta_0
        self.n = n
        self.cost_h = None
        self.n_qubits: int = 0
        self.parameters = ['n', 'delta_t', 'beta_0']

    @property
    def setup(self) -> dict:
        return {
            'driver_h': self.driver_h,
            'delta_t': self.delta_t,
            'beta_0': self.beta_0,
            'n': self.n,
            'cost_h': self.cost_h,
            'n_qubits': self.n_qubits,
            'parameters': self.parameters,
            'arg_kwargs': self.alg_kwargs
        }

    def _get_path(self) -> str:
        return f'{self.name}@{self.n}@{self.delta_t}@{self.beta_0}'

    def run(self, problem: Problem, backend: QiskitBackend):
        # TODO implement aux operator
        hamiltonian = problem.get_qiskit_hamiltonian()
        self.cost_h = hamiltonian
        self.n_qubits = hamiltonian.num_qubits
        if self.driver_h is None:
            self.driver_h = SparsePauliOp.from_sparse_list(
                [("X", [i], 1) for i in range(self.n_qubits)], num_qubits=self.n_qubits)

        betas = [self.beta_0]
        energies = []
        circuit_depths = []
        cxs = []

        estimator = backend.get_primitive_strategy().estimator
        sampler = backend.get_primitive_strategy().sampler

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
        """ building ansatz circuit """
        circ = (H ^ self.cost_h.num_qubits).to_circuit()
        params = ParameterVector("beta", length=len(betas))
        for param in params:
            circ.append(PauliEvolutionGate(self.cost_h, time=self.delta_t), circ.qubits)
            circ.append(PauliEvolutionGate(self.driver_h, time=self.delta_t * param), circ.qubits)
        return circ

    def falqon_subroutine(self, estimator,
                          sampler, energies, betas, circuit_depths, cxs):
        """ subroutine for falqon """
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
        """ Method to run FALQON algorithm """
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
        """ Not sure yet """
        ansatz = self.build_ansatz(betas)
        ansatz.measure_all()
        res = sampler.run(ansatz, betas).result()
        return res
