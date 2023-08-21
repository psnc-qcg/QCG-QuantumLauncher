from templates import QuantumLauncher, from_pickle
from algorithms import QAOA2, FALQON
from problems import EC, JSSP, QATM

pr = QATM(instance_name='RCP_3.txt', instance_path='data/qatm/')
# pr = JSSP(3, 'exact', instance_name='toy',optimization_problem=True)
qaoa = QAOA2(p=3)
dir_ = 'test_data'
launcher = QuantumLauncher(pr, qaoa)
launcher.set_dir(dir_)
inform = launcher.process('', 'local_simulator', None, save_to_file=True)
print(inform)
# print(from_pickle(launcher.res_path)) # This is the same but from pickle
# print(from_pickle("test_data/toy-3-decision-exact-local_simulator-falqon-10-0.03-0-4.596928704106529.pkl"))
