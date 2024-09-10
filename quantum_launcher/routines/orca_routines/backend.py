""" Backend class for Orca """
from quantum_launcher.base import Backend


class OrcaBackend(Backend):
    """ local backend """

    def __init__(self, name: str) -> None:
        super().__init__(name)

    def get_args(self):
        return {}
