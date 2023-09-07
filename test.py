''' Example of how Quantum Launcher works'''

from quantum_launcher import QuantumLauncher#, from_pickle
from algorithms import QAOA2, FALQON
from problems import EC, JSSP, QATM
from backends import LocalBackend
from analyzer import Analyzer
#pr = QATM('exact', instance_name='RCP_3.txt', instance_path='data/qatm/')
pr = JSSP(3, 'exact', instance_name='toy',optimization_problem=True)
qaoa = QAOA2(p=3)
qaoa = FALQON(delta_t=2, beta_0=2, n= 2)
backend = LocalBackend()
dir_ = 'test_data'
launcher = QuantumLauncher(pr, qaoa, backend)
launcher.set_dir(dir_)
inform = launcher.process('', save_to_file=True)
print(inform)
# print(from_pickle(launcher.res_path)) # This is the same but from pickle
# print(from_pickle("test_data/toy-3-decision-exact-local_simulator-falqon-10-0.03-0-4.596928704106529.pkl"))
