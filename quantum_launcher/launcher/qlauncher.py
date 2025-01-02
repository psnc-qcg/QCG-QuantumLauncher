""" File with templates """
import json
import os
import pickle
from typing import List, Literal, Optional, Union
from quantum_launcher.base.adapter_structure import get_formatter
from quantum_launcher.base import Problem, Algorithm, Backend, Result


class QuantumLauncher:
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

    def __init__(self, problem: Problem, algorithm: Algorithm, backend: Backend = None) -> None:
        self.problem: Problem = problem
        self.algorithm: Algorithm = algorithm
        self.backend: Backend = backend
        self.res: dict = {}

    def _prepare_problem(self):
        """
        Chooses a problem for current hardware taken from the algorithm and binds parameters.
        """
        self.problem.prepare_methods()

    def run(self) -> Result:
        """
        Prepares the problem, and runs the algorithm on the problem.

        Returns:
            dict: The results of the algorithm execution.
        """
        self._prepare_problem()
        formatter = get_formatter(
            self.problem._problem_id, self.algorithm._algorithm_format)
        self.result = self.algorithm.run(
            self.problem, self.backend, formatter=formatter)
        return self.result

    def save(self, path: str, format: Literal['pickle', 'txt', 'json'] = 'pickle'):
        if format == 'pickle':
            with open(path, mode='wb') as f:
                pickle.dump(self.result, f)
        elif format == 'json':
            with open(path, mode='w', encoding='utf-8') as f:
                json.dump(self.result, f, default=fix_json)
        elif format == 'txt':
            with open(path, mode='w', encoding='utf-8') as f:
                f.write(self.result.__str__())
        else:
            raise ValueError(
                f'format: {format} in not supported try: pickle, txt, csv or json')

    def process(self, *, file_path: Optional[str] = None, format: Union[Literal['pickle', 'txt', 'json'], List[Literal['pickle', 'txt', 'json']]]='pickle') -> dict:
        """
        Runs the algorithm, processes the data, and saves the results if specified.

        Args:
            file_path Optional[str]: Flag indicating whether to save the results to a file. Defaults to None.

        Returns:
            dict: The processed results.
        """
        results = self.run()
        energy = results.result['energy']
        res = {}
        res['problem_setup'] = self.problem.setup
        res['algorithm_setup'] = self.algorithm.setup
        res['algorithm_setup']['variant'] = self.problem.variant
        res['backend_setup'] = self.backend.setup
        res['results'] = results

        self._file_name = self.problem.path + '-' + \
            self.backend.path + '-' \
            + self.algorithm.path + '-' + str(energy)

        if file_path is not None:
            self.save(file_path, file_path.rsplit('.', 1)[1])

        return res


def fix_json(o: object):
    # if o.__class__.__name__ == 'SamplingVQEResult':
    #     parsed = self.algorithm.parse_samplingVQEResult(o, self._full_path)
    #     return parsed
    if o.__class__.__name__ == 'complex128':
        return repr(o)
    print(
        f'Name of object {o.__class__} not known, returning None as a json encodable')
    return None
