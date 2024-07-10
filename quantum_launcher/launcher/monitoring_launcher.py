from quantum_launcher.base.base import Algorithm, Backend, Problem
from .qlauncher import QuantumLauncher
import cProfile
import pstats


class MonitoringLauncher(QuantumLauncher):
    """Launcher made for debugging purposes of algorithms and other launchers focusing on performence issues"""

    def __init__(self, problem: Problem, algorithm: Algorithm, backend: Backend = None, path: str = 'results/', binding_params: dict | None = None, encoding_type: type = None, save_monitor_to_file: str = None) -> None:
        super().__init__(problem, algorithm, backend, path, binding_params, encoding_type)
        self.save_monitor_to_file = save_monitor_to_file

    def monitor(self, func, *args, **kwargs):
        with cProfile.Profile() as pr:
            result = func(*args, **kwargs)
        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.reverse_order()
        stats.print_stats()
        if self.save_monitor_to_file is True:
            stats.dump_stats(f"{func.__name__}.prof")
        elif self.save_monitor_to_file is not None:
            stats.dump_stats(f"{self.save_monitor_to_file}.prof")
        return result

    def _run(self, *args, **kwargs):
        return self.monitor(super()._run, *args, **kwargs)
