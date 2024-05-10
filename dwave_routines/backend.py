from templates import Backend
from .dwave_templates import DwaveRoutine
from tabu import TabuSampler


class tabuBackend(Backend, DwaveRoutine):
    def __init__(self, name: str = "tabu", parameters: list = None) -> None:
        super().__init__(name, parameters)
        self.sampler = TabuSampler()
