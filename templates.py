""" File with templates """
import pickle
from abc import ABC, abstractmethod
from os import makedirs, path


class Backend(ABC):
    """ Abstract class for backends """

    @abstractmethod
    def __init__(self, name: str, parameters: list = None) -> None:
        self.name = name
        self.path = name
        self.parameters = parameters if parameters is not None else []

    @abstractmethod
    def _set_path(self) -> None:
        self.path = f'{self.name}'


class Problem(ABC):
    """ Abstract class for Problems """

    @abstractmethod
    def __init__(self) -> None:
        self.variant = 'Optimization'
        self.path = ''
        self.name = ''
        self.instance_name = ''
        self.instance = None

    def set_instance(self, instance: any, instance_name: str | None = None):
        """ Sets an instance of problem """
        message= f"Setting instance for problem: {self.__class__.__name__}, hasn't been implemented"
        print(message)
        print("Forcing the instance, this method isn't safe")
        if instance_name is not None:
            self.instance_name = instance_name
        self.instance = instance

    @abstractmethod
    def _set_path(self) -> None:
        self.path = f'{self.name}/{self.instance_name}'

    def read_result(self, exp, log_path):
        """ pickling files """
        exp += exp
        with open(log_path, 'rb') as file:
            res = pickle.load(file)
        return res


class Algorithm(ABC):
    """ Abstract class for Algorithms"""

    @abstractmethod
    def __init__(self) -> None:
        self.name: str = ''
        self.path: str = ''
        self.parameters = []

    @abstractmethod
    def _set_path(self) -> None:
        self.path = f'{self.name}'

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
                            self.backend.name + '-' \
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
