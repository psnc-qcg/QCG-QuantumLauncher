""" File with templates """
import json
import os
import pickle
from abc import ABC, abstractmethod


class _FileSavingSupportClass:
    """
    A helper class for saving results to different file formats.
    Class created to avoid huge chunk of code in QuantumLauncher.

    Attributes:
        algorithm: The algorithm object.
        _res_path: The path to the results directory.
        _full_path: The full path to the results file.
        res: The results to be saved.

    Methods:
        fix_json: Fixes the JSON representation of an object.
        _save_results_pickle: Saves the results as a pickle file.
        _save_results_txt: Saves the results as a text file.
        _save_results_csv: Saves the results as a CSV file.
        _save_results_json: Saves the results as a JSON file.
        _save_results: Saves the results to specified file formats.
    """

    def __init__(self) -> None:
        self.algorithm = None
        self._res_path = None
        self._full_path = None
        self.res = None

    def fix_json(self, o: object):
        if o.__class__.__name__ == 'SamplingVQEResult':
            parsed = self.algorithm.parse_samplingVQEResult(o, self._full_path)
            return parsed
        elif o.__class__.__name__ == 'complex128':
            return repr(o)
        else:
            print(
                f'Name of object {o.__class__} not known, returning None as a json encodable')
            return None

    def _save_results_pickle(self, results: dict, file_name: str) -> None:
        with open(file_name, mode='wb') as file:
            pickle.dump(results, file)

    def _save_results_txt(self, results: dict, file_name: str) -> None:
        with open(file_name, mode='w', encoding='utf-8') as file:
            file.write(results.__str__())

    def _save_results_csv(self, results: dict, file_name: str) -> None:
        print(
            f'\033[93mSaving to csv has not been implemented yet {results= }{file_name= }\033[0m')

    def _save_results_json(self, results: dict, file_name: str) -> None:
        with open(file_name, mode='w', encoding='utf-8') as file:
            json.dump(results, file, default=self.fix_json, indent=4)

    def _save_results(self, path_pickle: str | None = None, path_txt: str | None = None,
                      path_csv: str | None = None, path_json: str | None = None) -> None:
        dir = os.path.dirname(self._full_path)
        if not os.path.exists(dir) and (path_pickle is True or path_txt is True
                                        or path_json is True or path_csv is True):
            os.makedirs(dir)
        if path_pickle:
            if path_pickle is True:
                path_pickle = self._full_path + '.pkl'
            self._save_results_pickle(self.res, path_pickle)
        if path_txt:
            if path_txt is True:
                path_txt = self._full_path + '.txt'
            self._save_results_txt(self.res, path_txt)
        if path_csv:
            if path_csv is True:
                path_csv = self._full_path + '.csv'
            self._save_results_csv(self.res, path_csv)
        if path_json:
            if path_json is True:
                path_json = self._full_path + '.json'
            self._save_results_json(self.res, path_json)


class _SupportClass(ABC):
    """Abstract base class for methods necessary for other classes in this module."""

    @property
    def setup(self) -> dict:
        """Returns a dictionary with class instance parameters."""
        return f'setup for {self.__class__.__name__} has not been implemented yet'

    @property
    def path(self) -> str:
        """Returns the path to the file."""
        if self._path is not None:
            return self._path
        return self._get_path()

    @path.setter
    def path(self, new_path: str | None) -> None:
        self._path = new_path

    @abstractmethod
    def _get_path(self):
        """Returns common path to the file."""


class Backend(_SupportClass, ABC):
    """
    Abstract class representing a backend for quantum computing.

    Attributes:
        name (str): The name of the backend.
        path (str | None): The path to the backend (optional).
        parameters (list): A list of parameters for the backend (optional).

    Methods:
        _get_path(): Returns the path to the backend.

    """

    @abstractmethod
    def __init__(self, name: str, parameters: list = None) -> None:
        self.name: str = name
        self.path: str | None = None
        self.parameters = parameters if parameters is not None else []

    def _get_path(self):
        return f'{self.name}'


