''' File with templates ? '''
import pickle
from os import makedirs, path
from pickle import load
from abc import ABC, abstractmethod
#from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
#from qiskit_ibm_runtime import QiskitRuntimeService, Session #, Sampler, Estimator
from qiskit_ibm_runtime import Sampler, Estimator
from qiskit_algorithms.optimizers import SPSA

class Backend(ABC):
    ''' Abstract class for backends '''

    @abstractmethod
    def __init__(self, name:str) -> None:
        self.name = name

    def get_estimator(self) -> Estimator:
        ''' returns backend's estimator '''
        return None

    def get_sampler(self) -> Sampler:
        ''' returns backend's sampler '''
        return None

    def get_optimizer(self):
        ''' returns backend's optimizer '''
        return SPSA()

class Problem(ABC):
    ''' Abstract class for Problems'''
    @abstractmethod
    def __init__(self) -> None:
        self.variant = 'Optimization'
        self.path_name = ''

    @abstractmethod
    def get_hamiltonian(self) -> SparsePauliOp:
        ''' Creates Hamiltonian for a problem '''

    def read_result(self, exp, log_path):
        ''' pickling files '''
        exp += exp
        with open(log_path, 'rb') as file:
            res = pickle.load(file)
        return res

class Algorithm(ABC):
    ''' Abstract class for Algorithms'''
    @abstractmethod
    def __init__(self) -> None:
        self.name: str = ''
        self.path_name: str = ''
        self.parameters = []

    @abstractmethod
    def run(self, hamiltonian:SparsePauliOp, backend:Backend):
        ''' Runs the hamiltonian on current algorithm '''

class QuantumLauncher():
    ''' Global Launcher problem'''

    def __init__(self, problem: Problem, algorithm: Algorithm, backend:Backend) -> None:
        self.problem: Problem = problem
        self.algorithm: Algorithm = algorithm
        self.backend: Backend = backend
        self.path = None
        self.res = {}
        self.dir = 'data/'
        self.res_path = None
        self.result_paths = []

    def run(self) -> dict:
        ''' runs problem on machine'''
        return self.algorithm.run(self.problem.get_hamiltonian(), self.backend)

    def get_path(self) -> str:
        ''' Outputs path of current output '''
        return self.path

    def set_dir(self, dir_path: str) -> None:
        ''' Setting output file directory path '''
        self.dir = dir_path

    def process(self, alg_options,
                save_to_file: bool = False) -> dict:
        ''' Runs and proccesses problem on algorithm '''
        results = self.run()
        energy = results['energy']
        variant = self.problem.variant
        results['variant'] = variant
        results['alg_options'] = alg_options
        results['backend_name'] = self.backend.name
        if save_to_file:
            self.res_path = self.dir + '/' + self.backend.name + '-' + \
                self.problem.path_name \
                + self.algorithm.path_name + '-' + str(energy) + '.pkl'
            self.result_paths.append(self.res_path)
            self.dir = path.dirname(self.res_path)
            if not path.exists(self.dir):
                makedirs(self.dir)
            with open(self.res_path, 'wb') as file:
                pickle.dump(results, file)
        self.res = {}
        self.res = results
        return results

def from_pickle(path_:str) -> dict:
    ''' reades pickle and returns as a dict '''
    with open(path_, 'rb') as file_:
        return load(file_)
