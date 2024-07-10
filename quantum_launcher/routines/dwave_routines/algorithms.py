from quantum_launcher.base import Algorithm, Problem, Backend, Result
from dimod.binary.binary_quadratic_model import BinaryQuadraticModel
from dimod import Sampler, SampleSet
import numpy as np


class DwaveSolver(Algorithm):
    _algorithm_format = 'bqm'

    def __init__(self, chain_strength=1, **alg_kwargs) -> None:
        self.chain_strength = chain_strength
        super().__init__(**alg_kwargs)

    def run(self, problem: Problem, backend: Backend, formatter, **kwargs):
        self._sampler: Sampler = backend.sampler
        self.label: str = f'{problem.name}_{problem.instance_name}'
        bqm: BinaryQuadraticModel = formatter(problem)
        res = self._solve_bqm(bqm, **kwargs)
        return self.construct_result(res)

    def _get_path(self) -> str:
        return super()._get_path()

    def _solve_bqm(self, bqm, **kwargs):
        res = self._sampler.sample(
            bqm, num_reads=1000, label=self.label, chain_strength=self.chain_strength, **kwargs)
        return res

    def get_bitstring(self, result: SampleSet) -> str:
        return ''.join(map(str, result.samples()[0].values()))

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

        best_bitstring = min(energies, key=energies.get)
        best_energy = energies[best_bitstring]
        most_common_bitstring = max(distribution, key=distribution.get)
        most_common_bitstring_energy = energies[most_common_bitstring]
        num_of_samples = result.record.size
        # TODO: Add multiplication by distribution
        average_energy = np.mean(list(energies.values()))
        # TODO: Add multiplication by distribution
        energy_std = np.std(list(energies.values()))
        return Result(best_bitstring, best_energy, most_common_bitstring, most_common_bitstring_energy, distribution, energies, num_of_samples, average_energy, energy_std, result)
