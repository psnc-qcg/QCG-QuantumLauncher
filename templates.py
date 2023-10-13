""" File with templates """
import pickle
from abc import ABC, abstractmethod
from os import makedirs, path
from qiskit.quantum_info import SparsePauliOp


class Backend(ABC):
    """ Abstract class for backends """

    @abstractmethod
    def __init__(self, name: str, parameters: list = None) -> None:
        self.name:str = name
        self._path:str | None = None
        self.parameters = parameters if parameters is not None else []

    @property
    def path(self) -> str:
        """ Backend's path """
        if self._path is not None:
            return self._path
        return self._get_path()

    @path.setter
    def path(self, new_path:str) -> None:
        self._path = new_path

    def _get_path(self) -> str:
        return f'{self.name}'



class Problem(ABC):
    """ Abstract class for Problems """

    @abstractmethod
    def __init__(self) -> None:
        self.variant:str = 'Optimization'
        self._path:str | None = None
        self.name:str = ''
        self.instance_name:str = 'unnamed'
        self.instance:any = None

    def set_instance(self, instance: any, instance_name: str | None = None):
        """ Sets an instance of problem """
        if instance_name is not None:
            self.instance_name = instance_name
        self.instance = instance

    def read_instance(self, instance_path:str) -> None:
        """ Reads an instance of problem from file """
        self.instance_name = instance_path.rsplit('/', 1)[1].split('.', 1)[0]
        with open(instance_path, 'rb') as file:
            self.instance = pickle.load(file)

    @property
    def path(self) -> str:
        """ Problem's path """
        if self._path is not None:
            return self._path
        return self._get_path()

    @path.setter
    def path(self, new_path:str|None):
        self._path = new_path

    @abstractmethod
    def _get_path(self) -> str:
        """ return's common path """
        return f'{self.name}/{self.instance_name}'


    def read_result(self, exp, log_path):
        """ pickling files """
        exp += exp
        with open(log_path, 'rb') as file:
            res = pickle.load(file)
        return res

    def get_qiskit_hamiltonian(self) -> SparsePauliOp:
        """ returns qiskit hamiltonian """
        raise NotImplementedError(f"Class {self.__class__.__name__} doesn't have implemented hamiltonian for qiskit yet")

    def get_atos_hamiltonian(self):
        """ returns atos hamiltonian """
        raise NotImplementedError(f"Class {self.__class__.__name__} doesn't have implemented hamiltonian for atos yet")

class Algorithm(ABC):
    """ Abstract class for Algorithms"""

    @abstractmethod
    def __init__(self) -> None:
        self.name: str = ''
        self._path: str | None = None
        self.parameters:list = []

    @property
    def path(self) -> str:
        """ Algorithm's path """
        if self._path is not None:
            return self._path
        return self._get_path()

    @path.setter
    def path(self, new_path:str|None):
        self._path = new_path

    @abstractmethod
    def _get_path(self) -> str:
        """ return's common path """

    @abstractmethod
    def run(self, problem: Problem, backend: Backend):
        """ Runs an algorithm on a specific problem using a backend """

    @abstractmethod
    def check_problem(self, problem: Problem) -> bool:
        """ Checks whether a problem implements a method required for the algorithm"""


class QuantumLauncher(ABC):
    """ Template for Quantum Launchers """

    def __init__(self, problem: Problem, algorithm: Algorithm, backend: Backend = None) -> None:
        self.problem: Problem = problem
        self.algorithm: Algorithm = algorithm
        self.backend = backend

        self.path = None
        self.res = {}
        self.dir = 'data/'
        self.res_path = None
        self.result_paths = []

    @property
    def get_path(self) -> str:
        """ Outputs path of current output """
        return self.path

    def set_dir(self, dir_path: str) -> None:
        """ Setting output file directory path """
        self.dir = dir_path

    @abstractmethod
    def run(self) -> dict:
        """ Run's algorithm """

    def process(self, alg_options,
                save_to_file: bool = False) -> dict:
        """ Run's and process'es the data """
        results = self.run()
        energy = results['energy']
        variant = self.problem.variant
        results['variant'] = variant
        results['alg_options'] = alg_options
        results['backend_name'] = self.backend.name
        if save_to_file:
            self.res_path = self.dir + '/' + self.problem.path + '-' + \
                            self.backend.path + '-' \
                            + self.algorithm.path + '-' + str(energy) + '.pkl'
            self.result_paths.append(self.res_path)
            self.dir = path.dirname(self.res_path)
            if not path.exists(self.dir):
                makedirs(self.dir)
            with open(self.res_path, 'wb') as file:
                pickle.dump(results, file)
        self.res = {}
        self.res = results
        return results
