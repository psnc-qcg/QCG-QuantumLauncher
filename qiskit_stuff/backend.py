""" Backend Class for Qiskit Launcher """
from qiskit.primitives import Estimator as LocalEstimator, BaseEstimator
from qiskit.primitives import Sampler as LocalSampler, BaseSampler
from qiskit_algorithms.optimizers import COBYLA, SPSA, SciPyOptimizer
from qiskit_ibm_runtime import Estimator, Sampler
from qiskit_ibm_runtime import Session, Options

from templates import Backend, QuantumLauncher
from .qiskit_template import QiskitStuff


class QiskitBackend(Backend, QiskitStuff):
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
            'session': self.session,
            'metrics': self._gather_metrics()
        }

    def prepare(self, launcher: QuantumLauncher):
        self.set_job_tags([launcher.input_path()])

    def _gather_metrics(self) -> None | dict:
        if self.session is None:
            return None
        elif self.name != 'local_simulator':
            service = self.session.service
            session_jobs = service.jobs(session_id=self.session.session_id)
            last_job = session_jobs[0]
            return last_job.metrics()

    def set_job_tags(self, tags: list):
        self.sampler.set_options(job_tags=tags)
        self.estimator.set_options(job_tags=tags)
        a = 1

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
