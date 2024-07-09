""" Algorithms for Qiskit routines """
import json
from abc import ABC
from datetime import datetime

import numpy as np
from qiskit import qpy, QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.circuit.library import PauliEvolutionGate
# from qiskit.opflow import H
from qiskit.primitives.base.base_primitive import BasePrimitive
from qiskit.quantum_info import SparsePauliOp
from qiskit_algorithms.minimum_eigensolvers import QAOA as QiskitQAOA
from qiskit_algorithms.minimum_eigensolvers import SamplingVQEResult

from quantum_launcher.base import Problem, Algorithm
from .backend import QiskitBackend
from typing import Callable


class QiskitOptimizationAlgorithm(Algorithm):
    """ Abstract class for Qiskit optimization algorithms """

    def make_tag(self, problem: Problem, backend: QiskitBackend) -> str:
        tag = problem.path + '-' + \
            backend.path + '-' + \
            self.path + '-' + \
            datetime.today().strftime('%Y-%m-%d')
        return tag

    def get_processing_times(self, tag: str, primitive: BasePrimitive) -> None | tuple[list, list, int]:
        timestamps = []
        usages = []
        qpu_time = 0
        if hasattr(primitive, 'session'):
            jobs = primitive.session.service.jobs(limit=None, job_tags=[tag])
            for job in jobs:
                m = job.metrics()
                timestamps.append(m['timestamps'])
                usages.append(m['usage'])
                qpu_time += m['usage']['quantum_seconds']
        return timestamps, usages, qpu_time


def commutator(op_a: SparsePauliOp, op_b: SparsePauliOp) -> SparsePauliOp:
    """ Commutator """
    return op_a @ op_b - op_b @ op_a


class QAOA(QiskitOptimizationAlgorithm):
    """Algorithm class with QAOA.

    Args:
        p (int): The number of QAOA steps. Defaults to 1.
        alternating_ansatz (bool): Whether to use an alternating ansatz. Defaults to False. If True, it's recommended to provide a mixer_h to alg_kwargs.
        aux: Auxiliary input for the QAOA algorithm.
        **alg_kwargs: Additional keyword arguments for the base class.

    Attributes:
        name (str): The name of the algorithm.
        aux: Auxiliary input for the QAOA algorithm.
        p (int): The number of QAOA steps.
        alternating_ansatz (bool): Whether to use an alternating ansatz.
        parameters (list): List of parameters for the algorithm.
        mixer_h (SparsePauliOp | None): The mixer Hamiltonian.
        mixer_h (QuantumCircuit | None): The initial state of the circuit.

    """
    _algorithm_format = 'hamiltonian'

    def __init__(self, p: int = 1, alternating_ansatz: bool = False, aux=None, **alg_kwargs):
        super().__init__(**alg_kwargs)
        self.name: str = 'qaoa'
        self.aux = aux
        self.p: int = p
        self.alternating_ansatz: bool = alternating_ansatz
        self.parameters = ['p']
        self.mixer_h: SparsePauliOp | None = None
        self.initial_state: QuantumCircuit | None = None

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
                    res_dict = {**res_dict, **
                                json.loads(json.dumps({key: v}, default=repr))}
                elif str(ex) == 'Object of type ndarray is not JSON serializable':
                    res_dict = {**res_dict, **
                                json.loads(json.dumps({key: v}, default=repr))}
                elif str(ex) == 'keys must be str, int, float, bool or None, not ParameterVectorElement':
                    res_dict = {**res_dict, **
                                json.loads(json.dumps({key: repr(v)}))}
                elif str(ex) == 'Object of type OptimizerResult is not JSON serializable':
                    # recursion ftw
                    new_v = self.parse_samplingVQEResult(v, res_path)
                    res_dict = {**res_dict, **
                                json.loads(json.dumps({key: new_v}))}
                elif str(ex) == 'Object of type QuantumCircuit is not JSON serializable':
                    path = res_path + '.qpy'
                    with open(path, 'wb') as f:
                        qpy.dump(v, f)
                    res_dict = {**res_dict, **{key: path}}
        return res_dict

    def run(self, problem: Problem, backend: QiskitBackend, formatter=Callable) -> dict:
        """ Runs the QAOA algorithm """
        hamiltonian: SparsePauliOp = formatter(problem)
        energies = []

        def qaoa_callback(evaluation_count, params, mean, std):
            energies.append(mean)

        tag = self.make_tag(problem, backend)
        sampler = backend.sampler
        sampler.set_options(job_tags=[tag])
        optimizer = backend.optimizer

        if self.alternating_ansatz:
            if self.mixer_h is None:
                self.mixer_h = formatter.get_mixer_hamiltonian(problem)
            if self.initial_state is None:
                self.initial_state = formatter.get_QAOAAnsatz_initial_state(
                    problem)

        qaoa = QiskitQAOA(sampler, optimizer, reps=self.p, callback=qaoa_callback,
                          mixer=self.mixer_h, initial_state=self.initial_state, **self.alg_kwargs)
        qaoa_result = qaoa.compute_minimum_eigenvalue(hamiltonian, self.aux)
        depth = qaoa.ansatz.decompose(reps=10).depth()
        if 'cx' in qaoa.ansatz.decompose(reps=10).count_ops():
            cx_count = qaoa.ansatz.decompose(reps=10).count_ops()['cx']
        else:
            cx_count = 0
        timestamps, usages, qpu_time = self.get_processing_times(tag, sampler)
        result = {'energy': qaoa_result.eigenvalue,
                  'depth': depth,
                  'cx_count': cx_count,
                  'qpu_time': qpu_time,
                  'energies': energies,
                  'SamplingVQEResult': qaoa_result,
                  'usages': usages,
                  'timestamps': timestamps}
        return result

    def get_bitstring(self, result) -> str:
        return result['SamplingVQEResult'].best_measurement['bitstring']


