from templates import Backend
from .dwave_templates import DwaveRoutine


class DwaveBackend(Backend, DwaveRoutine):
    def __init__(self, name: str = "local", parameters: list = None) -> None:
        super().__init__(name, parameters)
