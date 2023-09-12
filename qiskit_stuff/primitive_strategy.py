''' file with primitive strategy subclasses '''

from abc import abstractmethod, ABC

from qiskit.primitives import Estimator as LocalEstimator
from qiskit.primitives import Sampler as LocalSampler
from qiskit_algorithms.optimizers import COBYLA, SPSA
from qiskit_ibm_runtime import Estimator, Sampler


class PrimitiveStrategy(ABC):
    ''' Abstract class for primitive startegies '''

    @abstractmethod
    def __init__(self, name: str, parameters: list = None) -> None:
        self.name = name
        self.path_name = name
        self.parameters = parameters if parameters is not None else []

    def get_estimator(self) -> Estimator:
        ''' returns primitive strategy's estimator '''
        return None

    def get_sampler(self) -> Sampler:
        ''' returns primitive strategy's sampler '''
        return None

    def get_optimizer(self):
        ''' returns primitive strategy's optimizer '''
        return SPSA()


class LocalPrimitiveStrategy(PrimitiveStrategy):
    ''' local primitive strategy '''

    def __init__(self) -> None:
        super().__init__('local_simulator')

    def get_estimator(self) -> Estimator:
        return LocalEstimator()

    def get_sampler(self) -> Sampler:
        return LocalSampler()

    def get_optimizer(self):
        return COBYLA()


class RemotePrimitiveStrategy(PrimitiveStrategy):
    ''' remote primitive strategy '''

    def __init__(self, name: str, session: str) -> None:
        super().__init__(name)
        self.session = session

    def get_estimator(self) -> Estimator:
        return Estimator(session=self.session)

    def get_sampler(self) -> Sampler:
        return Sampler(session=self.session)


PRIMITIVE_STRATEGY_LIST = [LocalPrimitiveStrategy, RemotePrimitiveStrategy]
