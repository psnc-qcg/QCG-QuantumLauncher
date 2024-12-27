""" File with templates """
import json
import os
import pickle
from quantum_launcher.base.adapter_structure import get_formatter
from quantum_launcher.base import Problem, Algorithm, Backend, Result


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
            f'\033[93mSaving to csv has not been implemented yet {results=}{file_name=}\033[0m')

    def _save_results_json(self, results: dict, file_name: str) -> None:
        for i in results:
            if isinstance(results[i], Result):
                results[i] = results[i].__dict__
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


class QuantumLauncher(_FileSavingSupportClass):
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
        encoding_type (type): The encoding type to be used changing the class of the problem. Defaults to None.

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
                 path: str = 'results/', binding_params: dict | None = None, encoding_type: type = None) -> None:
        super().__init__()
        self.problem: Problem = problem
        self.algorithm: Algorithm = algorithm
        self.backend: Backend = backend

        self.path: str = path
        self.res: dict = {}
        self._res_path: str | None = None
        self.binding_params: dict | None = binding_params
        self.encoding_type: callable = encoding_type  # TODO variable to be renamed

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
        if self.binding_params is not None:
            self._bind_parameters()
        self.problem.prepare_methods()

    def _run(self) -> Result:
        """
        Prepares the problem, and runs the algorithm on the problem.

        Returns:
            dict: The results of the algorithm execution.
        """
        self._prepare_problem()
        formatter = get_formatter(
            self.problem._problem_id, self.algorithm._algorithm_format)

        return self.algorithm.run(self.problem, self.backend, formatter=formatter)

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
        energy = results.result['energy']

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
