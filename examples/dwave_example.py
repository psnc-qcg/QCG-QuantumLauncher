""" Quantum Launcher for Orca """
from dwave_routines import *
from dimod import SampleSet
from problems import MaxCut
from base import QuantumLauncher


def main():
    """ main """
    problem = MaxCut(instance_name='default')
    alg = DwaveSolver(1)
    backend = SimulatedAnnealingBackend('local')
    launcher = QuantumLauncher(problem, alg, backend)
    res: SampleSet = launcher._run()
    print(''.join(map(str, res.samples()[0].values())))


if __name__ == '__main__':
    main()
