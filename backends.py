''' file with backend subclasses '''

from qiskit.primitives import Estimator as LocalEstimator
from qiskit.primitives import Sampler as LocalSampler
from qiskit_ibm_runtime import Estimator, Sampler
from qiskit_algorithms.optimizers import COBYLA
from templates import Backend

class LocalBackend(Backend):
    ''' local backend '''
    def __init__(self) -> None:
        super().__init__('local_simulator')

    def get_estimator(self) -> Estimator:
        return LocalEstimator()

    def get_sampler(self) -> Sampler:
        return LocalSampler()

    def get_optimizer(self):
        return COBYLA()

class RemoteBackend(Backend):
    ''' remote backend '''
    def __init__(self, name: str, session:str) -> None:
        super().__init__(name)
        self.session = session

    def get_estimator(self) -> Estimator:
        return Estimator(session=self.session)

    def get_sampler(self) -> Sampler:
        return Sampler(session=self.session)

BACKEND_LIST = [LocalBackend, RemoteBackend]
