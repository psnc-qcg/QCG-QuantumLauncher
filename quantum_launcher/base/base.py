from abc import ABC, abstractmethod
from functools import wraps
import pickle
from typing import Callable
from .unified_result import Result


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

    _problem_id = None

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

    def __init_subclass__(cls) -> None:
        if Problem not in cls.__bases__:
            return
        cls._problem_id = cls

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

    def output(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if wrapper.__solved:
                return wrapper.__solved
            wrapper.__solved = func(*args, **kwargs)
            return wrapper.__solved
        wrapper._is_output = True
        wrapper.__solved = False
        return wrapper

    def prepare_methods(self):
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, '_is_output'):
                attr()


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
    _algorithm_format: str | None = None

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
    def run(self, problem: Problem, backend: Backend, formatter: Callable = None) -> Result:
        """Runs the algorithm on a specific problem using a backend.

        Args:
            problem (Problem): The problem to be solved.
            backend (Backend): The backend to be used for execution.
        """

    @abstractmethod
    def get_bitstring(self, result) -> str:
        """Returns the bitstring representation of the result.

        Args:
            result: The result to be converted to a bitstring.
        """
        pass