class FALQON(QiskitOptimizationAlgorithm):
    """ 
    Algorithm class with FALQON.

    Args:
        driver_h (Optional[Operator]): The driver Hamiltonian for the problem.
        delta_t (float): The time step for the evolution operators.
        beta_0 (float): The initial value of beta.
        n (int): The number of iterations to run the algorithm.
        **alg_kwargs: Additional keyword arguments for the base class.

    Attributes:
        driver_h (Optional[Operator]): The driver Hamiltonian for the problem.
        delta_t (float): The time step for the evolution operators.
        beta_0 (float): The initial value of beta.
        n (int): The number of iterations to run the algorithm.
        cost_h (Optional[Operator]): The cost Hamiltonian for the problem.
        n_qubits (int): The number of qubits in the problem.
        parameters (List[str]): The list of algorithm parameters.

    """

    def __init__(self, driver_h=None, delta_t=0, beta_0=0, n=1):
        super().__init__()
        self.driver_h = driver_h
        self.delta_t = delta_t
        self.beta_0 = beta_0
        self.n = n
        self.cost_h = None
        self.n_qubits: int = 0
        self.parameters = ['n', 'delta_t', 'beta_0']
        raise NotImplementedError('FALQON is not implemented yet')

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
        """ Runs the FALQON algorithm """
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

        tag = self.make_tag(problem, backend)
        estimator = backend.estimator
        sampler = backend.sampler
        sampler.set_options(job_tags=[tag])
        estimator.set_options(job_tags=[tag])

        best_sample, last_sample = self._falqon_subroutine(estimator,
                                                           sampler, energies, betas, circuit_depths, cxs)

        timestamps, usages, qpu_time = self.get_processing_times(tag, sampler)
        result = {'betas': betas,
                  'energies': energies,
                  'depths': circuit_depths,
                  'cxs': cxs,
                  'n': self.n,
                  'delta_t': self.delta_t,
                  'beta_0': self.beta_0,
                  'energy': min(energies),
                  'qpu_time': qpu_time,
                  'best_sample': best_sample,
                  'last_sample': last_sample,
                  'usages': usages,
                  'timestamps': timestamps}

        return result

    def _build_ansatz(self, betas):
        """ building ansatz circuit """
        H = None  # TODO: implement H
        circ = (H ^ self.cost_h.num_qubits).to_circuit()
        params = ParameterVector("beta", length=len(betas))
        for param in params:
            circ.append(PauliEvolutionGate(
                self.cost_h, time=self.delta_t), circ.qubits)
            circ.append(PauliEvolutionGate(self.driver_h,
                        time=self.delta_t * param), circ.qubits)
        return circ

    def _falqon_subroutine(self, estimator,
                           sampler, energies, betas, circuit_depths, cxs):
        """ subroutine for falqon """
        for i in range(self.n):
            betas, energy, depth, cx_count = self._run_falqon(betas, estimator)
            print(i, energy)
            energies.append(energy)
            circuit_depths.append(depth)
            cxs.append(cx_count)
        argmin = np.argmin(np.asarray(energies))
        best_sample = self._sample_at(betas[:argmin], sampler)
        last_sample = self._sample_at(betas, sampler)
        return best_sample, last_sample

    def _run_falqon(self, betas, estimator):
        """ Method to run FALQON algorithm """
        ansatz = self._build_ansatz(betas)
        comm_h = complex(0, 1) * commutator(self.driver_h, self.cost_h)
        beta = -1 * estimator.run(ansatz, comm_h, betas).result().values[0]
        betas.append(beta)

        ansatz = self._build_ansatz(betas)
        energy = estimator.run(ansatz, self.cost_h, betas).result().values[0]

        depth = ansatz.decompose(reps=10).depth()
        if 'cx' in ansatz.decompose(reps=10).count_ops():
            cx_count = ansatz.decompose(reps=10).count_ops()['cx']
        else:
            cx_count = 0

        return betas, energy, depth, cx_count

    def _sample_at(self, betas, sampler):
        """ Not sure yet """
        ansatz = self._build_ansatz(betas)
        ansatz.measure_all()
        res = sampler.run(ansatz, betas).result()
        return res
