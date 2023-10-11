''' Quantum Launcher for Atos '''
from atos_stuff.algorithms import QAOA2
from atos_stuff.launcher import AtosLauncher
from problems import MaxCut


def main():
    ''' main '''
    pr = MaxCut()
    pr.set_instance(instance_name='default')
    alg = QAOA2()
    launcher = AtosLauncher(pr, alg)
    print(launcher.run())


if __name__ == '__main__':
    main()
