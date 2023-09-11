''' Quantum Launcher '''

from templates import QuantumLauncher, PrimitiveStrategy
from .primitive_strategy import LocalPrimitiveStrategy


class QiskitLauncher(QuantumLauncher):
    ''' Global Launcher problem'''

    def run(self) -> dict:
        if self.primitive_strategy is None:
            self.primitive_strategy = LocalPrimitiveStrategy()
        return self.algorithm.run(self.problem, self.primitive_strategy)

    def set_primitive_strategy(self, primitive_strategy: PrimitiveStrategy) -> None:
        self.primitive_strategy = primitive_strategy
