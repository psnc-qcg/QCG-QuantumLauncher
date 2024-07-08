from typing import Tuple
import asyncio
from base import QuantumLauncher, Backend, Algorithm, Problem
from typing import List
import random


class asyncQuantumLauncher(QuantumLauncher):

    def start(self, times: int = 1, real_backend: Backend = None, debugging=False) -> None:
        self.real_backend = self.backend if real_backend is None else real_backend
        self._async_running = 1
        self._results = []
        self.debugging: bool = debugging
        self._prepare_problem()
        asyncio.run(self.run_async(times))
        return self._results

    async def run_async_task(self, pool: asyncio.BaseEventLoop):
        if self.debugging:
            print('cloud task started')
        result = await pool.run_in_executor(None, self.algorithm.run, self.problem, self.backend)
        self._results.append(result)
        if self.debugging:
            print('cloud task finished')
        return result

    async def run_async_fake_task(self, pool: asyncio.BaseEventLoop):
        if self.debugging:
            print('local task started')
        result = await pool.run_in_executor(None, self.algorithm.run, self.problem, self.backend)
        self._results.append(result)
        if self.debugging:
            print('local task finished')
        return result

    async def run_async(self, times: int):
        if self.debugging:
            print('creating tasks started')
        pool = asyncio.get_event_loop()
        tasks = [self.run_async_task(pool) for _ in range(times)]
        tasks += [self.run_async_fake_task(pool)]
        await asyncio.gather(*tasks)
        if self.debugging:
            print('all tasks finished')


class AQL:
    def __init__(self, backends: List[Tuple[Backend, int]], algorithms: List[Tuple[Algorithm, int]], problems: List[Tuple[Problem, int]],
                 debugging: bool = False):
        self.backends = backends
        self.algorithms = algorithms
        self.problems = problems
        self._results = []
        self._results_bitstring = []
        self._async_running = 0
        self.debugging: bool = False
        self.ROUTINE_CLASS = None

    def start(self) -> List[any]:
        self._async_running = 1
        self._results = []
        self._results_bitstring = []
        self.ROUTINE_CLASS = self.backends[0][0].ROUTINE_CLASS
        for problem, _ in self.problems:
            self._find_default_problem_class(problem)
            problem.__class__ = self._find_default_problem_class(problem)
            # print('binding', problem.__class__)
            problem.prepare_methods()

        asyncio.run(self.run_async())
        return self._results, self._results_bitstring

    def _find_default_problem_class(self, problem: Problem):
        for subclass in problem.__class__.__subclasses__():
            if self.ROUTINE_CLASS in subclass.__bases__:
                return subclass

    async def run_async_task(self, pool: asyncio.BaseEventLoop, backend: Backend, algorithm: Algorithm, problem: Problem):
        # print('Task Started')
        if self.debugging:
            print('cloud task started')

        result = await pool.run_in_executor(None, algorithm.run, problem, backend)
        self._results.append(result)
        self._results_bitstring.append(algorithm.get_bitstring(result))
        # print('Task Done')

        if self.debugging:
            print('cloud task finished')
        return result

    async def run_async(self):
        if self.debugging:
            print('creating tasks started')
        pool = asyncio.get_event_loop()
        tasks = []
        for backend, b_times in self.backends:
            for algorithm, a_times in self.algorithms:
                for problem, p_times in self.problems:
                    times = b_times * a_times * p_times
                    for _ in range(times):
                        tasks.append(self.run_async_task(
                            pool, backend, algorithm, problem))
        # print(len(tasks), tasks)
        await asyncio.gather(*tasks)
        if self.debugging:
            print('all tasks finished')


class AQLManager:
    """
    ### Context manager for asyncQuantumLauncher
    Simplified high-level context manager to support asynchronous flow of asyncQuantumLauncher.

    Inside is only initialization and whole processing is done at the end.

    To save the results it's recommended to assign manager's variables to local ones, so they don't get destroyed.


    ---

    #### Usage Example:
    ```
    with AQLManager('my_path') as launcher:
        launcher.add()
        launcher.add()
        launcher.add()
        result = aql.result
    print(result)
    ```
    """

    def __init__(self, path: str):
        self.aql: asyncQuantumLauncher | None = None
        self.path = path
        self.result = []
        self.result_bitstring = []
        self._backends: List[Backend] = []
        self._algorithms: List[Algorithm] = []
        self._problems: List[Problem] = []

    def __enter__(self):
        # self.aql: asyncQuantumLauncher = asyncQuantumLauncher(None, None, None)
        return self

    def add_backend(self, backend: Backend, times: int = 1):
        self._backends.append((backend, times))

    def add_algorithm(self, algorithm, times: int = 1):
        self._algorithms.append((algorithm, times))

    def add_problem(self, problem, times: int = 1):
        self._problems.append((problem, times))

    def add(self, backend: Backend = None, algorithm: Algorithm = None, problem: Problem = None, times: int = 1):
        self._backends.append((backend, times))
        self._algorithms.append((algorithm, 1))
        self._problems.append((problem, 1))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            raise exc_type(exc_val).with_traceback(exc_tb)
        aql = AQL(self._backends, self._algorithms, self._problems)
        result, result_bitstring = aql.start()
        self.result.extend(result)
        self.result_bitstring.extend(result_bitstring)


if __name__ == '__main__':
    from problems import MaxCut, EC
    from qiskit_routines import QAOA, QiskitBackend

    with AQLManager('test') as launcher:
        launcher.add(backend=QiskitBackend('local_simulator'),
                     algorithm=QAOA(p=1), problem=EC('exact', instance_name='toy'))
        for i in range(2, 3):
            launcher.add_algorithm(QAOA(p=i))
        result = launcher.result
        result_bitstring = launcher.result_bitstring
    print(len(result))
    print(result_bitstring)

    for ind, i in enumerate(result):
        print(ind, i['SamplingVQEResult'].best_measurement)
