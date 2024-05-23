""" Backend class for Orca """
from templates import Backend
from .orca_templates import OrcaRoutine


class OrcaBackend(Backend, OrcaRoutine):
    """ local backend """

    def __init__(self, name: str) -> None:
        super().__init__(name)

    def get_args():
        return {}


class PCSSOrcaBackend(Backend, OrcaRoutine):
    """ Orca QPU backend """

    def __init__(self, name: str) -> None:
        super().__init__(name)

    def get_args():
        return {"tbi_type": "PT-1", "ip_address": "169.254.109.10"}
