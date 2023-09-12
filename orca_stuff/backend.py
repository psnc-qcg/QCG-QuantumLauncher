from templates import Backend


class OrcaBackend(Backend):
    ''' local backend '''

    def __init__(self, name: str) -> None:
        super().__init__(name)
