""" Backend class for Orca """
from templates import Backend
from .orca_templates import OrcaRoutine
from typing import Literal


class OrcaBackend(Backend, OrcaRoutine):
    """ local backend """

    def __init__(self, name: str) -> None:
        super().__init__(name)

    def get_args(self):
        return {}


class PCSSOrcaBackend(Backend, OrcaRoutine):
    """ Orca QPU backend """

    def __init__(self, name: Literal['system-A', 'system-B']) -> None:
        super().__init__(name)
        self.system_name = name

    def get_args(self):
        if self.system_name == 'system-A':
            return {"tbi_type": "PT-1", "ip_address": "169.254.109.10"}
        if self.system_name == 'system-B':
            return {"tbi_type": "PT-2", "ip_address": "0.0.0.0"}
        raise ValueError(f"Unknown backend {self.system_name}")
