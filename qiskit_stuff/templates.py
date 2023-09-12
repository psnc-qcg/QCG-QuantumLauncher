from abc import abstractmethod, ABC

# from qiskit import QuantumCircuit
from qiskit_algorithms.optimizers import SPSA
# from qiskit_ibm_runtime import QiskitRuntimeService, Session #, Sampler, Estimator
from qiskit_ibm_runtime import Sampler, Estimator

from templates import Algorithm, Problem


class PrimitiveStrategy(ABC):
    ''' Abstract class for primitive startegies '''

    @abstractmethod
    def __init__(self, name: str, parameters: list = None) -> None:
        self.name = name
        self.path_name = name
        self.parameters = parameters if parameters is not None else []

    def get_estimator(self) -> Estimator:
        ''' returns primitive strategy's estimator '''
        return None

    def get_sampler(self) -> Sampler:
        ''' returns primitive strategy's sampler '''
        return None

    def get_optimizer(self):
        ''' returns primitive strategy's optimizer '''
        return SPSA()


class HamiltonianAlgorithm(Algorithm):

    @abstractmethod
    def run(self, problem: Problem, primitive_strategy: PrimitiveStrategy):
        ''' Runs the hamiltonian on current algorithm '''

    def check_problem(self, problem: Problem) -> bool:
        ''' Check if the problem implements get_hamiltonian method'''
        return callable(getattr(problem, 'get_hamiltonian', False))

    def get_problem_data(self, problem: Problem):
        if self.check_problem(problem):
            return problem.get_hamiltonian()
        else:
            raise NotImplementedError('The problem does not have hamiltonian getter implemented')
