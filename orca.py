''' Quantum Launcher for Orca '''
from orca_stuff.algorithms import BinaryBosonic
from orca_stuff.launcher import OrcaLauncher
from problems import MaxCut


def main():
    ''' main '''
    pr = MaxCut(instance_name='default')
    alg = BinaryBosonic()
    launcher = OrcaLauncher(pr, alg)
    print(launcher.run())


if __name__ == '__main__':
    main()
