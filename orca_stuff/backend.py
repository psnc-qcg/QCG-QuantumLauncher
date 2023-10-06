""" Backend class for Orca """
from templates import Backend


class OrcaBackend(Backend):
    """ local backend """

    def __init__(self, name: str) -> None:
        super().__init__(name)

    def _set_path(self) -> None:
        self.path = f'{self.name}'
