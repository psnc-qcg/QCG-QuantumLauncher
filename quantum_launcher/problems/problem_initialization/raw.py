""" This module contains the Raw class."""
from quantum_launcher.base import Problem


class Raw(Problem):
    """
    Class for solving problem implemented in raw mathematical form.

    "Raw mathematical form" means that the problem is defined in format 
    that can be directly read by the quantum algorithm, such as Qubo, Hamiltonian, etc.

    The object contains an instance of the problem written in mentioned raw mathematical form,
    can be passed into Quantum Launcher.

    Attributes:
        instance (any): Formulated problem instance.
    """

    def __init__(self, instance: any = None, instance_name: str | None = None) -> None:
        super().__init__(instance=instance, instance_name=instance_name)

    def _get_path(self) -> str:
        return f'{self.name}/{self.instance_name}'
