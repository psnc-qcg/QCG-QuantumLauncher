""" Backend class for Orca """
from templates import Backend
from .orca_templates import OrcaStuff

class OrcaBackend(Backend, OrcaStuff):
    """ local backend """
    PROBLEM_CLASS = OrcaStuff
    def __init__(self, name: str) -> None:
        super().__init__(name)
