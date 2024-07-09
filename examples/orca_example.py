""" Quantum Launcher for Orca """
from quantum_launcher import *
from quantum_launcher.routines.orca_routines import OrcaBackend, BBS


def main():
    """ main """
    problem = problems.MaxCut(instance_name='default')
    alg = BBS()
    backend = OrcaBackend('local')
    launcher = QuantumLauncher(problem, alg, backend)
    print((result := launcher._run()))
    print(alg.get_bitstring(result))


if __name__ == '__main__':
    main()
