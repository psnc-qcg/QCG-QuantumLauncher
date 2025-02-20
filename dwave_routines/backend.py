from templates import Backend
from .dwave_templates import DwaveRoutine
from tabu import TabuSampler
from dwave.system import DWaveSampler, EmbeddingComposite
from dwave.samplers import SimulatedAnnealingSampler


class TabuBackend(Backend, DwaveRoutine):
    def __init__(self, name: str = "TabuSampler", parameters: list = None) -> None:
        super().__init__(name, parameters)
        self.sampler = TabuSampler()


class DwaveBackend(Backend, DwaveRoutine):
    def __init__(self, name: str = "DWaveSampler", parameters: list = None) -> None:
        super().__init__(name, parameters)
        self.sampler = EmbeddingComposite(DWaveSampler())


class SimulatedAnnealingBackend(Backend, DwaveRoutine):
    def __init__(self, name: str = "SimulatedAnnealingSampler", parameters: list = None) -> None:
        super().__init__(name, parameters)
        self.sampler = SimulatedAnnealingSampler()
