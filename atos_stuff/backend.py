""" Backend class for Atos """
from templates import Backend


class AtosBackend(Backend):
    """ local backend """

    def __init__(self, name: str) -> None:
        super().__init__(name)
