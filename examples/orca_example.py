""" Quantum Launcher for Orca """
from templates import QuantumLauncher
from orca_stuff import *
from problems import MaxCut


def main():
    """ main """
    problem = MaxCut(instance_name='default')
    alg = BinaryBosonic()
    backend = OrcaBackend('local')
    launcher = QuantumLauncher(problem, alg, backend)
    print(launcher.run())

if __name__ == '__main__':
    main()
