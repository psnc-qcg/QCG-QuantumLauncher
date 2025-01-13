from typing import Tuple
import cProfile
import pstats
from quantum_launcher.base import Algorithm, Backend, Problem, Result
from .qlauncher import QuantumLauncher


class ProfilingLauncher(QuantumLauncher):
    """ Launcher made for debugging purposes of algorithms and other launchers focusing on performance issues """

    def __init__(self, problem: Problem, algorithm: Algorithm, backend: Backend, profiler_path: str = 'profiling-results.prof'):
        super().__init__(problem, algorithm, backend)
        self._profiler_path = profiler_path

    def run(self) -> Tuple[Result, pstats.Stats]:
        with cProfile.Profile() as pr:
            result = super().run()
        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.reverse_order()
        stats.print_stats()
        stats.dump_stats(self._profiler_path)
        return result
