from base import Algorithm, Problem, Backend
from dimod.binary.binary_quadratic_model import BinaryQuadraticModel
from dimod import Sampler, SampleSet


class DwaveSolver(Algorithm):
    _algorithm_format = 'bqm'

    def __init__(self, chain_strength=1, **alg_kwargs) -> None:
        self.chain_strength = chain_strength
        super().__init__(**alg_kwargs)

    def run(self, problem: Problem, backend: Backend, formatter, **kwargs):
        self._sampler: Sampler = backend.sampler
        self.label: str = f'{problem.name}_{problem.instance_name}'
        bqm: BinaryQuadraticModel = formatter(problem)
        return self._solve_bqm(bqm, **kwargs)

    def _get_path(self) -> str:
        return super()._get_path()

    def _solve_bqm(self, bqm, **kwargs):
        res = self._sampler.sample(
            bqm, num_reads=1000, label=self.label, chain_strength=self.chain_strength, **kwargs)
        return res

    def get_bitstring(self, result: SampleSet) -> str:
        return ''.join(map(str, result.samples()[0].values()))
