""" Backend Class for Qiskit Launcher """
from qiskit.primitives import Estimator as LocalEstimator, BaseEstimator
from qiskit.primitives import Sampler as LocalSampler, BaseSampler
from qiskit.primitives import BackendSampler, BackendEstimator
from qiskit.providers import BackendV1, BackendV2
from qiskit_algorithms.optimizers import COBYLA, SPSA, SciPyOptimizer, Optimizer
from qiskit_ibm_runtime import Estimator, Sampler
from qiskit_ibm_runtime import Session, Options

from base import Backend
from .qiskit_template import QiskitRoutine


class QiskitBackend(Backend, QiskitRoutine):
    """ 
    A class representing a local backend for Qiskit routines.

    This class extends the `Backend` and `QiskitRoutine` classes and provides functionality for a local backend.
    It allows for setting up a session, options, and various primitives such as estimators, samplers, and optimizers.

    Attributes:
        name (str): The name of the backend.
        session (Session): The session associated with the backend.
        options (Options): The options for the backend.
        primitive_strategy: The strategy for selecting primitives based on the backend name.
        sampler (BaseSampler): The sampler used for sampling.
        estimator (BaseEstimator): The estimator used for estimation.
        optimizer (Optimizer): The optimizer used for optimization.

    Methods:
        setup() -> dict: Returns a dictionary with the setup information of the backend.
        _set_primitives_on_backend_name() -> None: Sets the appropriate primitives based on the backend name.
    """

    def __init__(self, name: str, session: Session = None, options: Options = None, backendv1v2: BackendV1 | BackendV2 = None) -> None:
        super().__init__(name)
        self.session = session
        self.options = options
        self.backendv1v2 = backendv1v2
        self.primitive_strategy = None
        self.sampler = None
        self.estimator: BaseEstimator = None
        self.optimizer: Optimizer = None
        self._set_primitives_on_backend_name()

    @property
    def setup(self) -> dict:
        return {
            'name': self.name,
            'session': self.session
        }

    def _set_primitives_on_backend_name(self) -> None:
        if self.name == 'local_simulator':
            self.estimator = LocalEstimator(options=self.options)
            self.sampler = LocalSampler(options=self.options)
            self.optimizer = COBYLA()
        elif self.name == 'backendv1v2_simulator':
            self.estimator = BackendEstimator(backend=self.backendv1v2)
            self.sampler = BackendSampler(backend=self.backendv1v2)
            self.optimizer = COBYLA()
        elif self.session is None:
            raise AttributeError(
                'Please instantiate a session if using other backend than local')
        else:
            self.estimator = Estimator(
                session=self.session, options=self.options)
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
