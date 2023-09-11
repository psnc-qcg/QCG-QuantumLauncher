''' Quantum Launcher for Orca '''
from algorithms import BinaryBosonic
from problems import MaxCut
from quantum_launchers import OrcaLauncher


def main():
    ''' main '''
    pr = MaxCut(instance_name='default')
    alg = BinaryBosonic()
    launcher = OrcaLauncher(pr, alg)
    print(launcher.run())


if __name__ == '__main__':
    main()
