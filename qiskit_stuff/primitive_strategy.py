''' file with primitive strategy subclasses '''

from abc import abstractmethod, ABC

from qiskit.primitives import Estimator as LocalEstimator
from qiskit.primitives import Sampler as LocalSampler
from qiskit_algorithms.optimizers import COBYLA, SPSA
from qiskit_ibm_runtime import Estimator, Sampler, Session


class PrimitiveStrategy(ABC):
    ''' Abstract class for primitive startegies '''

    @abstractmethod
    def __init__(self) -> None:
        super().__init__()

    @property
    def estimator(self) -> Estimator:
        ''' returns primitive strategy's estimator '''
        return None

    @property
    def sampler(self) -> Sampler:
        ''' returns primitive strategy's sampler '''
        return None

    @property
    def optimizer(self):
        ''' returns primitive strategy's optimizer '''
        return SPSA()


class LocalPrimitiveStrategy(PrimitiveStrategy):
    ''' local primitive strategy '''

    def __init__(self) -> None:
        pass

    @property
    def estimator(self) -> Estimator:
        return LocalEstimator()

    @property
    def sampler(self) -> Sampler:
        return LocalSampler()

    @property
    def optimizer(self):
        return COBYLA()


class RemotePrimitiveStrategy(PrimitiveStrategy):
    ''' remote primitive strategy '''

    def __init__(self, session: Session) -> None:
        self.session = session

    @property
    def estimator(self) -> Estimator:
        return Estimator(session=self.session)

    @property
    def sampler(self) -> Sampler:
        return Sampler(session=self.session)


PRIMITIVE_STRATEGY_LIST = [LocalPrimitiveStrategy, RemotePrimitiveStrategy]
