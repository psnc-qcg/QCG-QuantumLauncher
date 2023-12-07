""" Backend class for Orca """
from templates import Backend
from .orca_templates import OrcaRoutine


class OrcaBackend(Backend, OrcaRoutine):
    """ local backend """

    def __init__(self, name: str) -> None:
        super().__init__(name)
