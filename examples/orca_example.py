""" Quantum Launcher for Orca """
from orca_routines import *
from problems import MaxCut
from templates import QuantumLauncher


def main():
    """ main """
    problem = MaxCut(instance_name='default')
    alg = BBS()
    backend = OrcaBackend('local')
    launcher = QuantumLauncher(problem, alg, backend)
    print((result := launcher._run()))
    print(alg.get_bitstring(result))


if __name__ == '__main__':
    main()
