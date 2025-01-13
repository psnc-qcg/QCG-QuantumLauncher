from typing import Callable
from quantum_launcher.base import Algorithm, Problem, Backend, Result
from dimod.binary.binary_quadratic_model import BinaryQuadraticModel
from dimod import Sampler, SampleSet
from tabu import TabuSampler
from dwave.system import DWaveSampler, EmbeddingComposite
from dwave.samplers import SimulatedAnnealingSampler


class DwaveSolver(Algorithm):
    _algorithm_format = 'bqm'

    def __init__(self, chain_strength=1, **alg_kwargs) -> None:
        self.chain_strength = chain_strength
        super().__init__(**alg_kwargs)

    def run(self, problem: Problem, backend: Backend, formatter: Callable, **kwargs):
        self._sampler: Sampler = backend.sampler
        self.label: str = f'{problem.name}_{problem.instance_name}'
        bqm: BinaryQuadraticModel = formatter(problem)
        res = self._solve_bqm(bqm, **kwargs)
        return self.construct_result(res)

    def _solve_bqm(self, bqm, **kwargs):
        res = self._sampler.sample(
            bqm, num_reads=1000, label=self.label, chain_strength=self.chain_strength, **kwargs)
        return res

    def construct_result(self, result: SampleSet) -> Result:
        distribution = {}
        energies = {}
        for (value, energy, occ) in result.record:
            bitstring = ''.join(map(str, value))
            if bitstring in distribution:
                distribution[bitstring] += occ
                continue
            distribution[bitstring] = occ
            energies[bitstring] = energy

        return Result.from_distributions(distribution, energies, result)


class TabuBackend(Backend):
    def __init__(self, name: str = "TabuSampler", parameters: list = None) -> None:
        super().__init__(name, parameters)
        self.sampler = TabuSampler()


class DwaveBackend(Backend):
    def __init__(self, name: str = "DWaveSampler", parameters: list = None) -> None:
        super().__init__(name, parameters)
        self.sampler = EmbeddingComposite(DWaveSampler())


class SimulatedAnnealingBackend(Backend):
    def __init__(self, name: str = "SimulatedAnnealingSampler", parameters: list = None) -> None:
        super().__init__(name, parameters)
        self.sampler = SimulatedAnnealingSampler()


__all__ = ['DwaveSolver', 'TabuBackend',
           'DwaveBackend', 'SimulatedAnnealingBackend']
