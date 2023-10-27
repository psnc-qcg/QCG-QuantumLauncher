""" Backend class for Atos """
from templates import Backend
from .atos_templates import AtosStuff


class AtosBackend(Backend, AtosStuff):
    """ local backend """

    def __init__(self, name: str) -> None:
        super().__init__(name)
