""" Quantum Launcher for Orca """
from quantum_launcher import *
from quantum_launcher.routines.dwave_routines import SimulatedAnnealingBackend, DwaveSolver


def main():
    """ main """
    problem = problems.MaxCut(instance_name='default')
    alg = DwaveSolver(1)
    backend = SimulatedAnnealingBackend('local')
    launcher = QuantumLauncher(problem, alg, backend)
    res = launcher.run()
    print(alg.get_bitstring(res))


if __name__ == '__main__':
    main()
