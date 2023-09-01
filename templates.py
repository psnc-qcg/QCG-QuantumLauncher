''' File with templates ? '''
import pickle
from os import makedirs, path
from pickle import load
from abc import ABC, abstractmethod
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit_ibm_runtime import QiskitRuntimeService, Session#, Sampler, Estimator

class Problem(ABC):
    ''' Abstract class for Problems'''
    @abstractmethod
    def __init__(self) -> None:
        self.variant = 'Optimization'
        self.path_name = ''

    @abstractmethod
    def get_hamiltonian(self) -> SparsePauliOp:
        ''' Creates Hamiltonian for a problem '''

    @abstractmethod
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
        self.name:str = ''
        self.path_name:str = ''

    @abstractmethod
    def run(self, hamiltonian:SparsePauliOp, backend_name:str, session=None):
        ''' Runs the hamiltonian on current algorithm '''

    @abstractmethod
    def create_circuit(self)->QuantumCircuit:
        ''' Generates circuit for certain problem '''

    @abstractmethod
    def solve_parameters(self)->list[complex]:
        ''' get good parameters '''
        parameters = []
        return parameters

class QuantumLauncher():
    ''' Global Launcher problem'''
    def __init__(self, problem: Problem, algorithm: Algorithm) -> None:
        self.problem:Problem = problem
        self.algorithm:Algorithm = algorithm
        self.path = None
        self.res = {}
        self.dir = 'data/'
        self.res_path = None
        self.result_paths = []

    def run(self, backend_name:str, session = None) -> tuple:
        ''' runs problem on machine'''
        return self.algorithm.run(self.problem.get_hamiltonian(), backend_name, session)

    def solve_problem(self, backend, shots:int=1):
        ''' Solving problem with algorithm TODO'''
        if backend == 'local_simulator':
            ...
        else:
            service = QiskitRuntimeService(channel="ibm_quantum")
            with Session(service=service, backend=backend) as session:
                self.run(backend, session)
        return ...

    def set_dir(self, dir_path:str) -> None:
        ''' Setting output file directory path '''
        self.dir = dir_path

    def process(self, alg_options,
                backend_name, session = None, save_to_file:bool = False) -> dict:
        ''' Runs and proccesses problem on algorithm '''
        values = self.run(backend_name, session)
        energy = 0
        results = {}
        for i, val in enumerate(values):
            match i:
                case 0:
                    results['alg_res'] = val
                case 1:
                    energy = val
                case 2:
                    results['depth'] = val
                case 3:
                    results['energies'] = val
        variant = self.problem.variant
        results['variant'] = variant
        results['alg_options'] = alg_options
        results['backend_name'] = backend_name
        if save_to_file:
            self.res_path = self.dir + '/' + self.problem.path_name \
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
