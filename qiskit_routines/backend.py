""" Backend Class for Qiskit Launcher """
from qiskit.primitives import Estimator as LocalEstimator, BaseEstimator
from qiskit.primitives import Sampler as LocalSampler, BaseSampler
from qiskit_algorithms.optimizers import COBYLA, SPSA, SciPyOptimizer
from qiskit_ibm_runtime import Estimator, Sampler
from qiskit_ibm_runtime import Session, Options

from templates import Backend
from .qiskit_template import QiskitRoutine


class QiskitBackend(Backend, QiskitRoutine):
    """ local backend """

    def __init__(self, name: str, session: Session = None, options: Options = None) -> None:
        super().__init__(name)
        self.session = session
        self.options = options
        self.primitive_strategy = None
        self.sampler = None
        self.estimator = None
        self.optimizer = None
        self._set_primitives_on_backend_name()

    @property
    def setup(self) -> dict:
        return {
            'name': self.name,
            'session': self.session
        }

    def _set_primitives_on_backend_name(self) -> None:
        if self.name == 'local_simulator':
            self.estimator = LocalEstimator()
            self.sampler = LocalSampler()
            self.optimizer = COBYLA()
        elif self.session is None:
            raise AttributeError('Please instantiate a session if using other backend than local')
        else:
            self.estimator = Estimator(session=self.session, options=self.options)
            self.sampler = Sampler(session=self.session, options=self.options)
            self.optimizer = SPSA()

    @property
    def estimator(self) -> BaseEstimator:
        return self._estimator

    @estimator.setter
    def estimator(self, estimator: BaseEstimator):
        self._estimator = estimator

    @property
    def sampler(self) -> BaseSampler:
        return self._sampler

    @sampler.setter
    def sampler(self, sampler: BaseSampler):
        self._sampler = sampler

    @property
    def optimizer(self) -> SciPyOptimizer:
        return self._optimizer

    @optimizer.setter
    def optimizer(self, optimizer: SciPyOptimizer):
        self._optimizer = optimizer
