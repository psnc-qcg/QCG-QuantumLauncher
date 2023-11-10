""" File with templates """
import json
import os
import pickle
from abc import ABC, abstractmethod


class _FileSavingSupportClass:

    def fix_json(self, o: object):
        if o.__class__.__name__ == 'SamplingVQEResult':
            parsed = self.algorithm.parse_samplingVQEResult(o, self._res_path)
            return parsed
        elif o.__class__.__name__ == 'complex128':
            return repr(o)
        else:
            print(f'Name of object {o.__class__} not known, returning None as a json encodable')
            return None

    def _save_results_pickle(self, results: dict, file_name: str) -> None:
        with open(file_name, mode='wb') as file:
            pickle.dump(results, file)

    def _save_results_txt(self, results: dict, file_name: str) -> None:
        with open(file_name, mode='w', encoding='utf-8') as file:
            file.write(results.__str__())

    def _save_results_csv(self, results: dict, file_name: str) -> None:
        print('\033[93mSaving to csv has not been implemented yet\033[0m')

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
    @property
    def setup(self) -> dict:
        return f'setup for {self.__class__.__name__} has not been implemented yet'

    @property
    def path(self) -> str:
        if self._path is not None:
            return self._path
        return self._get_path()

    @path.setter
    def path(self, new_path: str | None) -> None:
        self._path = new_path

    @abstractmethod
    def _get_path():
        pass


class Backend(_SupportClass, ABC):
    """ Abstract class for backends """

    @abstractmethod
    def __init__(self, name: str, parameters: list = None) -> None:
        self.name: str = name
        self.path: str | None = None
        self.parameters = parameters if parameters is not None else []

    def _get_path(self):
        return f'{self.name}'


class Problem(_SupportClass, ABC):
    """ Abstract class for Problems """

    @abstractmethod
    def __init__(self, instance: any = None,
                 instance_name: str | None = None, instance_path: str | None = None) -> None:
        self.variant: str = 'Optimization'
        self.path: str | None = None
        self.name = type(self).__name__.lower()
        self.instance_name: str = 'unnamed' if instance_name is None else instance_name
        self.instance: any = None
        if instance_path is not None:
            self.read_instance(instance_path)
        else:
            self.set_instance(instance=instance, instance_name=instance_name)

    def set_instance(self, instance: any, instance_name: str | None = None) -> None:
        """ Sets an instance of problem """
        if instance_name is not None:
            self.instance_name = instance_name
        self.instance = instance

    def read_instance(self, instance_path: str) -> None:
        """ Reads an instance of problem from file """
        self.instance_name = instance_path.rsplit('/', 1)[1].split('.', 1)[0]
        with open(instance_path, 'rb') as file:
            self.instance = pickle.load(file)

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


class Algorithm(_SupportClass, ABC):
    """ Abstract class for Algorithms"""

    @abstractmethod
    def __init__(self, **alg_kwargs) -> None:
        self.name: str = type(self).__name__.lower()
        self.path: str | None = None
        self.parameters: list = []
        self.alg_kwargs = alg_kwargs

    @abstractmethod
    def _get_path(self) -> str:
        """ return's common path """

    def parse_result_to_json(self, o: object) -> dict:
        """ Parses results so that it can be saved as a json file """
        print('Algorithm does not have the parse_result_to_json method implemented')
        return dict(o)

    @abstractmethod
    def run(self, problem: Problem, backend: Backend):
        """ Runs an algorithm on a specific problem using a backend """


class QuantumLauncher(ABC, _FileSavingSupportClass):
    """ Template for Quantum Launchers """

    def __init__(self, problem: Problem, algorithm: Algorithm, backend: Backend = None,
                 path: str = 'results/') -> None:
        self.problem: Problem = problem
        self.algorithm: Algorithm = algorithm
        self.backend: Backend = backend

        self.path: str = path
        self.res: dict = {}
        self._res_path: str | None = None

    def _run(self) -> dict:
        """ Run's algorithm """
        problem_class = list(set(self.problem.__class__.__subclasses__()) &
                             set(self.algorithm.SYSTEM_CLASS.__subclasses__()))[0]
        self.problem.__class__ = problem_class
        return self.algorithm.run(self.problem, self.backend)

    def process(self, save_to_file: bool = False,
                save_pickle: str | bool = False, save_txt: str | bool = False,
                save_csv: str | bool = False, save_json: str | bool = False) -> dict:
        """ Run's and process'es the data """
        results = self._run()
        energy = results['energy']
        variant = self.problem.variant
        results['variant'] = variant
        results['backend_name'] = self.backend.name

        self.res['problem_setup'] = self.problem.setup
        self.res['algorithm_setup'] = self.algorithm.setup
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
        if save_to_file:
            print('\033[93msave_to_file will be removed soon, change into save_pickle\033[0m')
            self._dir = os.path.dirname(self._res_path)
            if not os.path.exists(self._dir):
                os.makedirs(self._dir)
            with open(self._full_path + '.pkl', 'wb') as file:
                pickle.dump(results, file)

        if save_pickle or save_txt or save_csv or save_json:
            self._save_results(save_pickle, save_txt, save_csv, save_json)

        return self.res
