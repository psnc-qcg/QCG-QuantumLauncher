from templates import QuantumLauncher


class OrcaLauncher(QuantumLauncher):
    ''' Quantum Launcher for Orca '''

    def run(self) -> dict:
        return self.algorithm.run(self.problem)
