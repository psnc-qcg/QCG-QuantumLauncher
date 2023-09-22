""" Backend Class for Qiskit Launcher """
from qiskit_ibm_runtime import Session

from qiskit_stuff.primitive_strategy import LocalPrimitiveStrategy, \
        RemotePrimitiveStrategy, PrimitiveStrategy
from templates import Backend


class QiskitBackend(Backend):
    """ local backend """

    def __init__(self, name: str, session: Session = None) -> None:
        super().__init__(name)
        self.session = session
        self._set_primitive_strategy_on_backend_name()
        self.strategy = None

    def _set_primitive_strategy_on_backend_name(self) -> None:
        if self.name == 'local_simulator':
            self.primitive_strategy = LocalPrimitiveStrategy()
        elif self.session is None:
            raise AttributeError('Please instantiate a session if using other backend than local')
        else:
            self.primitive_strategy = RemotePrimitiveStrategy(self.session)

    def set_primitive_strategy(self, strategy: PrimitiveStrategy) -> None:
        """ Set's the primitve strategy for backend """
        self.strategy = strategy

    def get_primitive_strategy(self) -> PrimitiveStrategy:
        """ Returns the backend's primitive strategy """
        # Is it neccessary ?
        return self.primitive_strategy