class Problem(_SupportClass, ABC):
    """
    Abstract class for defining Problems.

    Attributes:
        variant (str): The variant of the problem. The default variant is "Optimization".
        path (str | None): The path to the problem.
        name (str): The name of the problem.
        instance_name (str): The name of the instance.
        instance (any): An instance of the problem.

    Methods:
        set_instance(self, instance: any, instance_name: str | None = None) -> None:
            Sets the instance of the problem.
        read_instance(self, instance_path: str) -> None:
            Reads the instance of the problem from a file.
        read_result(self, exp, log_path) -> any:
            Reads a result from a file.
        analyze_result(self, result) -> None:
            Analyzes the result.

    """
    @abstractmethod
    def __init__(self, instance: any = None, instance_name: str | None = None, instance_path: str | None = None) -> None:
        """
        Initializes a Problem instance.

        Args:
            instance (any): An instance of the problem.
            instance_name (str | None): The name of the instance.
            instance_path (str | None): The path to the instance file.

        Returns:
            None
        """
        self.variant: str = 'Optimization'
        self.path: str | None = None
        self.name = type(self).__name__.lower()
        self.instance_name: str = 'unnamed' if instance_name is None else instance_name
        self.instance: any = None
        if instance_path is None:
            self.set_instance(instance=instance, instance_name=instance_name)
        else:
            self.read_instance(instance_path)

    def set_instance(self, instance: any, instance_name: str | None = None) -> None:
        """
        Sets an instance of the problem.

        Args:
            instance (any): An instance of the problem.
            instance_name (str | None): The name of the instance.

        Returns:
            None
        """
        if instance_name is not None:
            self.instance_name = instance_name
        self.instance = instance

    def read_instance(self, instance_path: str) -> None:
        """
        Reads an instance of the problem from a file.

        Args:
            instance_path (str): The path to the instance file.

        Returns:
            None
        """
        if self.instance_name is None:
            self.instance_name = instance_path.rsplit(
                '/', 1)[1].split('.', 1)[0]
        with open(instance_path, 'rb') as file:
            self.instance = pickle.load(file)

    @abstractmethod
    def _get_path(self) -> str:
        """
        Returns the common path.

        Returns:
            str: The common path.
        """
        return f'{self.name}/{self.instance_name}'

    def read_result(self, exp, log_path):
        """
        Reads a result from a file.

        Args:
            exp: The experiment.
            log_path: The path to the log file.

        Returns:
            The result.
        """
        exp += exp
        with open(log_path, 'rb') as file:
            res = pickle.load(file)
        return res

    def analyze_result(self, result):
        """
        Analyzes the result.

        Args:
            result: The result.

        """


class Algorithm(_SupportClass, ABC):
    """
    Abstract class for Algorithms.

    Attributes:
        name (str): The name of the algorithm, derived from the class name in lowercase.
        path (str | None): The path to the algorithm, if applicable.
        parameters (list): A list of parameters for the algorithm.
        alg_kwargs (dict): Additional keyword arguments for the algorithm.

    Abstract methods:
        __init__(self, **alg_kwargs): Initializes the Algorithm object.
        _get_path(self) -> str: Returns the common path for the algorithm.
        run(self, problem: Problem, backend: Backend): Runs the algorithm on a specific problem using a backend.
    """
    @abstractmethod
    def __init__(self, **alg_kwargs) -> None:
        self.name: str = self.__class__.__name__.lower()
        self.path: str | None = None
        self.parameters: list = []
        self.alg_kwargs = alg_kwargs

    @abstractmethod
    def _get_path(self) -> str:
        """Returns the common path for the algorithm."""

    def parse_result_to_json(self, o: object) -> dict:
        """Parses results so that they can be saved as a JSON file.

        Args:
            o (object): The result object to be parsed.

        Returns:
            dict: The parsed result as a dictionary.
        """
        print('Algorithm does not have the parse_result_to_json method implemented')
        return dict(o)

    @abstractmethod
    def run(self, problem: Problem, backend: Backend):
        """Runs the algorithm on a specific problem using a backend.

        Args:
            problem (Problem): The problem to be solved.
            backend (Backend): The backend to be used for execution.
        """


