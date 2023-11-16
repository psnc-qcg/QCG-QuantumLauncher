""" Quantum Launcher for Orca """
from orca_stuff import *
from problems import MaxCut
from templates import QuantumLauncher


def main():
    """ main """
    problem = MaxCut(instance_name='default')
    alg = BinaryBosonic()
    backend = OrcaBackend('local')
    launcher = QuantumLauncher(problem, alg, backend)
    print(launcher._run())


if __name__ == '__main__':
    main()
