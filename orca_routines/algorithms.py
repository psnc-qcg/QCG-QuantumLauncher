""" file with orca algorithms subclasses """
from typing import List
from ptseries.algorithms.binary_solvers import BinaryBosonicSolver
from ptseries.common.logger import Logger

from templates import Problem, Algorithm
from .backend import OrcaBackend
from .orca_templates import OrcaRoutine


class BBS(Algorithm, OrcaRoutine):
    """
    Binary Bosonic Solver algorithm class.

    This class represents the Binary Bosonic Solver (BBS) algorithm. BBS is a quantum-inspired algorithm that
    solves optimization problems by mapping them onto a binary bosonic system. It uses a training process
    to find the optimal solution.

    Attributes:
    - learning_rate (float): The learning rate for the algorithm.
    - updates (int): The number of updates to perform during training.
    - tbi_loops (str): The type of TBI loops to use.
    - print_frequency (int): The frequency at which to print updates.
    - logger (Logger): The logger object for logging algorithm information.

    Methods:
    - __init__(self, learning_rate:float=1e-1, updates:int=80, tbi_loops:str='single-loop', print_frequency:int=20) -> None:
        Initialize the BBS algorithm.
    - run(self, problem: Problem, backend: OrcaBackend):
        Run the BBS algorithm.
    """

    def __init__(self, learning_rate: float = 1e-1, updates: int = 80, tbi_loops: str = 'single-loop', print_frequency: int = 20,
                 gradient_mode: str = 'spsa', n_samples: int = 20, input_state: list[int] | None = None) -> None:
        """
        Initialize the BBS algorithm.

        Parameters:
        - learning_rate (float): The learning rate for the algorithm. Default is 1e-1.
        - updates (int): The number of updates to perform during training. Default is 80.
        - tbi_loops (str): The type of TBI loops to use. Default is 'single-loop'.
        - print_frequency (int): The frequency at which to print updates. Default is 20.
        - gradient_mode (str, optional): 'spsa' or 'paramshift'. Type of method used to compute the gradient of the
                                   quantum parameters.
        - n_samples (int, optional): number of samples used to estimate expectation values
        """
        super().__init__()
        self.bbs = None
        self.learning_rate = learning_rate
        self.updates = updates
        self.tbi_loops = tbi_loops
        self.print_frequency = print_frequency
        self.logger = Logger(log_dir=None)
        self.gradient_mode = gradient_mode
        self.n_samples = n_samples
        self.input_state = input_state

    def _get_path(self) -> str:
        """
        Get the path for the BBS algorithm.

        Returns:
        - str: The path for the BBS algorithm.
        """
        return 'BinaryBosonic'

    def run(self, problem: Problem, backend: OrcaBackend):
        """
        Run the BBS algorithm.

        Parameters:
        - problem (Problem): The problem to solve.
        - backend (OrcaBackend): The backend to use for computation.

        Returns:
        - Solution: The solution obtained from running the BBS algorithm.
        """
        params = {"tbi_type": self.tbi_loops}
        if backend is not None:
            params.update(backend.get_args())
        qubo_fn_fact, Q = problem.get_orca_qubo()
        if self.input_state is None:
            self.input_state = [not i % 2 for i in range(len(Q))]
        self.bbs = BinaryBosonicSolver(
            pb_dim=len(Q),
            objective=Q,
            gradient_mode=self.gradient_mode,
            tbi_params=params,
            n_samples=self.n_samples,
            input_state=self.input_state
        )
        self.bbs.train(
            learning_rate=self.learning_rate,
            updates=self.updates,
            log_frequency=self.print_frequency,
            logger=self.logger
        )

        return self.bbs.config_min_encountered

    def get_bitstring(self, result: List[float]) -> str:
        return ''.join(map(str, map(int, result)))