class QuantumLauncher(ABC, _FileSavingSupportClass):
    """
    Quantum Launcher class.

    Quantum launcher is used to run quantum algorithms on specific problem instances and backends.
    It provides methods for binding parameters, preparing the problem, running the algorithm, and processing the results.

    Attributes:
        problem (Problem): The problem instance to be solved.
        algorithm (Algorithm): The quantum algorithm to be executed.
        backend (Backend, optional): The backend to be used for execution. Defaults to None.
        path (str): The path to save the results. Defaults to 'results/'.
        binding_params (dict or None): The parameters to be bound to the problem and algorithm. Defaults to None.

    Methods:
        _bind_parameters: Binds the specified parameters to the problem and algorithm.
        _prepare_problem: Chooses a problem and binds parameters.
        _run: Runs the algorithm on the problem.
        process: Runs the algorithm, processes the results, and saves them if specified.


        Example of usage:
            from templates import QuantumLauncher
            from problems import MaxCut
            from qiskit_routines import QAOA, QiskitBackend

            problem = MaxCut(instance_name='default')
            algorithm = QAOA()
            backend = QiskitBackend('local_simulator')

            launcher = QuantumLauncher(problem, algorithm, backend)
            result = launcher.process(save_pickle=True)
            print(result)

    """

    def __init__(self, problem: Problem, algorithm: Algorithm, backend: Backend = None,
                 path: str = 'results/', binding_params: dict | None = None) -> None:
        super().__init__()
        self.problem: Problem = problem
        self.algorithm: Algorithm = algorithm
        self.backend: Backend = backend

        self.path: str = path
        self.res: dict = {}
        self._res_path: str | None = None
        self.binding_params: dict | None = binding_params

    def _bind_parameters(self):
        """
        Binds parameters to the problem and algorithm.
        """
        for param, value in self.binding_params.items():
            if param in self.problem.__class__.__dict__:
                self.problem.__dict__[param] = value
            elif param in self.algorithm.__dict__:
                self.algorithm.__dict__[param] = value
            else:
                print(f'\033[93mClass {self.problem.__class__.__name__} nor class \
{self.algorithm.__class__.__name__} does not have parameter {param}, so it cannot be bound\033[0m')

    def _prepare_problem(self):
        """
        Chooses a problem for current hardware taken from the algorithm and binds parameters.
        """
        problem_class = list(set(self.problem.__class__.__subclasses__()) &
                             set(self.algorithm.ROUTINE_CLASS.__subclasses__()))[0]
        self.problem.__class__ = problem_class
        if self.binding_params is not None:
            self._bind_parameters()

    def _run(self) -> dict:
        """
        Prepares the problem, and runs the algorithm on the problem.

        Returns:
            dict: The results of the algorithm execution.
        """
        self._prepare_problem()

        return self.algorithm.run(self.problem, self.backend)

    def process(self, save_to_file: bool = False,
                save_pickle: str | bool = False, save_txt: str | bool = False,
                save_csv: str | bool = False, save_json: str | bool = False) -> dict:
        """
        Runs the algorithm, processes the data, and saves the results if specified.

        Args:
            save_to_file (bool): Flag indicating whether to save the results to a file. Defaults to False.
            save_pickle (str or bool): Flag indicating whether to save the results as a pickle file.
                If a string is provided, it represents the path to save the pickle file. Defaults to False.
            save_txt (str or bool): Flag indicating whether to save the results as a text file.
                If a string is provided, it represents the path to save the text file. Defaults to False.
            save_csv (str or bool): Flag indicating whether to save the results as a CSV file.
                If a string is provided, it represents the path to save the CSV file. Defaults to False.
            save_json (str or bool): Flag indicating whether to save the results as a JSON file.
                If a string is provided, it represents the path to save the JSON file. Defaults to False.

        Returns:
            dict: The processed results.
        """
        results = self._run()
        energy = results['energy']

        self.res['problem_setup'] = self.problem.setup
        self.res['algorithm_setup'] = self.algorithm.setup
        self.res['algorithm_setup']['variant'] = self.problem.variant
        self.res['backend_setup'] = self.backend.setup
        self.res['results'] = results

        self._file_name = self.problem.path + '-' + \
            self.backend.path + '-' \
            + self.algorithm.path + '-' + str(energy)

        if isinstance(save_to_file, str):
            self._res_path = save_to_file
        else:
            self._res_path = os.path.join(self.path, self.problem.name)

        self._full_path = os.path.join(self._res_path, self._file_name)

        if save_pickle or save_txt or save_csv or save_json:
            self._save_results(save_pickle, save_txt, save_csv, save_json)

        return self.res
